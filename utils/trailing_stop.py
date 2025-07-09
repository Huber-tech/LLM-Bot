import os
import pandas as pd

def update_trailing_stops(trades_csv="paper_trades.csv", current_prices=None, trail_pct=50):
    """
    Passt den Stop-Loss für offene Trades an (Trailing Stop).
    trail_pct bestimmt, wie viel Prozent des aktuell erzielten Profits abgesichert werden.
    """
    if current_prices is None or not os.path.isfile(trades_csv):
        return
    df = pd.read_csv(trades_csv)
    if "current_sl" not in df.columns:
        # Wenn kein Trailing-Stop-Feld vorhanden, keine Anpassung vornehmen
        return
    modified = False
    for idx, row in df.iterrows():
        # Nur offene Trades (ohne PnL) berücksichtigen
        if pd.isna(row["pnl"]) or row["pnl"] == "":
            symbol = row["symbol"]
            side = row["side"]
            entry_price = float(row["entry_price"])
            price = current_prices.get(symbol)
            if price is None:
                continue
            current_sl = None
            try:
                current_sl = float(row["current_sl"])
            except:
                current_sl = None
            # Trailing-Stop für Long-Positionen
            if side == "BUY" and current_sl is not None:
                if price > entry_price:
                    # Neuen SL so setzen, dass trail_pct% des Gewinns gesichert sind
                    desired_sl = entry_price + (price - entry_price) * (trail_pct / 100.0)
                    if desired_sl > current_sl:
                        df.at[idx, "current_sl"] = round(desired_sl, 4)
                        modified = True
            # Trailing-Stop für Short-Positionen
            elif side == "SELL" and current_sl is not None:
                if price < entry_price:
                    desired_sl = entry_price - (entry_price - price) * (trail_pct / 100.0)
                    if desired_sl < current_sl:
                        df.at[idx, "current_sl"] = round(desired_sl, 4)
                        modified = True
    if modified:
        df.to_csv(trades_csv, index=False)
