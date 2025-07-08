# utils/risk_manager.py

class RiskManager:
    def __init__(self, initial_balance, max_risk_per_trade=0.02, leverage=5):
        self.balance = initial_balance
        self.max_risk_per_trade = max_risk_per_trade
        self.leverage = leverage

    def update_balance(self, new_balance):
        self.balance = new_balance

    def calculate_position_size(self, entry_price, stop_loss):
        sl_distance = abs(entry_price - stop_loss)
        risk_amount = self.initial_balance * self.max_risk_per_trade
        if sl_distance == 0:
            return 0
        qty = risk_amount / sl_distance
        return qty

