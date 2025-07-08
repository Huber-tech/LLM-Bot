# utils/risk_manager.py

class RiskManager:
    """Simple risk manager with dynamic risk adjustment."""

    def __init__(self, initial_balance, max_risk_per_trade=0.02, leverage=5):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.base_risk = max_risk_per_trade
        self.max_risk_per_trade = max_risk_per_trade
        self.leverage = leverage

    def update_balance(self, new_balance):
        """Update balance and adjust risk proportionally to account performance."""
        self.balance = new_balance
        gain = (self.balance - self.initial_balance) / self.initial_balance
        # adjust risk between 1% and 5%
        self.max_risk_per_trade = max(0.01, min(0.05, self.base_risk * (1 + gain)))

    def calculate_position_size(self, entry_price, stop_loss, probability=1.0):
        sl_distance = abs(entry_price - stop_loss)
        risk_amount = self.balance * self.max_risk_per_trade * probability
        if sl_distance == 0:
            return 0
        qty = risk_amount / sl_distance
        return qty
