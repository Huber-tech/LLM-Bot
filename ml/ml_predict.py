import pickle
import pandas as pd

try:
    with open("ml/best_trading_model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    model = None

def predict_trade_signal(market_data):
    if model is None or not market_data:
        return False

    df = None

    if isinstance(market_data, list) and all(isinstance(x, list) for x in market_data):
        # Wir nehmen nur die relevanten Spalten (erste 6)
        df = pd.DataFrame(market_data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ])
    elif isinstance(market_data, dict):
        df = pd.DataFrame([market_data])
    elif isinstance(market_data, list) and all(isinstance(x, dict) for x in market_data):
        df = pd.DataFrame(market_data)
    else:
        df = pd.DataFrame(market_data)

    # Jetzt sauber reduzieren:
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    df['return'] = df['close'].pct_change().fillna(0)
    df['rolling_mean'] = df['close'].rolling(window=10).mean().fillna(0)
    df['volatility'] = df['close'].rolling(window=10).std().fillna(0)

    features = df[['return', 'volatility', 'rolling_mean']].tail(1).fillna(0)

    prediction = model.predict(features)[0]
    return prediction == 1
