#!/usr/bin/env python3
# bot.py — Version 1.0.1

import os
import asyncio
from dotenv import load_dotenv
from core.client import BinanceClient
from core.trade_executor import TradeExecutor
from utils.backtester import Backtester
from utils.logger import logger

__version__ = "1.0.1"

def load_config():
    load_dotenv()
    return {
        "api_key": os.getenv("BINANCE_API_KEY"),
        "api_secret": os.getenv("BINANCE_API_SECRET"),
        "testnet": os.getenv("USE_TESTNET", "True").lower() == "true",
        "symbol": os.getenv("SYMBOL", "BTCUSDC"),
        "backtest_start": os.getenv("BACKTEST_START", "2025-01-01T00:00"),
        "backtest_end": os.getenv("BACKTEST_END", "2025-06-01T00:00"),
        "granularity": os.getenv("GRANULARITY", "1h"),
        "initial_balance": float(os.getenv("INITIAL_BALANCE", "20.0")),
        "trade_quantity": float(os.getenv("TRADE_QUANTITY", "0.001")),
        "paper_trading": os.getenv("PAPER_TRADING", "True").lower() == "true",
        "atr_period": int(os.getenv("ATR_PERIOD", "14")),
        "sl_multiplier": float(os.getenv("SL_MULTIPLIER", "1.5")),
        "tp_multiplier": float(os.getenv("TP_MULTIPLIER", "3.0")),
        "martingale_factor": float(os.getenv("MARTINGALE_FACTOR", "1.0")),
    }

async def main():
    cfg = load_config()
    logger.info(f"🚀 Starting Grok-FuturesBot v{__version__}")

    # 1) Backtest
    logger.info("🔍 Running backtest…")
    bt = Backtester(
        symbol=cfg["symbol"],
        start=cfg["backtest_start"],
        end=cfg["backtest_end"],
        granularity=cfg["granularity"],
        initial_balance=cfg["initial_balance"],
    )
    await bt.run()

    # 2) Live-/Paper-Trading Beispiel
    logger.info("💡 Starting live/paper trading example…")
    client = await BinanceClient.create(
        api_key=cfg["api_key"],
        api_secret=cfg["api_secret"],
        testnet=cfg["testnet"],
    )
    executor = TradeExecutor(client)
    result = await executor.execute_trade(
        symbol=cfg["symbol"],
        side="BUY",
        quantity=cfg["trade_quantity"],
        atr_period=cfg["atr_period"],
        sl_multiplier=cfg["sl_multiplier"],
        tp_multiplier=cfg["tp_multiplier"],
        martingale_factor=cfg["martingale_factor"],
        paper=cfg["paper_trading"],
    )
    logger.info(
        f"🎯 Trade result (paper={cfg['paper_trading']}): Entry={result['entry_price']}, SL={result['sl_price']}, TP={result['tp_price']}"
    )

if __name__ == "__main__":
    asyncio.run(main())
