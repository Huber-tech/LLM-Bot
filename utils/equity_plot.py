import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_equity_curve(csv_file, output_file, start_balance=0.0):
    """
    Erstellt die Equity-Kurven-Grafik basierend auf den abgeschlossenen Trades.
    """
    if not os.path.isfile(csv_file):
        # Keine Trades – nur Startkapital als Linie
        balances = [start_balance, start_balance]
    else:
        df = pd.read_csv(csv_file)
        df_closed = df[df["pnl"].notna()]
        balances = [start_balance]
        cumulative_balance = start_balance
        for pnl in df_closed["pnl"]:
            cumulative_balance += pnl
            balances.append(cumulative_balance)
        if len(balances) < 2:
            balances = [start_balance, start_balance]
    plt.figure(figsize=(6, 4))
    plt.plot(balances, marker='o')
    plt.title("Equity Curve")
    plt.xlabel("Trades")
    plt.ylabel("Balance")
    plt.grid(True)
    try:
        plt.savefig(output_file, format='png')
    except Exception as e:
        print(f"Fehler beim Speichern der Equity-Kurve: {e}")
    plt.close()
