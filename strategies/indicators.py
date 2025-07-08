import numpy as np

def calculate_rsi(ohlcv, period=14):
    closes = [float(row[4]) for row in ohlcv if str(row[4]).replace('.', '', 1).isdigit()]
    if len(closes) < period + 1:
        return 50.0
    deltas = np.diff(closes)
    gain = np.where(deltas > 0, deltas, 0).sum() / period
    loss = -np.where(deltas < 0, deltas, 0).sum() / period
    if loss == 0:
        return 100.0
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_ema(ohlcv, period=14):
    closes = [float(row[4]) for row in ohlcv if str(row[4]).replace('.', '', 1).isdigit()]
    if len(closes) < period:
        return closes[-1] if closes else 0.0
    ema = np.mean(closes[-period:])
    multiplier = 2 / (period + 1)
    for price in closes[-period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_atr(ohlcv, period=14):
    if len(ohlcv) < period + 1:
        return 0.0
    high = [float(row[2]) for row in ohlcv]
    low = [float(row[3]) for row in ohlcv]
    close = [float(row[4]) for row in ohlcv]
    tr = []
    for i in range(1, len(ohlcv)):
        tr.append(max(
            high[i] - low[i],
            abs(high[i] - close[i-1]),
            abs(low[i] - close[i-1])
        ))
    if len(tr) < period:
        return np.mean(tr) if tr else 0.0
    atr = np.mean(tr[-period:])
    return atr

def calculate_bollinger_bands(ohlcv, period=20, multiplier=2):
    closes = [float(row[4]) for row in ohlcv if str(row[4]).replace('.', '', 1).isdigit()]
    if len(closes) < period:
        return (0.0, 0.0)
    moving_avg = np.mean(closes[-period:])
    std_dev = np.std(closes[-period:])
    upper_band = moving_avg + (std_dev * multiplier)
    lower_band = moving_avg - (std_dev * multiplier)
    return upper_band, lower_band
