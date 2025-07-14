# utils/risk_manager.py

import os
import json
from datetime import datetime
from utils.balance import get_current_equity
from utils.logger import logger
from utils.reinvest_manager import ReinvestManager


class RiskManager:
    """
    Equity-basierter Tages-Drawdown-Manager
    """
    def __init__(self, max_drawdown_percent=1.0, equity_log_path="logs/equity_snapshot.json"):
        self.max_drawdown_percent = max_drawdown_percent
        self.equity_log_path = equity_log_path
        self.today = datetime.utcnow().strftime("%Y-%m-%d")
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(self.equity_log_path):
            with open(self.equity_log_path, "r") as f:
                data = json.load(f)
        else:
            data = {}

        if self.today not in data:
            equity = get_current_equity()
            data[self.today] = {
                "start_equity": equity,
                "max_loss": equity * (self.max_drawdown_percent / 100)
            }
            with open(self.equity_log_path, "w") as f:
                json.dump(data, f, indent=4)

        self.start_equity = data[self.today]["start_equity"]
        self.max_loss = data[self.today]["max_loss"]

    def is_within_limit(self):
        current_equity = get_current_equity()
        allowed_min_equity = self.start_equity - self.max_loss
        if current_equity < allowed_min_equity:
            log(f"[RISK] Max daily drawdown exceeded: {current_equity:.2f} < {allowed_min_equity:.2f}")
            return False
        return True


class TradeRiskManager:
    """
    Berechnung der Positionsgröße mit dynamischem Risiko (Reinvest basiert auf Equity-Wachstum)
    """
    def __init__(self, initial_balance=100.0, leverage=1):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.leverage = leverage
        self.max_risk_per_trade = 0.02  # initial, wird dynamisch angepasst

    def calculate_position_size(self, entry_price, stop_loss):
        reinvest = ReinvestManager()
        self.max_risk_per_trade = reinvest.get_risk_pct()
        risk_amount = self.current_balance * self.max_risk_per_trade
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance == 0:
            return 0
        qty = (risk_amount / stop_distance) * self.leverage
        return round(qty, 4)

    def update_balance(self, new_balance):
        self.current_balance = new_balance
