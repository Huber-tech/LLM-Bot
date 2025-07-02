# utils/drawdown_guard.py

from datetime import datetime
import pandas as pd

class DrawdownGuard:
    def __init__(self, csv_file="paper_trades.csv", start_balance=20.0, max_loss_pct=5.0):
        self.csv_file = csv_file
        self.start_balance = start_balance
        self.max_loss_pct = max_loss_pct

    def loss_today_exceeded(self) -> bool:
        try:
            df = pd.read_csv(self.csv_file)
            df = df[df["pnl"].notna()]
            today = datetime.utcnow().date()
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df[df["timestamp"].dt.date == today]

            if df.empty:
                return False

            pnl_sum = df["pnl"].sum()
            loss_pct = -pnl_sum / self.start_balance * 100 if pnl_sum < 0 else 0

            return loss_pct >= self.max_loss_pct
        except Exception:
            return False  # Lieber weiter traden als fälschlich stoppen
