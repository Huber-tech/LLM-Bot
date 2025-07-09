# reentry_manager.py
from utils.equity import get_equity_scaling_factor
from utils.logger import log

class ReEntryManager:
    def __init__(self, base_order_size, max_levels=3):
        self.base_order_size = base_order_size
        self.max_levels = max_levels

    def get_order_size(self, level):
        scaling = get_equity_scaling_factor()  # returns 1.0 for neutral
        size = self.base_order_size * (2 ** level) * scaling
        log(f"[REENTRY] Level {level} → Size {size:.2f} (scaling: {scaling:.2f})")
        return round(size, 2)
