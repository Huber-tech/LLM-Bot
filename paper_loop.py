import os
import sys
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import aiohttp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.client import BinanceClient
from core.trade_executor import TradeExecutor
from strategies.engine import StrategyEngine
from strategies.indicators import ATR
from utils.logger import logger
from utils.trade_logger import log_trade
from utils.trade_tracker import update_trade_pnls
from utils.risk_manager import RiskManager
from utils.cooldown_manager import CooldownManager
from utils.signal_filter import SignalFilter
from utils.drawdown_guard import DrawdownGuard
from utils.strategy_watchdog import StrategyWatchdog

# Einstellungen
load_dotenv()
PAPER = True
INTERVAL = 30
START_BALANCE = 20.0
SYMBOLS = []

# Bot-Komponenten
engine = StrategyEngine()
risk_manager = RiskManager(initial_balance=START_BALANCE, max_risk_per_trade=0.02)
cooldown = CooldownManager(cooldown_minutes=30)
signal_filter = SignalFilter()
drawdown_guard = DrawdownGuard(start_balance=START_BALANCE, max_loss_pct=5.0)
watchdog = StrategyWatchdog()

# Abruf der Top 100 USDC-Futures-Paare nach Volumen
async def get_top_usdc_symbols_by_volume(limit=100):
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            filtered = [
                d for d in data if d["symbol"].endswith("USDC") and float(d["quoteVolume"]) > 100000
            ]
            sorted_pairs = sorted(filtered, key=lambda x: float(x["quoteVolume"]), reverse=True)
            return [item["symbol"] for item in sorted_pairs[:limit]]

# Hauptloop
async def trade_loop():
    global SYMBOLS
    client = await BinanceClient.create(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
        testnet=os.getenv("USE_TESTNET", "True").lower() == "true"
    )
    executor = TradeExecutor(client)

    # Handelsuniversum bestimmen
    SYMBOLS = await get_top_usdc_symbols_by_volume(limit=100)

    logger.info(f"📊 Überwachte Paare: {', '.join(SYMBOLS[:10])} ...")

    try:
        while True:
            if drawdown_guard.loss_today_exceeded():
                logger.warning("🛑 Tagesverlustgrenze erreicht – Trading pausiert.")
                await asyncio.sleep(INTERVAL)
                continue

            for symbol in SYMBOLS:
                try:
                    ohlcv = await client.fetch_ohlcv(symbol, "1h", limit=50)
                    closes = [row[4] for row in ohlcv]
                    price = closes[-1]
                    atr = ATR(ohlcv, 14)[-1]

                    strategy = engine.select_strategy(ohlcv)
                    signal = strategy.generate_signal(ohlcv)

                    if not signal:
                        continue

                    if cooldown.is_in_cooldown(symbol):
                        logger.info(f"[COOLDOWN] {symbol}: aktiv – übersprungen.")
                        continue

                    if not signal_filter.passes_filters(ohlcv):
                        logger.info(f"[FILTER] {symbol}: Markt ungeeignet.")
                        continue

                    sl, tp = strategy.sl_tp(price, atr)
                    qty = risk_manager.calculate_position_size(entry_price=price, stop_loss=sl)

                    if qty <= 0:
                        logger.warning(f"[RISK] {symbol}: Ordergröße zu klein – übersprungen.")
                        continue

                    logger.info(f"[TRADE] {symbol}: {signal} @ {price:.2f} SL={sl:.2f} TP={tp:.2f} QTY={qty:.4f}")

                    result = await executor.execute_trade(
                        symbol=symbol,
                        side=signal,
                        quantity=qty,
                        sl=sl,
                        tp=tp,
                        paper=PAPER
                    )

                    log_trade(
                        symbol=symbol,
                        side=signal,
                        entry_price=result["entry_price"],
                        sl=sl,
                        tp=tp,
                        qty=qty,
                        strategy=strategy.__class__.__name__
                    )

                    cooldown.update_cooldown(symbol)

                except Exception as e:
                    logger.error(f"[{symbol}] Fehler im Loop: {e}")

            try:
                current_prices = {symbol: await client.get_futures_price(symbol) for symbol in SYMBOLS}
                update_trade_pnls(current_prices=current_prices)
            except Exception as e:
                logger.warning(f"[PnL] Preisabruf fehlgeschlagen: {e}")

            logger.info(f"⏳ Nächster Zyklus in {INTERVAL} Sekunden...\n")
            await asyncio.sleep(INTERVAL)

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(trade_loop())
