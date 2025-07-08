from strategies.rsi_ema import RSIEMAStrategy
from strategies.breakout import BreakoutStrategy
from strategies.momentum import MomentumStrategy
from strategies.reversal import ReversalStrategy
from strategies.range_trading import RangeTradingStrategy
from strategies.volatility import VolatilityStrategy
from utils.strategy_leaderboard import StrategyLeaderboard

class StrategyEngine:
    def __init__(self):
        self.leaderboard = StrategyLeaderboard()
        self.strategies = [
            RSIEMAStrategy(),
            BreakoutStrategy(),
            MomentumStrategy(),
            ReversalStrategy(),
            RangeTradingStrategy(),
            VolatilityStrategy()
        ]
        

    def evaluate_market(self, ohlcv):
        closes = [float(row[4]) for row in ohlcv]
        if len(closes) < 21:
            return "sideways"
        change = abs(closes[-1] - closes[-20]) / closes[-20]
        if change > 0.03:
            return "trend"
        # Einfache Volatilitätsbestimmung
        atr = abs(max(closes[-20:]) - min(closes[-20:])) / closes[-20]
        if atr > 0.04:
            return "volatile"
        return "sideways"

    def select_strategy(self, ohlcv):
        enabled_strats, _ = self.leaderboard.compute_leaderboard(min_trades=10, top_n=2)
        market = self.evaluate_market(ohlcv)
        candidates = []
        for strategy in self.strategies:
            s_name = strategy.__class__.__name__
            if enabled_strats and s_name not in enabled_strats:
                continue  # Nur Top-Strategien verwenden!
            if hasattr(strategy, "suits"):
                if strategy.suits(market):
                    candidates.append(strategy)
            else:
                candidates.append(strategy)

        if candidates:
            return candidates[0]
        # Neu: Nimm beste Strategie aus enabled_strats (auch wenn sie nicht perfekt zum Markt passt)
        if enabled_strats:
            for strategy in self.strategies:
                if strategy.__class__.__name__ in enabled_strats:
                    return strategy
        # Noch härterer Fallback: erste in der Liste
        return self.strategies[0]


