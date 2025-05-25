import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import talib
import logging

class TradingStrategy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators for strategy decision making."""
        try:
            # Convert price data to numpy arrays
            close = data['close'].values
            high = data['high'].values
            low = data['low'].values
            volume = data['volume'].values
            
            indicators = {}
            
            # Moving Averages
            indicators['sma_20'] = talib.SMA(close, timeperiod=20)
            indicators['sma_50'] = talib.SMA(close, timeperiod=50)
            indicators['ema_12'] = talib.EMA(close, timeperiod=12)
            indicators['ema_26'] = talib.EMA(close, timeperiod=26)
            
            # MACD
            macd, macd_signal, macd_hist = talib.MACD(close)
            indicators['macd'] = macd
            indicators['macd_signal'] = macd_signal
            indicators['macd_hist'] = macd_hist
            
            # RSI
            indicators['rsi'] = talib.RSI(close, timeperiod=14)
            
            # Bollinger Bands
            upper, middle, lower = talib.BBANDS(close, timeperiod=20)
            indicators['bb_upper'] = upper
            indicators['bb_middle'] = middle
            indicators['bb_lower'] = lower
            
            # Stochastic
            slowk, slowd = talib.STOCH(high, low, close)
            indicators['stoch_k'] = slowk
            indicators['stoch_d'] = slowd
            
            # Volume indicators
            indicators['obv'] = talib.OBV(close, volume)
            indicators['adx'] = talib.ADX(high, low, close, timeperiod=14)
            
            # Ichimoku Cloud
            conv_line = (talib.MAX(high, 9) + talib.MIN(low, 9)) / 2
            base_line = (talib.MAX(high, 26) + talib.MIN(low, 26)) / 2
            lead_span_a = (conv_line + base_line) / 2
            lead_span_b = (talib.MAX(high, 52) + talib.MIN(low, 52)) / 2
            
            indicators['ichimoku_conv'] = conv_line
            indicators['ichimoku_base'] = base_line
            indicators['ichimoku_span_a'] = lead_span_a
            indicators['ichimoku_span_b'] = lead_span_b
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}")
            return {}

    def analyze_market_structure(self, data: pd.DataFrame) -> Dict:
        """Analyze market structure and identify key levels."""
        try:
            high = data['high'].values
            low = data['low'].values
            close = data['close'].values
            
            # Find swing highs and lows
            swing_high = talib.MAX(high, timeperiod=20)
            swing_low = talib.MIN(low, timeperiod=20)
            
            # Calculate volatility
            atr = talib.ATR(high, low, close, timeperiod=14)
            
            # Identify trend strength
            adx = talib.ADX(high, low, close, timeperiod=14)
            
            return {
                'swing_high': swing_high[-1],
                'swing_low': swing_low[-1],
                'atr': atr[-1],
                'adx': adx[-1]
            }
        except Exception as e:
            self.logger.error(f"Error analyzing market structure: {str(e)}")
            return {}

    def generate_signals(self, data: pd.DataFrame) -> Dict:
        """Generate trading signals based on multiple indicators."""
        try:
            indicators = self.calculate_indicators(data)
            market_structure = self.analyze_market_structure(data)
            
            signals = {
                'entry_long': False,
                'entry_short': False,
                'exit_long': False,
                'exit_short': False,
                'strength': 0,  # Signal strength from 0 to 100
                'risk_level': 0  # Risk level from 0 to 100
            }
            
            # Check for entry conditions
            if len(data) < 50:
                return signals
                
            current_close = data['close'].iloc[-1]
            
            # Trend Analysis
            trend_up = (indicators['sma_20'][-1] > indicators['sma_50'][-1] and 
                       current_close > indicators['sma_20'][-1])
            trend_down = (indicators['sma_20'][-1] < indicators['sma_50'][-1] and 
                        current_close < indicators['sma_20'][-1])
            
            # MACD Analysis
            macd_bullish = (indicators['macd_hist'][-1] > 0 and 
                          indicators['macd_hist'][-2] <= 0)
            macd_bearish = (indicators['macd_hist'][-1] < 0 and 
                          indicators['macd_hist'][-2] >= 0)
            
            # RSI Analysis
            rsi = indicators['rsi'][-1]
            rsi_oversold = rsi < 30
            rsi_overbought = rsi > 70
            
            # Volume Confirmation
            volume_increasing = data['volume'].iloc[-1] > data['volume'].iloc[-2]
            
            # Calculate signal strength
            strength_factors = []
            
            if trend_up:
                strength_factors.append(20)
            if macd_bullish:
                strength_factors.append(15)
            if rsi_oversold:
                strength_factors.append(15)
            if volume_increasing:
                strength_factors.append(10)
            if market_structure['adx'] > 25:
                strength_factors.append(20)
                
            signals['strength'] = min(sum(strength_factors), 100)
            
            # Generate entry signals
            signals['entry_long'] = (
                trend_up and 
                macd_bullish and 
                rsi_oversold and 
                volume_increasing and 
                market_structure['adx'] > 25
            )
            
            signals['entry_short'] = (
                trend_down and 
                macd_bearish and 
                rsi_overbought and 
                volume_increasing and 
                market_structure['adx'] > 25
            )
            
            # Calculate risk level
            risk_factors = []
            
            # Volatility risk
            atr_risk = min((market_structure['atr'] / current_close) * 100, 40)
            risk_factors.append(atr_risk)
            
            # Trend strength risk (inverse of ADX)
            trend_risk = max(40 - market_structure['adx'], 0)
            risk_factors.append(trend_risk)
            
            # RSI extreme risk
            rsi_risk = 0
            if rsi < 20 or rsi > 80:
                rsi_risk = 20
            risk_factors.append(rsi_risk)
            
            signals['risk_level'] = min(sum(risk_factors), 100)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating signals: {str(e)}")
            return {
                'entry_long': False,
                'entry_short': False,
                'exit_long': False,
                'exit_short': False,
                'strength': 0,
                'risk_level': 100  # Maximum risk on error
            }

    def calculate_position_size(self, 
                              account_balance: float,
                              risk_percentage: float,
                              entry_price: float,
                              stop_loss: float) -> Tuple[float, Dict]:
        """Calculate optimal position size based on risk management rules."""
        try:
            # Validate inputs
            if not all([account_balance, risk_percentage, entry_price, stop_loss]):
                return 0, {'error': 'Invalid inputs'}
            
            if risk_percentage <= 0 or risk_percentage > 2:  # Max 2% risk per trade
                return 0, {'error': 'Risk percentage must be between 0 and 2%'}
            
            # Calculate risk amount
            risk_amount = account_balance * (risk_percentage / 100)
            
            # Calculate stop loss distance
            if entry_price > stop_loss:  # Long position
                stop_distance = entry_price - stop_loss
            else:  # Short position
                stop_distance = stop_loss - entry_price
            
            if stop_distance <= 0:
                return 0, {'error': 'Invalid stop loss'}
            
            # Calculate position size
            position_size = risk_amount / stop_distance
            
            # Round position size to appropriate precision
            position_size = round(position_size, 8)
            
            return position_size, {
                'risk_amount': risk_amount,
                'stop_distance': stop_distance,
                'position_value': position_size * entry_price
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0, {'error': str(e)}

    def get_trade_recommendation(self, 
                               data: pd.DataFrame,
                               account_balance: float,
                               max_risk_percentage: float = 1.0) -> Dict:
        """Get complete trade recommendation including entry, stop loss, and position size."""
        try:
            signals = self.generate_signals(data)
            current_price = data['close'].iloc[-1]
            
            if not (signals['entry_long'] or signals['entry_short']):
                return {
                    'recommendation': 'NO_TRADE',
                    'reason': 'No valid setup found'
                }
            
            # Calculate ATR for stop loss
            high = data['high'].values
            low = data['low'].values
            close = data['close'].values
            atr = talib.ATR(high, low, close, timeperiod=14)[-1]
            
            trade_type = 'LONG' if signals['entry_long'] else 'SHORT'
            
            # Calculate stop loss (2 * ATR for now, can be adjusted)
            stop_loss = (current_price - (2 * atr)) if trade_type == 'LONG' else (current_price + (2 * atr))
            
            # Calculate position size
            position_size, position_info = self.calculate_position_size(
                account_balance=account_balance,
                risk_percentage=max_risk_percentage,
                entry_price=current_price,
                stop_loss=stop_loss
            )
            
            if 'error' in position_info:
                return {
                    'recommendation': 'NO_TRADE',
                    'reason': f"Position size calculation error: {position_info['error']}"
                }
            
            # Calculate take profit (risk:reward 1:2)
            take_profit = (current_price + (4 * atr)) if trade_type == 'LONG' else (current_price - (4 * atr))
            
            return {
                'recommendation': 'ENTER_' + trade_type,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size,
                'signal_strength': signals['strength'],
                'risk_level': signals['risk_level'],
                'risk_amount': position_info['risk_amount'],
                'potential_profit': abs(take_profit - current_price) * position_size,
                'risk_reward_ratio': 2.0,  # Based on our 1:2 setup
                'position_value': position_info['position_value']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting trade recommendation: {str(e)}")
            return {
                'recommendation': 'ERROR',
                'reason': str(e)
            }

from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class EntrySetup:
    name: str
    timeframe: str
    confidence: float
    signal_type: str  # 'reversal', 'breakout', 'trend', 'pattern'
    indicators: Dict

class AdvancedStrategies:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.min_setup_confidence = 0.7
        self.required_confirmations = 2
        
    def identify_entry_setups(self, data: Dict[str, pd.DataFrame], 
                            indicators: Dict) -> List[EntrySetup]:
        """Identify potential entry setups across multiple timeframes"""
        setups = []
        try:
            for timeframe, df in data.items():
                # 1. Reversal Setups
                reversal = self._check_reversal_setup(df, indicators[timeframe])
                if reversal[0]:
                    setups.append(EntrySetup(
                        name="Reversal",
                        timeframe=timeframe,
                        confidence=reversal[1],
                        signal_type="reversal",
                        indicators=reversal[2]
                    ))
                
                # 2. Breakout Setups
                breakout = self._check_breakout_setup(df, indicators[timeframe])
                if breakout[0]:
                    setups.append(EntrySetup(
                        name="Breakout",
                        timeframe=timeframe,
                        confidence=breakout[1],
                        signal_type="breakout",
                        indicators=breakout[2]
                    ))
                
                # 3. Trend Continuation
                trend = self._check_trend_setup(df, indicators[timeframe])
                if trend[0]:
                    setups.append(EntrySetup(
                        name="Trend",
                        timeframe=timeframe,
                        confidence=trend[1],
                        signal_type="trend",
                        indicators=trend[2]
                    ))
                
                # 4. Pattern Recognition
                pattern = self._check_pattern_setup(df, indicators[timeframe])
                if pattern[0]:
                    setups.append(EntrySetup(
                        name="Pattern",
                        timeframe=timeframe,
                        confidence=pattern[1],
                        signal_type="pattern",
                        indicators=pattern[2]
                    ))
                    
            return [s for s in setups if s.confidence >= self.min_setup_confidence]
            
        except Exception as e:
            self.logger.error(f"Error identifying entry setups: {str(e)}")
            return []
            
    def calculate_exit_points(self, entry_price: float, direction: str,
                            atr: float, setup: EntrySetup) -> Tuple[float, List[float]]:
        """Calculate optimal exit points based on setup type"""
        try:
            # Base ATR multipliers
            sl_mult = 2.0
            tp_mult = [3.0, 5.0]  # Multiple take profit levels
            
            # Adjust multipliers based on setup type
            if setup.signal_type == "breakout":
                sl_mult = 1.5  # Tighter stop for breakouts
                tp_mult = [4.0, 6.0]  # Higher targets for breakouts
            elif setup.signal_type == "reversal":
                sl_mult = 2.5  # Wider stop for reversals
                tp_mult = [2.5, 4.0]  # Conservative targets
            elif setup.signal_type == "trend":
                sl_mult = 2.0
                tp_mult = [3.5, 7.0]  # Higher targets for trends
                
            # Calculate stops and targets
            if direction == "long":
                stop_loss = entry_price - (atr * sl_mult)
                take_profits = [
                    entry_price + (atr * tp_mult[0]),
                    entry_price + (atr * tp_mult[1])
                ]
            else:
                stop_loss = entry_price + (atr * sl_mult)
                take_profits = [
                    entry_price - (atr * tp_mult[0]),
                    entry_price - (atr * tp_mult[1])
                ]
                
            return stop_loss, take_profits
            
        except Exception as e:
            self.logger.error(f"Error calculating exit points: {str(e)}")
            return entry_price * 0.99, [entry_price * 1.02, entry_price * 1.05]
            
    def _check_reversal_setup(self, data: pd.DataFrame, 
                             indicators: Dict) -> Tuple[bool, float, Dict]:
        """Check for reversal setups"""
        try:
            # Get latest values
            rsi = indicators['rsi'][-1]
            stoch_k = indicators['stoch_k'][-1]
            stoch_d = indicators['stoch_d'][-1]
            macd = indicators['macd'][-1]
            macd_signal = indicators['macd_signal'][-1]
            
            # Check oversold conditions
            oversold = (
                rsi < 30 and
                stoch_k < 20 and
                stoch_d < 20 and
                macd < macd_signal and
                macd < 0
            )
            
            # Check overbought conditions
            overbought = (
                rsi > 70 and
                stoch_k > 80 and
                stoch_d > 80 and
                macd > macd_signal and
                macd > 0
            )
            
            # Calculate confidence
            if oversold or overbought:
                confidence = min(
                    abs(50 - rsi) / 50,  # RSI divergence from midpoint
                    abs(50 - stoch_k) / 50,  # Stochastic divergence
                    abs(macd - macd_signal) / abs(macd) if macd != 0 else 0  # MACD divergence
                )
                
                return True, confidence, {
                    'type': 'oversold' if oversold else 'overbought',
                    'rsi': rsi,
                    'stoch_k': stoch_k,
                    'stoch_d': stoch_d,
                    'macd': macd,
                    'macd_signal': macd_signal
                }
                
            return False, 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Error checking reversal setup: {str(e)}")
            return False, 0.0, {}
            
    def _check_breakout_setup(self, data: pd.DataFrame, 
                             indicators: Dict) -> Tuple[bool, float, Dict]:
        """Check for breakout setups"""
        try:
            # Get latest values
            close = data['close'].iloc[-1]
            bb_upper = indicators['bb_upper'][-1]
            bb_lower = indicators['bb_lower'][-1]
            volume = data['volume'].iloc[-1]
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            
            # Check for price breakouts
            breakout_up = close > bb_upper and volume > avg_volume * 1.5
            breakout_down = close < bb_lower and volume > avg_volume * 1.5
            
            if breakout_up or breakout_down:
                # Calculate confidence based on volume and price distance
                volume_factor = min(volume / avg_volume / 2, 1.0)
                price_distance = abs(close - (bb_upper if breakout_up else bb_lower))
                price_factor = min(price_distance / (bb_upper - bb_lower), 1.0)
                
                confidence = (volume_factor + price_factor) / 2
                
                return True, confidence, {
                    'type': 'up' if breakout_up else 'down',
                    'close': close,
                    'bb_upper': bb_upper,
                    'bb_lower': bb_lower,
                    'volume': volume,
                    'avg_volume': avg_volume
                }
                
            return False, 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Error checking breakout setup: {str(e)}")
            return False, 0.0, {}
            
    def _check_trend_setup(self, data: pd.DataFrame, 
                          indicators: Dict) -> Tuple[bool, float, Dict]:
        """Check for trend continuation setups"""
        try:
            # Get latest values
            close = data['close'].iloc[-1]
            ema_20 = indicators['ema_20'][-1]
            ema_50 = indicators['ema_50'][-1]
            ema_200 = indicators['ema_200'][-1]
            adx = indicators['adx'][-1]
            
            # Check for strong trend
            uptrend = (
                close > ema_20 > ema_50 > ema_200 and
                adx > 25
            )
            
            downtrend = (
                close < ema_20 < ema_50 < ema_200 and
                adx > 25
            )
            
            if uptrend or downtrend:
                # Calculate confidence based on ADX and EMA alignment
                adx_factor = min((adx - 25) / 25, 1.0)
                ema_spread = abs(ema_20 - ema_200) / ema_200
                ema_factor = min(ema_spread, 1.0)
                
                confidence = (adx_factor + ema_factor) / 2
                
                return True, confidence, {
                    'type': 'up' if uptrend else 'down',
                    'close': close,
                    'ema_20': ema_20,
                    'ema_50': ema_50,
                    'ema_200': ema_200,
                    'adx': adx
                }
                
            return False, 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Error checking trend setup: {str(e)}")
            return False, 0.0, {}
            
    def _check_pattern_setup(self, data: pd.DataFrame, 
                            indicators: Dict) -> Tuple[bool, float, Dict]:
        """Check for chart patterns"""
        try:
            # Get pattern signals
            engulfing = indicators.get('engulfing', [0])[-1]
            doji = indicators.get('doji', [0])[-1]
            hammer = indicators.get('hammer', [0])[-1]
            
            # Check if any pattern is present
            if any(abs(x) >= 100 for x in [engulfing, doji, hammer]):
                pattern_type = None
                pattern_strength = 0
                
                if abs(engulfing) >= 100:
                    pattern_type = 'bullish_engulfing' if engulfing > 0 else 'bearish_engulfing'
                    pattern_strength = abs(engulfing) / 100
                elif abs(doji) >= 100:
                    pattern_type = 'doji'
                    pattern_strength = abs(doji) / 100
                elif abs(hammer) >= 100:
                    pattern_type = 'hammer'
                    pattern_strength = abs(hammer) / 100
                    
                # Calculate confidence based on pattern strength and volume
                volume = data['volume'].iloc[-1]
                avg_volume = data['volume'].rolling(20).mean().iloc[-1]
                volume_factor = min(volume / avg_volume, 1.0)
                
                confidence = (pattern_strength + volume_factor) / 2
                
                return True, confidence, {
                    'type': pattern_type,
                    'strength': pattern_strength,
                    'volume_factor': volume_factor
                }
                
            return False, 0.0, {}
            
        except Exception as e:
            self.logger.error(f"Error checking pattern setup: {str(e)}")
            return False, 0.0, {}
