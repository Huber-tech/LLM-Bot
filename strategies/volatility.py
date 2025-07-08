from strategies.indicators import calculate_atr, calculate_ema

class VolatilityStrategy:
    def suits(self, market_type: str) -> bool:
        return market_type == "volatile"

    def generate_signal(self, ohlcv):
        closes = [float(row[4]) for row in ohlcv]
        if len(closes) < 50:
            return None
        atr = calculate_atr(ohlcv, 14)
        ema50 = calculate_ema(ohlcv, 50)
        price = closes[-1]
        if atr > price * 0.02:  # Nur sehr volatile Märkte
            if price > ema50:
                return "BUY"
            elif price < ema50:
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
        if market_state == "volatile":
            sl_mult = 3.0
            tp_mult = 6.0
        elif market_state == "trend":
            sl_mult = 2.0
            tp_mult = 4.0
        else:  # sideways
            sl_mult = 1.2
            tp_mult = 1.6
        return sl_mult, tp_mult
