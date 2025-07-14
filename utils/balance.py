# utils/balance.py

import os
import csv

def get_current_equity(balance_file="logs/equity_log.csv"):
    """
    Gibt das aktuelle verfügbare Kapital aus der letzten Zeile der equity_log.csv zurück.
    Fallback: START_BALANCE aus .env
    """
    if os.path.exists(balance_file):
        try:
            with open(balance_file, "r") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_line = lines[-1]
                    equity = float(last_line.strip().split(",")[1])
                    return equity
        except Exception:
            pass
    return get_fallback_balance()

def get_fallback_balance():
    """
    Fallback: START_BALANCE aus Umgebungsvariablen (.env) laden
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return float(os.getenv("START_BALANCE", 100.0))
    except Exception:
        return 100.0
