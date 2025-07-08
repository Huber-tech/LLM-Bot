from strategies.indicators import calculate_ema

class MomentumStrategy:
    def suits(self, market_type: str) -> bool:
        # Nur in klaren Trends sinnvoll!
        return market_type == "trend"

    def generate_signal(self, ohlcv):
        closes = [float(row[4]) for row in ohlcv]
        if len(closes) < 11:
            return None
        # Momentum = aktueller Schluss minus vor 10 Perioden
        momentum = closes[-1] - closes[-10]
        if momentum > 0:
            return "BUY"
        elif momentum < 0:
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
        if market_state == "trend":
            sl_mult = 1.2 if volatility < 0.01 else 2.0
            tp_mult = 2.0 if volatility < 0.01 else 4.0
        elif market_state == "sideways":
            sl_mult = 0.8
            tp_mult = 1.2
        else:  # volatile
            sl_mult = 2.0
            tp_mult = 5.0
        return sl_mult, tp_mult
