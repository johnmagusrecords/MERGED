"""
Signal Processor for Trading Bot
"""
import re
from typing import Dict, Optional
from config import Config

class SignalProcessor:
    def __init__(self, config: Config):
        self.config = config
        
    def parse_message(self, message: str) -> Optional[Dict]:
        """Parse trading signal from Telegram message"""
        try:
            # Regular expression patterns for different message formats
            patterns = {
                'standard': r'#(\w+)\s+(BUY|SELL)\nEntry:\s*([\d.]+)\nSL:\s*([\d.]+)\nTP1:\s*([\d.]+)\nTP2:\s*([\d.]+)\nTP3:\s*([\d.]+)',
                'short': r'#(\w+)\s+(BUY|SELL)\s+@\s*([\d.]+)\s+SL\s*([\d.]+)\s+TP\s*([\d.]+)',
            }
            
            # Try each pattern
            for pattern_name, pattern in patterns.items():
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    if pattern_name == 'standard':
                        return {
                            'symbol': match.group(1),
                            'type': match.group(2),
                            'entry': float(match.group(3)),
                            'stop_loss': float(match.group(4)),
                            'tp1': float(match.group(5)),
                            'tp2': float(match.group(6)),
                            'tp3': float(match.group(7)),
                            'pattern': pattern_name
                        }
                    elif pattern_name == 'short':
                        return {
                            'symbol': match.group(1),
                            'type': match.group(2),
                            'entry': float(match.group(3)),
                            'stop_loss': float(match.group(4)),
                            'tp1': float(match.group(5)),
                            'pattern': pattern_name
                        }
            
            return None
            
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None
            
    def validate_signal(self, signal: Dict) -> bool:
        """Validate trading signal"""
        try:
            # Check required fields
            required_fields = ['symbol', 'type', 'entry', 'stop_loss']
            if not all(field in signal for field in required_fields):
                return False
                
            # Validate symbol
            if not self._is_valid_symbol(signal['symbol']):
                return False
                
            # Validate trade type
            if signal['type'] not in ['BUY', 'SELL']:
                return False
                
            # Validate prices
            if not self._are_valid_prices(signal):
                return False
                
            return True
            
        except Exception as e:
            print(f"Error validating signal: {e}")
            return False
            
    def _is_valid_symbol(self, symbol: str) -> bool:
        """Check if symbol is supported"""
        valid_symbols = (
            self.config.SYMBOLS +
            self.config.COMMODITIES +
            self.config.INDICES
        )
        return symbol in valid_symbols
        
    def _are_valid_prices(self, signal: Dict) -> bool:
        """Validate price levels"""
        entry = signal['entry']
        sl = signal['stop_loss']
        
        # Basic price validation
        if entry <= 0 or sl <= 0:
            return False
            
        # Validate stop loss
        if signal['type'] == 'BUY':
            if sl >= entry:
                return False
        else:  # SELL
            if sl <= entry:
                return False
                
        # Validate take profit levels if present
        for tp in ['tp1', 'tp2', 'tp3']:
            if tp in signal:
                tp_price = signal[tp]
                if tp_price <= 0:
                    return False
                if signal['type'] == 'BUY':
                    if tp_price <= entry:
                        return False
                else:  # SELL
                    if tp_price >= entry:
                        return False
                        
        return True