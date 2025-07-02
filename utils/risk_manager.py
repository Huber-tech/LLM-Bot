# utils/risk_manager.py

class RiskManager:
    def __init__(self, initial_balance: float = 20.0, max_risk_per_trade: float = 0.02):
        self.balance = initial_balance
        self.risk_pct = max_risk_per_trade  # z. B. 2 %

    def update_balance(self, new_balance: float):
        self.balance = new_balance

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        sl_distance = abs(entry_price - stop_loss)
        if sl_distance == 0:
            return 0.0  # keine sinnvolle Positionsgröße möglich
        risk_amount = self.balance * self.risk_pct
        qty = risk_amount / sl_distance
        return round(qty, 6)
