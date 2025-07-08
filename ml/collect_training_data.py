import csv
import os
from threading import Lock

file_lock = Lock()

def append_training_data(
    timestamp,
    symbol,
    open_,
    high,
    low,
    close,
    volume,
    rsi,
    ema,
    atr,
    bb_upper,
    bb_lower,
    market_state,
    strategy,
    signal,
    result,
    type="live",
    filename="ml/training_data.csv"
):
    """
    Loggt einen Datensatz für das ML-Training.
    """
    fieldnames = [
        "timestamp", "symbol", "open", "high", "low", "close", "volume", "rsi", "ema", "atr",
        "bb_upper", "bb_lower", "market_state", "strategy", "signal", "result", "type"
    ]
    file_exists = os.path.isfile(filename)
    data = {
        "timestamp": timestamp,
        "symbol": symbol,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "rsi": rsi,
        "ema": ema,
        "atr": atr,
        "bb_upper": bb_upper,
        "bb_lower": bb_lower,
        "market_state": market_state,
        "strategy": strategy,
        "signal": signal,
        "result": result,
        "type": type
    }
    with file_lock:
        with open(filename, mode="a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
