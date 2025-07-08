import os
import csv
import time
from datetime import datetime
import ccxt
from tqdm import tqdm
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategies.indicators import calculate_ema, calculate_rsi, calculate_atr, calculate_bollinger_bands
from strategies.engine import StrategyEngine

# Konfiguration
EXCHANGE = ccxt.binance({
    'rateLimit': 1200,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

OUTPUT_FILE = "ml/training_data_backtest.csv"
SYMBOLS = ["BTC/USDC", "ETH/USDC", "SOL/USDC"]  # Beliebig erweiterbar
TIMEFRAME = "1h"
START_DATE = "2024-01-01T00:00:00Z"  # YYYY-MM-DDTHH:MM:SSZ
END_DATE = "2024-06-30T00:00:00Z"

# Helper
def parse_iso8601(date_str):
    return int(EXCHANGE.parse8601(date_str))

def ohlcv_to_dict(symbol, ohlcv, strategy, market_state):
    # ohlcv: [timestamp, open, high, low, close, volume]
    close = float(ohlcv[4])
    ema = calculate_ema([ohlcv], 1)     # Für Einzelkerze = Kerzenwert
    rsi = calculate_rsi([ohlcv], 1)
    atr = calculate_atr([ohlcv], 1)
    bb_upper, bb_lower = calculate_bollinger_bands([ohlcv], 1)
    return {
        "timestamp": datetime.utcfromtimestamp(ohlcv[0]/1000).isoformat(),
        "symbol": symbol,
        "open": ohlcv[1],
        "high": ohlcv[2],
        "low": ohlcv[3],
        "close": ohlcv[4],
        "volume": ohlcv[5],
        "ema": ema,
        "rsi": rsi,
        "atr": atr,
        "bb_upper": bb_upper,
        "bb_lower": bb_lower,
        "market_state": market_state,
        "strategy": strategy,
        "signal": "",    # Noch leer (optional für späteren Backtest/ML-Label)
        "result": ""
    }

def fetch_all_ohlcv(symbol, timeframe, since, until):
    all_candles = []
    limit = 1000
    now = since
    pbar = tqdm(desc=f"Lade {symbol}", total=(until-since)//(60*60*1000))
    while now < until:
        candles = EXCHANGE.fetch_ohlcv(symbol, timeframe, since=now, limit=limit)
        if not candles:
            break
        for c in candles:
            if c[0] > until:
                break
            all_candles.append(c)
        now = candles[-1][0] + 1
        pbar.update(len(candles))
        time.sleep(0.1)
    pbar.close()
    return all_candles

def main():
    # Setup
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline='') as f:
        fieldnames = [
            "timestamp", "symbol", "open", "high", "low", "close", "volume",
            "ema", "rsi", "atr", "bb_upper", "bb_lower",
            "market_state", "strategy", "signal", "result"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        engine = StrategyEngine()
        for symbol in SYMBOLS:
            since = parse_iso8601(START_DATE)
            until = parse_iso8601(END_DATE)
            ohlcv_data = fetch_all_ohlcv(symbol, TIMEFRAME, since, until)
            # Sliding-Window für Indikatoren und Strategieauswahl:
            window = []
            for row in tqdm(ohlcv_data, desc=f"Verarbeite {symbol}"):
                window.append(row)
                if len(window) > 50:
                    window = window[-50:]  # nur die letzten 50 Kerzen
                # Marktzustand und Strategie wählen:
                market_state = engine.evaluate_market(window) if len(window) >= 20 else ""
                strategy = engine.select_strategy(window).__class__.__name__ if len(window) >= 20 else ""
                writer.writerow(
                    ohlcv_to_dict(symbol, row, strategy, market_state)
                )

if __name__ == "__main__":
    main()
