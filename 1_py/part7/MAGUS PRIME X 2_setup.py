import os
import json
import sys

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def create_file(path, content):
    """Create file with specified content"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created file: {path}")

def setup_project():
    """Set up the entire MAGUS PRIME X project structure"""
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create directories
    directories = [
        'templates',
        'modules',
        'data',
        'logs',
        'config',
        'utils'
    ]
    
    for directory in directories:
        create_directory(os.path.join(base_dir, directory))
    
    # Create bot.py (main file)
    bot_py_content = """# Main MAGUS PRIME X Trading Bot Application
import os
import time
import asyncio
import logging
import threading
from datetime import datetime
import json
import pytz
from flask import Flask, request, render_template_string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MAGUS_PRIME_X")

# Initialize global variables
bot_state = {"balance": 10000.00, "equity": 10000.00}
active_signals = {}
trade_history = []
bot_start_time = None
trading_paused = False

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ENABLE_AUTOMATIC_TRADING = os.getenv("ENABLE_AUTOMATIC_TRADING", "true").lower() == "true"
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
ENABLE_RECOVERY_MODE = os.getenv("ENABLE_RECOVERY_MODE", "true").lower() == "true"
ENABLE_TRADE_RECAPS = os.getenv("ENABLE_TRADE_RECAPS", "true").lower() == "true"
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "admin123")

# Add this function to load HTML templates from files
def load_html_template(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error loading HTML template {filename}: {str(e)}")
        return f"<h1>Error loading template</h1><p>{str(e)}</p>"

# Initialize Flask application for web dashboard
dashboard_app = Flask(__name__)

@dashboard_app.route("/")
def dashboard():
    password = request.args.get("password")
    if password != DASHBOARD_PASSWORD:
        return "Unauthorized. Add ?password=YOUR_PASSWORD to access.", 401

    # Load the HTML template from file
    html = load_html_template('templates/dashboard.html')
    
    # Replace template variables with actual data
    html = html.replace("{{balance}}", str(bot_state.get("balance", "N/A")))
    html = html.replace("{{positions}}", str(len(active_signals)))
    
    # Calculate win rate from trade history
    total_completed = sum(1 for t in trade_history if t.get('result') not in ['pending', None])
    wins = sum(1 for t in trade_history if t.get('result') in ['TP1', 'TP2', 'TP3'])
    win_rate = int((wins / total_completed) * 100) if total_completed > 0 else 0
    
    html = html.replace("{{win_rate}}", str(win_rate))
    html = html.replace("{{total_trades}}", str(len(trade_history)))
    
    return html

def run_dashboard():
    dashboard_app.run(host="0.0.0.0", port=5000)

async def handle_trade_result(symbol, direction, result, entry_price=None, exit_price=None):
    """Handle trade result including stop loss recovery and sending trade recap"""
    logger.info(f"Trade result for {symbol} {direction}: {result}")
    trade_data = active_signals.get(symbol, {})
    timeframe = trade_data.get('timeframe', '15m')
    
    # Determine result description
    if result == "TP1" or result == "TP2" or result == "TP3":
        hit_level = result
        result_description = "Take Profit"
    elif result == "SL":
        hit_level = "SL"
        result_description = "Stop Loss"
    else:
        hit_level = "Unknown"
        result_description = result
    
    # Update trade history
    for trade in trade_history:
        if trade.get('symbol') == symbol and trade.get('result') == 'pending':
            trade['result'] = result
            trade['exit_time'] = datetime.now().isoformat()
            if entry_price and exit_price:
                trade['entry_price'] = entry_price
                trade['exit_price'] = exit_price
            break
    
    # Classify asset type
    asset_type = "Crypto" 
    if "JPY" in symbol or "USD" in symbol or "EUR" in symbol or "GBP" in symbol:
        asset_type = "Forex"
    elif symbol in ("GOLD", "XAUUSD", "SILVER", "XAGUSD", "OIL", "USOIL"):
        asset_type = "Commodity" 
    elif symbol.startswith(("US30", "US500", "NASDAQ", "SPX")):
        asset_type = "Index"
    
    # Handle recovery mode for stop losses
    if result == "SL" and ENABLE_RECOVERY_MODE:
        logger.warning(f"❌ Trade stopped out. Activating recovery mode for {symbol}")
        # Recovery logic would go here

async def main():
    """Main function to initialize and start the bot"""
    global bot_start_time
    bot_start_time = datetime.now()
    
    logger.info("Initializing MAGUS PRIME X Trading Bot...")
    logger.info(f"Configuration loaded. Mode: {'DEMO' if DEMO_MODE else 'LIVE'}")
    
    # Start background services
    threading.Thread(target=run_dashboard, daemon=True).start()
    logger.info("Dashboard started on port 5000")
    
    # Keep the bot running
    logger.info("MAGUS PRIME X Trading Bot is now online")
    try:
        while True:
            await asyncio.sleep(60)  # Sleep for a minute
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
"""
    create_file(os.path.join(base_dir, 'bot.py'), bot_py_content)
    
    # Create config.py
    config_py_content = """# Configuration settings for MAGUS PRIME X
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Trading settings
STRATEGY_MODE = os.getenv("STRATEGY_MODE", "Default")
MAX_OPEN_TRADES = int(os.getenv("MAX_OPEN_TRADES", "3"))
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "1.0"))  # Percentage of account

