# utils/cooldown_manager.py

from datetime import datetime, timedelta

class CooldownManager:
    def __init__(self, cooldown_minutes=30):
        self.cooldowns = {}  # symbol → datetime
        self.cooldown_duration = timedelta(minutes=cooldown_minutes)

    def is_in_cooldown(self, symbol: str) -> bool:
        now = datetime.utcnow()
        last = self.cooldowns.get(symbol)
        return last and (now - last) < self.cooldown_duration

    def update_cooldown(self, symbol: str):
        self.cooldowns[symbol] = datetime.utcnow()
