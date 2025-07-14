import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import pickle

ML_LOGGING = os.getenv("ENABLE_TRAINING_DATA", "true").lower() == "true"

CSV_FILE = "ml/training_data.csv"
df = pd.read_csv(CSV_FILE)

filter_type = os.getenv("FEAT_TYPE", "paper")
df = df[df["type"] == filter_type]

# Nur Trades mit Signal und Result
df_trades = df[df["signal"].notna() & df["result"].notna()]

# Zusätzliche Feature-Berechnungen falls noch nicht vorhanden
df_trades["high_low_range"] = (df_trades["high"] - df_trades["low"]) / df_trades["close"]
df_trades["atr_relative"] = df_trades["atr"] / df_trades["close"]
df_trades["hour"] = pd.to_datetime(df_trades["timestamp"]).dt.hour
df_trades["weekday"] = pd.to_datetime(df_trades["timestamp"]).dt.weekday

# Prüfen ob Spalten fehlen und ggf. ergänzen
def ensure_column(df, col, default=0):
    if col not in df.columns:
        df[col] = default

for col in ['market_state', 'strategy']:
    ensure_column(df_trades, col)

features = [
    'open', 'high', 'low', 'close', 'volume',
    'rsi', 'ema', 'atr', 'bb_upper', 'bb_lower',
    'market_state', 'strategy'
]

X = df_trades[features]
y = (df_trades["result"] > 0).astype(int)  # 1 = Gewinn, 0 = Verlust

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print(classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

cv_scores = cross_val_score(clf, X, y, cv=5)
print(f"Cross-Validation Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

with open("ml/best_trading_model.pkl", "wb") as f:
    pickle.dump(clf, f)

df_trades[features + ["result"]].to_csv("ml/training_features.csv", index=False)

print("✅ Feature-Engineering & Modelltraining abgeschlossen. Modell gespeichert als best_trading_model.pkl.")
