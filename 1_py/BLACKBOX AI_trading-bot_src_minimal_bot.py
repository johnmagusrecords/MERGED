import logging
import json
from flask import Flask, request, jsonify
import pandas as pd
from .technical_indicators import calculate_atr

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Trading Settings
SYMBOLS = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "ADAUSD"]
LOT_SIZES = {
    "BTCUSD": 0.001,
    "ETHUSD": 0.01,
    "ADAUSD": 0.5,
    "XRPUSD": 100,
    "LTCUSD": 1
}
DEFAULT_LOT_SIZE = 0.01

def calculate_risk_parameters(symbol, price, action):
    """Calculate risk management parameters using ATR"""
    try:
        # Sample data for testing
        data = {
            'high': [price * 1.01, price * 1.02, price * 1.015, price * 1.025, price],
            'low': [price * 0.99, price * 0.98, price * 0.985, price * 0.975, price],
            'close': [price * 1.0, price * 1.01, price * 0.99, price * 1.02, price]
        }
        df = pd.DataFrame(data)
        
        # Calculate ATR
        df['ATR'] = calculate_atr(df['high'], df['low'], df['close'], period=3)
        atr_value = df['ATR'].iloc[-1]
        
        # Dynamic stop-loss and take-profit levels based on ATR
        if action == "BUY":
            stop_loss = price - (atr_value * 2)
            take_profit = price + (atr_value * 3)
        else:
            stop_loss = price + (atr_value * 2)
            take_profit = price - (atr_value * 3)
            
        logging.info(f"Calculated ATR: {atr_value:.2f} for {symbol}")
        logging.info(f"Risk levels - SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
        
        return {
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "atr": atr_value
        }
    except Exception as e:
        logging.error(f"Error calculating risk parameters: {str(e)}")
        return None

def execute_trade(symbol, action, price):
    """Execute a trade with the calculated risk parameters"""
    logging.info(f"Processing trade: {action} {symbol} at {price}")
    
    # Get lot size for the symbol
    lot_size = LOT_SIZES.get(symbol, DEFAULT_LOT_SIZE)
    
    # Calculate risk parameters
    risk_params = calculate_risk_parameters(symbol, price, action)
    if not risk_params:
        return {"status": "error", "message": "Failed to calculate risk parameters"}
    
    # Simulate trade execution
    trade_details = {
        "symbol": symbol,
        "action": action,
        "price": price,
        "lot_size": lot_size,
        "stop_loss": risk_params["stop_loss"],
        "take_profit": risk_params["take_profit"],
        "atr": risk_params["atr"]
    }
    
    logging.info(f"Trade executed: {json.dumps(trade_details, indent=2)}")
    return {"status": "success", "trade": trade_details}

# Flask application
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        action = data.get("action")
        price = float(data.get("price", 0))
        
        if not symbol or not action or price <= 0:
            return jsonify({"status": "error", "message": "Invalid request parameters"}), 400
        
        if symbol not in SYMBOLS:
            return jsonify({"status": "error", "message": f"Symbol {symbol} not supported"}), 400
        
        if action not in ["BUY", "SELL"]:
            return jsonify({"status": "error", "message": f"Action {action} not supported"}), 400
        
        result = execute_trade(symbol, action, price)
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    logging.info("Starting minimal trading bot...")
    app.run(host='0.0.0.0', port=5000)
