import pandas as pd
import os

TRAIL_FACTOR = float(os.getenv("TRAILING_SL_PCT", "0.01"))  # 1% default

def update_trailing_stops(csv_file="paper_trades.csv", current_prices=None):
    # Wir nehmen an, dass paper_trades.csv alles enthält!
    df = pd.read_csv(csv_file)
    updated = False

    # Max/Min-Preis seit Entry je Trade speichern
    if "max_price" not in df.columns:
        df["max_price"] = df["entry_price"]
    if "min_price" not in df.columns:
        df["min_price"] = df["entry_price"]

    for idx, row in df[df["pnl"].isna()].iterrows():
        symbol = row["symbol"]
        price = current_prices.get(symbol)
        if price is None:
            continue

        side = row["side"]
        if side == "BUY":
            # Höchster Kurs seit Entry aktualisieren
            if price > row["max_price"]:
                df.at[idx, "max_price"] = price
            new_sl = df.at[idx, "max_price"] * (1 - TRAIL_FACTOR)
            # SL nur anheben, niemals senken!
            if new_sl > row["stop_loss"]:
                df.at[idx, "stop_loss"] = new_sl
                updated = True

        elif side == "SELL":
            # Tiefster Kurs seit Entry aktualisieren
            if price < row["min_price"]:
                df.at[idx, "min_price"] = price
            new_sl = df.at[idx, "min_price"] * (1 + TRAIL_FACTOR)
            # SL nur senken, niemals anheben!
            if new_sl < row["stop_loss"]:
                df.at[idx, "stop_loss"] = new_sl
                updated = True

    if updated:
        df.to_csv(csv_file, index=False)
