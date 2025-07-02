# utils/trade_logger.py

import csv
import os
from datetime import datetime

TRADE_LOG_FILE = "paper_trades.csv"

def log_trade(symbol, side, entry_price, sl, tp, qty, pnl=None, strategy=None):
    file_exists = os.path.isfile(TRADE_LOG_FILE)
    with open(TRADE_LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp", "symbol", "side", "entry_price",
                "stop_loss", "take_profit", "qty", "pnl"
            ])
        writer.writerow([
	    datetime.utcnow().isoformat(), symbol, side, entry_price,
    	sl, tp, qty, pnl if pnl is not None else "", strategy or ""
	])
