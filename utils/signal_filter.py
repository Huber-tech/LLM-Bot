# Analyse:
# Der Fehler
# "'SignalFilter' object has no attribute 'passes_all'"
# bedeutet klar: Deine Klasse utils/signal_filter.py enthält KEINE Methode "passes_all"

# === Vorgehen ===
# 1️⃣ SignalFilter prüfen und entweder Methode ergänzen oder Aufruf ändern.

# Beispielkorrektur für utils/signal_filter.py:

class SignalFilter:
    def __init__(self):
        pass

    def passes_all(self, market_data):
        # Beispiel-Filter: prüft ob market_data nicht leer ist und Volumen > 0
        if not market_data:
            return False

        try:
            # Beispiel: Verwende das letzte Kline-Volumen als Filter
            last_candle = market_data[-1]
            volume = float(last_candle[5])  # Index 5 = Volume bei Binance Klines
            return volume > 0
        except (IndexError, ValueError, TypeError):
            return False

# 2️⃣ Damit funktioniert Dein paper_loop korrekt an dieser Stelle.

# Hinweis zur zweiten Exception "int() argument must be a string, ...":

