import asyncio
import os
import logging
from datetime import datetime

from core.client import BinanceClient
from core.trade_executor import TradeExecutor
from utils.logger import logger
from utils.reentry_manager import ReEntryManager
from utils.equity_protector import EquityProtector
from utils.trade_logger import log_trade
from utils.risk_manager import TradeRiskManager
from strategies.engine import StrategyEngine

PAPER = True
START_BALANCE = 1000
BALANCE = START_BALANCE

client = BinanceClient(testnet=PAPER)
executor = TradeExecutor(client)
reentry = ReEntryManager()
equity_protect = EquityProtector(START_BALANCE)
strategy_engine = StrategyEngine()
risk_manager = TradeRiskManager(initial_balance=START_BALANCE, leverage=1, max_exposure_pct=10.0, use_kelly=False)

async def handle_symbol(symbol):
    global BALANCE
    #logger.info(f"[INFO] Prüfe Symbol: {symbol}")

    if not reentry.can_reenter(symbol):
        logger.info(f"[INFO] Cooldown aktiv für {symbol}, überspringe.")
        return

    try:
        market_data = await client.fetch_market_data(symbol)
        if not market_data or len(market_data) < 1 or len(market_data[-1]) < 5:
            logger.warning(f"[DATA] Ungültige Marktdatenstruktur für {symbol}, überspringe.")
            return

        selected_strategy = strategy_engine.select_strategy(market_data)
        if selected_strategy is None:
            #logger.info(f"[INFO] Keine geeignete Strategie für {symbol}")
            return

        strategy_name = selected_strategy.__class__.__name__
        signal = selected_strategy.generate_signal(market_data)

        if signal != "BUY":
            #logger.info(f"[INFO] Strategy {strategy_name} liefert kein BUY-Signal für {symbol}.")
            return

        logger.info(f"[SIGNAL] Strategy {strategy_name} liefert BUY Entry für {symbol}")

        orderbook = await client.fetch_order_book(symbol)
        best_bid = float(orderbook['bids'][0][0])
        best_ask = float(orderbook['asks'][0][0])
        spread = (best_ask - best_bid) / best_bid

        if spread > 0.001:
            logger.info(f"[SPREAD] Spread zu hoch für {symbol}: {spread:.4%}, Trade übersprungen.")
            return

        best_bid_qty = float(orderbook['bids'][0][1])
        best_ask_qty = float(orderbook['asks'][0][1])
        bid_liquidity = best_bid_qty * best_bid
        ask_liquidity = best_ask_qty * best_ask

        if min(bid_liquidity, ask_liquidity) < 500:
            logger.info(f"[DEPTH] Liquidity zu gering für {symbol}: Bid {bid_liquidity:.2f}, Ask {ask_liquidity:.2f}, Trade übersprungen.")
            return

        latest_candle = market_data[-1]
        entry_price = float(latest_candle[4])
        stop_loss = entry_price * 0.98

        recovery_mode = equity_protect.should_reduce_risk()
        if recovery_mode:
            logger.warning(f"[RECOVERY] Recovery Mode aktiv für {symbol}: Risk auf 3% + Grid Entries erlaubt.")

        position_size = risk_manager.calculate_position_size(
            entry_price=entry_price,
            stop_loss=stop_loss,
            symbol=symbol,
            historical_data=market_data,
            recovery_mode=recovery_mode
        )

        if position_size <= 0:
            logger.info(f"[RISK] Position Size für {symbol} zu klein oder 0. Trade übersprungen.")
            return

        # Hauptorder
        trade = await executor.execute_trade(
            symbol=symbol,
            side="Buy",
            quantity=position_size,
            paper=True
        )

        logger.info(f"[PAPER] Entry für {symbol} bei {trade['entry_price']:.4f} (Strategy={strategy_name}, Qty={position_size})")

        # Grid Entries falls Recovery aktiv
        if recovery_mode:
            grid_levels = 2
            grid_step = 0.005  # 0.5% pro Stufe
            for i in range(1, grid_levels + 1):
                grid_price = entry_price * (1 - grid_step * i)
                grid_position_size = position_size
                await executor.execute_trade(
                    symbol=symbol,
                    side="Buy",
                    quantity=grid_position_size,
                    paper=True
                )
                logger.info(f"[RECOVERY] Grid Entry {i} für {symbol} @ {grid_price:.4f}, Qty={grid_position_size}")

        log_trade(
            symbol=symbol,
            side="Buy",
            entry_price=trade["entry_price"],
            stop_loss=trade.get("sl_price"),
            take_profit=trade.get("tp_price"),
            qty=position_size,
            strategy=strategy_name,
            leverage=1
        )

        equity_protect.update_balance(BALANCE)

    except Exception as e:
        logger.error(f"[ERROR] Fehler bei Symbol {symbol}: {e}")

async def main_loop():
    await client.initialize()

    try:
        while True:
            symbols = await client.get_top_volume_symbols(limit=30)
            await asyncio.gather(*(handle_symbol(symbol) for symbol in symbols))
            await asyncio.sleep(30)

    except Exception as e:
        logger.error(f"Main loop error: {e}")

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main_loop())
