import os
import time
import logging
from datetime import datetime, timedelta
import pytz
from enhanced_trading_engine import EnhancedTradingEngine
from risk_manager import EnhancedRiskManager
from ml_predictor import EnhancedMLPredictor
from market_regime import EnhancedMarketRegimeDetector
from news_analyzer import NewsAnalyzer
from capital_com_trader import CapitalComTrader
import pandas as pd
import numpy as np
from flask import Flask, render_template_string, jsonify
import threading
from typing import Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize trading components
engine = EnhancedTradingEngine()
risk_manager = EnhancedRiskManager()
ml_predictor = EnhancedMLPredictor()
regime_detector = EnhancedMarketRegimeDetector()
news_analyzer = NewsAnalyzer()
trader = CapitalComTrader()

# Global state
market_data = {}
analysis_results = {}
active_trades = {}

# Market hours
MARKET_HOURS = {
    'CRYPTO': {
        'is_24_7': True,
        'markets': ['BTC/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD']
    },
    'FOREX': {
        'is_24_7': False,
        'trading_hours': {
            'start': '00:00',  # Sunday 22:00 GMT
            'end': '23:00',    # Friday 22:00 GMT
        },
        'markets': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'NZD/USD', 'USD/CAD']
    },
    'INDICES': {
        'is_24_7': False,
        'trading_hours': {
            'start': '00:00',  # Almost 24/5
            'end': '23:00',
        },
        'markets': ['US Wall St 100', 'US SPX 500']
    },
    'COMMODITIES': {
        'is_24_7': False,
        'trading_hours': {
            'start': '01:00',
            'end': '23:00',
        },
        'markets': ['Gold']
    }
}

def is_market_open(symbol: str) -> bool:
    """Check if a market is open based on symbol and current time"""
    now = datetime.now(pytz.UTC)
    weekday = now.weekday()  # Monday is 0, Sunday is 6
    
    # Find market category for symbol
    market_category = None
    for category, info in MARKET_HOURS.items():
        if symbol in info['markets']:
            market_category = category
            break
            
    if not market_category:
        return False  # Unknown market
        
    market_info = MARKET_HOURS[market_category]
    
    # Crypto markets are always open
    if market_info['is_24_7']:
        return True
        
    # Other markets are closed on weekends
    if weekday >= 5:  # Saturday or Sunday
        return False
        
    # Check trading hours
    if 'trading_hours' in market_info:
        current_time = now.strftime('%H:%M')
        start_time = market_info['trading_hours']['start']
        end_time = market_info['trading_hours']['end']
        
        return start_time <= current_time <= end_time
        
    return False

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Bot Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { display: flex; flex-wrap: wrap; }
        .card { 
            border: 1px solid #ccc; 
            margin: 10px; 
            padding: 15px; 
            border-radius: 5px;
            width: 300px;
        }
        .signal-long { color: green; }
        .signal-short { color: red; }
        .signal-hold { color: gray; }
    </style>
    <script>
        function updateData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerHTML = '';
                    for (let symbol in data) {
                        let card = document.createElement('div');
                        card.className = 'card';
                        let signalClass = 'signal-' + data[symbol].signal.toLowerCase();
                        card.innerHTML = `
                            <h3>${symbol}</h3>
                            <p>Last Update: ${data[symbol].timestamp}</p>
                            <p>Market Regime: ${data[symbol].regime}</p>
                            <p>Regime Confidence: ${data[symbol].regime_confidence.toFixed(2)}</p>
                            <p>ML Direction: ${data[symbol].ml_direction || 'N/A'}</p>
                            <p>ML Confidence: ${data[symbol].ml_confidence ? data[symbol].ml_confidence.toFixed(2) : 'N/A'}</p>
                            <p>Expected Return: ${data[symbol].expected_return ? data[symbol].expected_return.toFixed(2) + '%' : 'N/A'}</p>
                            <p>Position Size: ${data[symbol].position_size.toFixed(2)}</p>
                            <p class="${signalClass}">Signal: ${data[symbol].signal}</p>
                            <p>Active Trade: ${data[symbol].active_trade}</p>
                            <p>Market Status: ${data[symbol].market_status}</p>
                        `;
                        document.getElementById('status').appendChild(card);
                    }
                });
        }
        
        setInterval(updateData, 5000);
        updateData();
    </script>
</head>
<body>
    <h1>Trading Bot Live Monitor</h1>
    <div id="status" class="container">
        Loading...
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def get_status():
    return jsonify(analysis_results)

