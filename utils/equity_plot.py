import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_equity_curve(csv_file="paper_trades.csv", out_file="dashboard/static/equity_curve.png", start_balance=20.0):
    if not os.path.isfile(csv_file):
        # Wenn keine Trades existieren, einfach Startlinie plotten
        plt.figure(figsize=(10, 4))
        plt.plot([0, 1], [start_balance, start_balance], label="Equity")
        plt.xlabel("Trades")
        plt.ylabel("Balance")
        plt.title("Equity Curve")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out_file)
        plt.close()
        return

    df = pd.read_csv(csv_file)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    if "pnl" not in df.columns or df["pnl"].isnull().all():
        balances = [start_balance] * len(df)
    else:
        df_closed = df[df["pnl"].notna()]
        balances = [start_balance]
        for pnl in df_closed["pnl"]:
            balances.append(balances[-1] + pnl)
        balances = balances[1:]

    plt.figure(figsize=(10, 4))
    plt.plot(range(len(balances)), balances, label="Equity")
    plt.xlabel("Closed Trades")
    plt.ylabel("Balance")
    plt.title("Equity Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
