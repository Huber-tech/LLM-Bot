import os
import sys
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.collect_training_data import append_training_data

def analyze_backtest(backtest_csv_path="ml/backtest_results.csv"):
    df = pd.read_csv(backtest_csv_path)
    print(f"Analysiere {len(df)} Backtest-Trades aus {backtest_csv_path}")

    for idx, row in df.iterrows():
        append_training_data(
            timestamp=row.get("timestamp", datetime.utcnow().isoformat()),
            symbol=row.get("symbol", ""),
            open_=row.get("open", ""),
            high=row.get("high", ""),
            low=row.get("low", ""),
            close=row.get("close", ""),
            volume=row.get("volume", ""),
            rsi=row.get("rsi", ""),
            ema=row.get("ema", ""),
            atr=row.get("atr", ""),
            bb_upper=row.get("bb_upper", ""),
            bb_lower=row.get("bb_lower", ""),
            market_state=row.get("market_state", ""),
            strategy=row.get("strategy", ""),
            signal=row.get("signal", ""),
            result=row.get("result", ""),
            type="backtest"
        )
    print("Alle Backtest-Trades wurden ins Training-CSV geschrieben.")

if __name__ == "__main__":
    analyze_backtest()
