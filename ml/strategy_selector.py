import pandas as pd
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "paper_trades.csv")
LEADERBOARD_PATH = os.path.join(BASE_DIR, "strategy_leaderboard.json")

MIN_TRADES = 10
MIN_WINRATE = 0.5

def load_leaderboard():
    if os.path.exists(LEADERBOARD_PATH):
        with open(LEADERBOARD_PATH, "r") as f:
            return json.load(f)
    return {}

def save_leaderboard(board):
    with open(LEADERBOARD_PATH, "w") as f:
        json.dump(board, f, indent=2)

def update_leaderboard():
    if not os.path.exists(CSV_PATH):
        return {}

    df = pd.read_csv(CSV_PATH)
    if "strategy" not in df.columns or df.empty:
        return {}

    df = df[df["pnl"].notna()]
    if df.empty:
        return {}

    grouped = df.groupby("strategy").agg(
        trades=("strategy", "count"),
        wins=("pnl", lambda x: (x > 0).sum()),
        pnl_sum=("pnl", "sum")
    )
    grouped["winrate"] = grouped["wins"] / grouped["trades"]

    leaderboard = {}
    for strategy, row in grouped.iterrows():
        leaderboard[strategy] = {
            "trades": int(row["trades"]),
            "wins": int(row["wins"]),
            "pnl_sum": float(row["pnl_sum"]),
            "winrate": float(row["winrate"]),
            "active": bool(row["trades"] >= MIN_TRADES and row["winrate"] >= MIN_WINRATE)
        }

    if leaderboard:
        save_leaderboard(leaderboard)

    return leaderboard

def get_active_strategies():
    leaderboard = load_leaderboard()
    return [s for s, stats in leaderboard.items() if stats.get("active", True)]

if __name__ == "__main__":
    lb = update_leaderboard()
    print(f"Aktives Leaderboard:\n{json.dumps(lb, indent=2)}")
