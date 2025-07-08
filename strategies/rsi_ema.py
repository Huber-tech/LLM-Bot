from strategies.indicators import calculate_rsi, calculate_ema, calculate_atr

class RSIEMAStrategy:
    def __init__(self, rsi_period=14, ema_period=50):
        self.rsi_period = rsi_period
        self.ema_period = ema_period

    def generate_signal(self, ohlcv):
        closes = [row[4] for row in ohlcv]
        rsi = calculate_rsi(ohlcv, self.rsi_period)
        ema = calculate_ema(ohlcv, self.ema_period)
        price = closes[-1]

        # Long wenn RSI unter 32 UND über EMA (bullisher Dip)
        if rsi < 32 and price > ema:
            return "BUY"
        # Short wenn RSI über 68 UND unter EMA (bearisher Spike)
        elif rsi > 68 and price < ema:
            return "SELL"
        else:
            return None

    def sl_tp(self, entry, atr, side, market_state, volatility):
        sl_mult, tp_mult = self.get_sl_tp_mults(market_state, volatility)
        if side == "BUY":
            sl = entry - sl_mult * atr
            tp = entry + tp_mult * atr
        else:  # SELL
            sl = entry + sl_mult * atr
            tp = entry - tp_mult * atr
        return sl, tp

    @staticmethod
    def get_sl_tp_mults(market_state, volatility):
        if market_state == "trend":
            sl_mult = 1.2 if volatility < 0.01 else 2.0
            tp_mult = 2.5 if volatility < 0.01 else 5.0
        elif market_state == "sideways":
            sl_mult = 0.7
            tp_mult = 1.0
        else:  # volatile
            sl_mult = 2.5
            tp_mult = 5.0
        return sl_mult, tp_mult

    def score(self, ohlcv, market_type):
        # Sehr gut in trendarmen oder schwankenden Märkten
        if market_type == "sideways":
            return 1
        return 0