# API credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Feature flags
ENABLE_AUTOMATIC_TRADING = os.getenv("ENABLE_AUTOMATIC_TRADING", "true").lower() == "true"
ENABLE_RECOVERY_MODE = os.getenv("ENABLE_RECOVERY_MODE", "true").lower() == "true"
ENABLE_TRADE_RECAPS = os.getenv("ENABLE_TRADE_RECAPS", "true").lower() == "true"
ENABLE_NEWS_MONITORING = os.getenv("ENABLE_NEWS_MONITORING", "true").lower() == "true"
ENABLE_PRE_NEWS_EXIT = os.getenv("ENABLE_PRE_NEWS_EXIT", "true").lower() == "true"
ENABLE_AUTO_CLOSE_TIME = os.getenv("ENABLE_AUTO_CLOSE_TIME", "false").lower() == "true"
MAGUS_ASSISTANT_ENABLED = os.getenv("MAGUS_ASSISTANT_ENABLED", "true").lower() == "true"

# Auto-close settings
AUTO_CLOSE_HOUR = int(os.getenv("AUTO_CLOSE_HOUR", "16"))
AUTO_CLOSE_MINUTE = int(os.getenv("AUTO_CLOSE_MINUTE", "55"))
AUTO_CLOSE_DAYS = ["mon", "tue", "wed", "thu", "fri"]

# Dashboard settings
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "admin123")

# Create a single config object that other modules can import
config = {
    "STRATEGY_MODE": STRATEGY_MODE,
    "MAX_OPEN_TRADES": MAX_OPEN_TRADES,
    "DEMO_MODE": DEMO_MODE,
    "RISK_PER_TRADE": RISK_PER_TRADE,
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "ENABLE_AUTOMATIC_TRADING": ENABLE_AUTOMATIC_TRADING,
    "ENABLE_RECOVERY_MODE": ENABLE_RECOVERY_MODE,
    "ENABLE_TRADE_RECAPS": ENABLE_TRADE_RECAPS,
    "ENABLE_NEWS_MONITORING": ENABLE_NEWS_MONITORING,
    "ENABLE_PRE_NEWS_EXIT": ENABLE_PRE_NEWS_EXIT,
    "ENABLE_AUTO_CLOSE_TIME": ENABLE_AUTO_CLOSE_TIME,
    "MAGUS_ASSISTANT_ENABLED": MAGUS_ASSISTANT_ENABLED,
    "AUTO_CLOSE_HOUR": AUTO_CLOSE_HOUR,
    "AUTO_CLOSE_MINUTE": AUTO_CLOSE_MINUTE,
    "AUTO_CLOSE_DAYS": AUTO_CLOSE_DAYS,
    "DASHBOARD_PASSWORD": DASHBOARD_PASSWORD
}
"""
    create_file(os.path.join(base_dir, 'config.py'), config_py_content)
    
    # Create requirements.txt
    requirements_content = """python-telegram-bot>=20.0
