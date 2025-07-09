# utils/equity_reporter.py

import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_equity_curve(csv_path="paper_trades.csv", output_path="logs/equity_curve.png"):
    if not os.path.exists(csv_path):
        print("CSV nicht gefunden.")
        return

    df = pd.read_csv(csv_path)
    if df.empty or "pnl" not in df.columns:
        print("Ungültiges Format.")
        return

    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce").fillna(0)
    df["equity"] = df["pnl"].cumsum() + 100  # Start Equity 100
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    plt.figure(figsize=(10, 5))
    plt.plot(df["timestamp"], df["equity"], label="Equity")
    plt.title("📈 Equity-Kurve (Paper Trading)")
    plt.xlabel("Zeit")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
