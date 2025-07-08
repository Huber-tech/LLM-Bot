# utils/market_classifier.py

import numpy as np
from strategies.indicators import calculate_ema, calculate_atr

def classify_market(ohlcv):
    """
    Klassifiziert den Markt als 'trend', 'sideways' oder 'volatile' basierend auf EMA, ATR und Preisdynamik.
    """
    closes = [row[4] for row in ohlcv]
    highs = [row[2] for row in ohlcv]
    lows = [row[3] for row in ohlcv]

    # Trendbestimmung über EMA-Slope und Abstand
    ema50 = calculate_ema(ohlcv, 50)
    ema200 = calculate_ema(ohlcv, 200)
    price = closes[-1]
    slope = ema50 - ema50 if len(closes) < 52 else (ema50 - calculate_ema(ohlcv[-52:], 50))

    # ATR (Volatilität)
    atr = calculate_atr(ohlcv, 14)
    price_range = max(highs[-20:]) - min(lows[-20:])
    vola_ratio = atr / price if price != 0 else 0

    # Dynamische Schwellen (tune nach Wunsch!)
    strong_trend = abs(ema50 - ema200) / price > 0.01 and abs(slope) > 0.05 * price  # mind. 1% EMA-Diff, steile Steigung
    very_volatile = vola_ratio > 0.025 or price_range / price > 0.05  # 2.5% ATR oder 5% Range in 20 Kerzen

    if strong_trend:
        return "trend"
    elif very_volatile:
        return "volatile"
    else:
        return "sideways"