flask==2.0.1
aiohttp>=3.8.1
python-dotenv==0.19.1
pytz==2021.3
numpy==1.21.4
pandas==1.3.4
matplotlib==3.5.0
openai>=0.27.0
python-dateutil==2.8.2
jinja2==3.0.3
requests==2.28.1
"""
    create_file(os.path.join(base_dir, 'requirements.txt'), requirements_content)
    
    # Create README.md
    readme_content = """# MAGUS PRIME X Trading Bot

An advanced algorithmic trading bot with AI-enhanced capabilities, technical analysis, and automated trade management.

## Features

- **Automated Trading**: Execute trades based on technical signals
- **Recovery Mode**: Handle stop-loss hits with intelligent retries  
- **News Monitoring**: Protection against volatile market events
- **AI Assistant**: Built-in AI-powered trading advisor
- **Web Dashboard**: Real-time monitoring of trades and account status
- **Telegram Integration**: Command the bot and receive trade notifications

## Setup

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys and configuration
4. Run the bot: `python bot.py`

## Environment Variables

```
# API Keys
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key

# Trading Configuration
DEMO_MODE=true
MAX_OPEN_TRADES=3
RISK_PER_TRADE=1.0

# Features
ENABLE_RECOVERY_MODE=true
ENABLE_NEWS_MONITORING=true
```

## Commands

- `/status` - Get current trading status
- `/pause` - Pause trading operations
- `/resume` - Resume trading operations
- `/forcebuy SYMBOL` - Force a buy order
- `/closeall` - Close all open positions

## Project Structure

```
📁 MAGUS PRIME X/
│
├── 📄 bot.py                     # Main bot application file
├── 📄 config.py                  # Configuration settings
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # Documentation
│
├── 📁 templates/                 # HTML templates for web interface
├── 📁 modules/                   # Core functionality modules
├── 📁 data/                      # Data storage
├── 📁 logs/                      # Log files
├── 📁 config/                    # Configuration files
└── 📁 utils/                     # Utility functions
```

## License

