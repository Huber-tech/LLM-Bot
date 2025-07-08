import pandas as pd
from utils.email_notify import send_email
from datetime import date

df = pd.read_csv('/home/idppadm/trading-bot/paper_trades.csv')
def send_daily_report():
    # PASSE DEN PFAD AN falls nötig
    df = pd.read_csv("paper_trades.csv")
    today = datetime.utcnow().date()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df_today = df[df['timestamp'].dt.date == today]
    df_closed = df_today[df_today['pnl'].notna()]

    trades = len(df_closed)
    wins = (df_closed['pnl'] > 0).sum()
    losses = (df_closed['pnl'] < 0).sum()
    winrate = 100 * wins / trades if trades > 0 else 0

    msg = f"""Trading-Bot Tagesreport {today}

Trades: {trades}
Wins: {wins}
Losses: {losses}
Winrate: {winrate:.1f}%

Die letzten 5 Trades:
{df_closed.tail(5).to_string(index=False)}
"""
    send_email("Tagesreport Trading-Bot", msg)

if __name__ == "__main__":
    send_daily_report()