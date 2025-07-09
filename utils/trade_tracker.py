import os
import pandas as pd
from utils.strategy_watchdog import StrategyWatchdog

def update_trade_pnls(current_prices, atr_lookup=None, trades_csv="paper_trades.csv"):
    """
    Aktualisiert offene Trades in der CSV mit aktuellen Stop-Loss/Take-Profit-Verletzungen und berechnet PnL.
    Gibt eine Liste geschlossener Verlust-Trades zurück, um Grid-Recovery anzustoßen.
    """
    if not os.path.isfile(trades_csv):
        return []
    df = pd.read_csv(trades_csv)
    closed_loss_trades = []
    # Iteriere über alle Trades und überprüfe offene Positionen
    for idx, row in df.iterrows():
        if pd.isna(row["pnl"]) or row["pnl"] == "":
            symbol = row["symbol"]
            side = row["side"]
            price = current_prices.get(symbol)
            if price is None:
                continue
            # Aktuellen Stop-Loss (getrailt oder initial) und Take-Profit bestimmen
            stop_price = None
            tp_price = None
            if "current_sl" in df.columns:
                val = str(row.get("current_sl"))
                stop_price = float(val) if val not in ["", "nan", "None"] else None
            if stop_price is None:
                # Fallback auf initialen Stop-Loss
                val = str(row.get("stop_loss"))
                stop_price = float(val) if val not in ["", "nan", "None"] else None
            val_tp = str(row.get("take_profit"))
            tp_price = float(val_tp) if val_tp not in ["", "nan", "None"] else None
            exit_price = None
            exit_reason = None
            # Exit-Bedingungen überprüfen
            if side == "BUY":
                if stop_price is not None and price <= stop_price:
                    exit_price = stop_price
                    exit_reason = "stop_loss_hit"
                elif tp_price is not None and price >= tp_price:
                    exit_price = tp_price
                    exit_reason = "take_profit_hit"
            elif side == "SELL":
                if stop_price is not None and price >= stop_price:
                    exit_price = stop_price
                    exit_reason = "stop_loss_hit"
                elif tp_price is not None and price <= tp_price:
                    exit_price = tp_price
                    exit_reason = "take_profit_hit"
            # Wenn ein Exit ausgelöst wird, Trade schließen
            if exit_price is not None and exit_reason is not None:
                entry_price = float(row["entry_price"])
                qty = float(row["qty"])
                # PnL berechnen
                if side == "BUY":
                    pnl_value = (exit_price - entry_price) * qty
                else:  # SELL
                    pnl_value = (entry_price - exit_price) * qty
                df.at[idx, "exit_price"] = round(exit_price, 4)
                df.at[idx, "exit_reason"] = exit_reason
                df.at[idx, "pnl"] = round(pnl_value, 4)
                # Watchdog-Statistik aktualisieren
                try:
                    sw = StrategyWatchdog()
                    sw.record_trade(row["strategy"], float(pnl_value))
                except Exception as e:
                    print(f"Watchdog-Update Fehler: {e}")
                # Bei Verlust-Trade für Grid-Recovery vormerken
                if pnl_value < 0:
                    closed_loss_trades.append((
                        symbol,
                        side,
                        entry_price,
                        qty,
                        float(row["stop_loss"]) if str(row.get("stop_loss")) not in ["", "nan", "None"] else exit_price,
                        float(row["take_profit"]) if str(row.get("take_profit")) not in ["", "nan", "None"] else exit_price
                    ))
    # CSV mit aktualisierten Trades speichern
    df.to_csv(trades_csv, index=False)
    return closed_loss_trades
