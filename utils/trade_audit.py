# utils/trade_audit.py

import csv
import os
from datetime import datetime
from utils.balance import get_current_equity

AUDIT_FILE = "logs/trade_audit.csv"

def audit_trade(symbol, strategy, signal, market_state, indicators):
    fieldnames = ["timestamp", "symbol", "strategy", "signal", "market_state", "equity", "rsi", "ema", "atr", "bb_upper", "bb_lower"]
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "strategy": strategy,
        "signal": signal,
        "market_state": market_state,
        "equity": get_current_equity(),
        **indicators
    }
    file_exists = os.path.isfile(AUDIT_FILE)
    with open(AUDIT_FILE, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
