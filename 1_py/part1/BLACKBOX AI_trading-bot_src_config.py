# Configuration settings
import os

# API Configuration
API_KEY = os.getenv('CAPITAL_API_KEY', '')
API_SECRET = os.getenv('CAPITAL_API_SECRET', '')
IDENTIFIER = os.getenv('CAPITAL_IDENTIFIER', '')

# API Endpoints
BASE_URL = "https://api-capital.backend-capital.com/api/v1"
ENDPOINTS = {
    'prices': '/prices',
    'positions': '/positions',
    'orders': '/workingorders',
    'account': '/account'
}

# Trading Parameters
RISK_PER_TRADE = 0.02  # 2% risk per trade
ATR_PERIOD = 14  # Period for ATR calculation
MIN_HISTORY_BARS = 20  # Minimum bars needed for analysis
PRICE_HISTORY_SIZE = 100  # Number of historical prices to maintain
TRADE_CHECK_INTERVAL = 300  # 5 minutes between trade checks

# Position Management
MAX_POSITIONS = 5  # Maximum number of concurrent positions
MAX_POSITION_SIZE = 0.1  # Maximum position size as fraction of account
STOP_LOSS_ATR_MULTIPLE = 2.0  # Stop loss distance in ATR
TAKE_PROFIT_ATR_MULTIPLE = 3.0  # Take profit distance in ATR

# Market Hours (UTC)
MARKET_HOURS = {
    'open': '00:00',  # 24/7 for crypto
    'close': '23:59'
}

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = 'trading_bot.log'
