from flask import Flask, request, jsonify
import logging
import threading
from src.bot import trade_action, monitor_trades

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Initialize Flask app
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests for trade signals."""
    try:
        data = request.get_json()
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
        threading.Thread(target=trade_action, args=(symbol, action, price, "SCALP")).start()
        
        return jsonify({
            "status": "success", 
            "message": f"✅ Trade request received: {action} {symbol} at {price}"
        }), 200
    except Exception as e:
        logging.error(f"❌ Webhook error: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Start monitoring trades in a separate thread
    threading.Thread(target=monitor_trades, daemon=True).start()
    logging.info("🚀 Starting trading bot server...")
    app.run(host='0.0.0.0', port=5000)
