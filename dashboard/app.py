from flask import Flask, render_template, send_file, jsonify
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "logs", "performance_report.json")
EQUITY_IMAGE_PATH = os.path.join(BASE_DIR, "logs", "equity_curve.png")

app = Flask(__name__)

@app.route("/")
def index():
    # Lade vorbereiteten Report aus performance_report.py
    if os.path.isfile(REPORT_PATH):
        with open(REPORT_PATH, "r") as f:
            report = json.load(f)
    else:
        report = {
            "latest_equity": 0,
            "winrate": 0,
            "total_trades": 0,
            "last_daily_pnl": 0,
            "active_strategies": {}
        }
    return render_template(
        "index.html",
        balance=report["latest_equity"],
        winrate=report["winrate"],
        total_trades=report["total_trades"],
        last_daily_pnl=report["last_daily_pnl"],
        active_strategies=report["active_strategies"]
    )

@app.route("/chart")
def chart():
    if os.path.isfile(EQUITY_IMAGE_PATH):
        return send_file(EQUITY_IMAGE_PATH, mimetype='image/png')
    else:
        return "Equity curve not available", 404

@app.route("/api/performance")
def api_performance():
    if os.path.isfile(REPORT_PATH):
        with open(REPORT_PATH, "r") as f:
            report = json.load(f)
        return jsonify(report)
    return jsonify({"error": "No report available"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
