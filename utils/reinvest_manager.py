# utils/reinvest_manager.py

from utils.balance import get_current_equity

class ReinvestManager:
    def __init__(self, base_risk_pct=0.02, growth_factor=0.005):
        self.base_risk_pct = base_risk_pct
        self.growth_factor = growth_factor
        self.start_equity = 100.0  # kann auch aus Snapshot geladen werden

    def get_risk_pct(self):
        current_equity = get_current_equity()
        growth = (current_equity - self.start_equity) / self.start_equity
        adjusted_risk = self.base_risk_pct + growth * self.growth_factor
        return max(0.005, round(adjusted_risk, 4))  # mind. 0.5 %
