from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from functools import wraps
import pandas as pd
import os
import json
from datetime import datetime
import logging
import requests
import threading
import time
import hmac
import hashlib
import base64
import websocket
from enhanced_trading_engine import EnhancedTradingEngine, Position
from news_analyzer import NewsAnalyzer
from hedging_strategy import HedgingStrategy
from ai_learning_system import AILearningSystem
from chatgpt_analyst import ChatGPTAnalyst
from chart_analyzer import ChartAnalyzer
from telegram_notifier import TelegramNotifier
from pine_script_integration import PineScriptIntegration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
    template_folder=os.path.abspath('templates'),
    static_folder=os.path.abspath('static'),
    static_url_path='/static'
)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = os.getenv("CAPITAL_API_KEY")
API_SECRET = os.getenv("CAPITAL_API_PASSWORD")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_IDENTIFIER")
CAPITAL_WS_URL = "wss://api-streaming.capital.com/api/v1/streaming"
CAPITAL_API_URL = os.getenv("CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1")

# Initialize components
trading_engine = EnhancedTradingEngine()
news_analyzer = NewsAnalyzer()
hedging_strategy = HedgingStrategy()
ai_learning_system = AILearningSystem()
chatgpt_analyst = ChatGPTAnalyst()
chart_analyzer = ChartAnalyzer()
telegram_notifier = TelegramNotifier()
pine_script_integration = PineScriptIntegration()

# Global variables
ws_client = None
subscribed_symbols = set()
market_data = {}
active_positions = []
connection_retry_count = 0
MAX_RETRIES = 5
RETRY_DELAY = 5
bot_running = False
bot_start_time = None

def generate_signature(secret, message):
    return hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