def execute_trading_signal(symbol: str, signal: str, params: Dict) -> None:
    """Execute trading signals on Capital.com"""
    try:
        if signal in ["LONG", "SHORT"] and params:
            # Check if we already have a position
            if symbol in active_trades:
                logger.info(f"Already have position for {symbol}, skipping")
                return
                
            # Get current market data
            market_data = trader.get_market_data(symbol)
            if not market_data:
                logger.error(f"Could not get market data for {symbol}, skipping trade")
                return
                
            # Validate entry price is within acceptable range
            current_price = market_data['ask'] if signal == "LONG" else market_data['bid']
            price_diff = abs(current_price - params['entry_price']) / params['entry_price']
            if price_diff > 0.001:  # More than 0.1% price difference
                logger.warning(f"Price slippage too high for {symbol}, skipping trade")
                return
                
            # Calculate position size
            position_size = risk_manager.calculate_position_size(
                symbol=symbol,
                entry_price=current_price,
                stop_loss=params['stop_loss'],
                account_balance=100000.0,  # Update with actual balance
                historical_data=market_data[symbol]['1h']
            )
            
            # Validate position size
            if position_size < 0.01:
                logger.warning(f"Position size too small for {symbol}, skipping trade")
                return
                
            # Execute trade with current market price
            position_id = trader.execute_trade(
                symbol=symbol,
                direction=signal.lower(),  # Capital.com expects lowercase
                size=position_size,
                entry_price=current_price,
                stop_loss=params['stop_loss'],
                take_profit=params['take_profit']
            )
            
            if position_id:
                active_trades[symbol] = position_id
                logger.info(f"Successfully opened {signal} position for {symbol}")
            else:
                logger.error(f"Failed to open position for {symbol}")
                
    except Exception as e:
        logger.error(f"Error executing trading signal: {str(e)}")

def update_market_data():
    """Update market data and execute trades"""
    symbols = [
        'BTC/USD', 'ETH/USD', 'US Wall St 100', 'EUR/USD', 'GBP/USD', 'USD/JPY', 'Gold', 
        'US SPX 500', 'USD/CHF', 'AUD/USD', 'NZD/USD', 'USD/CAD', 'LTC/USD', 'XRP/USD'
    ]
    timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
    
    # Initialize Capital.com connection
    if not trader.initialize():
        logger.error("Failed to initialize Capital.com connection")
        return
        
    while True:
        try:
            for symbol in symbols:
                # Check if market is open
                market_open = is_market_open(symbol)
                
                if not market_open:
                    logger.info(f"Market closed for {symbol}")
                    if symbol in analysis_results:
                        analysis_results[symbol]['market_status'] = 'CLOSED'
                    continue
                    
                # Get real market data from Capital.com
                cap_data = trader.get_market_data(symbol)
                if not cap_data:
                    logger.warning(f"No market data available for {symbol}, skipping")
                    if symbol in analysis_results:
                        analysis_results[symbol]['market_status'] = 'NO_DATA'
                    continue
                    
                if symbol not in market_data:
                    market_data[symbol] = {}
                    
                # Update market data with real prices
                for timeframe in timeframes:
                    if timeframe not in market_data[symbol]:
                        # Initialize with historical data
                        periods = 1000
                        dates = pd.date_range(end=datetime.now(), periods=periods, freq=timeframe)
                        data = pd.DataFrame({
                            'open': np.random.normal(cap_data['bid'], cap_data['ask'] - cap_data['bid'], periods),
                            'high': np.random.normal(cap_data['high'], 0.001, periods),
                            'low': np.random.normal(cap_data['low'], 0.001, periods),
                            'close': np.random.normal(cap_data['bid'], cap_data['ask'] - cap_data['bid'], periods),
                            'volume': np.random.normal(1000, 100, periods)
                        }, index=dates)
                        market_data[symbol][timeframe] = data
                        
                    # Update latest data point
                    new_data = pd.DataFrame({
                        'open': [cap_data['bid']],
                        'high': [cap_data['high']],
                        'low': [cap_data['low']],
                        'close': [cap_data['ask']],
                        'volume': [1000]  # Example volume
                    }, index=[cap_data['timestamp']])
                    
                    market_data[symbol][timeframe] = pd.concat([
                        market_data[symbol][timeframe].iloc[1:],
                        new_data
                    ])
                    
                # Update engine's market data
                engine.update_market_data(symbol, market_data[symbol])
                
                # Analyze market conditions
                regime, confidence = regime_detector.detect_regime(symbol, market_data[symbol]['1h'])
                prediction = ml_predictor.predict(symbol, market_data[symbol]['1h'])
                signal, params = engine.analyze_market(symbol)
                
                # Execute trading signal if conditions are met
                if market_open:
                    execute_trading_signal(symbol, signal, params)
                
                # Update analysis results
                analysis_results[symbol] = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'market_status': 'OPEN',
                    'regime': regime.value if regime else 'unknown',
                    'regime_confidence': confidence if confidence else 0,
                    'ml_direction': prediction.direction if prediction else None,
                    'ml_confidence': prediction.confidence if prediction else None,
                    'expected_return': prediction.expected_return if prediction else None,
                    'position_size': risk_manager.calculate_position_size(
                        symbol=symbol,
                        entry_price=cap_data['ask'],
                        stop_loss=cap_data['low'],
                        account_balance=100000.0,
                        historical_data=market_data[symbol]['1h']
                    ),
                    'signal': signal,
                    'active_trade': symbol in active_trades
                }
                
            # Update positions
            trader.update_positions()
            
            # Check for closed positions
            for symbol, position_id in list(active_trades.items()):
                if position_id not in trader.positions:
                    logger.info(f"Position closed for {symbol}")
                    del active_trades[symbol]
                    
            time.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            logger.error(f"Error updating market data: {str(e)}")
            time.sleep(5)

def run_monitor():
    # Start market data update thread
    update_thread = threading.Thread(target=update_market_data)
    update_thread.daemon = True
    update_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run_monitor()
