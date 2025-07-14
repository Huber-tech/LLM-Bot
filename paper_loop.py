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
from strategies.engine import StrategyEngine

PAPER = True
START_BALANCE = 1000
BALANCE = START_BALANCE
TRADE_QUANTITY = 10

client = BinanceClient(testnet=PAPER)
executor = TradeExecutor(client)
reentry = ReEntryManager()
equity_protect = EquityProtector(START_BALANCE)
strategy_engine = StrategyEngine()

async def main_loop():
    global BALANCE

    await client.initialize()

    try:
        while True:
            symbols = await client.get_top_volume_symbols(limit=10)

            for symbol in symbols:
                logger.info(f"[INFO] Prüfe Symbol: {symbol}")

                if not reentry.can_reenter(symbol):
                    logger.info(f"[INFO] Cooldown aktiv für {symbol}, überspringe.")
                    continue

                market_data = await client.fetch_market_data(symbol)

                selected_strategy = strategy_engine.select_strategy(market_data)
                if selected_strategy is None:
                    logger.info(f"[INFO] Keine geeignete Strategie für {symbol}")
                    continue

                strategy_name = selected_strategy.__class__.__name__
                signal = selected_strategy.generate_signal(market_data)

                if signal != "BUY":
                    logger.info(f"[INFO] Strategy {strategy_name} liefert kein BUY-Signal für {symbol}.")
                    continue

                logger.info(f"[SIGNAL] Strategy {strategy_name} liefert BUY Entry für {symbol}")

                trade = await executor.execute_trade(
                    symbol=symbol,
                    side="Buy",
                    quantity=TRADE_QUANTITY,
                    paper=True
                )

                entry_price = trade["entry_price"]
                sl = trade.get("sl_price")
                tp = trade.get("tp_price")

                log_trade(
                    symbol=symbol,
                    side="Buy",
                    entry_price=entry_price,
                    stop_loss=sl,
                    take_profit=tp,
                    qty=TRADE_QUANTITY,
                    strategy=strategy_name,
                    leverage=1
                )

                logger.info(f"[PAPER] Entry für {symbol} bei {entry_price:.4f} (Strategy={strategy_name})")

                equity_protect.update_balance(BALANCE)
                if equity_protect.should_reduce_risk():
                    logger.warning("Equity-Protection aktiv! Risikoniveau reduzieren.")

            await asyncio.sleep(30)

    except Exception as e:
        logger.error(f"Main loop error: {e}")

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main_loop())
