import os
import pandas as pd

class StrategyLeaderboard:
    def compute_leaderboard(self, min_trades=0, top_n=None):
        """
        Berechnet die Performance je Strategie und gibt die Top-N Strategien zurück.
        Rückgabewert: (enabled_strategies, stats_df)
         - enabled_strategies: Liste der Strategie-Namen mit Top-Performance (oder None)
         - stats_df: DataFrame mit Spalten ["strategy","trades","wins","losses","winrate","total_pnl","avg_pnl"]
        """
        if not os.path.isfile("paper_trades.csv"):
            # Keine Trades vorhanden
            stats_df = pd.DataFrame(columns=["strategy", "trades", "wins", "losses", "winrate", "total_pnl", "avg_pnl"])
            return (None, stats_df)
        df = pd.read_csv("paper_trades.csv")
        df_closed = df[df["pnl"].notna()]
        if df_closed.empty:
            stats_df = pd.DataFrame(columns=["strategy", "trades", "wins", "losses", "winrate", "total_pnl", "avg_pnl"])
            return (None, stats_df)
        stats_list = []
        grouped = df_closed.groupby("strategy")
        for strat_name, group in grouped:
            trades = len(group)
            wins = int((group["pnl"] > 0).sum())
            losses = int((group["pnl"] <= 0).sum())
            winrate = round((wins / trades * 100) if trades > 0 else 0.0, 2)
            total_pnl = round(group["pnl"].sum(), 2)
            avg_pnl = round((total_pnl / trades) if trades > 0 else 0.0, 2)
            stats_list.append({
                "strategy": strat_name,
                "trades": trades,
                "wins": wins,
                "losses": losses,
                "winrate": winrate,
                "total_pnl": total_pnl,
                "avg_pnl": avg_pnl
            })
        stats_df = pd.DataFrame(stats_list)
        # DataFrame nach Gesamt-PnL sortieren (beste Strategie zuerst)
        stats_df = stats_df.sort_values(by="total_pnl", ascending=False).reset_index(drop=True)
        enabled_strategies = None
        if top_n is not None:
            eligible = stats_df
            if min_trades:
                eligible = stats_df[stats_df["trades"] >= min_trades]
            if not eligible.empty:
                top_strats = eligible.sort_values(by="total_pnl", ascending=False).head(top_n)
                enabled_strategies = top_strats["strategy"].tolist()
        return (enabled_strategies, stats_df)
