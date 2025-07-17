from flask import Flask, render_template, send_file, jsonify
import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "dashboard", "templates")
STATIC_FOLDER = os.path.join(BASE_DIR, "dashboard", "static")

REPORT_PATH = os.path.join(BASE_DIR, "logs", "performance_report.json")
EQUITY_IMAGE_PATH = os.path.join(BASE_DIR, "logs", "equity_curve.png")

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/performance")
def api_performance():
    if os.path.isfile(REPORT_PATH):
        with open(REPORT_PATH, "r") as f:
            report = json.load(f)
        return jsonify(report)
    return jsonify({"error": "No report available"}), 404

@app.route("/chart")
def chart():
    if os.path.isfile(EQUITY_IMAGE_PATH):
        return send_file(EQUITY_IMAGE_PATH, mimetype='image/png')
    else:
        return "Equity curve not available", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
