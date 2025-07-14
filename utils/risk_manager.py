import os
import json
from datetime import datetime
from utils.balance import get_current_equity
from utils.logger import logger
from utils.reinvest_manager import ReinvestManager
from strategies.indicators import calculate_atr

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
            logger.warning(f"[RISK] Max daily drawdown exceeded: {current_equity:.2f} < {allowed_min_equity:.2f}")
            return False
        return True

class TradeRiskManager:
    """
    Erweiterte Positionsgrößenberechnung mit:
    - dynamischem Risiko (ATR)
    - optional Kelly Criterion
    - Capital Exposure Limit pro Symbol
    - Recovery Mode Support
    """
    def __init__(self, initial_balance=100.0, leverage=1, max_exposure_pct=10.0, use_kelly=False):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.leverage = leverage
        self.max_risk_per_trade = 0.02
        self.max_exposure_pct = max_exposure_pct
        self.use_kelly = use_kelly

    def calculate_position_size(self, entry_price, stop_loss, symbol=None, historical_data=None, winrate=None, rr_ratio=None, recovery_mode=False):
        reinvest = ReinvestManager()
        base_risk = reinvest.get_risk_pct()
        self.max_risk_per_trade = max(base_risk, 0.03) if recovery_mode else base_risk

        risk_amount = self.current_balance * self.max_risk_per_trade

        atr_multiplier = 1.0
        if historical_data:
            atr = calculate_atr(historical_data)
            if atr > 0:
                atr_multiplier = atr / entry_price

        stop_distance = abs(entry_price - stop_loss)
        if stop_distance == 0:
            return 0

        position_size = (risk_amount / stop_distance) * self.leverage

        # Capital Exposure Limiter pro Symbol
        exposure_limit = self.current_balance * (self.max_exposure_pct / 100)
        notional_value = position_size * entry_price / self.leverage
        if notional_value > exposure_limit:
            position_size = (exposure_limit * self.leverage) / entry_price
            logger.info(f"[RISK] Exposure limit angepasst: {symbol} max {self.max_exposure_pct}% vom Kapital")

        position_size *= atr_multiplier
        position_size = round(position_size, 4)
        logger.info(f"[RISK] Position Size berechnet für {symbol}: {position_size} @ {entry_price}, Risk {self.max_risk_per_trade*100:.2f}%, Recovery={recovery_mode}")

        return position_size

    def update_balance(self, new_balance):
        self.current_balance = new_balance
