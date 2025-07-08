import pandas as pd
import os

def update_trade_pnls(current_prices, trades_csv="paper_trades.csv", atr_lookup=None):
    """
    Aktualisiert PnL und setzt Trailing Stop für offene Trades.
    current_prices: dict {symbol: aktueller Preis}
    atr_lookup: dict {symbol: ATR}, falls du aktuelle ATRs brauchst (optional)
    """
    if not os.path.isfile(trades_csv):
        return

    df = pd.read_csv(trades_csv)
    updated = False
    for idx, row in df[df['pnl'].isnull()].iterrows():
        symbol = row['symbol']
        side = row['side']
        entry = float(row['entry_price'])
        sl = float(row.get('current_sl', row['sl'] if 'sl' in row else row['stop_loss']))
        tp = float(row.get('tp', row['take_profit'])) if 'tp' in row else float(row['take_profit'])
        atr = float(atr_lookup[symbol]) if atr_lookup and symbol in atr_lookup else abs(entry * 0.01)
        qty = float(row['qty'])

        price = float(current_prices.get(symbol, entry))
        # Trailing-Stop-Abstand (z. B. 1.5 × ATR)
        trail_dist = 1.5 * atr

        # Trailing für BUY
        if side == "BUY":
            new_sl = max(sl, price - trail_dist)
        else:  # SELL
            new_sl = min(sl, price + trail_dist)

        # Nur bei SL-Verbesserung updaten
        if new_sl != sl:
            df.at[idx, 'current_sl'] = new_sl
            updated = True

        pnl = None
        exit_reason = None

        # TP/SL/Trailing prüfen
        if side == "BUY":
            if price <= new_sl:
                pnl = (price - entry) * qty
                exit_reason = "trailing_stop"
            elif price >= tp:
                pnl = (tp - entry) * qty
                exit_reason = "take_profit"
        else:
            if price >= new_sl:
                pnl = (entry - price) * qty
                exit_reason = "trailing_stop"
            elif price <= tp:
                pnl = (entry - tp) * qty
                exit_reason = "take_profit"

        if pnl is not None:
            df.at[idx, 'pnl'] = pnl
            df.at[idx, 'exit_price'] = price
            df.at[idx, 'exit_reason'] = exit_reason
            updated = True

            # Optional: Strategie-Watchdog informieren
            strategy_name = row.get("strategy", "Unknown")
            try:
                from utils.strategy_watchdog import StrategyWatchdog
                StrategyWatchdog().record_trade(strategy_name=strategy_name, pnl=pnl)
            except Exception as e:
                print(f"[Watchdog] Fehler bei Strategie-Tracking: {e}")

    if updated:
        df.to_csv(trades_csv, index=False)
