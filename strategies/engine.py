from strategies.rsi_ema import RSIEMAStrategy
from strategies.breakout import BreakoutStrategy
from strategies.momentum import MomentumStrategy
from strategies.reversal import ReversalStrategy
from strategies.range_trading import RangeTradingStrategy
from strategies.volatility import VolatilityStrategy
from ml.strategy_selector import get_active_strategies, update_leaderboard
from strategies.indicators import calculate_atr, calculate_ema, calculate_rsi, calculate_bollinger_bands

try:
    from ml.ml_predict import predict_trade_signal
except ImportError:
    predict_trade_signal = None

class StrategyEngine:
    def __init__(self):
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
        atr = abs(max(closes[-20:]) - min(closes[-20:])) / closes[-20]
        if atr > 0.04:
            return "volatile"
        return "sideways"

    def select_strategy(self, ohlcv):
        update_leaderboard()
        active_strategy_names = get_active_strategies()
        market = self.evaluate_market(ohlcv)

        candidates = []
        for strategy in self.strategies:
            s_name = strategy.__class__.__name__
            if active_strategy_names and s_name not in active_strategy_names:
                continue
            if hasattr(strategy, "suits") and strategy.suits(market):
                candidates.append(strategy)

        if candidates and predict_trade_signal:
            open_val = float(ohlcv[-1][1]); high_val = float(ohlcv[-1][2])
            low_val = float(ohlcv[-1][3]); close_val = float(ohlcv[-1][4])
            volume_val = float(ohlcv[-1][5])
            atr_val = calculate_atr(ohlcv, 14)
            ema_val = calculate_ema(ohlcv, 50)
            rsi_val = calculate_rsi(ohlcv, 14)
            bb_upper_val, bb_lower_val = calculate_bollinger_bands(ohlcv, 20, 2)

            best_strat = None
            best_prob = 0.0
            for strat in candidates:
                try:
                    test_signal = strat.generate_signal(ohlcv)
                except Exception:
                    test_signal = None
                if not test_signal:
                    continue

                features = {
                    "open": open_val, "high": high_val, "low": low_val, "close": close_val, "volume": volume_val,
                    "rsi": rsi_val, "ema": ema_val, "atr": atr_val,
                    "bb_upper": bb_upper_val, "bb_lower": bb_lower_val,
                    "market_state": market, "strategy": strat.__class__.__name__, "signal": test_signal
                }
                try:
                    pred, prob = predict_trade_signal(features)
                except Exception:
                    pred, prob = None, 0.0
                if pred == 1 and prob >= best_prob:
                    best_prob = prob
                    best_strat = strat

            if best_strat:
                return best_strat

        if candidates:
            return candidates[0]

        for strategy in self.strategies:
            if strategy.__class__.__name__ in active_strategy_names:
                return strategy

        for strategy in self.strategies:
            if hasattr(strategy, "suits") and strategy.suits(market):
                return strategy

        return self.strategies[0]