MIT License
"""
    create_file(os.path.join(base_dir, 'README.md'), readme_content)
    
    # Create dashboard.html template
    # We'll use the existing dashboard.html file if it exists
    if not os.path.exists(os.path.join(base_dir, 'templates', 'dashboard.html')):
        dashboard_html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAGUS PRIME X - Trading Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f5f7fa;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #2d3748;
        }
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        h2 {
            margin-top: 0;
            color: #4a5568;
            border-bottom: 1px solid #edf2f7;
            padding-bottom: 10px;
        }
        .stats {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }
        .stat-card {
            background-color: #f8fafc;
            border-radius: 6px;
            padding: 15px;
            width: calc(25% - 15px);
            box-sizing: border-box;
        }
        .stat-label {
            font-size: 12px;
            color: #718096;
            text-transform: uppercase;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #2d3748;
            margin-top: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #edf2f7;
        }
        th {
            background-color: #f8fafc;
            color: #718096;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>&#128302; MAGUS PRIME X Dashboard</h1>
        
        <div class="card">
            <h2>Account Summary</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Balance</div>
                    <div class="stat-value">${{balance}}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Open Positions</div>
                    <div class="stat-value">{{positions}}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Win Rate</div>
                    <div class="stat-value">{{win_rate}}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Trades</div>
                    <div class="stat-value">{{total_trades}}</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Active Positions</h2>
            <table id="positionsTable">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Direction</th>
                        <th>Entry</th>
                        <th>SL</th>
                        <th>TP</th>
                        <th>Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Positions will be inserted here by JavaScript -->
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>Recent Signals</h2>
            <table id="signalsTable">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Direction</th>
                        <th>Strategy</th>
                        <th>Timeframe</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Signals will be inserted here by JavaScript -->
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Refresh the page every 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
    </script>
</body>
</html>"""
        create_file(os.path.join(base_dir, 'templates', 'dashboard.html'), dashboard_html_content)
    
    # Create essential module files
    
    # Signal sender module
    signal_sender_content = """# Signal generation and sending functionality
import random
import logging
from datetime import datetime

logger = logging.getLogger("MAGUS_PRIME_X.signal_sender")

class SignalSender:
    def __init__(self):
        self.logger = logger
    
    def generate_signal(self, symbol):
        """Generate a trading signal for a symbol"""
        try:
            # In a real implementation, this would use technical analysis
            # This is just a placeholder with random logic
            direction = random.choice(["BUY", "SELL"])
            timeframe = random.choice(["15m", "1h", "4h"])
            strategy = random.choice(["Breakout", "RSI", "MACD", "Recovery"])
            confidence = random.randint(70, 95)
            
            signal = {
                "symbol": symbol,
                "direction": direction,
                "timeframe": timeframe,
                "strategy": strategy,
                "confidence": confidence,
                "stop_loss": random.uniform(1.0, 2.5),
                "take_profit": random.uniform(2.0, 5.0),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Generated signal for {symbol}: {signal}")
            return signal
        except Exception as e:
            self.logger.error(f"Error generating signal: {str(e)}")
            return None
    
    async def send_signal(self, symbol, signal):
        """Send a signal for processing"""
        try:
            # In a real implementation, this might publish to a queue or API
            self.logger.info(f"Sending signal for {symbol}: {signal}")
            
            # Implement your signal sending logic here
            # For example: await api_client.send_signal(signal)
            
            return {"status": "success", "message": f"Signal sent for {symbol}"}
        except Exception as e:
            self.logger.error(f"Error sending signal: {str(e)}")
            return {"status": "error", "message": str(e)}
"""
    create_file(os.path.join(base_dir, 'modules', 'signal_sender.py'), signal_sender_content)
    
    # Exchange module
    exchange_content = """# Exchange API integration
import logging
import random
from datetime import datetime

logger = logging.getLogger("MAGUS_PRIME_X.exchange")

class ExchangeClient:
    def __init__(self, api_key="", api_secret="", demo_mode=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.demo_mode = demo_mode
        self.logger = logger
        
    async def get_balance(self):
        """Get account balance"""
        if self.demo_mode:
            # Return demo balance
            return {"balance": 10000.0, "equity": 10050.0, "margin": 100.0}
        else:
            # Implement actual exchange API call
            self.logger.info("Getting real balance from exchange")
            return {"balance": 0.0, "equity": 0.0, "margin": 0.0}
    
    async def create_order(self, symbol, direction, amount, stop_loss=None, take_profit=None):
        """Create a new order"""
        try:
            order_id = f"ord_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
            
            if self.demo_mode:
                # Create a demo order
                current_price = await self.get_current_price(symbol)
                order = {
                    "id": order_id,
                    "symbol": symbol,
                    "direction": direction,
                    "amount": amount,
                    "price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "status": "open",
                    "timestamp": datetime.now().isoformat()
                }
                self.logger.info(f"Created demo order: {order}")
                return order
            else:
                # Implement actual exchange API call
                self.logger.info(f"Creating real order for {symbol} {direction}")
                # Example: result = await exchange_api.create_order(...)
                return {"id": order_id, "status": "open"}
        except Exception as e:
            self.logger.error(f"Error creating order: {str(e)}")
            raise
    
    async def get_current_price(self, symbol):
        """Get current price for a symbol"""
        if self.demo_mode:
            # Generate a realistic price
            base_prices = {
                "BTCUSDT": 50000.0,
                "ETHUSDT": 3000.0,
                "EURUSD": 1.1,
                "GBPUSD": 1.3,
                "XAUUSD": 1800.0,
                "US30": 33000.0,
            }
            
            base = base_prices.get(symbol, 100.0)
            variation = base * random.uniform(-0.002, 0.002)
            return base + variation
        else:
            # Implement actual exchange API call
            self.logger.info(f"Getting real price for {symbol}")
            return 0.0
    
    async def close_position(self, symbol):
        """Close an open position"""
        try:
            if self.demo_mode:
                # Close a demo position
                self.logger.info(f"Closing demo position for {symbol}")
                return {"symbol": symbol, "status": "closed", "profit": random.uniform(-10, 20)}
            else:
                # Implement actual exchange API call
                self.logger.info(f"Closing real position for {symbol}")
                # Example: result = await exchange_api.close_position(...)
                return {"symbol": symbol, "status": "closed"}
        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}")
            raise
    
    async def get_open_positions(self):
        """Get all open positions"""
        if self.demo_mode:
            # Return demo positions
            return []
        else:
            # Implement actual exchange API call
            self.logger.info("Getting real open positions")
            return []
"""
    create_file(os.path.join(base_dir, 'modules', 'exchange.py'), exchange_content)
    
    # OpenAI assistant module
    openai_assistant_content = """# OpenAI assistant integration for AI-powered trading advice
import logging
import os

logger = logging.getLogger("MAGUS_PRIME_X.openai_assistant")

# Try to import OpenAI, but don't fail if it's not installed
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. AI assistant functionality will be limited.")

class TradingAssistant:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.logger = logger
        
        if OPENAI_AVAILABLE and self.api_key:
            openai.api_key = self.api_key
            self.initialized = True
            self.logger.info("OpenAI assistant initialized")
        else:
            self.initialized = False
            self.logger.warning("OpenAI assistant not initialized (missing API key or package)")
    
    async def ask_question(self, question):
        """Ask a question to the AI assistant"""
        if not self.initialized:
            return "AI assistant not available. Please install OpenAI package and set API key."
        
        try:
            self.logger.info(f"Asking AI assistant: {question}")
            
            # Make API call to OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful trading assistant for the MAGUS PRIME X trading bot."},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                n=1,
                temperature=0.7,
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            self.logger.error(f"Error with AI assistant: {str(e)}")
            return f"Error: {str(e)}"
    
    async def analyze_trade(self, symbol, direction, entry_price, current_price=None):
        """Analyze a potential trade and give advice"""
        if not self.initialized:
            return "AI analysis not available"
        
        try:
            prompt = f"Analyze this trade: Symbol: {symbol}, Direction: {direction}, Entry Price: {entry_price}"
            if current_price:
                prompt += f", Current Price: {current_price}"
            prompt += ". Give a brief analysis."
            
            return await self.ask_question(prompt)
        except Exception as e:
            self.logger.error(f"Error with trade analysis: {str(e)}")
            return f"Error analyzing trade: {str(e)}"

async def process_user_query(query):
    """Process a user query using the AI assistant"""
    assistant = TradingAssistant()
    return await assistant.ask_question(query)
"""
    create_file(os.path.join(base_dir, 'modules', 'openai_assistant.py'), openai_assistant_content)
    
    # Create empty data files
    create_file(os.path.join(base_dir, 'data', 'trade_history.json'), '[]')
    create_file(os.path.join(base_dir, 'data', 'signals.json'), '[]')
    
    # Create empty log files
    create_file(os.path.join(base_dir, 'logs', 'bot.log'), '')
    create_file(os.path.join(base_dir, 'logs', 'trades.log'), '')
    
    # Create sample config files
    credentials_json = {
        "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
        "openai_api_key": "YOUR_OPENAI_API_KEY"
    }
    create_file(os.path.join(base_dir, 'config', 'credentials.json'), json.dumps(credentials_json, indent=4))
    
    settings_json = {
        "strategy_mode": "Default",
        "max_open_trades": 3,
        "demo_mode": True,
        "risk_per_trade": 1.0,
        "recovery_enabled": True,
        "news_monitoring": True,
        "dashboard_password": "admin123"
    }
    create_file(os.path.join(base_dir, 'config', 'settings.json'), json.dumps(settings_json, indent=4))
    
    # Create utility files
    helpers_py_content = """# Helper utility functions for the MAGUS PRIME X bot
import json
import logging
from datetime import datetime

logger = logging.getLogger("MAGUS_PRIME_X.utils.helpers")

def save_to_json(data, filename):
    """Save data to a JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving to {filename}: {str(e)}")
        return False

