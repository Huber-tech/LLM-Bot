# ml/ml_predict.py
import joblib
import pandas as pd

# Modell laden (Pfad ggf. anpassen)
ml_model = joblib.load('ml/best_trading_model.pkl')

FEATURES = [
    'open', 'high', 'low', 'close', 'volume',
    'rsi', 'ema', 'atr', 'bb_upper', 'bb_lower',
    'market_state', 'strategy', 'signal'
]

def predict_trade_signal(trade_dict):
    df = pd.DataFrame([trade_dict])
    # Kategorische Features umcodieren
    for col in ['market_state', 'strategy', 'signal']:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].astype('category').cat.codes
    # Fehlende Features füllen
    for f in FEATURES:
        if f not in df.columns:
            df[f] = 0
    X = df[FEATURES]
    prediction = ml_model.predict(X)[0]
    probability = ml_model.predict_proba(X)[0][1]
    return prediction, probability
