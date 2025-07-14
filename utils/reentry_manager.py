# 3️⃣ utils/reentry_manager.py
from datetime import datetime, timedelta

class ReEntryManager:
    def __init__(self, cooldown_minutes=30):
        self.last_losses = {}
        self.cooldown = timedelta(minutes=cooldown_minutes)

    def register_loss(self, symbol):
        self.last_losses[symbol] = datetime.utcnow()

    def can_reenter(self, symbol):
        last = self.last_losses.get(symbol)
        if last is None:
            return True
        return datetime.utcnow() - last > self.cooldown
