# utils/strategy_watchdog.py

import csv
import os
from datetime import datetime
from collections import defaultdict

WATCHDOG_FILE = "strategy_watchdog.csv"

class StrategyWatchdog:
    def __init__(self):
        self.stats = defaultdict(lambda: {"trades": 0, "wins": 0, "losses": 0})
        self._load_existing()

    def _load_existing(self):
        if not os.path.isfile(WATCHDOG_FILE):
            return
        with open(WATCHDOG_FILE, mode="r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                strat = row["strategy"]
                self.stats[strat] = {
                    "trades": int(row["trades"]),
                    "wins": int(row["wins"]),
                    "losses": int(row["losses"])
                }

    def record_trade(self, strategy_name: str, pnl: float):
        stat = self.stats[strategy_name]
        stat["trades"] += 1
        if pnl > 0:
            stat["wins"] += 1
        else:
            stat["losses"] += 1
        self._save()

    def _save(self):
        with open(WATCHDOG_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["strategy", "trades", "wins", "losses"])
            for strat, s in self.stats.items():
                writer.writerow([strat, s["trades"], s["wins"], s["losses"]])
