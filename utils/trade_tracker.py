import pandas as pd
from datetime import datetime
from utils.trade_logger import log_trade

def update_trade_pnls(csv_file="paper_trades.csv", current_prices=None):
    df = pd.read_csv(csv_file)
    updated = False

    for idx, row in df[df["pnl"].isna()].iterrows():
        symbol = row["symbol"]
        price = current_prices.get(symbol)
        if price is None:
            continue

        side = row["side"]
        entry = row["entry_price"]
        sl = row["stop_loss"]
        tp = row["take_profit"]
        qty = row["qty"]

        pnl = None
        # Prüfen, ob SL oder TP erreicht wurde
        if side == "BUY" and (price <= sl or price >= tp):
            pnl = (price - entry) * qty
        elif side == "SELL" and (price >= sl or price <= tp):
            pnl = (entry - price) * qty

        # Nur wenn Trade geschlossen wurde:
        if pnl is not None:
            df.at[idx, "pnl"] = pnl
            updated = True

            # Optional: Watchdog informieren, falls Strategie geloggt wurde
            strategy_name = row.get("strategy", "Unknown")
            try:
                from utils.strategy_watchdog import StrategyWatchdog
                StrategyWatchdog().record_trade(strategy_name=strategy_name, pnl=pnl)
            except Exception as e:
                print(f"[Watchdog] Fehler bei Strategie-Tracking: {e}")

    if updated:
        df.to_csv(csv_file, index=False)