# strategies/breakout.py

class BreakoutStrategy:
    def suits(self, market_type: str) -> bool:
        return market_type == "trend"

    def generate_signal(self, ohlcv):
        highs = [c[2] for c in ohlcv[-20:]]
        lows = [c[3] for c in ohlcv[-20:]]
        close = ohlcv[-1][4]
        if close > max(highs[:-1]):
            return "BUY"
        elif close < min(lows[:-1]):
            return "SELL"
        return None

    def sl_tp(self, price, atr):
        sl = price - 1.0 * atr
        tp = price + 2.5 * atr
        return sl, tp