def load_from_json(filename):
    """Load data from a JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {filename}, returning empty list")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {filename}, returning empty list")
        return []
    except Exception as e:
        logger.error(f"Error loading from {filename}: {str(e)}")
        return []

def format_datetime(dt=None):
    """Format a datetime object to a readable string"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def calculate_win_rate(trade_history):
    """Calculate win rate from trade history"""
    if not trade_history:
        return 0.0
    
    total_completed = sum(1 for t in trade_history if t.get('result') not in ['pending', None])
    if total_completed == 0:
        return 0.0
    
    wins = sum(1 for t in trade_history if t.get('result') in ['TP1', 'TP2', 'TP3'])
    return (wins / total_completed) * 100

def is_crypto(symbol):
    """Check if a symbol is a cryptocurrency"""
    crypto_suffixes = ["USDT", "BTC", "ETH", "USD", "BUSD"]
    crypto_prefixes = ["BTC", "ETH", "LTC", "XRP", "BCH", "ADA", "DOT", "LINK", "XLM", "UNI"]
    
    for prefix in crypto_prefixes:
        if symbol.startswith(prefix):
            return True
    
    for suffix in crypto_suffixes:
        if symbol.endswith(suffix):
            return True
    
    return False
"""
    create_file(os.path.join(base_dir, 'utils', 'helpers.py'), helpers_py_content)
    
    # Create notifications utility
    notifications_py_content = """# Notification functions for Telegram and other services
