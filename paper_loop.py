import os
import sys
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import aiohttp
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.client import BinanceClient
from core.trade_executor import TradeExecutor
from strategies.engine import StrategyEngine
from strategies.indicators import calculate_atr, calculate_ema, calculate_rsi, calculate_bollinger_bands
from utils.logger import logger
from utils.trade_logger import log_trade
from utils.trade_tracker import update_trade_pnls
from utils.risk_manager import RiskManager, TradeRiskManager
from utils.cooldown_manager import CooldownManager
from utils.signal_filter import SignalFilter
from utils.drawdown_guard import DrawdownGuard
from utils.strategy_watchdog import StrategyWatchdog
from utils.email_notify import send_email
from ml.collect_training_data import append_training_data
from utils.trailing_stop import update_trailing_stops
from utils.grid_manager import GridManager
from utils.reentry_manager import ReEntryManager
from utils.strategy_blocklist import StrategyBlocklist
from utils.equity_protector import EquityProtector
from utils.equity_tracker import update_equity_snapshot
try:
    from ml.ml_predict import predict_trade_signal
except ImportError:
    predict_trade_signal = None

load_dotenv()
ML_LOGGING = os.getenv("ENABLE_TRAINING_DATA", "true").lower() == "true"

# SYSTEM-SETUP
PAPER = True
INTERVAL = 30
START_BALANCE = float(os.getenv("START_BALANCE", "20.0"))
LEVERAGE = 5
SYMBOLS = []

grid = GridManager()
reentry = ReEntryManager()
blocklist = StrategyBlocklist()
equity_protect = EquityProtector()
engine = StrategyEngine()
cooldown = CooldownManager(cooldown_minutes=30)
signal_filter = SignalFilter()
drawdown_guard = DrawdownGuard(start_balance=START_BALANCE, max_loss_pct=5.0)
strategy_watchdog = StrategyWatchdog()
daily_risk = RiskManager()
risk_manager = TradeRiskManager(initial_balance=START_BALANCE, leverage=LEVERAGE)

def has_open_trade(symbol, trades_csv="paper_trades.csv"):
    if not os.path.isfile(trades_csv):
        return False
    df = pd.read_csv(trades_csv)
    df_symbol = df[df["symbol"] == symbol]
    open_trades = df_symbol[df_symbol["pnl"].isnull() | (df_symbol["pnl"] == "")]
    return not open_trades.empty

async def get_top_usdc_symbols_by_volume(limit=100):
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            filtered = [d for d in data if d["symbol"].endswith("USDC") and float(d["quoteVolume"]) > 100000]
            sorted_pairs = sorted(filtered, key=lambda x: float(x["quoteVolume"]), reverse=True)
            return [item["symbol"] for item in sorted_pairs[:limit]]

async def execute_grid_recovery(symbol, signal, price, qty, sl, tp, executor):
    try:
        levels = 3
        grid_prices = grid.generate_grid_orders(price, side=signal)
        for level_price in grid_prices:
            recovery_qty = grid.scale_order_qty(qty / levels)
            logger.info(f"[GRID] {symbol}: Recovery-Level {signal} @ {level_price:.2f}, QTY={recovery_qty:.4f}")
            await executor.execute_trade(
                symbol=symbol,
                side=signal,
                quantity=recovery_qty,
                sl=sl,
                tp=tp,
                paper=PAPER,
                custom_price=level_price
            )
    except Exception as e:
        logger.warning(f"[GRID] {symbol}: Grid-Ausführung fehlgeschlagen: {e}")

