from flask import Flask, render_template, send_file
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.equity_plot import plot_equity_curve
from utils.trade_logger import log_trade
CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'paper_trades.csv'))
from utils.strategy_leaderboard import StrategyLeaderboard
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
START_BALANCE = float(os.getenv("START_BALANCE", "20.0"))

@app.route("/")
def index():
    if not os.path.isfile(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        balance = START_BALANCE
        winrate = 0.0
        total_trades = 0
        trades = []
    else:
        df = pd.read_csv(CSV_PATH)
        df_closed = df[df["pnl"].notna()]
        balance = START_BALANCE + df_closed["pnl"].sum()
        winrate = (df_closed["pnl"] > 0).mean() * 100 if len(df_closed) else 0.0
        total_trades = len(df)
        trades = df.tail(10).to_dict(orient="records")
    # Equity-Kurve aktualisieren
    plot_equity_curve(CSV_PATH, "dashboard/static/equity_curve.png", start_balance=START_BALANCE)
    return render_template(
        "index.html",
        balance=balance,
        winrate=winrate,
        total_trades=total_trades,
        trades=trades,
        equity_curve_path="static/equity_curve.png"
    )

@app.route("/leaderboard")
def leaderboard():
    lb = StrategyLeaderboard()
    _, stats = lb.compute_leaderboard()
    return render_template("leaderboard.html", stats=stats.to_dict(orient="records"))

@app.route("/chart")
def chart():
    return send_file("static/equity_curve.png", mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
