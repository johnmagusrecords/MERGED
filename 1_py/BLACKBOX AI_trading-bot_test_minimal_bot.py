import requests
import logging
import json
import time
from src.minimal_bot import app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def test_webhook():
    """Test the trading bot with a sample trade request"""
    # Start the Flask app in a separate thread
    import threading
    server = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    server.daemon = True
    server.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test data
    test_trade = {
        "symbol": "BTCUSD",
        "action": "BUY",
        "price": 65000.00
    }
    
    try:
        # Send test webhook request
        logging.info("Sending test trade request...")
        response = requests.post(
            "http://localhost:5000/webhook",
            json=test_trade,
            headers={"Content-Type": "application/json"}
        )
        
        # Print response
        logging.info(f"Response status: {response.status_code}")
        logging.info(f"Response body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success":
                trade = result["trade"]
                logging.info("\nTrade details:")
                logging.info(f"Symbol: {trade['symbol']}")
                logging.info(f"Action: {trade['action']}")
                logging.info(f"Price: ${trade['price']:,.2f}")
                logging.info(f"Stop Loss: ${trade['stop_loss']:,.2f}")
                logging.info(f"Take Profit: ${trade['take_profit']:,.2f}")
                logging.info(f"ATR: ${trade['atr']:,.2f}")
                logging.info(f"Lot Size: {trade['lot_size']}")
            else:
                logging.error(f"Trade failed: {result.get('message', 'Unknown error')}")
        else:
            logging.error(f"Request failed with status code {response.status_code}")
            
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    logging.info("Starting minimal bot test...")
    test_webhook()
