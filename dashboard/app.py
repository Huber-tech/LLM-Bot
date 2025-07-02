from flask import Flask, render_template, send_file
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.equity_plot import plot_equity_curve
from utils.trade_logger import log_trade 


app = Flask(__name__)

@app.route("/")
def index():
    # Equity-Kurve aktualisieren
    plot_equity_curve("paper_trades.csv", "dashboard/static/equity_curve.png")

    # Daten aus CSV laden
    df = pd.read_csv("paper_trades.csv")
    df_closed = df[df["pnl"].notna()]
    balance = 20.0 + df_closed["pnl"].sum()
    winrate = (df_closed["pnl"] > 0).mean() * 100 if not df_closed.empty else 0

    return render_template("index.html", 
        balance=round(balance, 2),
        total_trades=len(df),
        winrate=round(winrate, 1),
        trades=df.tail(10).to_dict(orient="records")
    )

@app.route("/chart")
def chart():
    return send_file("static/equity_curve.png", mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
