import sys
import os
import asyncio
import pandas as pd

# Damit die Importe klappen, egal von wo du startest:
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ccxt.async_support as ccxt

from strategies.indicators import calculate_rsi, calculate_ema, calculate_atr, calculate_bollinger_bands
from strategies.rsi_ema import RSIEMAStrategy
from strategies.momentum import MomentumStrategy
from strategies.volatility import VolatilityStrategy
from strategies.breakout import BreakoutStrategy
from strategies.reversal import ReversalStrategy

STRATEGIES = [
    ("rsi_ema", RSIEMAStrategy()),
    ("momentum", MomentumStrategy()),
    ("volatility", VolatilityStrategy()),
    ("breakout", BreakoutStrategy()),
    ("reversal", ReversalStrategy())
]

async def fetch_ohlcv_ccxt(symbol, timeframe="1h", since=None, limit=1000):
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
    await exchange.close()
    return ohlcv

def simulate_trade(entry, side, sl, tp, ohlcv_next):
    for row in ohlcv_next:
        price = float(row[4])
        if side == "BUY":
            if price <= sl:
                return sl, (sl - entry)
            elif price >= tp:
                return tp, (tp - entry)
        elif side == "SELL":
            if price >= sl:
                return sl, (entry - sl)
            elif price <= tp:
                return tp, (entry - tp)
    return price, (price - entry) if side == "BUY" else (entry - price)

def run_backtest(symbol, ohlcv, out_csv="ml/backtest_results.csv", lookahead=10):
    results = []
    for i in range(50, len(ohlcv) - lookahead):
        sub_ohlcv = ohlcv[:i]
        future_ohlcv = ohlcv[i:i+lookahead]
        price = float(ohlcv[i][4])
        atr = calculate_atr(sub_ohlcv, 14)
        for strat_name, strat in STRATEGIES:
            signal = strat.generate_signal(sub_ohlcv)
            if signal:
                sl, tp = strat.sl_tp(price, atr)
                exit_price, pnl = simulate_trade(price, signal, sl, tp, future_ohlcv)
                results.append({
                    "timestamp": ohlcv[i][0],
                    "symbol": symbol,
                    "strategy": strat_name,
                    "side": signal,
                    "entry": price,
                    "sl": sl,
                    "tp": tp,
                    "exit": exit_price,
                    "pnl": pnl
                })
                
    out_dir = os.path.dirname(out_csv)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)
            
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"Backtest für {symbol} abgeschlossen – {len(results)} Trades.")

async def main(symbol="BTCUSDT", timeframe="1h", candles=1000, out_csv="ml/backtest_results.csv"):
    print(f"Lade OHLCV für {symbol}, Intervall {timeframe}, Anzahl {candles} ...")
    ohlcv = await fetch_ohlcv_ccxt(symbol, timeframe=timeframe, limit=candles)
    run_backtest(symbol, ohlcv, out_csv=out_csv)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTCUSDT", help="Symbol, z.B. BTCUSDT")
    parser.add_argument("--timeframe", default="1h", help="Kerzenintervall, z.B. 1h, 15m, 5m")
    parser.add_argument("--candles", type=int, default=1000, help="Anzahl Kerzen")
    parser.add_argument("--out", default="ml/backtest_results.csv", help="Ziel-Datei")
    args = parser.parse_args()
    asyncio.run(main(symbol=args.symbol, timeframe=args.timeframe, candles=args.candles, out_csv=args.out))