import os
import logging
import asyncio

logger = logging.getLogger("MAGUS_PRIME_X.utils.notifications")

# Try to import Telegram libraries
try:
    import telegram
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("Telegram package not installed. Telegram notifications will not work.")

class NotificationManager:
    def __init__(self, telegram_token=None, telegram_chat_id=None):
        self.logger = logger
        
        # Telegram configuration
        self.telegram_token = telegram_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        
        # Initialize Telegram if available
        if TELEGRAM_AVAILABLE and self.telegram_token:
            try:
                self.telegram_bot = telegram.Bot(token=self.telegram_token)
                self.telegram_initialized = True
                self.logger.info("Telegram notifications initialized")
            except Exception as e:
                self.telegram_initialized = False
                self.logger.error(f"Error initializing Telegram: {str(e)}")
        else:
            self.telegram_initialized = False
            self.logger.warning("Telegram notifications not available")
    
    async def send_telegram_message(self, message):
        """Send a message via Telegram"""
        if not self.telegram_initialized:
            self.logger.warning("Telegram not initialized, can't send message")
            return False
        
        try:
            await self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode="Markdown"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def send_telegram_message_sync(self, message):
        """Send a Telegram message synchronously"""
        if not self.telegram_initialized:
            self.logger.warning("Telegram not initialized, can't send message")
            return False
        
        try:
            # Create an event loop if there isn't one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async function in the event loop
            return loop.run_until_complete(self.send_telegram_message(message))
        except Exception as e:
            self.logger.error(f"Error sending sync Telegram message: {str(e)}")
            return False

# Create a global instance of the notification manager
notification_manager = NotificationManager()

# Convenience functions to send messages
async def send_telegram_message_async(message):
    return await notification_manager.send_telegram_message(message)

def send_telegram_message_sync(message):
    return notification_manager.send_telegram_message_sync(message)

async def send_trade_notification(symbol, direction, entry=None, sl=None, tp=None, strategy=None):
    """Send a notification about a new trade"""
    message = f"🚨 *New Trade Alert*\n\n"
    message += f"🔹 *{symbol}* - {direction.upper()}\n"
    
    if entry:
        message += f"🔹 Entry: {entry}\n"
    if sl:
        message += f"🔹 Stop Loss: {sl}\n"
    if tp:
        message += f"🔹 Take Profit: {tp}\n"
    if strategy:
        message += f"🔹 Strategy: {strategy}\n"
    
    message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return await send_telegram_message_async(message)

async def send_trade_recap(symbol, direction, result, entry=None, exit=None, profit=None):
    """Send a notification about a trade result"""
    # Determine emoji based on result
    if "TP" in result:
        emoji = "✅"
    elif "SL" in result:
        emoji = "❌"
    else:
        emoji = "ℹ️"
    
    message = f"{emoji} *Trade Completed*\n\n"
    message += f"🔹 *{symbol}* - {direction.upper()}\n"
    message += f"🔹 Result: {result}\n"
    
    if entry:
        message += f"🔹 Entry: {entry}\n"
    if exit:
        message += f"🔹 Exit: {exit}\n"
    if profit:
        message += f"🔹 Profit: {profit}\n"
    
    message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return await send_telegram_message_async(message)
"""
    create_file(os.path.join(base_dir, 'utils', 'notifications.py'), notifications_py_content)
    
    print("\nProject setup complete! MAGUS PRIME X project structure created successfully.\n")
    print(f"Main components created in: {base_dir}")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Add your API credentials to config/credentials.json")
    print("3. Run the bot: python bot.py")

if __name__ == "__main__":
    setup_project()
    print("\nThank you for using MAGUS PRIME X!")
