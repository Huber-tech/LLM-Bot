import csv
import os
from datetime import datetime

def log_trade(symbol, side, entry_price, stop_loss, take_profit, qty, strategy, leverage, trades_csv="paper_trades.csv"):
    """
    Loggt einen neuen Trade-Einstieg in die CSV-Datei (paper_trades.csv).
    Enthält alle relevanten Felder, zunächst ohne Exit-Informationen.
    """
    file_exists = os.path.isfile(trades_csv)
    fieldnames = [
        "timestamp", "symbol", "side", "entry_price", "qty",
        "stop_loss", "take_profit", "current_sl",
        "exit_price", "exit_reason", "pnl",
        "leverage", "strategy"
    ]
    trade_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "side": side,
        "entry_price": round(float(entry_price), 4),
        "qty": round(float(qty), 4),
        "stop_loss": (round(float(stop_loss), 4) if stop_loss is not None else ""),
        "take_profit": (round(float(take_profit), 4) if take_profit is not None else ""),
        "current_sl": (round(float(stop_loss), 4) if stop_loss is not None else ""),
        "exit_price": "",
        "exit_reason": "",
        "pnl": "",
        "leverage": leverage,
        "strategy": strategy
    }
    with open(trades_csv, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade_data)
