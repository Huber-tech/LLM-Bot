# utils/equity_tracker.py
import json
import os
from datetime import datetime
from utils.balance import get_current_equity

EQUITY_LOG_PATH = "logs/equity_snapshot.json"

def update_equity_snapshot():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    current_equity = get_current_equity()

    if os.path.exists(EQUITY_LOG_PATH):
        with open(EQUITY_LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[today] = {
        "timestamp": datetime.utcnow().isoformat(),
        "equity": current_equity
    }

    with open(EQUITY_LOG_PATH, "w") as f:
        json.dump(data, f, indent=4)
