from strategies.indicators import calculate_atr

class BreakoutStrategy:
    def generate_signal(self, ohlcv):
        closes = [row[4] for row in ohlcv]
        highs = [row[2] for row in ohlcv[-21:]]
        lows = [row[3] for row in ohlcv[-21:]]
        price = closes[-1]

        # Buy-Breakout: schließt über dem lokalen Hoch der letzten 20 Kerzen, mit Volumenfilter
        if price > max(highs[:-1]) and ohlcv[-1][5] > sum([row[5] for row in ohlcv[-11:-1]])/10:
            return "BUY"
        # Sell-Breakout: schließt unter dem lokalen Tief der letzten 20 Kerzen
        elif price < min(lows[:-1]) and ohlcv[-1][5] > sum([row[5] for row in ohlcv[-11:-1]])/10:
            return "SELL"
        else:
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
            sl_mult = 1.5 if volatility < 0.01 else 2.5
            tp_mult = 3.5 if volatility < 0.01 else 7.0
        elif market_state == "sideways":
            sl_mult = 1.0
            tp_mult = 1.2
        else:  # volatile
            sl_mult = 3.0
            tp_mult = 6.0
        return sl_mult, tp_mult

    def score(self, ohlcv, market_type):
        # Perfekt in klaren Trendphasen!
        if market_type == "trend":
            return 2
        return 0
