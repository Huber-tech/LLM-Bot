# utils/equity_protector.py

import pandas as pd
import os

# utils/equity_protector.py

class EquityProtector:
    def __init__(self, initial_balance: float, threshold_pct: float = 10.0):
        """
        Schützt das Kapital, indem bei Unterschreiten einer Drawdown-Schwelle 
        die Risikonahme reduziert wird.
        :param initial_balance: Startkapital
        :param threshold_pct: Drawdown-Schwelle in Prozent, ab der das Risiko reduziert wird
        """
        self.initial_balance = initial_balance
        self.threshold_pct = threshold_pct
        self.highest_balance = initial_balance
        self._reduce_risk = False

    def update_balance(self, current_balance: float):
        """Nach jedem Trade den aktuellen Kontostand übermitteln."""
        # Höchststand aktualisieren, wenn erreicht
        if current_balance > self.highest_balance:
            self.highest_balance = current_balance
            # Bei neuem Höchststand: Risikoreduktion zurücksetzen
            self._reduce_risk = False
        # Prüfen, ob Drawdown-Schwelle unterschritten ist
        if current_balance <= self.highest_balance * (1 - self.threshold_pct/100):
            self._reduce_risk = True

    def should_reduce_risk(self) -> bool:
        """Gibt True zurück, wenn das Risiko aktuell reduziert werden soll."""
        return self._reduce_risk