async def trade_task(symbol, client, executor):
    try:
        if has_open_trade(symbol):
            logger.info(f"[POSITION] {symbol}: Offene Position vorhanden – übersprungen.")
            return
        if not reentry.can_reenter(symbol):
            logger.info(f"[REENTRY] {symbol}: Cooldown nach Verlust aktiv – übersprungen.")
            return

        ohlcv = await client.fetch_ohlcv(symbol, "1h", limit=50)
        closes = [float(row[4]) for row in ohlcv if str(row[4]).replace('.', '', 1).isdigit()]
        price = closes[-1]
        atr = calculate_atr(ohlcv, 14)
        ema = calculate_ema(ohlcv, 50)
        rsi = calculate_rsi(ohlcv, 14)
        bb_upper, bb_lower = calculate_bollinger_bands(ohlcv, 20, 2)

        strategy = engine.select_strategy(ohlcv)
        strategy_name = strategy.__class__.__name__
        if blocklist.is_blocked(strategy_name):
            logger.info(f"[BLOCKED] {symbol}: {strategy_name} gesperrt – übersprungen.")
            return
        signal = strategy.generate_signal(ohlcv)
        market_state = engine.evaluate_market(ohlcv)

        if market_state == "volatile" and signal in ["BUY", "SELL"] and not has_open_trade(symbol):
            sl, tp = strategy.sl_tp(price, atr, signal, market_state, atr / price)
            qty = risk_manager.calculate_position_size(entry_price=price, stop_loss=sl)
            if qty > 0:
                logger.warning(f"[GRID-MODE] {symbol}: Volatilität erkannt – starte Grid-Trading.")
                await execute_grid_recovery(symbol, signal, price, qty, sl, tp, executor)
                return

        if ML_LOGGING:
            append_training_data(
                timestamp=datetime.utcnow().isoformat(),
                symbol=symbol,
                open_=ohlcv[-1][1], high=ohlcv[-1][2], low=ohlcv[-1][3], close=ohlcv[-1][4],
                volume=ohlcv[-1][5], rsi=rsi, ema=ema, atr=atr, bb_upper=bb_upper, bb_lower=bb_lower,
                market_state=market_state, strategy=strategy_name, signal=signal,
                result=None, type="paper"
            )
        if not signal:
            logger.info(f"[FILTER] {symbol}: Kein Signal.")
            return
        if cooldown.is_in_cooldown(symbol):
            logger.info(f"[COOLDOWN] {symbol}: aktiv – übersprungen.")
            return
        if not signal_filter.passes_filters(ohlcv):
            logger.info(f"[FILTER] {symbol}: Markt ungeeignet – übersprungen.")
            return
        if predict_trade_signal:
            features = {
                "open": float(ohlcv[-1][1]), "high": float(ohlcv[-1][2]), "low": float(ohlcv[-1][3]), "close": float(ohlcv[-1][4]), "volume": float(ohlcv[-1][5]),
                "rsi": rsi, "ema": ema, "atr": atr, "bb_upper": bb_upper, "bb_lower": bb_lower,
                "market_state": market_state, "strategy": strategy_name, "signal": signal
            }
            try:
                pred, prob = predict_trade_signal(features)
            except Exception:
                pred, prob = None, 0.0
            if pred == 0:
                logger.info(f"[ML] {symbol}: Modell prognostiziert Verlust (Wahrscheinlichkeit {prob*100:.1f}%) – Trade übersprungen.")
                return

        sl, tp = strategy.sl_tp(price, atr, signal, market_state, atr / price)
        qty = risk_manager.calculate_position_size(entry_price=price, stop_loss=sl)
        if equity_protect.should_reduce_risk():
            qty *= 0.5
        if qty <= 0 or qty > 10000:
            logger.warning(f"[RISK] {symbol}: Ordergröße unzulässig – übersprungen.")
            return
        logger.info(f"[TRADE] {symbol}: {signal} @ {price:.4f} SL={sl:.4f} TP={tp:.4f} QTY={qty:.4f} Leverage={risk_manager.leverage}")
        result = await executor.execute_trade(symbol=symbol, side=signal, quantity=qty, sl=sl, tp=tp, paper=PAPER)
        log_trade(symbol=symbol, side=signal, entry_price=result["entry_price"], stop_loss=sl, take_profit=tp, qty=qty, strategy=strategy_name, leverage=risk_manager.leverage)
        cooldown.update_cooldown(symbol)

        if ML_LOGGING:
            append_training_data(
                timestamp=datetime.utcnow().isoformat(),
                symbol=symbol,
                open_=ohlcv[-1][1], high=ohlcv[-1][2], low=ohlcv[-1][3], close=ohlcv[-1][4],
                volume=ohlcv[-1][5], rsi=rsi, ema=ema, atr=atr, bb_upper=bb_upper, bb_lower=bb_lower,
                market_state=market_state, strategy=strategy_name, signal=signal,
                result=(result.get("pnl") if result else None), type="paper"
            )

        strategy_watchdog.evaluate(strategy_name)

    except Exception as e:
        logger.error(f"[{symbol}] Fehler im Trade: {e}")
        if "exchangeInfo" not in str(e):
            send_email(subject=f"TradingBot ERROR [{symbol}]", body=f"Fehler im Trading-Bot für {symbol}:\n{e}")

async def trade_loop():
    global SYMBOLS
    client = await BinanceClient.create(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
        testnet=os.getenv("USE_TESTNET", "True").lower() == "true"
    )
    executor = TradeExecutor(client)
    try:
        SYMBOLS = await get_top_usdc_symbols_by_volume(limit=25)
        logger.info(f"📊 Überwachte Paare: {', '.join(SYMBOLS[:10])} ...")
        while True:
            update_equity_snapshot()
            if not daily_risk.is_within_limit():
                logger.warning("🛑 Maximaler Tagesdrawdown (Equity) erreicht – pausiert.")
                await asyncio.sleep(INTERVAL)
                continue
            if drawdown_guard.loss_today_exceeded():
                logger.warning("🛑 Tagesverlustgrenze erreicht – pausiert.")
                await asyncio.sleep(INTERVAL)
                continue
            tasks = [trade_task(symbol, client, executor) for symbol in SYMBOLS]
            await asyncio.gather(*tasks)
            try:
                current_prices = {symbol: await client.get_futures_price(symbol) for symbol in SYMBOLS}
                atr_lookup = {symbol: calculate_atr(await client.fetch_ohlcv(symbol, "1h", limit=50), 14) for symbol in SYMBOLS}
                update_trailing_stops("paper_trades.csv", current_prices)
                closed_losses = update_trade_pnls(current_prices=current_prices, atr_lookup=atr_lookup)
                for (sym, side, entry_price, qty, sl, tp) in closed_losses:
                    reentry.register_loss(sym)
                    logger.warning(f"[LOSS] {sym}: Trade mit Verlust geschlossen – starte Grid-Recovery.")
                    await execute_grid_recovery(sym, side, entry_price, qty, sl, tp, executor)
                df_all = pd.read_csv("paper_trades.csv")
                total_closed_pnl = df_all[df_all["pnl"].notna()]["pnl"].sum()
                current_balance = START_BALANCE + total_closed_pnl
                risk_manager.update_balance(current_balance)
            except Exception as e:
                logger.warning(f"[PnL] Fehler beim Preisabruf: {e}")
            logger.info(f"⏳ Nächster Zyklus in {INTERVAL} Sekunden...\n")
            await asyncio.sleep(INTERVAL)
    finally:
        await client.close()
