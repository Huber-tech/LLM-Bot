import pandas as pd
import matplotlib.pyplot as plt
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "paper_trades.csv")
REPORT_PATH = os.path.join(BASE_DIR, "logs", "performance_report.json")
EQUITY_CURVE_PATH = os.path.join(BASE_DIR, "logs", "equity_curve.png")

os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

def generate_report():
    if not os.path.exists(CSV_PATH):
        print("[REPORT] Keine paper_trades.csv gefunden.")
        return

    df = pd.read_csv(CSV_PATH)
    if df.empty or "pnl" not in df.columns:
        print("[REPORT] paper_trades.csv leer oder kein pnl-Feld.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["date"] = df["timestamp"].dt.date

    daily_pnl = df.groupby("date")["pnl"].sum()
    win_trades = df[df["pnl"] > 0]
    winrate = len(win_trades) / len(df) * 100 if len(df) > 0 else 0
    equity = df["pnl"].cumsum() + 1000  # Start Equity = 1000

    active_strategies = df["strategy"].value_counts().to_dict()

    # Save Equity Curve Plot
    plt.figure(figsize=(8,4))
    plt.plot(equity.index, equity.values)
    plt.title("Equity Curve")
    plt.xlabel("Trades")
    plt.ylabel("Equity")
    plt.tight_layout()
    plt.savefig(EQUITY_CURVE_PATH)
    plt.close()

    # Save Performance Report JSON
    report = {
        "total_trades": len(df),
        "winrate": round(winrate, 2),
        "latest_equity": round(equity.values[-1], 2),
        "active_strategies": active_strategies,
        "last_daily_pnl": round(daily_pnl.iloc[-1], 2) if not daily_pnl.empty else 0
    }

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    print("[REPORT] Performance Report + Equity Curve aktualisiert.")

if __name__ == "__main__":
    generate_report()
