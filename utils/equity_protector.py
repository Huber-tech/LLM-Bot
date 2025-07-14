class EquityProtector:
    def __init__(self, initial_balance, threshold_pct=10):
        self.initial_balance = initial_balance
        self.highest_balance = initial_balance
        self.threshold_pct = threshold_pct
        self._reduce_risk = False

    def update_balance(self, current_balance):
        if current_balance > self.highest_balance:
            self.highest_balance = current_balance
        elif current_balance <= self.highest_balance * (1 - self.threshold_pct / 100):
            self._reduce_risk = True

    def should_reduce_risk(self):
        return self._reduce_risk
