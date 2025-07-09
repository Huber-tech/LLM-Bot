import pandas as pd
# utils/strategy_blocklist.py

# utils/strategy_blocklist.py

import json
import os

BLOCKLIST_PATH = "logs/strategy_blocklist.json"

class StrategyBlocklist:
    def __init__(self):
        if os.path.exists(BLOCKLIST_PATH):
            with open(BLOCKLIST_PATH, "r") as f:
                self.blocked = set(json.load(f))
        else:
            self.blocked = set()

    def is_blocked(self, strategy_name):
        return strategy_name in self.blocked

    def block(self, strategy_name):
        self.blocked.add(strategy_name)
        self._save()

    def unblock(self, strategy_name):
        self.blocked.discard(strategy_name)
        self._save()

    def _save(self):
        with open(BLOCKLIST_PATH, "w") as f:
            json.dump(sorted(list(self.blocked)), f, indent=2)

# Einzelaufruf von außerhalb:
def block_strategy(strategy_name):
    bl = StrategyBlocklist()
    bl.block(strategy_name)
