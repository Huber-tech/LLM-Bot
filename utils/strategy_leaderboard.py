import pandas as pd
import os

class StrategyLeaderboard:
    def __init__(self, trades_csv="paper_trades.csv"):
        self.trades_csv = trades_csv

    def compute_leaderboard(self, min_trades=10, top_n=2):
        if not os.path.isfile(self.trades_csv):
            return []

        df = pd.read_csv(self.trades_csv)
        # Nur abgeschlossene Trades zählen
        df = df[df['pnl'].notnull()]
        if 'strategy' not in df.columns:
            return []

        stats = (
            df.groupby('strategy')
              .agg(trades=('pnl', 'count'),
                   wins=('pnl', lambda x: (x > 0).sum()),
                   losses=('pnl', lambda x: (x < 0).sum()),
                   winrate=('pnl', lambda x: round(100 * (x > 0).sum() / len(x), 2)),
                   total_pnl=('pnl', 'sum'),
                   avg_pnl=('pnl', 'mean'))
              .reset_index()
        )
        # Nur Strategien mit genug Trades
        stats = stats[stats['trades'] >= min_trades]
        # Sortiere nach Total-PnL (kannst du auch nach Winrate ändern)
        stats = stats.sort_values("total_pnl", ascending=False)
        # Wähle die besten N aus
        top_strategies = stats.head(top_n)["strategy"].tolist()
        return top_strategies, stats

    def is_strategy_enabled(self, strategy, min_trades=10, top_n=2):
        enabled_strats, _ = self.compute_leaderboard(min_trades=min_trades, top_n=top_n)
        return strategy in enabled_strats
