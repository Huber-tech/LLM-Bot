# utils/strategy_watchdog.py

from utils.equity import get_equity_scaling_factor
from utils.strategy_blocklist import block_strategy
from utils.logger import log

class StrategyWatchdog:
    def __init__(self):
        self.equity_baseline = get_equity_scaling_factor()
        self.threshold = 0.02  # Deaktiviere Strategie, wenn -2% Equity-Verlust

    def evaluate(self, strategy_name):
        current_equity_score = get_equity_scaling_factor()
        delta = current_equity_score - self.equity_baseline

        log(f"[WATCHDOG] Strategy {strategy_name}: Equity-Delta seit Start = {delta:.4f}")

        if delta < -self.threshold:
            block_strategy(strategy_name)
            log(f"[WATCHDOG] ⚠️ Strategie '{strategy_name}' wurde deaktiviert: Equityverlust {delta:.2%}")

        self.equity_baseline = current_equity_score
