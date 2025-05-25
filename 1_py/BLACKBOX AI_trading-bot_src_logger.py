import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def log_trade_execution(symbol, action, price):
    logging.info(f"Executed trade: {action} {symbol} at price {price}")

def log_error(message):
    logging.error(message)
