from strategies.indicators import calculate_rsi

class ReversalStrategy:
    def suits(self, market_type: str) -> bool:
        # Nur sinnvoll im Seitwärtsmarkt
        return market_type == "sideways"

    def generate_signal(self, ohlcv):
        closes = [float(row[4]) for row in ohlcv]
        if len(closes) < 15:
            return None
        rsi = calculate_rsi(ohlcv, 14)
        if rsi > 75:
            return "SELL"
        elif rsi < 25:
            return "BUY"
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
            sl_mult = 0.8
            tp_mult = 1.3
        elif market_state == "trend":
            sl_mult = 1.3
            tp_mult = 1.7
        else:  # volatile
            sl_mult = 1.8
            tp_mult = 3.0
        return sl_mult, tp_mult
