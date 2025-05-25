"""Main application module for the trading bot."""

import logging
import sys
import os
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, flash
from src.bot import trade_action, analyze_market, monitor_trades
from src.technical_indicators import calculate_atr

# Configure logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "trading_bot_output.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

# Trading Settings
SYMBOLS = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "ADAUSD", "SOLUSD", "DOGEUSD", "DOTUSD", "MATICUSD", "BNBUSD"]

# Store recent trades in memory
recent_trades = []

# Simple HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Bot Dashboard</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5; 
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .status { 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
            background-color: #dff0d8; 
            color: #3c763d;
            border: 1px solid #d6e9c6;
        }
        .trades { 
            margin: 20px 0;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .trade-form {
            margin: 20px 0;
            background-color: white;
            padding: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .form-group label {
            width: 100px;
            margin-right: 10px;
            font-weight: bold;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 10px;
            background-color: white;
        }
        th, td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd;
        }
        th { 
            background-color: #f8f9fa;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 12px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #45a049;
        }
        select, input {
            padding: 10px;
            margin: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 200px;
            font-size: 14px;
        }
        select:focus, input:focus {
            outline: none;
            border-color: #4CAF50;
            box-shadow: 0 0 5px rgba(74, 175, 80, 0.2);
        }
        .flash-message {
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            font-weight: bold;
        }
        .flash-success { 
            background-color: #dff0d8; 
            color: #3c763d;
            border: 1px solid #d6e9c6;
        }
        .flash-error { 
            background-color: #f2dede; 
            color: #a94442;
            border: 1px solid #ebccd1;
        }
        .trade-history {
            margin: 20px 0;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .current-price {
            font-weight: bold;
            color: #4CAF50;
        }
        .section-title {
            margin-bottom: 20px;
            color: #333;
            font-size: 24px;
        }
    </style>
    <script>
        function refreshStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('botStatus').innerHTML = data.status;
                    document.getElementById('lastUpdate').innerHTML = data.last_update;
                });
        }
        
        setInterval(refreshStatus, 5000);
    </script>
</head>
<body>
    <div class="container">
        <h1>Trading Bot Dashboard</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message flash-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="status">
            <h2>Bot Status: <span id="botStatus">Running</span></h2>
            <p>Last Update: <span id="lastUpdate">{{ last_update }}</span></p>
        </div>
        
        <div class="trades">
            <h2 class="section-title">Available Trading Pairs</h2>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Status</th>
                    <th>Current Price</th>
                </tr>
                {% for symbol in symbols %}
                <tr>
                    <td>{{ symbol }}</td>
                    <td>Active</td>
                    <td id="price-{{ symbol }}">Loading...</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <div class="trade-form">
            <h2 class="section-title">Manual Trade Entry</h2>
            <form action="/" method="post">
                <div class="form-group">
                    <label for="symbol">Symbol:</label>
                    <select name="symbol" id="symbol" required>
                        {% for symbol in symbols %}
                        <option value="{{ symbol }}">{{ symbol }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="action">Action:</label>
                    <select name="action" id="action" required>
                        <option value="BUY">BUY</option>
                        <option value="SELL">SELL</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="price">Price:</label>
                    <input type="number" name="price" id="price" placeholder="Enter price" step="0.01" required>
                </div>
                
                <div class="form-group">
                    <button type="submit" class="button">Execute Trade</button>
                </div>
            </form>
        </div>

        <div class="trade-history">
            <h2 class="section-title">Recent Trades</h2>
            <table>
                <tr>
                    <th>Time</th>
                    <th>Symbol</th>
                    <th>Action</th>
                    <th>Price</th>
                    <th>Stop Loss</th>
                    <th>Take Profit</th>
                </tr>
                {% for trade in recent_trades %}
                <tr>
                    <td>{{ trade.timestamp }}</td>
                    <td>{{ trade.symbol }}</td>
                    <td>{{ trade.action }}</td>
                    <td>${{ "%.2f"|format(trade.price) }}</td>
                    <td>${{ "%.2f"|format(trade.stop_loss) }}</td>
                    <td>${{ "%.2f"|format(trade.take_profit) }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    """Render the trading bot dashboard."""
    if request.method == 'POST':
        try:
            symbol = request.form.get('symbol')
            action = request.form.get('action')
            price = float(request.form.get('price'))
            
            # Execute trade
            result = trade_action(symbol, action, price, "MANUAL")
            
            if result:
                # Add trade to recent trades list (limit to last 10 trades)
                trade_info = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": symbol,
                    "action": action,
                    "price": price,
                    "stop_loss": result.get("stop_loss", 0),
                    "take_profit": result.get("take_profit", 0)
                }
                recent_trades.insert(0, trade_info)
                recent_trades[:] = recent_trades[:10]  # Keep only last 10 trades
                
                flash(f"Trade executed successfully: {action} {symbol} at ${price:.2f}", "success")
            else:
                flash(f"Failed to execute trade: {action} {symbol}", "error")
                
        except ValueError:
            flash("Invalid price value", "error")
        except Exception as e:
            flash(f"Error executing trade: {str(e)}", "error")
            logging.error(f"Trade execution error: {str(e)}", exc_info=True)
    
    return render_template_string(
        DASHBOARD_HTML,
        symbols=SYMBOLS,
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        recent_trades=recent_trades
    )

@app.route('/status')
def status():
    """Get the current bot status."""
    return jsonify({
        "status": "Running",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests for trade signals."""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        symbol = data.get("symbol")
        action = data.get("action")
        
        if not symbol or not action:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        try:
            price = float(data.get("price", 0))
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Invalid price value"}), 400
            
        logging.info(f"🌐 Webhook received: {data}")
        
        # Execute trade in a separate thread
        threading.Thread(target=trade_action, args=(symbol, action, price, "WEBHOOK")).start()
        
        return jsonify({
            "status": "success", 
            "message": f"✅ Trade request received: {action} {symbol} at {price}"
        }), 200
    except Exception as e:
        logging.error(f"❌ Webhook error: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

def main():
    """Main function to execute the trading bot application."""
    try:
        logging.info("🚀 Starting the trading bot application...")
        
        # Start monitoring trades in a separate thread
        monitor_thread = threading.Thread(target=monitor_trades, daemon=True)
        monitor_thread.start()
        logging.info("✅ Trade monitoring started")
        
        # Start the Flask application
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logging.error(f"❌ Application error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
