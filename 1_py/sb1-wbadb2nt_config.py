"""
Configuration Settings for Trading Bot
"""
from typing import Dict, List
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class Config:
    # API Settings
    CAPITAL_API_ENV = os.getenv('CAPITAL_API_ENV', 'demo')
    CAPITAL_API_KEY = os.getenv('CAPITAL_API_KEY')
    CAPITAL_API_PASSWORD = os.getenv('CAPITAL_API_PASSWORD')
    CAPITAL_API_IDENTIFIER = os.getenv('CAPITAL_API_IDENTIFIER')
    CAPITAL_API_URL = os.getenv('CAPITAL_API_URL')
    CAPITAL_API_DEMO_URL = os.getenv('CAPITAL_API_DEMO_URL')

    # Telegram Settings
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # Strategy Settings
    STRATEGY_MODE = os.getenv('STRATEGY_MODE', 'Balanced')
    DAILY_LOSS_LIMIT = float(os.getenv('DAILY_LOSS_LIMIT', '-500'))
    DAILY_PROFIT_LIMIT = float(os.getenv('DAILY_PROFIT_LIMIT', '1000'))
    
    # Trading Settings
    TRADE_INTERVAL = int(os.getenv('TRADE_INTERVAL', '300'))
    RISK_PERCENT = float(os.getenv('RISK_PERCENT', '1.5'))
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '10'))
    
    # Market Coverage
    SYMBOLS = json.loads(os.getenv('SYMBOLS', '[]'))
    COMMODITIES = json.loads(os.getenv('COMMODITIES', '[]'))
    INDICES = json.loads(os.getenv('INDICES', '[]'))

    # Technical Analysis Parameters
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    MACD_FAST = int(os.getenv('MACD_FAST', '12'))
    MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))

    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'MAGUS PRIME X')
    APP_VERSION = os.getenv('APP_VERSION', '2.0.0')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
    LOG_FILE = os.getenv('LOG_FILE', 'trading_bot.log')
    
    # Localization settings
    localization = {
        'enable_arabic': os.getenv('ENABLE_ARABIC', 'true').lower() == 'true'
    }

# Create a global CONFIG instance
CONFIG = Config()