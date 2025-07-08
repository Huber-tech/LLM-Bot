from strategies.indicators import calculate_ema

class RangeTradingStrategy:
    def suits(self, market_type: str) -> bool:
        return market_type == "sideways"

    def generate_signal(self, ohlcv):
        closes = [float(row[4]) for row in ohlcv]
        if len(closes) < 21:
            return None
        highs = [float(row[2]) for row in ohlcv[-21:]]
        lows = [float(row[3]) for row in ohlcv[-21:]]
        price = closes[-1]
        # Kauf am unteren Bereich, Verkauf am oberen Bereich der Range
        if price <= min(lows[:-1]) * 1.01:
            return "BUY"
        elif price >= max(highs[:-1]) * 0.99:
            return "SELL"
        return None

    
    def sl_tp(self, entry, atr, side, market_state, volatility):
        sl_mult, tp_mult = self.get_sl_tp_mults(market_state, volatility)
        if side == "BUY":
            sl = entry - sl_mult * atr
            tp = entry + tp_mult * atr
        else:
            sl = entry + sl_mult * atr
            tp = entry - tp_mult * atr
        return sl, tp

    @staticmethod
    def get_sl_tp_mults(market_state, volatility):
        if market_state == "sideways":
            sl_mult = 0.6
            tp_mult = 1.0
        elif market_state == "trend":
            sl_mult = 1.0
            tp_mult = 1.5
        else:  # volatile
            sl_mult = 1.5
            tp_mult = 3.0
        return sl_mult, tp_mult

