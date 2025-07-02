# utils/equity_plot.py

import pandas as pd
import matplotlib.pyplot as plt

def plot_equity_curve(csv_file="paper_trades.csv", out_file="equity_curve.png"):
    df = pd.read_csv(csv_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Equity berechnen
    equity = []
    balance = 20  # Startwert
    for _, row in df.iterrows():
        if pd.notna(row["pnl"]):
            balance += row["pnl"]
        equity.append(balance)

    df["equity"] = equity

    plt.figure(figsize=(10, 5))
    plt.plot(df["timestamp"], df["equity"], label="Equity Curve", color="green")
    plt.title("Equity Curve (Paper-Trades)")
    plt.xlabel("Zeit")
    plt.ylabel("USDC")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
