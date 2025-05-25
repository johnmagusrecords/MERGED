import os
import time
import threading
import logging
import requests
import pandas as pd
import numpy as np
import talib
import json
import re
from flask import Flask, request, jsonify, render_template_string, redirect
from dotenv import load_dotenv
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import telegram

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Credentials
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_API_IDENTIFIER")
CAPITAL_API_URL = os.getenv("CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "1234")

TRADE_LOG = []
TRADE_HISTORY_FILE = "trade_history.csv"
STRATEGY_MODE = os.getenv("STRATEGY_MODE", "Balanced")
DAILY_LOSS_LIMIT = float(os.getenv("DAILY_LOSS_LIMIT", -500))
DAILY_PROFIT_LIMIT = float(os.getenv("DAILY_PROFIT_LIMIT", 1000))

if STRATEGY_MODE == "Safe":
    TRADE_INTERVAL = 600
    TP_MOVE_PERCENT = 0.3 / 100
    BREAKEVEN_TRIGGER = 0.5 / 100
    RISK_PERCENT = 1
elif STRATEGY_MODE == "Aggressive":
    TRADE_INTERVAL = 120
    TP_MOVE_PERCENT = 1 / 100
    BREAKEVEN_TRIGGER = 1.5 / 100
    RISK_PERCENT = 3
else:  # Balanced
    TRADE_INTERVAL = 300
    TP_MOVE_PERCENT = 0.5 / 100
    BREAKEVEN_TRIGGER = 1 / 100
    RISK_PERCENT = 2

USE_ALL_MARKETS = True
MARKET_CACHE = {}
MARKET_CACHE_TTL = 3600

# Initialize session with retries
session = requests.Session()
retry = Retry(total=5, backoff_factor=0.2)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Initialize Telegram bot
telegram_bot = telegram.Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    try:
        telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {str(e)}")

def save_trade_to_csv(timestamp, symbol, action, tp, sl, result=None):
    df = pd.DataFrame([[timestamp, symbol, action, tp, sl, result]],
                      columns=["Time", "Symbol", "Action", "TP", "SL", "Result"])
    df.to_csv(TRADE_HISTORY_FILE, mode='a', header=not os.path.exists(TRADE_HISTORY_FILE), index=False)

def load_trade_history():
    if os.path.exists(TRADE_HISTORY_FILE):
        return pd.read_csv(TRADE_HISTORY_FILE).tail(100).to_dict(orient='records')
    return []

def clear_trade_history():
    if os.path.exists(TRADE_HISTORY_FILE):
        os.remove(TRADE_HISTORY_FILE)

import os
import time
import threading
import logging
import requests
import pandas as pd
import numpy as np
import talib
import json
import re
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import telegram

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Credentials
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_API_IDENTIFIER")
CAPITAL_API_URL = os.getenv("CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD")

TRADE_LOG = []
TRADE_HISTORY_FILE = "trade_history.csv"
STRATEGY_MODE = os.getenv("STRATEGY_MODE", "Balanced")

if STRATEGY_MODE == "Safe":
    TRADE_INTERVAL = 600
    TP_MOVE_PERCENT = 0.3 / 100
    BREAKEVEN_TRIGGER = 0.5 / 100
    RISK_PERCENT = 1
elif STRATEGY_MODE == "Aggressive":
    TRADE_INTERVAL = 120
    TP_MOVE_PERCENT = 1 / 100
    BREAKEVEN_TRIGGER = 1.5 / 100
    RISK_PERCENT = 3
else:  # Balanced
    TRADE_INTERVAL = 300
    TP_MOVE_PERCENT = 0.5 / 100
    BREAKEVEN_TRIGGER = 1 / 100
    RISK_PERCENT = 2

USE_ALL_MARKETS = True
MARKET_CACHE = {}
MARKET_CACHE_TTL = 3600

# Initialize Telegram bot
telegram_bot = telegram.Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    try:
        telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {str(e)}")

# Flask Dashboard Routes
@app.route("/", methods=["GET", "POST"])
def dashboard():
    """Render the trading bot dashboard"""
    if request.method == "POST":
        if request.form.get("password") != DASHBOARD_PASSWORD:
            return "Access Denied", 403
        if request.form.get("reset"):
            clear_trade_history()
            return redirect("/")
        new_mode = request.form.get("strategy")
        if new_mode in ["Safe", "Balanced", "Aggressive"]:
            global STRATEGY_MODE, TRADE_INTERVAL, TP_MOVE_PERCENT, BREAKEVEN_TRIGGER, RISK_PERCENT
            STRATEGY_MODE = new_mode
            # Update trading settings based on new mode
            if new_mode == "Safe":
                TRADE_INTERVAL = 600
                TP_MOVE_PERCENT = 0.3 / 100
                BREAKEVEN_TRIGGER = 0.5 / 100
                RISK_PERCENT = 1.0
            elif new_mode == "Aggressive":
                TRADE_INTERVAL = 120
                TP_MOVE_PERCENT = 1.0 / 100
                BREAKEVEN_TRIGGER = 1.5 / 100
                RISK_PERCENT = 2.0
            else:
                TRADE_INTERVAL = 300
                TP_MOVE_PERCENT = 0.5 / 100
                BREAKEVEN_TRIGGER = 1.0 / 100
                RISK_PERCENT = 1.5
            logging.info(f"Strategy mode changed to {new_mode}")
            send_telegram_message(f"🔄 Strategy changed to {new_mode} mode")
            return redirect("/")
            
    trade_records = load_trade_history()
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MAGUS PRIME X Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1000px; margin: 0 auto; }
                .card { background: white; padding: 20px; border-radius: 10px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                .running { background-color: #d4edda; color: #155724; }
                .error { background-color: #f8d7da; color: #721c24; }
                .controls { display: flex; gap: 10px; align-items: center; }
                input, select, button { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                button { background: #007bff; color: white; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
                .chart-container { height: 300px; margin: 20px 0; }
                .trade-list { max-height: 300px; overflow-y: auto; }
                .trade-item { padding: 8px; border-bottom: 1px solid #eee; }
                .trade-item:hover { background: #f8f9fa; }
            </style>
            <meta http-equiv="refresh" content="30">
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h1>🚀 MAGUS PRIME X Trading Bot</h1>
                    <div class="status running">
                        <h3>Status: Active</h3>
                    </div>
                </div>
                
                <div class="card">
                    <h3>Strategy Configuration</h3>
                    <p><strong>Mode:</strong> {{ mode }}</p>
                    <p><strong>Trade Interval:</strong> {{ interval }} seconds</p>
                    <p><strong>Risk Level:</strong> {{ risk }}%</p>
                    <p><strong>TP Movement:</strong> {{ tp }}%</p>
                    <p><strong>Breakeven Trigger:</strong> {{ be }}%</p>
                    
                    <form method="POST" class="controls">
                        <input type="password" name="password" placeholder="Dashboard password" required>
                        <select name="strategy">
                            <option value="Safe" {{ 'selected' if mode == 'Safe' else '' }}>Safe</option>
                            <option value="Balanced" {{ 'selected' if mode == 'Balanced' else '' }}>Balanced</option>
                            <option value="Aggressive" {{ 'selected' if mode == 'Aggressive' else '' }}>Aggressive</option>
                        </select>
                        <button type="submit">Change Mode</button>
                        <button type="submit" name="reset" value="1" onclick="return confirm('Clear all trade history?')">Reset History</button>
                    </form>
                </div>
                
                <div class="card">
                    <h3>📈 Performance Chart</h3>
                    <div class="chart-container">
                        <canvas id="performanceChart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📜 Recent Trades</h3>
                    <div class="trade-list">
                        {% for trade in history|reverse %}
                        <div class="trade-item">
                            {{ trade['Time'] }} - {{ trade['Symbol'] }} {{ trade['Action'] }}
                            | TP: {{ "%.2f"|format(trade['TP']) }}
                            | SL: {{ "%.2f"|format(trade['SL']) }}
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <script>
                const ctx = document.getElementById('performanceChart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: {{ history|map(attribute='Time')|list|tojson }},
                        datasets: [{
                            label: 'Take Profit',
                            data: {{ history|map(attribute='TP')|list|tojson }},
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            fill: true
                        }, {
                            label: 'Stop Loss',
                            data: {{ history|map(attribute='SL')|list|tojson }},
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            intersect: false,
                            mode: 'index'
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                }
                            }
                        }
                    }
                });
            </script>
        </body>
        </html>
    """, 
    mode=STRATEGY_MODE,
    interval=TRADE_INTERVAL,
    risk=RISK_PERCENT,
    tp=TP_MOVE_PERCENT*100,
    be=BREAKEVEN_TRIGGER*100,
    history=trade_records
    )

def load_unmatched_symbols():
    """Load list of previously unmatched symbols"""
    try:
        if os.path.exists("unmatched_symbols.json"):
            with open("unmatched_symbols.json", 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"Error loading unmatched symbols: {str(e)}")
        return {}

def save_unmatched_symbol(symbol, attempted_matches):
    """Save unmatched symbol with details for analysis"""
    try:
        unmatched = load_unmatched_symbols()
        unmatched[symbol] = {
            'timestamp': datetime.now().isoformat(),
            'attempted_matches': attempted_matches,
            'normalized_form': normalize_symbol(symbol)
        }
        with open("unmatched_symbols.json", 'w') as f:
            json.dump(unmatched, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving unmatched symbol: {str(e)}")

def normalize_symbol(symbol):
    """Normalize a trading symbol to match Capital.com format"""
    # Remove any whitespace
    symbol = symbol.strip()
    # Remove common separators (/, -, _)
    symbol = re.sub(r'[/_-]', '', symbol)
    # Convert to uppercase
    symbol = symbol.upper()
    return symbol

def find_market_match(symbol, markets):
    """Find the best matching market for a given symbol"""
    normalized_symbol = normalize_symbol(symbol)
    attempted_matches = []
    
    # Try exact match with normalized names
    for market in markets:
        market_name = normalize_symbol(market.get('instrumentName', ''))
        if normalized_symbol == market_name:
            logging.info(f"[Symbol Match] Exact match found: {symbol} -> {market['instrumentName']}")
            return market
        attempted_matches.append(f"Exact: {market_name}")
            
    # Try matching by removing suffixes like "/USD", "/GBP", etc.
    for market in markets:
        market_name = normalize_symbol(market.get('instrumentName', ''))
        if normalized_symbol in market_name or market_name in normalized_symbol:
            logging.info(f"[Symbol Match] Partial match found: {symbol} -> {market['instrumentName']}")
            return market
        attempted_matches.append(f"Partial: {market_name}")
            
    # Try matching by checking epic directly
    for market in markets:
        epic = normalize_symbol(market.get('epic', ''))
        if normalized_symbol in epic or epic in normalized_symbol:
            logging.info(f"[Symbol Match] Epic match found: {symbol} -> {market['epic']}")
            return market
        attempted_matches.append(f"Epic: {epic}")
    
    # Log and save unmatched symbol
    logging.warning(f"[Symbol Match] No match found for {symbol} after all attempts")
    save_unmatched_symbol(symbol, attempted_matches)
    return None

class TradingBot:
    def __init__(self):
        self.active_trades = {}
        self.market_data = {}
        self.session = self.create_session()
        self.available_markets = self.get_available_markets()
        self.indicators = {
            'EMA200': {'timeframe': '1h', 'period': 200},
            'RSI': {'timeframe': '15m', 'period': 14},
            'MACD': {'timeframe': '15m', 'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9},
            'BB': {'timeframe': '15m', 'period': 20, 'nbdevup': 2, 'nbdevdn': 2},
            'VWAP': {'timeframe': '15m'},
            'StochRSI': {'timeframe': '15m', 'period': 14, 'fastk_period': 3, 'fastd_period': 3}
        }
        
    def create_session(self):
        session = requests.Session()
        retry = Retry(total=5, backoff_factor=0.1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def authenticate(self):
        """Authenticate with Capital.com API"""
        url = f"{CAPITAL_API_URL}/session"
        headers = {"X-CAP-API-KEY": CAPITAL_API_KEY}
        data = {
            "identifier": CAPITAL_IDENTIFIER,
            "password": CAPITAL_API_PASSWORD
        }
        
        try:
            response = self.session.post(url, headers=headers, json=data)
            if response.status_code == 200:
                data = response.json()
                return data.get('CST'), data.get('X-SECURITY-TOKEN')
            else:
                logging.error(f"Authentication failed: {response.text}")
                return None, None
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return None, None

    def get_available_markets(self):
        """Get list of available markets from Capital.com"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return []

            response = self.session.get(
                f"{CAPITAL_API_URL}/markets",
                headers={
                    "CST": cst,
                    "X-SECURITY-TOKEN": security,
                    "X-CAP-API-KEY": CAPITAL_API_KEY
                }
            )
            
            if response.status_code == 200:
                markets = response.json().get('markets', [])
                # Return full market objects for tradeable markets
                tradeable_markets = [m for m in markets if m.get('marketStatus') == 'TRADEABLE']
                logging.info(f"Found {len(tradeable_markets)} tradeable markets")
                return tradeable_markets
                
            logging.error(f"Failed to get markets: {response.text}")
            return []
            
        except Exception as e:
            logging.error(f"Error getting markets: {str(e)}")
            return []

    def calculate_position_size(self, symbol, risk_percent=1):
        """Calculate position size based on account balance and risk"""
        try:
            account_info = self.get_account_info()
            balance = account_info['balance']
            risk_amount = balance * (risk_percent / 100)
            
            # Get current price and ATR for SL calculation
            price_data = self.get_market_data(symbol)
            if not price_data:
                return None
                
            current_price = price_data['close'].iloc[-1]
            atr = self.calculate_atr(symbol)
            
            # Use ATR for stop loss distance
            sl_distance = atr * 1.5
            
            # Calculate position size
            position_size = risk_amount / sl_distance
            
            # Adjust for minimum lot size
            min_size = self.get_min_size(symbol)
            position_size = max(min_size, position_size)
            
            return position_size
            
        except Exception as e:
            logging.error(f"Error calculating position size: {str(e)}")
            return None

    def analyze_news_sentiment(self, symbol):
        """Analyze news sentiment for a given symbol"""
        try:
            # Get relevant news
            news = newsapi.get_everything(
                q=symbol,
                language='en',
                sort_by='publishedAt',
                page_size=10
            )
            
            if not news['articles']:
                return 0  # Neutral if no news
                
            # Simple sentiment analysis
            sentiment_score = 0
            for article in news['articles']:
                title = article['title'].lower()
                if any(word in title for word in ['surge', 'jump', 'rise', 'gain', 'bull']):
                    sentiment_score += 1
                elif any(word in title for word in ['drop', 'fall', 'decline', 'bear', 'crash']):
                    sentiment_score -= 1
                    
            return sentiment_score / len(news['articles'])  # Normalize between -1 and 1
            
        except Exception as e:
            logging.error(f"News sentiment analysis error: {str(e)}")
            return 0

    def get_historical_candles(self, epic, resolution='MINUTE_15', num_points=50):
        """Fetch historical OHLCV candles from Capital.com"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return None

            url = f"{CAPITAL_API_URL}/prices/{epic}"
            params = {
                'resolution': resolution,
                'max': num_points
            }
            headers = {
                "CST": cst,
                "X-SECURITY-TOKEN": security,
                "X-CAP-API-KEY": CAPITAL_API_KEY
            }
            
            response = self.session.get(url, headers=headers, params=params)
            if response.status_code == 200:
                prices = response.json().get('prices', [])
                if not prices:
                    logging.warning(f"No historical prices found for {epic}")
                    return None
                    
                df = pd.DataFrame([{
                    'timestamp': pd.to_datetime(p['snapshotTime']),
                    'open': float(p['openPrice']['bid']),
                    'high': float(p['highPrice']['bid']),
                    'low': float(p['lowPrice']['bid']),
                    'close': float(p['closePrice']['bid']),
                    'volume': float(p.get('lastTradedVolume', 0))
                } for p in prices if 'closePrice' in p])
                
                if len(df) < 2:
                    logging.warning(f"Insufficient historical data for {epic}")
                    return None
                    
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                
                logging.info(f"Retrieved {len(df)} historical candles for {epic}")
                return df
                
            logging.error(f"Failed to fetch historical candles: {response.text}")
            return None
            
        except Exception as e:
            logging.error(f"Historical data error for {epic}: {str(e)}")
            return None

    def get_market_data(self, symbol):
        """Get market data with historical candles for analysis"""
        try:
            # Check cache first
            cache_key = normalize_symbol(symbol)
            current_time = time.time()
            
            if cache_key in MARKET_CACHE:
                cached_data = MARKET_CACHE[cache_key]
                if current_time - cached_data['timestamp'] < MARKET_CACHE_TTL:
                    logging.debug(f"Using cached data for {symbol}")
                    return cached_data['data']
            
            # Add delay to avoid rate limiting
            time.sleep(0.5)
            
            # Get market details
            cst, security = self.authenticate()
            if not cst or not security:
                return None

            search_response = self.session.get(
                f"{CAPITAL_API_URL}/markets",
                params={'searchTerm': symbol},
                headers={
                    "CST": cst,
                    "X-SECURITY-TOKEN": security,
                    "X-CAP-API-KEY": CAPITAL_API_KEY
                }
            )
            
            if search_response.status_code != 200:
                logging.error(f"Failed to search markets: {search_response.text}")
                return None
                
            markets = search_response.json().get('markets', [])
            if not markets:
                logging.error(f"No markets found for symbol: {symbol}")
                return None
                
            # Find the best matching market
            market = find_market_match(symbol, markets)
            if not market:
                logging.error(f"Could not find matching market for symbol: {symbol}")
                return None
                
            # Get historical candles
            epic = market.get('epic')
            data = self.get_historical_candles(epic)
            
            if data is not None:
                # Update cache
                MARKET_CACHE[cache_key] = {
                    'data': data,
                    'timestamp': current_time,
                    'epic': epic,
                    'market': market
                }
                return data
                
            logging.error(f"Failed to get market data for {symbol}")
            return None
            
        except Exception as e:
            logging.error(f"Error getting market data for {symbol}: {str(e)}")
            return None

    def calculate_indicators(self, data):
        """Calculate technical indicators"""
        try:
            if data is None or len(data) < 2:
                return None
                
            # Convert data to numpy arrays
            high = data['high'].astype(float).values
            low = data['low'].astype(float).values
            close = data['close'].astype(float).values
            volume = data['volume'].astype(float).values
            
            # Calculate indicators
            sma = talib.SMA(close, timeperiod=20)
            rsi = talib.RSI(close, timeperiod=14)
            macd, macdsignal, macdhist = talib.MACD(close)
            upper, middle, lower = talib.BBANDS(close)
            
            return {
                'sma': sma[-1] if not np.isnan(sma[-1]) else None,
                'rsi': rsi[-1] if not np.isnan(rsi[-1]) else None,
                'macd': macd[-1] if not np.isnan(macd[-1]) else None,
                'macd_signal': macdsignal[-1] if not np.isnan(macdsignal[-1]) else None,
                'bb_upper': upper[-1] if not np.isnan(upper[-1]) else None,
                'bb_middle': middle[-1] if not np.isnan(middle[-1]) else None,
                'bb_lower': lower[-1] if not np.isnan(lower[-1]) else None
            }
            
        except Exception as e:
            logging.error(f"Error calculating indicators: {str(e)}")
            return None

    def analyze_market(self, symbol):
        """Enhanced market analysis with multiple timeframes and indicators"""
        try:
            # Get market data
            data = self.get_market_data(symbol)
            if data is None:
                return 'HOLD', None, None
                
            # Calculate indicators
            indicators = self.calculate_indicators(data)
            if indicators is None:
                return 'HOLD', None, None
                
            current_price = float(data['close'].iloc[-1])
            
            # Trading signals
            signals = []
            
            # Trend following (SMA)
            if current_price > indicators['sma']:
                signals.append(1)  # Bullish
            else:
                signals.append(-1)  # Bearish
                
            # RSI
            if indicators['rsi'] < 30:
                signals.append(1)  # Oversold
            elif indicators['rsi'] > 70:
                signals.append(-1)  # Overbought
                
            # MACD
            if indicators['macd'] > indicators['macd_signal']:
                signals.append(1)
            else:
                signals.append(-1)
                
            # Bollinger Bands
            if current_price < indicators['bb_lower']:
                signals.append(1)  # Potential bounce
            elif current_price > indicators['bb_upper']:
                signals.append(-1)  # Potential reversal
                
            # News sentiment
            sentiment = self.analyze_news_sentiment(symbol)
            if sentiment > 0.3:
                signals.append(1)
            elif sentiment < -0.3:
                signals.append(-1)
                
            # Final decision
            signal_sum = sum(signals)
            signal_threshold = len(signals) * 0.6  # 60% agreement needed
            
            if signal_sum > signal_threshold:
                return 'BUY', self.calculate_take_profit(current_price, 'BUY'), self.calculate_stop_loss(current_price, 'BUY')
            elif signal_sum < -signal_threshold:
                return 'SELL', self.calculate_take_profit(current_price, 'SELL'), self.calculate_stop_loss(current_price, 'SELL')
            
            return 'HOLD', None, None
            
        except Exception as e:
            logging.error(f"Market analysis error: {str(e)}")
            return 'HOLD', None, None

    def execute_trade(self, symbol, action, tp, sl):
        """Execute a trade with proper risk management"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return False

            # Get current price
            current_price = self.get_current_price(symbol)
            if current_price is None:
                return False

            # Calculate position size based on risk
            account_info = self.get_account_info()
            if not account_info:
                return False

            balance = float(account_info.get('balance', 0))
            risk_amount = balance * (RISK_PERCENT / 100)
            
            # Calculate stop loss distance
            sl_distance = abs(current_price - sl)
            if sl_distance == 0:
                logging.error(f"Invalid stop loss distance for {symbol}")
                return False
                
            # Calculate position size
            position_size = risk_amount / sl_distance
            
            # Execute the trade
            success = self.place_order(symbol, action, position_size, tp, sl)
            if success:
                # Save trade to history
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_trade_to_csv(now, symbol, action, tp, sl)
                
                # Send detailed notification
                msg = f"✅ Trade Executed: {symbol}\n"
                msg += f"Action: {action}\n"
                msg += f"Entry: {current_price:.2f}\n"
                msg += f"Size: {position_size:.4f}\n"
                msg += f"TP: {tp:.2f}\n"
                msg += f"SL: {sl:.2f}\n"
                msg += f"Risk: ${risk_amount:.2f} ({RISK_PERCENT}%)"
                send_telegram_message(msg)
                
                # Update active trades
                self.active_trades[symbol] = {
                    'entry_price': current_price,
                    'position_size': position_size,
                    'direction': action,
                    'take_profit': tp,
                    'stop_loss': sl,
                    'timestamp': now
                }
                
                logging.info(f"Trade executed successfully for {symbol}")
                return True
            else:
                logging.error(f"Failed to execute trade for {symbol}")
                return False
                
        except Exception as e:
            logging.error(f"Trade execution error: {str(e)}")
            return False

    def update_active_trades(self):
        """Update active trades with trailing stop-loss and breakeven logic"""
        try:
            for symbol, trade in list(self.active_trades.items()):
                current_price = self.get_current_price(symbol)
                if current_price is None:
                    continue
                
                entry_price = trade['entry_price']
                stop_loss = trade['stop_loss']
                take_profit = trade['take_profit']
                direction = trade['direction']
                position_size = trade['position_size']
                
                # Calculate profit/loss percentage
                if direction == 'BUY':
                    pnl_percent = (current_price - entry_price) / entry_price * 100
                else:
                    pnl_percent = (entry_price - current_price) / entry_price * 100
                
                # Trailing stop-loss logic
                if pnl_percent > 0:
                    # Move stop loss to breakeven
                    if pnl_percent >= BREAKEVEN_TRIGGER * 100:
                        new_sl = entry_price
                        if direction == 'BUY' and new_sl > stop_loss:
                            stop_loss = new_sl
                            msg = f"🔒 Moving SL to breakeven: {symbol}\n"
                            msg += f"Current Price: {current_price:.2f}\n"
                            msg += f"New SL: {stop_loss:.2f}"
                            send_telegram_message(msg)
                            logging.info(f"Moving SL to breakeven for {symbol}")
                        elif direction == 'SELL' and new_sl < stop_loss:
                            stop_loss = new_sl
                            msg = f"🔒 Moving SL to breakeven: {symbol}\n"
                            msg += f"Current Price: {current_price:.2f}\n"
                            msg += f"New SL: {stop_loss:.2f}"
                            send_telegram_message(msg)
                            logging.info(f"Moving SL to breakeven for {symbol}")
                    
                    # Trail take profit
                    if pnl_percent >= TP_MOVE_PERCENT * 100:
                        tp_movement = current_price * TP_MOVE_PERCENT
                        if direction == 'BUY':
                            new_tp = take_profit + tp_movement
                            if new_tp > take_profit:
                                take_profit = new_tp
                                msg = f"📈 Trailing TP up: {symbol}\n"
                                msg += f"Current Price: {current_price:.2f}\n"
                                msg += f"New TP: {take_profit:.2f}"
                                send_telegram_message(msg)
                                logging.info(f"Trailing TP up for {symbol} to {take_profit:.2f}")
                        else:
                            new_tp = take_profit - tp_movement
                            if new_tp < take_profit:
                                take_profit = new_tp
                                msg = f"📉 Trailing TP down: {symbol}\n"
                                msg += f"Current Price: {current_price:.2f}\n"
                                msg += f"New TP: {take_profit:.2f}"
                                send_telegram_message(msg)
                                logging.info(f"Trailing TP down for {symbol} to {take_profit:.2f}")
                
                # Check for stop-loss or take-profit hit
                if direction == 'BUY':
                    if current_price <= stop_loss:
                        self.close_trade(symbol, 'Stop Loss')
                        pnl = (stop_loss - entry_price) * position_size
                        msg = f"🔴 Stop Loss Hit: {symbol}\n"
                        msg += f"Entry: {entry_price:.2f}\n"
                        msg += f"Exit: {stop_loss:.2f}\n"
                        msg += f"P/L: ${pnl:.2f}"
                        send_telegram_message(msg)
                        continue
                    if current_price >= take_profit:
                        self.close_trade(symbol, 'Take Profit')
                        pnl = (take_profit - entry_price) * position_size
                        msg = f"🟢 Take Profit Hit: {symbol}\n"
                        msg += f"Entry: {entry_price:.2f}\n"
                        msg += f"Exit: {take_profit:.2f}\n"
                        msg += f"P/L: ${pnl:.2f}"
                        send_telegram_message(msg)
                        continue
                else:  # SELL
                    if current_price >= stop_loss:
                        self.close_trade(symbol, 'Stop Loss')
                        pnl = (entry_price - stop_loss) * position_size
                        msg = f"🔴 Stop Loss Hit: {symbol}\n"
                        msg += f"Entry: {entry_price:.2f}\n"
                        msg += f"Exit: {stop_loss:.2f}\n"
                        msg += f"P/L: ${pnl:.2f}"
                        send_telegram_message(msg)
                        continue
                    if current_price <= take_profit:
                        self.close_trade(symbol, 'Take Profit')
                        pnl = (entry_price - take_profit) * position_size
                        msg = f"🟢 Take Profit Hit: {symbol}\n"
                        msg += f"Entry: {entry_price:.2f}\n"
                        msg += f"Exit: {take_profit:.2f}\n"
                        msg += f"P/L: ${pnl:.2f}"
                        send_telegram_message(msg)
                        continue
                
                # Update trade with new levels
                self.active_trades[symbol].update({
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'pnl_percent': pnl_percent,
                    'current_price': current_price
                })
                
        except Exception as e:
            logging.error(f"Error updating active trades: {str(e)}")

    def get_position(self, deal_ref):
        """Get position details by deal reference"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return None
                
            response = self.session.get(
                f"{CAPITAL_API_URL}/positions/{deal_ref}",
                headers={
                    "CST": cst,
                    "X-SECURITY-TOKEN": security,
                    "X-CAP-API-KEY": CAPITAL_API_KEY
                }
            )
            
            if response.status_code == 200:
                return response.json()
                
            return None
            
        except Exception as e:
            logging.error(f"Error getting position: {str(e)}")
            return None

    def move_stop_loss(self, deal_ref, new_level):
        """Move stop loss level for a position"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return False
                
            response = self.session.put(
                f"{CAPITAL_API_URL}/positions/{deal_ref}/stop-level",
                headers={
                    "CST": cst,
                    "X-SECURITY-TOKEN": security,
                    "X-CAP-API-KEY": CAPITAL_API_KEY
                },
                json={'stopLevel': str(new_level)}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"Error moving stop loss: {str(e)}")
            return False

    def update_take_profit(self, deal_ref, new_level):
        """Update take profit level for a position"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return False
                
            response = self.session.put(
                f"{CAPITAL_API_URL}/positions/{deal_ref}/profit-level",
                headers={
                    "CST": cst,
                    "X-SECURITY-TOKEN": security,
                    "X-CAP-API-KEY": CAPITAL_API_KEY
                },
                json={'profitLevel': str(new_level)}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"Error updating take profit: {str(e)}")
            return False

    def calculate_atr(self, symbol, period=14):
        """Calculate Average True Range"""
        try:
            data = self.get_market_data(symbol)
            if data is None or len(data) < period:
                return None
                
            high = data['high'].values
            low = data['low'].values
            close = data['close'].values
            
            return talib.ATR(high, low, close, timeperiod=period)[-1]
            
        except Exception as e:
            logging.error(f"Error calculating ATR: {str(e)}")
            return None

    def calculate_take_profit(self, price, direction, atr_multiplier=2):
        """Calculate take profit level"""
        try:
            if direction == 'BUY':
                return price * (1 + atr_multiplier * 0.01)  # 2% above entry
            else:
                return price * (1 - atr_multiplier * 0.01)  # 2% below entry
        except Exception as e:
            logging.error(f"Error calculating TP: {str(e)}")
            return None

    def calculate_stop_loss(self, price, direction, atr_multiplier=1):
        """Calculate stop loss level"""
        try:
            if direction == 'BUY':
                return price * (1 - atr_multiplier * 0.01)  # 1% below entry
            else:
                return price * (1 + atr_multiplier * 0.01)  # 1% above entry
        except Exception as e:
            logging.error(f"Error calculating SL: {str(e)}")
            return None

    def is_market_open(self, symbol):
        """Check if market is open"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return False
                
            # First get the epic
            search_response = self.session.get(
                f"{CAPITAL_API_URL}/markets",
                params={'searchTerm': symbol},
                headers={
                    "CST": cst,
                    "X-SECURITY-TOKEN": security,
                    "X-CAP-API-KEY": CAPITAL_API_KEY
                }
            )
            
            if search_response.status_code == 200:
                markets = search_response.json().get('markets', [])
                for market in markets:
                    if market.get('instrumentName') == symbol:
                        return market.get('marketStatus') == 'TRADEABLE'
                        
            return False
            
        except Exception as e:
            logging.error(f"Error checking market status: {str(e)}")
            return False

    def get_min_size(self, symbol):
        """Get minimum position size for a symbol"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return 0.1  # Default minimum size
                
            # First get the epic
            search_response = self.session.get(
                f"{CAPITAL_API_URL}/markets",
                params={'searchTerm': symbol},
                headers={
                    "CST": cst,
                    "X-SECURITY-TOKEN": security,
                    "X-CAP-API-KEY": CAPITAL_API_KEY
                }
            )
            
            if search_response.status_code == 200:
                markets = search_response.json().get('markets', [])
                for market in markets:
                    if market.get('instrumentName') == symbol:
                        return float(market.get('minDealSize', 0.1))
                        
            return 0.1  # Default minimum size
            
        except Exception as e:
            logging.error(f"Error getting min size: {str(e)}")
            return 0.1

    def get_account_info(self):
        """Get account information"""
        try:
            cst, security = self.authenticate()
            if not cst or not security:
                return None
                
            response = self.session.get(
                f"{CAPITAL_API_URL}/accounts",
                headers={
                    "CST": cst,
                    "X-SECURITY-TOKEN": security,
                    "X-CAP-API-KEY": CAPITAL_API_KEY
                }
            )
            
            if response.status_code == 200:
                accounts = response.json().get('accounts', [])
                if accounts:
                    return {
                        'balance': float(accounts[0].get('balance', 0)),
                        'currency': accounts[0].get('currency', 'USD')
                    }
                    
            return None
            
        except Exception as e:
            logging.error(f"Error getting account info: {str(e)}")
            return None

    def run(self):
        """Main bot loop with enhanced features"""
        logging.info(f"Starting trading bot in {STRATEGY_MODE} mode")
        send_telegram_message(f"🚀 Bot Started\nMode: {STRATEGY_MODE}\nRisk: {RISK_PERCENT}%")
        
        while True:
            try:
                test_markets = ["BTC/USD", "ETH/USD", "LTC/USD", "XRP/USD"]
                for symbol in test_markets:
                    try:
                        logging.info(f"\n{'='*50}\nAnalyzing {symbol}")
                        
                        if not self.is_market_open(symbol):
                            logging.info(f"Market closed for {symbol}")
                            continue
                        
                        data = self.get_market_data(symbol)
                        if data is None:
                            logging.error(f"No market data available for {symbol}")
                            continue
                        
                        # Get trading signal
                        action, tp, sl = self.analyze_market(symbol)
                        
                        if action in ['BUY', 'SELL']:
                            # Execute trade with risk management
                            success = self.execute_trade(symbol, action, tp, sl)
                            
                            if success:
                                msg = f"✅ Trade Executed: {symbol}\n"
                                msg += f"Action: {action}\n"
                                msg += f"Entry: {data['close'].iloc[-1]:.2f}\n"
                                msg += f"TP: {tp:.2f}\n"
                                msg += f"SL: {sl:.2f}"
                                send_telegram_message(msg)
                                logging.info(f"Trade executed successfully for {symbol}")
                            else:
                                logging.error(f"Failed to execute trade for {symbol}")
                        
                        # Update existing trades
                        self.update_active_trades()
                        
                    except Exception as e:
                        logging.error(f"Error processing {symbol}: {str(e)}")
                        continue
                
                logging.info(f"Sleeping for {TRADE_INTERVAL} seconds...")
                time.sleep(TRADE_INTERVAL)
                
            except Exception as e:
                error_msg = f"Bot runtime error: {str(e)}"
                logging.error(error_msg)
                send_telegram_message(f"❌ {error_msg}")
                time.sleep(60)

def load_trade_history():
    """Load trade history"""
    try:
        if os.path.exists("trade_history.json"):
            with open("trade_history.json", 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Error loading trade history: {str(e)}")
        return []

def clear_trade_history():
    """Clear trade history"""
    try:
        with open("trade_history.json", 'w') as f:
            json.dump([], f)
    except Exception as e:
        logging.error(f"Error clearing trade history: {str(e)}")

def save_trade_to_csv(timestamp, symbol, action, tp, sl):
    """Save trade to CSV file"""
    try:
        with open("trade_history.json", 'r') as f:
            history = json.load(f)
            
        history.append({
            'Time': timestamp,
            'Symbol': symbol,
            'Action': action,
            'TP': tp,
            'SL': sl
        })
        
        with open("trade_history.json", 'w') as f:
            json.dump(history, f)
            
    except Exception as e:
        logging.error(f"Error saving trade to CSV: {str(e)}")

# Start the bot
if __name__ == "__main__":
    try:
        bot = TradingBot()
        
        # Start Flask server for webhooks
        webhook_thread = threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000})
        webhook_thread.daemon = True
        webhook_thread.start()
        
        # Start trading bot
        bot.run()
        
    except Exception as e:
        logging.error(f"Bot startup error: {str(e)}")

# Dashboard with advanced analytics
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        if request.form.get("password") != DASHBOARD_PASSWORD:
            return "Access Denied", 403
        if request.form.get("reset"):
            clear_trade_history()
            return redirect("/dashboard")
        if request.form.get("pause"):
            os.environ['BOT_PAUSED'] = '1'
            return redirect("/dashboard")
        if request.form.get("resume"):
            os.environ['BOT_PAUSED'] = '0'
            return redirect("/dashboard")
    trades = load_trade_history()
    pnl = sum([(float(t['TP']) - float(t['SL'])) if t.get('Result') == 'WIN' else -abs(float(t['SL'])) for t in trades if t.get('Result')])
    wins = sum(1 for t in trades if t.get('Result') == 'WIN')
    losses = sum(1 for t in trades if t.get('Result') == 'LOSS')
    winrate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0
    return render_template_string("""
    <html>
    <head>
        <title>MAGUS PRIME X Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body style="font-family:sans-serif;">
        <h2>🤖 MAGUS PRIME X – AI Trading Bot</h2>
        <p><b>Status:</b> {{ 'Paused' if paused else 'Running' }}</p>
        <p><b>Strategy:</b> {{ mode }} | Interval: {{ interval }}s</p>
        <p><b>Performance:</b> Net PnL = ${{ pnl }}, Win Rate = {{ winrate|round(2) }}%</p>
        <form method="POST">
            <input type="password" name="password" placeholder="Password" required>
            <select name="strategy">
                <option value="Safe">Safe</option>
                <option value="Balanced">Balanced</option>
                <option value="Aggressive">Aggressive</option>
            </select>
            <button type="submit">Switch Strategy</button>
            <button name="pause" value="1">Pause</button>
            <button name="resume" value="1">Resume</button>
            <button name="reset" value="1">Reset History</button>
        </form>
        <hr>
        <h3>📈 Recent Trades</h3>
        <canvas id="chart"></canvas>
        <script>
            const ctx = document.getElementById('chart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: {{ trades|map(attribute='Time')|list|tojson }},
                    datasets: [{
                        label: 'TP',
                        data: {{ trades|map(attribute='TP')|list|tojson }},
                        borderColor: 'green',
                        fill: false
                    }, {
                        label: 'SL',
                        data: {{ trades|map(attribute='SL')|list|tojson }},
                        borderColor: 'red',
                        fill: false
                    }]
                },
                options: { responsive: true }
            });
        </script>
        <ul>
        {% for t in trades %}
            <li>{{ t['Time'] }} - {{ t['Symbol'] }} {{ t['Action'] }} | TP: {{ t['TP'] }} | SL: {{ t['SL'] }} | Result: {{ t['Result'] or 'N/A' }}</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """, mode=STRATEGY_MODE, interval=TRADE_INTERVAL, pnl=pnl, winrate=winrate, trades=trades, paused=os.environ.get('BOT_PAUSED') == '1')

# Root redirect to dashboard
@app.route("/")
def root():
    return redirect("/dashboard")

if __name__ == '__main__':
    try:
        bot = TradingBot()
        
        # Start Flask server in a daemon thread
        threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000}, daemon=True).start()
        
        # Start trading bot
        bot.run()
        
    except Exception as e:
        send_telegram_message(f"❌ Startup failed: {str(e)}")
        logging.error(f"Startup error: {str(e)}")
