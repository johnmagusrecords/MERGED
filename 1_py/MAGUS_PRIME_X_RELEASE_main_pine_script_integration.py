import logging
import re
import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
import requests
from datetime import datetime, timedelta
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PineScriptIndicator:
    """
    Represents a Pine Script indicator with metadata and implementation
    """
    def __init__(self, name: str, description: str, script: str, 
                parameters: Dict[str, Any], implementation: Callable = None):
        self.name = name
        self.description = description
        self.script = script
        self.parameters = parameters
        self.implementation = implementation
        self.created_at = datetime.now()
        
    def to_dict(self) -> Dict:
        """Convert indicator to dictionary for storage"""
        return {
            "name": self.name,
            "description": self.description,
            "script": self.script,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'PineScriptIndicator':
        """Create indicator from dictionary"""
        indicator = cls(
            name=data.get("name", "Unknown"),
            description=data.get("description", ""),
            script=data.get("script", ""),
            parameters=data.get("parameters", {})
        )
        
        if "created_at" in data:
            try:
                indicator.created_at = datetime.fromisoformat(data["created_at"])
            except:
                pass
                
        return indicator

class PineScriptIntegration:
    """
    Pine Script Integration for the trading bot.
    Allows importing, parsing, and using indicators from TradingView Pine Script.
    """
    
    def __init__(self, indicators_path: str = "pine_indicators"):
        self.logger = logging.getLogger(__name__)
        self.indicators_path = indicators_path
        self.indicators: Dict[str, PineScriptIndicator] = {}
        
        # Create indicators directory if it doesn't exist
        os.makedirs(self.indicators_path, exist_ok=True)
        
        # Load existing indicators
        self.load_indicators()
        
        # Map of built-in implementations
        self.implementations = {
            "RSI": self._implement_rsi,
            "MACD": self._implement_macd,
            "Bollinger Bands": self._implement_bollinger_bands,
            "Supertrend": self._implement_supertrend,
            "Ichimoku Cloud": self._implement_ichimoku,
            "ATR": self._implement_atr,
            "Fibonacci Retracement": self._implement_fibonacci
        }
        
    def load_indicators(self) -> None:
        """Load all saved indicators from the indicators directory"""
        try:
            indicator_files = [f for f in os.listdir(self.indicators_path) 
                              if f.endswith('.json')]
            
            for file_name in indicator_files:
                file_path = os.path.join(self.indicators_path, file_name)
                try:
                    with open(file_path, 'r') as f:
                        indicator_data = json.load(f)
                        indicator = PineScriptIndicator.from_dict(indicator_data)
                        
                        # Try to assign implementation
                        name = indicator.name.strip()
                        for impl_name, impl_func in self.implementations.items():
                            if impl_name.lower() in name.lower():
                                indicator.implementation = impl_func
                                break
                        
                        self.indicators[indicator.name] = indicator
                        self.logger.info(f"Loaded indicator: {indicator.name}")
                except Exception as e:
                    self.logger.error(f"Error loading indicator {file_name}: {str(e)}")
                    
            self.logger.info(f"Loaded {len(self.indicators)} Pine Script indicators")
        except Exception as e:
            self.logger.error(f"Error loading indicators: {str(e)}")
            
    def save_indicator(self, indicator: PineScriptIndicator) -> bool:
        """Save indicator to JSON file"""
        try:
            # Create safe filename from indicator name
            safe_name = re.sub(r'[^\w]', '_', indicator.name).lower()
            file_path = os.path.join(self.indicators_path, f"{safe_name}.json")
            
            with open(file_path, 'w') as f:
                json.dump(indicator.to_dict(), f, indent=2)
                
            self.logger.info(f"Saved indicator: {indicator.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving indicator {indicator.name}: {str(e)}")
            return False
            
    def add_indicator(self, name: str, description: str, script: str, 
                     parameters: Dict[str, Any] = None) -> PineScriptIndicator:
        """Add a new indicator and save it"""
        if parameters is None:
            parameters = {}
            
        # Extract parameters from Pine Script if not provided
        if not parameters:
            parameters = self._extract_parameters_from_script(script)
            
        # Create new indicator
        indicator = PineScriptIndicator(name, description, script, parameters)
        
        # Try to assign implementation
        for impl_name, impl_func in self.implementations.items():
            if impl_name.lower() in name.lower():
                indicator.implementation = impl_func
                break
                
        # Save to storage
        self.indicators[name] = indicator
        self.save_indicator(indicator)
        
        return indicator
        
    def parse_pine_script(self, script: str) -> Dict:
        """Parse Pine Script to extract metadata and logic"""
        try:
            # Extract indicator name (usually in comment at top)
            name_match = re.search(r'\/\/\s*(.+?)(?:\n|$)', script)
            name = name_match.group(1).strip() if name_match else "Unnamed Indicator"
            
            # Extract description
            desc_match = re.search(r'\/\/\s*@description\s+(.+?)(?:\n|$)', script)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Extract parameters
            parameters = self._extract_parameters_from_script(script)
            
            return {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        except Exception as e:
            self.logger.error(f"Error parsing Pine Script: {str(e)}")
            return {
                "name": "Error parsing script",
                "description": str(e),
                "parameters": {}
            }
            
    def _extract_parameters_from_script(self, script: str) -> Dict[str, Any]:
        """Extract input parameters from Pine Script"""
        parameters = {}
        
        # Find all input declarations
        input_pattern = r'input\s*(?:\.\w+)?\s*\(([^)]+)\)\s*(?:=>)?\s*(\w+)'
        input_matches = re.finditer(input_pattern, script)
        
        for match in input_matches:
            # Parse input arguments
            args_str = match.group(1)
            var_name = match.group(2)
            
            # Parse arguments from string
            args = {}
            
            # Handle string arguments (those with quotes)
            string_pattern = r'(?:title|defval|options)\s*=\s*["\']([^"\']+)["\']'
            string_matches = re.finditer(string_pattern, args_str)
            for string_match in string_matches:
                key = string_match.group(0).split('=')[0].strip()
                value = string_match.group(1)
                args[key] = value
                
            # Handle numeric arguments
            numeric_pattern = r'(?:defval|minval|maxval|step)\s*=\s*([0-9.]+)'
            numeric_matches = re.finditer(numeric_pattern, args_str)
            for numeric_match in numeric_matches:
                key = numeric_match.group(0).split('=')[0].strip()
                value = float(numeric_match.group(1))
                args[key] = value
                
            # Get default value and type
            default_value = args.get('defval', 0)
            
            # Store parameter info
            parameters[var_name] = {
                'title': args.get('title', var_name),
                'default': default_value,
                'type': type(default_value).__name__,
                'options': args.get('options', None),
                'min': args.get('minval', None),
                'max': args.get('maxval', None),
                'step': args.get('step', None)
            }
            
        return parameters
        
    def apply_indicator(self, indicator_name: str, data: pd.DataFrame,
                       parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Apply a Pine Script indicator to market data
        
        Args:
            indicator_name: Name of the indicator to apply
            data: OHLCV DataFrame
            parameters: Optional custom parameters (uses defaults if not provided)
            
        Returns:
            DataFrame with indicator columns added
        """
        if indicator_name not in self.indicators:
            self.logger.error(f"Indicator not found: {indicator_name}")
            return data
            
        indicator = self.indicators[indicator_name]
        
        # Merge provided parameters with defaults
        merged_params = {}
        if indicator.parameters:
            for param_name, param_info in indicator.parameters.items():
                merged_params[param_name] = param_info.get('default')
                
        if parameters:
            merged_params.update(parameters)
            
        # If we have implementation, use it
        if indicator.implementation:
            try:
                result = indicator.implementation(data, merged_params)
                
                # Check if we need to merge result with original data
                if isinstance(result, pd.DataFrame):
                    # If result has same index as data, assume it contains all original data plus indicators
                    if result.index.equals(data.index) and len(result.columns) >= len(data.columns):
                        return result
                    
                    # Otherwise, we need to merge with original data
                    result_df = data.copy()
                    
                    # Add new columns from result
                    for col in result.columns:
                        if col not in result_df.columns:
                            result_df[col] = result[col]
                            
                    return result_df
                else:
                    # Result is a series or similar, add as new column
                    result_df = data.copy()
                    result_df[indicator_name] = result
                    return result_df
            except Exception as e:
                self.logger.error(f"Error applying indicator {indicator_name}: {str(e)}")
                return data
        else:
            self.logger.warning(f"No implementation available for indicator: {indicator_name}")
            return data
            
    def get_indicator_names(self) -> List[str]:
        """Get list of available indicator names"""
        return list(self.indicators.keys())
        
    def get_indicator_info(self, indicator_name: str) -> Dict:
        """Get information about a specific indicator"""
        if indicator_name not in self.indicators:
            return {"error": f"Indicator not found: {indicator_name}"}
            
        indicator = self.indicators[indicator_name]
        return {
            "name": indicator.name,
            "description": indicator.description,
            "parameters": indicator.parameters,
            "has_implementation": indicator.implementation is not None,
            "created_at": indicator.created_at.isoformat()
        }
        
    def delete_indicator(self, indicator_name: str) -> bool:
        """Delete an indicator"""
        if indicator_name not in self.indicators:
            return False
            
        # Remove from memory
        indicator = self.indicators.pop(indicator_name)
        
        # Delete file
        try:
            safe_name = re.sub(r'[^\w]', '_', indicator_name).lower()
            file_path = os.path.join(self.indicators_path, f"{safe_name}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Deleted indicator file: {file_path}")
                
            return True
        except Exception as e:
            self.logger.error(f"Error deleting indicator {indicator_name}: {str(e)}")
            self.indicators[indicator_name] = indicator  # Restore in memory
            return False
            
    # Implementation of common indicators
    def _implement_rsi(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Implement RSI indicator"""
        import talib
        
        period = int(params.get('length', 14))
        price_col = params.get('source', 'close')
        
        result = data.copy()
        result['RSI'] = talib.RSI(data[price_col].values, timeperiod=period)
        
        # Add additional RSI signals
        result['RSI_Overbought'] = result['RSI'] > 70
        result['RSI_Oversold'] = result['RSI'] < 30
        
        return result
        
    def _implement_macd(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Implement MACD indicator"""
        import talib
        
        fast_period = int(params.get('fastLength', 12))
        slow_period = int(params.get('slowLength', 26))
        signal_period = int(params.get('signalLength', 9))
        price_col = params.get('source', 'close')
        
        result = data.copy()
        macd, signal, hist = talib.MACD(
            data[price_col].values,
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period
        )
        
        result['MACD'] = macd
        result['MACD_Signal'] = signal
        result['MACD_Histogram'] = hist
        
        # Add MACD cross signals
        result['MACD_Bull_Cross'] = (macd > signal) & (macd.shift(1) <= signal.shift(1))
        result['MACD_Bear_Cross'] = (macd < signal) & (macd.shift(1) >= signal.shift(1))
        
        return result
        
    def _implement_bollinger_bands(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Implement Bollinger Bands indicator"""
        import talib
        
        period = int(params.get('length', 20))
        std_dev = float(params.get('mult', 2.0))
        price_col = params.get('source', 'close')
        
        result = data.copy()
        upper, middle, lower = talib.BBANDS(
            data[price_col].values,
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev
        )
        
        result['BB_Upper'] = upper
        result['BB_Middle'] = middle
        result['BB_Lower'] = lower
        
        # Calculate bandwidth and %B
        result['BB_Width'] = (upper - lower) / middle
        result['BB_Percent_B'] = (data[price_col] - lower) / (upper - lower)
        
        # Add signals
        result['BB_Upper_Touch'] = data[price_col] >= upper
        result['BB_Lower_Touch'] = data[price_col] <= lower
        
        return result
        
    def _implement_supertrend(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Implement Supertrend indicator"""
        import talib
        
        period = int(params.get('period', 10))
        multiplier = float(params.get('factor', 3.0))
        
        result = data.copy()
        
        # Calculate ATR
        atr = talib.ATR(data['high'].values, data['low'].values, data['close'].values, timeperiod=period)
        
        # Calculate basic upper and lower bands
        hl2 = (data['high'] + data['low']) / 2
        
        # Initialize Supertrend columns
        result['ST_UpperBand'] = hl2 + (multiplier * atr)
        result['ST_LowerBand'] = hl2 - (multiplier * atr)
        result['ST_Direction'] = 0
        result['Supertrend'] = 0
        
        # Calculate Supertrend
        for i in range(1, len(data)):
            if data['close'].iloc[i-1] <= result['ST_UpperBand'].iloc[i-1]:
                result.at[result.index[i], 'ST_UpperBand'] = min(
                    result['ST_UpperBand'].iloc[i],
                    result['ST_UpperBand'].iloc[i-1]
                )
            else:
                result.at[result.index[i], 'ST_UpperBand'] = result['ST_UpperBand'].iloc[i]
                
            if data['close'].iloc[i-1] >= result['ST_LowerBand'].iloc[i-1]:
                result.at[result.index[i], 'ST_LowerBand'] = max(
                    result['ST_LowerBand'].iloc[i],
                    result['ST_LowerBand'].iloc[i-1]
                )
            else:
                result.at[result.index[i], 'ST_LowerBand'] = result['ST_LowerBand'].iloc[i]
                
            # Determine trend direction
            if (data['close'].iloc[i] > result['ST_UpperBand'].iloc[i-1]):
                result.at[result.index[i], 'ST_Direction'] = 1
            elif (data['close'].iloc[i] < result['ST_LowerBand'].iloc[i-1]):
                result.at[result.index[i], 'ST_Direction'] = -1
            else:
                result.at[result.index[i], 'ST_Direction'] = result['ST_Direction'].iloc[i-1]
                
            # Set Supertrend value
            if result['ST_Direction'].iloc[i] == 1:
                result.at[result.index[i], 'Supertrend'] = result['ST_LowerBand'].iloc[i]
            else:
                result.at[result.index[i], 'Supertrend'] = result['ST_UpperBand'].iloc[i]
                
        # Add signals
        result['ST_UpTrend'] = result['ST_Direction'] == 1
        result['ST_DownTrend'] = result['ST_Direction'] == -1
        result['ST_UpTrend_Changed'] = (result['ST_Direction'] == 1) & (result['ST_Direction'].shift(1) == -1)
        result['ST_DownTrend_Changed'] = (result['ST_Direction'] == -1) & (result['ST_Direction'].shift(1) == 1)
        
        return result
        
    def _implement_ichimoku(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Implement Ichimoku Cloud indicator"""
        tenkan_period = int(params.get('tenkan', 9))
        kijun_period = int(params.get('kijun', 26))
        senkou_span_b_period = int(params.get('senkou', 52))
        displacement = int(params.get('displacement', 26))
        
        result = data.copy()
        
        # Tenkan-sen (Conversion Line)
        tenkan_sen_high = data['high'].rolling(window=tenkan_period).max()
        tenkan_sen_low = data['low'].rolling(window=tenkan_period).min()
        result['Ichimoku_Tenkan'] = (tenkan_sen_high + tenkan_sen_low) / 2
        
        # Kijun-sen (Base Line)
        kijun_sen_high = data['high'].rolling(window=kijun_period).max()
        kijun_sen_low = data['low'].rolling(window=kijun_period).min()
        result['Ichimoku_Kijun'] = (kijun_sen_high + kijun_sen_low) / 2
        
        # Senkou Span A (Leading Span A)
        result['Ichimoku_SpanA'] = ((result['Ichimoku_Tenkan'] + result['Ichimoku_Kijun']) / 2).shift(displacement)
        
        # Senkou Span B (Leading Span B)
        senkou_span_b_high = data['high'].rolling(window=senkou_span_b_period).max()
        senkou_span_b_low = data['low'].rolling(window=senkou_span_b_period).min()
        result['Ichimoku_SpanB'] = ((senkou_span_b_high + senkou_span_b_low) / 2).shift(displacement)
        
        # Chikou Span (Lagging Span)
        result['Ichimoku_Chikou'] = data['close'].shift(-displacement)
        
        # Add signals
        result['Ichimoku_TK_Cross_Bull'] = (result['Ichimoku_Tenkan'] > result['Ichimoku_Kijun']) & (result['Ichimoku_Tenkan'].shift(1) <= result['Ichimoku_Kijun'].shift(1))
        result['Ichimoku_TK_Cross_Bear'] = (result['Ichimoku_Tenkan'] < result['Ichimoku_Kijun']) & (result['Ichimoku_Tenkan'].shift(1) >= result['Ichimoku_Kijun'].shift(1))
        result['Ichimoku_Price_Above_Cloud'] = (data['close'] > result['Ichimoku_SpanA']) & (data['close'] > result['Ichimoku_SpanB'])
        result['Ichimoku_Price_Below_Cloud'] = (data['close'] < result['Ichimoku_SpanA']) & (data['close'] < result['Ichimoku_SpanB'])
        result['Ichimoku_Cloud_Green'] = result['Ichimoku_SpanA'] > result['Ichimoku_SpanB']
        result['Ichimoku_Cloud_Red'] = result['Ichimoku_SpanA'] < result['Ichimoku_SpanB']
        
        return result
        
    def _implement_atr(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Implement Average True Range (ATR) indicator"""
        import talib
        
        period = int(params.get('length', 14))
        
        result = data.copy()
        result['ATR'] = talib.ATR(data['high'].values, data['low'].values, data['close'].values, timeperiod=period)
        
        # Normalizing ATR as percentage of price
        result['ATR_Percent'] = (result['ATR'] / data['close']) * 100
        
        # Add volatility indicator based on ATR percentile rank
        lookback = min(100, len(data))
        result['ATR_Percentile'] = result['ATR'].rolling(lookback).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], 
            raw=False
        )
        
        # Volatility regime
        result['High_Volatility'] = result['ATR_Percentile'] > 0.8
        result['Low_Volatility'] = result['ATR_Percentile'] < 0.2
        
        return result
        
    def _implement_fibonacci(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Implement Fibonacci Retracement levels"""
        lookback = int(params.get('lookback', 50))
        levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        
        result = data.copy()
        
        # Get max and min in lookback period
        max_price = data['high'].rolling(lookback).max()
        min_price = data['low'].rolling(lookback).min()
        
        # Calculate Fibonacci levels (assuming downtrend)
        for level in levels:
            col_name = f'Fib_{level}'.replace('.', '_')
            result[col_name] = max_price - ((max_price - min_price) * level)
            
        # Add columns for price relation to fib levels
        current_price = data['close']
        for level in levels:
            if level == 1.0:
                continue
                
            next_level = next((l for l in levels if l > level), 1.0)
            col_between = f'Price_Between_Fib_{level}_{next_level}'.replace('.', '_')
            level_price = result[f'Fib_{level}'.replace('.', '_')]
            next_level_price = result[f'Fib_{next_level}'.replace('.', '_')]
            
            result[col_between] = (current_price >= level_price) & (current_price <= next_level_price)
            
        return result
