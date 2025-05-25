import os

# Configuration settings
API_KEY = "ZhNNE4pnHX1Ku67d"
API_SECRET = "@boutonY27"  # Keeping the same password
BASE_URL = "https://demo-api-capital.backend-capital.com/api/v1"

# Trading configuration
TRADE_INTERVAL = 60  # Interval in seconds between trades
RISK_PERCENT = 1.0  # Percentage of capital to risk per trade
TP_RATIO = 2.0  # Take-profit ratio
TRAILING_SL_ATR_MULTIPLIER = 1.5  # Multiplier for trailing stop-loss based on ATR

# Trading pairs configuration
TRADING_PAIRS = {
    "BTCUSD": {
        "lot_size": float(os.getenv("BTCUSD_LOT_SIZE", 0.001)),
        "min_spread": float(os.getenv("BTCUSD_MIN_SPREAD", 50))
    },
    "ETHUSD": {
        "lot_size": float(os.getenv("ETHUSD_LOT_SIZE", 0.01)),
        "min_spread": float(os.getenv("ETHUSD_MIN_SPREAD", 10))
    },
    # Add other pairs similarly
}

# Technical analysis parameters
TA_PARAMS = {
    "RSI_PERIOD": int(os.getenv("RSI_PERIOD", 14)),
    "RSI_OVERBOUGHT": int(os.getenv("RSI_OVERBOUGHT", 70)),
    "RSI_OVERSOLD": int(os.getenv("RSI_OVERSOLD", 30)),
    "MACD_FAST": int(os.getenv("MACD_FAST", 12)),
    "MACD_SLOW": int(os.getenv("MACD_SLOW", 26)),
    "MACD_SIGNAL": int(os.getenv("MACD_SIGNAL", 9)),
    # Add other parameters
}
