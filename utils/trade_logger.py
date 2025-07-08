import csv
import os
from datetime import datetime

TRADE_LOG_FILE = "paper_trades.csv"

def log_trade(
    symbol, side, entry_price, sl, tp, qty, strategy, leverage,
    pnl=None, exit_price=None, exit_reason=None
):
    file_exists = os.path.isfile(TRADE_LOG_FILE)
    with open(TRADE_LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp", "symbol", "side", "entry_price",
                "sl", "tp", "qty", "strategy", "leverage",
                "current_sl", "pnl", "exit_price", "exit_reason"
            ])
        writer.writerow([
            datetime.utcnow().isoformat(), symbol, side, entry_price,
            sl, tp, qty, strategy, leverage,
            sl,                         # initial: current_sl = sl
            pnl if pnl is not None else "",
            exit_price if exit_price is not None else "",
            exit_reason if exit_reason is not None else ""
        ])
