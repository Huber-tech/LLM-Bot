# strategies/engine.py

from strategies.rsi_ema import RSIEMAStrategy
from strategies.breakout import BreakoutStrategy

class StrategyEngine:
    def __init__(self):
        self.strategies = [
            RSIEMAStrategy(),
            BreakoutStrategy()
        ]

    def evaluate_market(self, ohlcv):
        closes = [row[4] for row in ohlcv]
        change = abs(closes[-1] - closes[-20]) / closes[-20]
        if change > 0.02:
            return "trend"
        return "sideways"

    def select_strategy(self, ohlcv):
        market = self.evaluate_market(ohlcv)
        for strategy in self.strategies:
            if strategy.suits(market):
                return strategy
        return self.strategies[0]
