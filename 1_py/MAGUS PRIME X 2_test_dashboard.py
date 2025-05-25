"""
MAGUS PRIME X Dashboard Test Server
This script simulates the API endpoints needed for testing the React dashboard.
"""

import os
from datetime import datetime, timedelta

import flask
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template_string,
    request,
    send_from_directory,
)

# Create Flask app
app = Flask(__name__, static_url_path="/static", static_folder="static")

# Sample trade data
SAMPLE_TRADES = [
    {
        "time": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
        "symbol": "US500",
        "direction": "BUY",
        "entry": "5200.5",
        "tp": "5250.0",
        "sl": "5150.0",
        "result": "WIN",
        "profit": 49.5,
        "loss": 0,
        "pnl": 49.5,
    },
    {
        "time": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
        "symbol": "EURUSD",
        "direction": "SELL",
        "entry": "1.0850",
        "tp": "1.0800",
        "sl": "1.0900",
        "result": "LOSS",
        "profit": 0,
        "loss": 50.0,
        "pnl": -50.0,
    },
    {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "symbol": "BTCUSD",
        "direction": "BUY",
        "entry": "68500.0",
        "tp": "71000.0",
        "sl": "66000.0",
        "result": "OPEN",
        "profit": None,
        "loss": None,
        "pnl": None,
    },
]

# Sample metrics
METRICS = {
    "strategy": "Balanced",
    "interval": "5 min",
    "paused": False,
    "win_rate": 50.0,
    "total_trades": 2,
    "cumulative_pnl": -0.5,
    "avg_win": 49.5,
    "avg_loss": 50.0,
    "profit_factor": 0.99,
    "max_drawdown": 50.0,
    "today_pnl": -0.5,
}

# Current strategy
CURRENT_STRATEGY = "Balanced"


@app.route("/")
def index():
    """Redirect to test dashboard"""
    return redirect("/test")


@app.route("/test")
def test_page():
    """Serve the test dashboard HTML"""
    return send_from_directory("static", "test_dashboard.html")


@app.route("/dashboard/react")
def dashboard_react():
    """Serve the React dashboard"""
    try:
        # Make sure templates directory exists
        if not os.path.exists("templates"):
            os.makedirs("templates")

        # Open the template file
        if os.path.exists("templates/dashboard_react.html"):
            with open("templates/dashboard_react.html", "r") as f:
                template_content = f.read()
                return render_template_string(template_content)
        else:
            return " "
Dashboard template not found. Please mak + "e sure templates/dashboard_react.html ex + "ists."
    except Exception as e:
        return f"Error loading dashboard: {str(e)}"


@app.route("/components/<path:filename>")
def serve_components(filename):
    """Serve React component files"""
    return flask.send_from_directory("components", filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    """Serve JavaScript files"""
    return flask.send_from_directory("static/js", filename)


@app.route("/css/<path:filename>")
def serve_css(filename):
    """Serve CSS files"""
    return flask.send_from_directory("static/css", filename)


@app.route("/api/trades")
def get_trades():
    """API endpoint for trades"""
    return jsonify(SAMPLE_TRADES)


@app.route("/api/metrics")
def get_metrics():
    """API endpoint for metrics"""
    global METRICS
    METRICS["strategy"] = CURRENT_STRATEGY
    return jsonify(METRICS)


@app.route("/api/strategy", methods=["POST"])
def change_strategy():
    """API endpoint to change strategy"""
    global CURRENT_STRATEGY
    try:
        data = request.json
        if not data or "strategy" not in data:
            return jsonify({"success": False, "error": "Invalid request data"}), 400

        strategy = data["strategy"]
        if strategy not in ["Safe", "Balanced", "Aggressive"]:
            return jsonify({"success": False, "error": "Invalid strategy"}), 400

        # Update strategy
        CURRENT_STRATEGY = strategy
        print(f"Strategy changed to: {strategy}")

        return jsonify({"success": True, "strategy": strategy})

    except Exception as e:
        print(f"Error changing strategy: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/clear-history", methods=["POST"])
def clear_history():
    """API endpoint to clear trade history"""
    global SAMPLE_TRADES
    try:
        # Clear trade history
        SAMPLE_TRADES = []
        print("Trade history cleared")

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error clearing history: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print("MAGUS PRIME X Dashboard Test Server")
    print(f"{'='*50}")
    print("\nStarting test server on port 5000...")
    print("Dashboard will be available at: http://localhost:5000/test")
    print("\nPress Ctrl+C to stop the server")
    print(f"{'='*50}\n")

    # Start the server
    app.run(host="0.0.0.0", port=5000, debug=True)
