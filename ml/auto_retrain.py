import pandas as pd
import os
import pickle
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "paper_trades.csv")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "best_trading_model.pkl")
LOG_FILE = os.path.join(BASE_DIR, "logs", "auto_retrain.log")

# Logging korrekt in File und stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

MIN_TRAIN_ROWS = 200

def load_data():
    if not os.path.exists(CSV_PATH):
        logger.info("[RETRAIN] Keine paper_trades.csv gefunden. Retrain übersprungen.")
        return None

    df = pd.read_csv(CSV_PATH)
    if df.empty or len(df) < MIN_TRAIN_ROWS:
        logger.info(f"[RETRAIN] Nicht genug Daten für Retraining ({len(df)} Zeilen).")
        return None

    return df

def prepare_features(df):
    features = df[[
        "entry_price", "stop_loss", "take_profit", "qty", "leverage"
    ]].copy()

    features["pnl_positive"] = (df["pnl"] > 0).astype(int)
    X = features.drop(columns=["pnl_positive"])
    y = features["pnl_positive"]
    return X, y

def retrain():
    df = load_data()
    if df is None:
        return

    X, y = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    logger.info(f"[RETRAIN] Model retrained. Test Accuracy: {acc:.2%}")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    logger.info(f"[RETRAIN] Model gespeichert als {MODEL_PATH}")

if __name__ == "__main__":
    retrain()