def capital_api_request(method, endpoint, data=None):
    try:
        timestamp = str(int(time.time() * 1000))
        signature = generate_signature(API_SECRET, timestamp + method + endpoint + (json.dumps(data) if data else ""))
        
        headers = {
            "X-CAP-API-KEY": API_KEY,
            "X-CAP-API-TIMESTAMP": timestamp,
            "X-CAP-API-SIGNATURE": signature,
            "Content-Type": "application/json"
        }
        
        url = f"{CAPITAL_API_URL}{endpoint}"
        response = requests.request(method, url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        return {"error": str(e), "status": "failed"}

def get_account_info():
    """Fetch account information from Capital.com"""
    try:
        endpoint = "/accounts"
        response = capital_api_request("GET", endpoint)
        if "accounts" in response:
            account = response["accounts"][0]  # Get the first account
            return {
                "totalBalance": account.get("balance", 0),
                "availableMargin": account.get("available", 0),
                "usedMargin": account.get("margin", 0),
                "openPnL": account.get("unrealizedPL", 0),
                "dailyPnL": account.get("dayPL", 0),
                "positions": account.get("positions", []),
                "currency": account.get("currency", "USD")
            }
        return {}
    except Exception as e:
        logging.error(f"Error fetching account info: {str(e)}")
        return {}

@app.route('/api/account')
def get_account_data():
    """API endpoint to get account information"""
    account_info = get_account_info()
    return jsonify(account_info)

def fetch_available_symbols():
    """Fetch all available trading symbols from Capital.com"""
    try:
        endpoint = "/markets"
        response = capital_api_request("GET", endpoint)
        symbols = []
        if "markets" in response:
            for market in response["markets"]:
                symbol_info = {
                    "symbol": market["symbol"],
                    "name": market["name"],
                    "type": market["type"],
                    "leverage": market.get("leverageRatio", 1),
                    "minSize": market.get("minDealSize", 0.01),
                    "maxSize": market.get("maxDealSize", 1000),
                    "precision": market.get("decimalPlaces", 2)
                }
                symbols.append(symbol_info)
        return symbols
    except Exception as e:
        logging.error(f"Error fetching symbols: {str(e)}")
        return []

@app.route('/api/symbols')
def get_symbols():
    """API endpoint to get available symbols"""
    symbols = fetch_available_symbols()
    return jsonify(symbols)

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    """Execute a trade with Capital.com"""
    try:
        data = request.json
        trade_params = {
            "symbol": data["symbol"],
            "direction": data["direction"],
            "size": data["size"],
            "stopLoss": data.get("stopLoss"),
            "takeProfit": data.get("takeProfit"),
            "leverage": data.get("leverage", 1)
        }
        
        endpoint = "/positions"
        response = capital_api_request("POST", endpoint, trade_params)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/position/<position_id>', methods=['PUT'])
def modify_position(position_id):
    """Modify an existing position (stop loss, take profit)"""
    try:
        data = request.json
        modify_params = {
            "stopLoss": data.get("stopLoss"),
            "takeProfit": data.get("takeProfit")
        }
        
        endpoint = f"/positions/{position_id}"
        response = capital_api_request("PUT", endpoint, modify_params)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/position/<position_id>', methods=['DELETE'])
def close_position(position_id):
    """Close a position"""
    try:
        endpoint = f"/positions/{position_id}"
        response = capital_api_request("DELETE", endpoint)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def start_websocket():
    """Start the WebSocket connection to Capital.com"""
    global ws_client, bot_running
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            if 'marketData' in data:
                symbol = data['marketData']['symbol']
                timeframe = data['marketData']['timeframe']
                
                if symbol not in market_data:
                    market_data[symbol] = {}
                if timeframe not in market_data[symbol]:
                    market_data[symbol][timeframe] = pd.DataFrame()
                    
                # Update market data
                new_data = pd.DataFrame([data['marketData']])
                market_data[symbol][timeframe] = pd.concat([market_data[symbol][timeframe], new_data])
                
                # Update indicators
                if bot_running:
                    trading_engine.market_data = market_data
                    trading_engine.calculate_indicators(market_data[symbol][timeframe], timeframe)
                    
                    # Check for trading signals
                    signal, params = trading_engine.analyze_market(symbol)
                    
                    if signal != "HOLD":
                        # Check news before trading
                        should_pause, reason = news_analyzer.should_pause_trading(symbol)
                        if should_pause:
                            logging.info(f"Trading paused for {symbol}: {reason}")
                            return
                            
                        # Execute trade if conditions are met
                        position = execute_trade(symbol, signal, params)
                        
                        # Check for hedging opportunities
                        if position:
                            should_hedge, reason, ratio = hedging_strategy.check_hedge_conditions(
                                position, market_data, trading_engine.indicators
                            )
                            if should_hedge:
                                hedge_position = hedging_strategy.create_hedge(position, ratio, reason)
                                if hedge_position:
                                    execute_trade(symbol, 'HEDGE', {'position': hedge_position})
                                    
                    # Manage existing positions
                    trading_engine.manage_positions()
                    hedging_strategy.manage_hedged_positions(market_data, trading_engine.indicators)
                    
                # Emit updated data to clients
                socketio.emit('market_update', {
                    'symbol': symbol,
                    'data': data['marketData']
                })
                
        except Exception as e:
            logging.error(f"Error processing WebSocket message: {str(e)}")
            
    def on_error(ws, error):
        logging.error(f"WebSocket error: {str(error)}")
        
    def on_close(ws, close_status_code, close_msg):
        logging.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        reconnect_websocket()
        
    def on_open(ws):
        logging.info("WebSocket connection established")
        # Authenticate
        auth_message = {
            "action": "auth",
            "token": API_KEY,
            "identifier": CAPITAL_IDENTIFIER
        }
        ws.send(json.dumps(auth_message))
        # Subscribe to initial symbols
        subscribe_symbols(['BTCUSD', 'EURUSD', 'US100'])
        
    # Create WebSocket connection
    ws_client = websocket.WebSocketApp(
        CAPITAL_WS_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
        header={
            'Content-Type': 'application/json',
            'X-CAP-API-KEY': API_KEY
        }
    )
    
    ws_thread = threading.Thread(target=ws_client.run_forever)
    ws_thread.daemon = True
    ws_thread.start()

def reconnect_websocket():
    """Attempt to reconnect the WebSocket"""
    global connection_retry_count
    
    if connection_retry_count < MAX_RETRIES:
        time.sleep(RETRY_DELAY * (2 ** connection_retry_count))
        connection_retry_count += 1
        start_websocket()
    else:
        logging.error("Max reconnection attempts reached")
        socketio.emit('connection_status', {'status': 'disconnected'})

def subscribe_symbols(symbols):
    """Subscribe to market data for given symbols"""
    if not ws_client:
        return
        
    for symbol in symbols:
        message = {
            "action": "subscribe",
            "symbols": [symbol],
            "granularity": ["5m", "1h", "4h"]  # Multiple timeframes
        }
        ws_client.send(json.dumps(message))
        subscribed_symbols.add(symbol)

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    emit('connection_status', {'status': 'connected'})
    # Send initial data
    emit('market_data', {'data': market_data})
    emit('positions_update', {'positions': active_positions})

@socketio.on('subscribe')
def handle_subscribe(data):
    if 'symbols' in data:
        subscribe_symbols(data['symbols'])

# API key authentication
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Invalid API key"}), 401
    return decorated_function

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/test_connection', methods=['POST'])
def test_connection():
    try:
        data = request.get_json()
        api_key = data.get('apiKey')
        api_password = data.get('apiPassword')
        identifier = data.get('identifier')

        # Test the connection with provided credentials
        headers = {
            'X-SECURITY-TOKEN': api_key,
            'CST': identifier,
            'Content-Type': 'application/json'
        }

        response = requests.get(f"{CAPITAL_API_URL}/session", headers=headers)
        response.raise_for_status()

        return jsonify({
            'success': True,
            'message': 'Connection test successful'
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'Connection test failed: {str(e)}'
        })

@app.route('/api/connect', methods=['POST'])
def connect_broker():
    try:
        data = request.get_json()
        api_key = data.get('apiKey')
        api_password = data.get('apiPassword')
        identifier = data.get('identifier')

        # Save credentials to environment variables
        os.environ['CAPITAL_API_KEY'] = api_key
        os.environ['CAPITAL_API_PASSWORD'] = api_password
        os.environ['CAPITAL_IDENTIFIER'] = identifier

        # Update global variables
        global API_KEY, API_SECRET, CAPITAL_IDENTIFIER
        API_KEY = api_key
        API_SECRET = api_password
        CAPITAL_IDENTIFIER = identifier

        # Test the connection
        headers = {
            'X-SECURITY-TOKEN': API_KEY,
            'CST': CAPITAL_IDENTIFIER,
            'Content-Type': 'application/json'
        }

        response = requests.get(f"{CAPITAL_API_URL}/session", headers=headers)
        response.raise_for_status()

        # Start WebSocket connection
        start_websocket()

        return jsonify({
            'success': True,
            'message': 'Successfully connected to Capital.com'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Connection failed: {str(e)}'
        })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email and password:
        return jsonify({
            'token': API_KEY,
            'username': email.split('@')[0]
        })
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/portfolio')
@require_api_key
def get_portfolio():
    return jsonify({
        'value': 124578.34,
        'change_percent': 2.45,
        'active_trades': {
            'total': 12,
            'scalping': 8,
            'swing': 4
        },
        'win_rate': 76
    })

@app.route('/api/portfolio/analytics')
def get_portfolio_analytics():
    timeframe = request.args.get('timeframe', '1m')
    
    # Mock data - replace with actual data from Capital.com API
    portfolio_data = {
        'portfolioValue': 24567.89,
        'winRate': 68.5,
        'avgProfitLoss': 2.3,
        'sharpeRatio': 1.85,
        'maxDrawdown': -15.2,
        'leverageUsage': 5.2,
        'marginUsage': 42.5,
        'riskPerTrade': 1.2,
        'dailyVar': 3.5,
        'sortinoRatio': 2.1,
        'calmarRatio': 0.95,
        'profitFactor': 1.75,
        'correlations': {
            'BTC/USD': {
                'BTC/USD': 1.0,
                'ETH/USD': 0.85,
                'EUR/USD': 0.15,
                'GOLD': -0.25
            },
            'ETH/USD': {
                'BTC/USD': 0.85,
                'ETH/USD': 1.0,
                'EUR/USD': 0.20,
                'GOLD': -0.15
            },
            'EUR/USD': {
                'BTC/USD': 0.15,
                'ETH/USD': 0.20,
                'EUR/USD': 1.0,
                'GOLD': 0.35
            },
            'GOLD': {
                'BTC/USD': -0.25,
                'ETH/USD': -0.15,
                'EUR/USD': 0.35,
                'GOLD': 1.0
            }
        },
        'trades': [
            {
                'date': '2025-03-20T10:30:00Z',
                'entryTime': '2025-03-20T10:30:00Z',
                'exitTime': '2025-03-20T14:45:00Z',
                'pair': 'BTC/USD',
                'type': 'Long',
                'entry': 65000.00,
                'exit': 66300.00,
                'size': '0.5 BTC',
                'pnl': 1300.00,
                'assetClass': 'crypto'
            },
            {
                'date': '2025-03-20T09:15:00Z',
                'entryTime': '2025-03-20T09:15:00Z',
                'exitTime': '2025-03-20T16:30:00Z',
                'pair': 'EUR/USD',
                'type': 'Short',
                'entry': 1.0850,
                'exit': 1.0830,
                'size': '100,000 EUR',
                'pnl': 200.00,
                'assetClass': 'forex'
            },
            {
                'date': '2025-03-20T08:45:00Z',
                'entryTime': '2025-03-20T08:45:00Z',
                'exitTime': '2025-03-21T10:15:00Z',
                'pair': 'GOLD',
                'type': 'Long',
                'entry': 2100.50,
                'exit': 2095.25,
                'size': '10 oz',
                'pnl': -525.00,
                'assetClass': 'commodities'
            }
        ]
    }
    
    return jsonify(portfolio_data)

@app.route('/api/dashboard/signals')
@require_api_key
def get_signals():
    return jsonify([
        {
            'asset': 'BTC/USD',
            'type': 'BUY',
            'entry': 65000,
            'stop_loss': 64000,
            'take_profit': 67000,
            'timestamp': datetime.now().isoformat()
        }
    ])

@app.route('/api/dashboard/positions')
@require_api_key
def get_positions():
    return jsonify([
        {
            'asset': 'ETH/USD',
            'type': 'LONG',
            'entry': 3500,
            'current': 3600,
            'pnl': '+2.85%'
        }
    ])

@app.route('/api/dashboard/market_news')
@require_api_key
def get_market_news():
    return jsonify([
        {
            'title': 'Market Update',
            'content': 'Crypto markets showing strong momentum',
            'timestamp': datetime.now().isoformat()
        }
    ])

@app.route('/api/assets')
@require_api_key
def get_assets():
    # Read assets from .env file
    assets = []
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=')
                    if key.startswith('ASSET_'):
                        assets.append(value)
    except:
        pass
    
    # Add default assets
    default_assets = [
        'BTC/USD', 'ETH/USD', 'XRP/USD',  # Crypto
        'EUR/USD', 'GBP/USD', 'USD/JPY',  # Forex
        'US500', 'US100', 'UK100',        # Indices
        'XAUUSD', 'XAGUSD', 'USOIL'       # Commodities
    ]
    assets.extend([a for a in default_assets if a not in assets])
    
    return jsonify(assets)

@app.route('/api/bot/configure', methods=['POST'])
@require_api_key
def configure_bot():
    data = request.get_json()
    trading_style = data.get('trading_style', 'scalping')
    trade_amount = data.get('trade_amount', 0)
    selected_assets = data.get('assets', [])
    
    # Here you would save the configuration to a database or a file
    print(f"Bot configured with style: {trading_style}, amount: {trade_amount}, assets: {selected_assets}")

    return jsonify({
        'status': 'success',
        'message': 'Bot configuration updated'
    })

@app.route('/api/subscription/plans')
def get_subscription_plans():
    return jsonify([
        {'duration': '1 month', 'price': 45},
        {'duration': '3 months', 'price': 130},
        {'duration': '5 months', 'price': 200},
        {'duration': '1 year', 'price': 500}
    ])

@app.route('/api/subscription/purchase', methods=['POST'])
@require_api_key
def purchase_subscription():
    data = request.get_json()
    plan = data.get('plan')
    return jsonify({
        'status': 'success',
        'message': f'Successfully subscribed to {plan} plan'
    })

@app.route('/api/notifications')
@require_api_key
def get_notifications():
    return jsonify([
        {
            'id': 1,
            'type': 'trade',
            'message': 'New trade opened: BTC/USD',
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': 2,
            'type': 'alert',
            'message': 'Take profit hit on ETH/USD',
            'timestamp': datetime.now().isoformat()
        }
    ])

@app.route('/api/portfolio/optimization')
def get_portfolio_optimization():
    risk_profile = request.args.get('risk', 'medium')
    
    # Mock optimization data - replace with actual optimization calculations
    optimization_data = {
        'currentAllocation': {
            'BTC/USD': 25,
            'ETH/USD': 18,
            'EUR/USD': 35,
            'GOLD': 22
        },
        'metrics': {
            'currentReturn': 15.8,
            'currentRisk': 18.5,
            'sharpeRatio': 1.85,
            'diversificationScore': 7.5
        },
        'efficientFrontier': {
            'portfolioCombinations': [
                {'risk': 12.5, 'return': 8.2},
                {'risk': 15.8, 'return': 11.5},
                {'risk': 18.5, 'return': 15.8},
                {'risk': 22.3, 'return': 19.2},
                {'risk': 25.7, 'return': 22.5}
            ],
            'optimalPortfolios': {
                'low': {
                    'risk': 12.5,
                    'return': 8.2,
                    'allocation': {
                        'BTC/USD': 20,
                        'ETH/USD': 15,
                        'EUR/USD': 40,
                        'GOLD': 25
                    }
                },
                'medium': {
                    'risk': 18.5,
                    'return': 15.8,
                    'allocation': {
                        'BTC/USD': 35,
                        'ETH/USD': 25,
                        'EUR/USD': 25,
                        'GOLD': 15
                    }
                },
                'high': {
                    'risk': 25.7,
                    'return': 22.5,
                    'allocation': {
                        'BTC/USD': 45,
                        'ETH/USD': 35,
                        'EUR/USD': 15,
                        'GOLD': 5
                    }
                }
            }
        },
        'rebalancing': {
            'lastRebalanced': '2025-03-06T10:00:00Z',
            'portfolioHealth': 'healthy',
            'recommendations': [
                {
                    'asset': 'BTC/USD',
                    'currentAllocation': 25,
                    'targetAllocation': 35,
                    'action': 'increase',
                    'change': 10
                },
                {
                    'asset': 'EUR/USD',
                    'currentAllocation': 35,
                    'targetAllocation': 25,
                    'action': 'decrease',
                    'change': -10
                }
            ]
        }
    }
    
    return jsonify(optimization_data)

@app.route('/api/portfolio/rebalancing')
def get_rebalancing_status():
    threshold = float(request.args.get('threshold', '5'))
    
    # Mock rebalancing data - replace with actual calculations
    rebalancing_data = {
        'status': {
            'lastCheck': '2025-03-21T12:21:35Z',
            'totalDrift': 3.8,
            'driftStatus': 'within_bounds',
            'lastRebalanced': '2025-03-06T10:00:00Z'
        },
        'triggers': {
            'timeBased': {
                'enabled': True,
                'interval': 30,  # days
                'nextScheduled': '2025-04-05T10:00:00Z'
            },
            'driftBased': {
                'enabled': True,
                'threshold': threshold,
                'currentMax': 3.8
            },
            'marketEvents': {
                'enabled': True,
                'volatilityThreshold': 25,  # VIX level
                'currentVolatility': 18.5
            },
            'cashFlow': {
                'enabled': True,
                'threshold': 5,  # % of portfolio
                'recentFlows': []
            }
        },
        'driftByAsset': [
            {
                'asset': 'BTC/USD',
                'targetAllocation': 35,
                'currentAllocation': 25,
                'drift': 10,
                'action': 'buy',
                'amount': 2456.79,  # USD
                'estimatedFee': 2.46
            },
            {
                'asset': 'ETH/USD',
                'targetAllocation': 25,
                'currentAllocation': 18,
                'drift': 7,
                'action': 'buy',
                'amount': 1719.75,
                'estimatedFee': 1.72
            },
            {
                'asset': 'EUR/USD',
                'targetAllocation': 25,
                'currentAllocation': 35,
                'drift': -10,
                'action': 'sell',
                'amount': 2456.79,
                'estimatedFee': 2.46
            },
            {
                'asset': 'GOLD',
                'targetAllocation': 15,
                'currentAllocation': 22,
                'drift': -7,
                'action': 'sell',
                'amount': 1719.75,
                'estimatedFee': 1.72
            }
        ],
        'costs': {
            'tradingFees': 12.50,
            'estimatedSlippage': 0.15,  # percentage
            'totalCost': 45.75,
            'costPercentage': 0.18
        }
    }
    
    return jsonify(rebalancing_data)

@app.route('/api/connect', methods=['POST'])
def api_connect():
    """Connect to the Capital.com API"""
    try:
        # Validate required environment variables
        required_vars = ['CAPITAL_API_KEY', 'CAPITAL_API_SECRET', 'CAPITAL_IDENTIFIER', 'CAPITAL_API_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return jsonify({
                "success": False, 
                "error": f"Missing required environment variables: {', '.join(missing_vars)}"
            }), 400
            
        # Test the connection by making a simple API call
        account_info = get_account_info()
        if not account_info:
            return jsonify({
                "success": False, 
                "error": "Failed to fetch account data. Please check your API credentials."
            }), 400
            
        # Start WebSocket if not already running
        if not ws_client or not ws_client.sock or not ws_client.sock.connected:
            start_websocket()
            
        return jsonify({
            "success": True, 
            "message": "Successfully connected to Capital.com API",
            "account": account_info
        })
        
    except Exception as e:
        logging.error(f"Connection error: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Failed to connect to Capital.com API. Please check your credentials and try again."
        }), 500

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    """Disconnect from the Capital.com API"""
    try:
        global ws_client
        if ws_client:
            ws_client.close()
            ws_client = None
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Disconnection error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    try:
        # Initialize bot with current settings
        bot_settings = {
            'active': True,
            'strategy': request.json.get('strategy', 'default'),
            'risk_level': request.json.get('risk_level', 'medium'),
            'max_positions': request.json.get('max_positions', 5)
        }
        
        # Start the bot process
        from bot import start_bot_process
        start_bot_process(bot_settings)
        
        return jsonify({
            "success": True, 
            "message": "Bot started successfully",
            "settings": bot_settings
        })
    except Exception as e:
        logging.error(f"Error starting bot: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    try:
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Error stopping bot: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/currency', methods=['POST'])
def set_currency():
    """Set the account currency"""
    try:
        data = request.get_json()
        currency = data.get('currency')
        if currency not in ['USD', 'EUR', 'GBP', 'AED']:
            return jsonify({"success": False, "error": "Invalid currency"}), 400
            
        # Update currency in Capital.com API
        endpoint = "/account/currency"
        response = capital_api_request("POST", endpoint, {"currency": currency})
        return jsonify({"success": True, "currency": currency})
    except Exception as e:
        logging.error(f"Error setting currency: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/available_assets')
def get_available_assets():
    try:
        # Get all available assets from Capital.com
        assets = capital_api_request("GET", "/markets")
        return jsonify({
            'success': True,
            'assets': assets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/connect', methods=['POST'])
def connect_api():
    try:
        # Initialize Capital.com API connection
        api_key = request.json.get('apiKey')
        api_secret = request.json.get('apiSecret')
        
        capital_api_request("POST", "/auth", {"key": api_key, "secret": api_secret})
        account_info = capital_api_request("GET", "/account")
        
        return jsonify({
            'success': True,
            'account': account_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/api_start_bot', methods=['POST'])
def api_start_bot():
    """Start the trading bot"""
    global bot_running, bot_start_time
    
    try:
        # Initialize components
        trading_engine.market_data = market_data
        news_analyzer.update_news()
        
        # Start the bot
        bot_running = True
        bot_start_time = datetime.now()
        
        # Start periodic tasks
        threading.Thread(target=periodic_tasks).daemon = True
        threading.Thread(target=periodic_tasks).start()
        
        return jsonify({
            'status': 'success',
            'message': 'Bot started successfully'
        })
        
    except Exception as e:
        logging.error(f"Error starting bot: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def periodic_tasks():
    """Run periodic tasks for the bot"""
    while bot_running:
        try:
            # Update news every 5 minutes
            news_analyzer.update_news()
            
            # Sleep for 5 minutes
            time.sleep(300)
            
        except Exception as e:
            logging.error(f"Error in periodic tasks: {str(e)}")
            time.sleep(60)  # Sleep for 1 minute on error

@app.route('/api/api_stop_bot', methods=['POST'])
def api_stop_bot():
    try:
        bot.stop()
        return jsonify({
            'success': True,
            'message': 'Bot stopped successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/api_bot_status')
def api_bot_status():
    try:
        status = bot.get_status()
        return jsonify({
            'success': True,
            'active': status['active'],
            'lastTrade': status['last_trade'],
            'openPositions': status['open_positions'],
            'performance': status['performance']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

# API Endpoints for AI Learning System
@app.route('/api/ai/learn', methods=['POST'])
def learn_from_trade():
    """API endpoint to learn from a completed trade"""
    try:
        data = request.json
        result = ai_learning_system.learn_from_trade(
            symbol=data.get('symbol'),
            direction=data.get('direction'),
            entry_price=data.get('entry_price'),
            exit_price=data.get('exit_price'),
            outcome=data.get('outcome'),
            market_conditions=data.get('market_conditions', {}),
            indicators=data.get('indicators', {})
        )
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logging.error(f"Error in AI learning: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/ai/analyze/<symbol>', methods=['GET'])
def ai_analyze_symbol(symbol):
    """API endpoint to get AI analysis for a symbol"""
    try:
        timeframe = request.args.get('timeframe', '1h')
        depth = int(request.args.get('depth', 100))
        
        if symbol not in market_data or timeframe not in market_data[symbol]:
            return jsonify({"success": False, "error": "No data available for this symbol/timeframe"}), 404
            
        data = market_data[symbol][timeframe].tail(depth)
        analysis = ai_learning_system.analyze_market(symbol, data)
        return jsonify({"success": True, "analysis": analysis})
    except Exception as e:
        logging.error(f"Error in AI analysis: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/ai/performance', methods=['GET'])
def ai_performance():
    """API endpoint to get AI learning system performance metrics"""
    try:
        metrics = ai_learning_system.get_performance_metrics()
        return jsonify({"success": True, "metrics": metrics})
    except Exception as e:
        logging.error(f"Error getting AI performance: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# API Endpoints for ChatGPT Integration
@app.route('/api/chatgpt/analyze', methods=['POST'])
def chatgpt_analyze():
    """API endpoint to get ChatGPT analysis of market conditions"""
    try:
        data = request.json
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '1h')
        analysis_type = data.get('analysis_type', 'general')
        
        if symbol not in market_data or timeframe not in market_data[symbol]:
            return jsonify({"success": False, "error": "No data available for this symbol/timeframe"}), 404
            
        market_data_df = market_data[symbol][timeframe].tail(100)
        
        # Get news if available
        news = []
        try:
            news = news_analyzer.get_news(symbol, days=3)
        except:
            pass
            
        # Get chart patterns if available
        patterns = []
        try:
            chart_results = chart_analyzer.analyze_candles(symbol, market_data_df)
            patterns = chart_results.get('patterns', [])
        except:
            pass
            
        # Get analysis based on type
        if analysis_type == 'general':
            result = chatgpt_analyst.analyze_market(symbol, market_data_df, news)
        elif analysis_type == 'strategy':
            result = chatgpt_analyst.generate_strategy(symbol, market_data_df, patterns)
        elif analysis_type == 'news':
            result = chatgpt_analyst.analyze_news_impact(symbol, news)
        else:
            result = chatgpt_analyst.analyze_market(symbol, market_data_df, news)
            
        return jsonify({"success": True, "analysis": result})
    except Exception as e:
        logging.error(f"Error in ChatGPT analysis: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/chatgpt/strategy', methods=['POST'])
def chatgpt_create_strategy():
    """API endpoint to generate a trading strategy using ChatGPT"""
    try:
        data = request.json
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '1h')
        risk_profile = data.get('risk_profile', 'moderate')
        
        if symbol not in market_data or timeframe not in market_data[symbol]:
            return jsonify({"success": False, "error": "No data available for this symbol/timeframe"}), 404
            
        market_data_df = market_data[symbol][timeframe].tail(100)
        strategy = chatgpt_analyst.generate_strategy(symbol, market_data_df, risk_profile=risk_profile)
        
        return jsonify({"success": True, "strategy": strategy})
    except Exception as e:
        logging.error(f"Error generating strategy: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# API Endpoints for Chart Analysis
@app.route('/api/chart/analyze/<symbol>', methods=['GET'])
def chart_analyze(symbol):
    """API endpoint to analyze chart patterns for a symbol"""
    try:
        timeframe = request.args.get('timeframe', '1h')
        
        if symbol not in market_data or timeframe not in market_data[symbol]:
            return jsonify({"success": False, "error": "No data available for this symbol/timeframe"}), 404
            
        data = market_data[symbol][timeframe]
        analysis = chart_analyzer.analyze_candles(symbol, data)
        return jsonify({"success": True, "analysis": analysis})
    except Exception as e:
        logging.error(f"Error analyzing chart: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/chart/trend/<symbol>', methods=['GET'])
def chart_trend(symbol):
    """API endpoint to analyze trend for a symbol across timeframes"""
    try:
        timeframes = request.args.get('timeframes', '1h,4h,1d').split(',')
        
        # Check if we have data for the requested timeframes
        available_timeframes = {}
        for tf in timeframes:
            if symbol in market_data and tf in market_data[symbol]:
                available_timeframes[tf] = market_data[symbol][tf]
        
        if not available_timeframes:
            return jsonify({"success": False, "error": "No data available for this symbol/timeframes"}), 404
            
        trend_analysis = chart_analyzer.analyze_trend(symbol, available_timeframes)
        return jsonify({"success": True, "analysis": trend_analysis})
    except Exception as e:
        logging.error(f"Error analyzing trend: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# API Endpoints for Telegram Notifications
@app.route('/api/telegram/send', methods=['POST'])
def send_telegram():
    """API endpoint to send a telegram notification"""
    try:
        data = request.json
        notification_type = data.get('type', 'custom')
        
        if notification_type == 'signal':
            result = telegram_notifier.send_signal(
                symbol=data.get('symbol'),
                direction=data.get('direction'),
                entry=data.get('entry'),
                take_profit=data.get('take_profit'),
                stop_loss=data.get('stop_loss'),
                timeframe=data.get('timeframe', '1h'),
                confidence=data.get('confidence', 0.7),
                additional_info=data.get('additional_info', '')
            )
        elif notification_type == 'warning':
            result = telegram_notifier.send_warning(
                warning_message=data.get('message'),
                symbol=data.get('symbol', ''),
                timeframe=data.get('timeframe', '')
            )
        elif notification_type == 'analysis':
            result = telegram_notifier.send_market_analysis(
                symbol=data.get('symbol'),
                timeframe=data.get('timeframe', '1h'),
                price=data.get('price'),
                trend=data.get('trend'),
                sentiment=data.get('sentiment'),
                key_points=data.get('key_points', [])
            )
        else:
            result = telegram_notifier.send_custom_notification(
                title=data.get('title', 'Notification'),
                message=data.get('message'),
                importance=data.get('importance', 'normal')
            )
            
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Error sending telegram notification: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/telegram/subscribers', methods=['GET'])
def telegram_subscribers():
    """API endpoint to get telegram subscriber count"""
    try:
        count = telegram_notifier.get_subscribers_count()
        return jsonify({"success": True, "count": count})
    except Exception as e:
        logging.error(f"Error getting subscribers count: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# API Endpoints for Pine Script Integration
@app.route('/api/pine/indicators', methods=['GET'])
def get_pine_indicators():
    """API endpoint to get all available Pine Script indicators"""
    try:
        indicators = pine_script_integration.get_indicator_names()
        return jsonify({"success": True, "indicators": indicators})
    except Exception as e:
        logging.error(f"Error getting Pine indicators: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/pine/indicator/<indicator_name>', methods=['GET'])
def get_pine_indicator(indicator_name):
    """API endpoint to get details of a specific Pine Script indicator"""
    try:
        info = pine_script_integration.get_indicator_info(indicator_name)
        return jsonify({"success": True, "info": info})
    except Exception as e:
        logging.error(f"Error getting indicator info: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/pine/upload', methods=['POST'])
def upload_pine_script():
    """API endpoint to upload a new Pine Script indicator"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
            
        script_content = file.read().decode('utf-8')
        
        # Parse script metadata
        metadata = pine_script_integration.parse_pine_script(script_content)
        
        # Add the indicator
        indicator = pine_script_integration.add_indicator(
            name=metadata.get('name', file.filename),
            description=metadata.get('description', ''),
            script=script_content,
            parameters=metadata.get('parameters', {})
        )
        
        return jsonify({
            "success": True, 
            "message": f"Indicator '{indicator.name}' added successfully",
            "info": pine_script_integration.get_indicator_info(indicator.name)
        })
    except Exception as e:
        logging.error(f"Error uploading Pine Script: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/pine/apply', methods=['POST'])
def apply_pine_indicator():
    """API endpoint to apply a Pine Script indicator to market data"""
    try:
        data = request.json
        indicator_name = data.get('indicator')
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '1h')
        parameters = data.get('parameters', {})
        
        if symbol not in market_data or timeframe not in market_data[symbol]:
            return jsonify({"success": False, "error": "No data available for this symbol/timeframe"}), 404
            
        # Apply the indicator
        market_data_df = market_data[symbol][timeframe].copy()
        result_df = pine_script_integration.apply_indicator(indicator_name, market_data_df, parameters)
        
        # Convert result to dictionary for JSON response
        result_dict = {}
        for col in result_df.columns:
            if col not in market_data_df.columns:
                # Only include new columns from the indicator
                result_dict[col] = result_df[col].iloc[-20:].tolist()  # Last 20 values
                
        return jsonify({
            "success": True, 
            "results": result_dict,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error applying Pine indicator: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    start_websocket()
    socketio.run(app, debug=True, host='0.0.0.0', port=8000)
