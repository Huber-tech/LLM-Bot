# utils/signal_filter.py

from strategies.indicators import EMA, ATR

class SignalFilter:
    def __init__(self, volume_factor=1.2, atr_threshold=0.001, trend_strength=0.001):
        self.volume_factor = volume_factor       # z. B. 1.2x über 10er-Avg
        self.atr_threshold = atr_threshold       # z. B. mind. 0.1 % Bewegung
        self.trend_strength = trend_strength     # z. B. Preisabstand zu EMA20 > 0.1 %

    def passes_filters(self, ohlcv) -> bool:
        closes = [c[4] for c in ohlcv]
        highs = [c[2] for c in ohlcv]
        lows = [c[3] for c in ohlcv]
        volumes = [c[5] for c in ohlcv]

        # Trend-Erkennung
        ema = EMA(closes, 20)[-1]
        price = closes[-1]
        trend_diff = abs(price - ema) / ema
        if trend_diff < self.trend_strength:
            return False  # Kein klarer Trend

        # Volumen-Filter
        avg_vol = sum(volumes[-11:-1]) / 10
        if volumes[-1] < avg_vol * self.volume_factor:
            return False  # Kein Volumenimpuls

        # ATR-basierte Volatilitätsprüfung
        atr = ATR(ohlcv, 14)[-1]
        if atr / price < self.atr_threshold:
            return False  # Markt zu ruhig

        return True  # Alles passt
