# ml/strategy_selector.py

import pandas as pd
import os

CSV_PATH = "paper_trades.csv"

def select_top_strategies(n=3, min_trades=10):
    if not os.path.exists(CSV_PATH):
        return []

    df = pd.read_csv(CSV_PATH)
    if "strategy" not in df.columns or df.empty:
        return []

    df = df[df["pnl"].notna()]
    grouped = df.groupby("strategy").agg(
        trades=("strategy", "count"),
        wins=("pnl", lambda x: (x > 0).sum()),
        pnl_sum=("pnl", "sum")
    )
    grouped["winrate"] = grouped["wins"] / grouped["trades"]
    grouped = grouped[grouped["trades"] >= min_trades]
    grouped = grouped.sort_values(by=["pnl_sum", "winrate"], ascending=False)
    return list(grouped.head(n).index)
