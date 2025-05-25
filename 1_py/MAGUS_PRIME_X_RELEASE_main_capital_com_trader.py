import os
import logging
import requests
from typing import Dict, Optional
from datetime import datetime
import json
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class CapitalPosition:
    id: str
    symbol: str
    direction: str
    size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    unrealized_pnl: float
    timestamp: datetime

class CapitalComTrader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('CAPITAL_API_KEY')
        self.api_password = os.getenv('CAPITAL_API_PASSWORD')
        self.api_identifier = os.getenv('CAPITAL_API_IDENTIFIER')
        self.base_url = os.getenv('CAPITAL_API_URL', 'https://demo-api-capital.backend-capital.com/api/v1')
        self.session = None
        self.positions = {}
        self.security_token = None
        self.cst = None
        self.client_token = None
        
    def initialize(self) -> bool:
        """Initialize the API session"""
        try:
            # Create a new session
            self.session = requests.Session()
            
            # Set API key in headers
            self.session.headers.update({
                'X-CAP-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            })
            
            # Prepare session data
            session_data = {
                'identifier': self.api_identifier,
                'password': self.api_password,
                'encryptedPassword': False
            }
            
            # Initialize session
            response = self.session.post(
                f"{self.base_url}/session",
                json=session_data
            )
            
            if response.status_code == 200:
                # Store tokens
                self.security_token = response.headers.get('X-SECURITY-TOKEN')
                self.cst = response.headers.get('CST')
                self.client_token = response.headers.get('CLIENT-TOKEN')
                
                # Update session headers with tokens
                self.session.headers.update({
                    'X-SECURITY-TOKEN': self.security_token,
                    'CST': self.cst,
                    'CLIENT-TOKEN': self.client_token
                })
                
                self.logger.info("Successfully initialized Capital.com session")
                return True
            else:
                self.logger.error(f"Failed to initialize session: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing session: {str(e)}")
            return False
            
    def execute_trade(self, symbol: str, direction: str, size: float,
                     entry_price: float, stop_loss: float,
                     take_profit: float) -> Optional[str]:
        """Execute a trade on Capital.com"""
        try:
            if not self.session:
                if not self.initialize():
                    return None
                    
            # Get current market data to validate prices
            market_data = self.get_market_data(symbol)
            if not market_data:
                self.logger.error(f"Could not get market data for {symbol}")
                return None
                
            # Validate prices
            current_price = market_data['ask'] if direction == "long" else market_data['bid']
            price_diff = abs(current_price - entry_price) / entry_price
            if price_diff > 0.001:  # More than 0.1% price difference
                self.logger.error(f"Price slippage too high for {symbol}")
                return None
                
            # Prepare order data
            order_data = {
                'epic': symbol,
                'direction': direction.upper(),
                'size': str(size),
                'orderType': 'MARKET',
                'guaranteedStop': True,
                'stopLevel': str(stop_loss),
                'profitLevel': str(take_profit),
                'currencyCode': 'USD'  # Specify trading currency
            }
            
            # Place the order
            response = self.session.post(
                f"{self.base_url}/positions",
                json=order_data
            )
            
            if response.status_code == 200:
                position_data = response.json()
                position_id = position_data['dealReference']
                self.logger.info(f"Successfully opened position: {position_id}")
                
                # Store position details
                self.positions[position_id] = CapitalPosition(
                    id=position_id,
                    symbol=symbol,
                    direction=direction,
                    size=size,
                    entry_price=current_price,  # Use actual execution price
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    unrealized_pnl=0.0,
                    timestamp=datetime.now()
                )
                
                return position_id
            else:
                self.logger.error(f"Failed to open position: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
            return None
            
    def close_position(self, position_id: str) -> bool:
        """Close a position by its ID"""
        try:
            if not self.session:
                if not self.initialize():
                    return False
                    
            if position_id not in self.positions:
                self.logger.error(f"Position {position_id} not found")
                return False
                
            response = self.session.delete(
                f"{self.base_url}/positions/{position_id}"
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully closed position: {position_id}")
                del self.positions[position_id]
                return True
            else:
                self.logger.error(f"Failed to close position: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}")
            return False
            
    def update_positions(self) -> None:
        """Update the status of all open positions"""
        try:
            if not self.session:
                if not self.initialize():
                    return
                    
            response = self.session.get(f"{self.base_url}/positions")
            
            if response.status_code == 200:
                positions_data = response.json()
                
                # Update positions
                for pos in positions_data['positions']:
                    position_id = pos['dealId']
                    if position_id in self.positions:
                        self.positions[position_id].unrealized_pnl = float(pos['profit'])
                        
            else:
                self.logger.error(f"Failed to update positions: {response.text}")
                
        except Exception as e:
            self.logger.error(f"Error updating positions: {str(e)}")
            
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get real-time market data for a symbol"""
        try:
            if not self.session:
                if not self.initialize():
                    return None
                    
            # First get the epic (market pair) for the symbol
            search_response = self.session.get(
                f"{self.base_url}/markets",
                params={'searchTerm': symbol}
            )
            
            if search_response.status_code != 200:
                self.logger.error(f"Failed to search markets: {search_response.text}")
                return None
                
            markets = search_response.json().get('markets', [])
            if not markets:
                self.logger.error(f"No markets found for symbol: {symbol}")
                return None
                
            # Find the exact match for our symbol
            market = None
            for m in markets:
                if m.get('instrumentName') == symbol:
                    market = m
                    break
                    
            if not market:
                self.logger.error(f"Could not find exact market for symbol: {symbol}")
                return None
                
            # Get market data using the epic
            epic = market.get('epic')
            response = self.session.get(f"{self.base_url}/markets/{epic}")
            
            if response.status_code == 200:
                market_data = response.json()
                
                # Extract required fields
                snapshot = market_data.get('snapshot', {})
                if not snapshot:
                    self.logger.error(f"No snapshot data for {symbol}")
                    return None
                    
                return {
                    'bid': float(snapshot.get('bid', 0)),
                    'ask': float(snapshot.get('offer', 0)),
                    'high': float(snapshot.get('high', 0)),
                    'low': float(snapshot.get('low', 0)),
                    'timestamp': datetime.now()  # Use current time as snapshot time
                }
            else:
                self.logger.error(f"Failed to get market data: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting market data: {str(e)}")
            return None
