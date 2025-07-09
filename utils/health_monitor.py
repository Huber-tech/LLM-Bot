# utils/health_monitor.py

import time
import traceback
from utils.logger import log

class HealthMonitor:
    def __init__(self, retry_limit=5, cooldown=30):
        self.retry_limit = retry_limit
        self.cooldown = cooldown
        self.errors = 0

    def wrap(self, func, *args, **kwargs):
        while self.errors < self.retry_limit:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.errors += 1
                log(f"[HEALTH] Fehler: {e}\n{traceback.format_exc()}")
                time.sleep(self.cooldown)
        raise SystemExit(f"[HEALTH] Abbruch nach {self.retry_limit} Fehlern.")
