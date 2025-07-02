# strategies/rsi_ema.py

from strategies.indicators import EMA, RSI

class RSIEMAStrategy:
    def suits(self, market_type: str) -> bool:
        return market_type == "sideways"

    def generate_signal(self, ohlcv):
        closes = [row[4] for row in ohlcv]
        price = closes[-1]
        ema = EMA(closes, 20)[-1]
        rsi = RSI(closes, 14)[-1]

        if price > ema and rsi < 45:
            return "BUY"
        elif price < ema and rsi > 55:
            return "SELL"
        return None

    def sl_tp(self, price, atr):
        sl = price - 1.5 * atr
        tp = price + 3.0 * atr
        return sl, tp
