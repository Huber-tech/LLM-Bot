# utils/equity.py
from utils.balance import get_current_equity

EQUITY_BASELINE = 100.0  # Startwert als Basis (wird dynamisch ersetzt)

def get_equity_scaling_factor():
    current_equity = get_current_equity()
    if current_equity <= 0:
        return 1.0
    return current_equity / EQUITY_BASELINE
