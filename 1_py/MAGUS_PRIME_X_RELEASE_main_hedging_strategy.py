import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from enhanced_trading_engine import Position

@dataclass
class HedgePosition:
    original_position: Position
    hedge_position: Position
    hedge_ratio: float
    creation_time: datetime
    hedge_reason: str

class HedgingStrategy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.hedged_positions: Dict[str, HedgePosition] = {}
        self.min_hedge_duration = 15  # minutes
        
    def check_hedge_conditions(self, position: Position, market_data: Dict, indicators: Dict) -> Tuple[bool, str, float]:
        """Check if a position should be hedged."""
        try:
            symbol = position.symbol
            timeframe = position.timeframe
            
            # Get relevant data
            data_5m = market_data[symbol]['5m']
            data_1h = market_data[symbol]['1h']
            data_4h = market_data[symbol]['4h']
            
            # Check for strong trend reversal
            trend_reversal = self._detect_trend_reversal(
                position.direction,
                data_5m, data_1h, data_4h,
                indicators[symbol]['5m'],
                indicators[symbol]['1h'],
                indicators[symbol]['4h']
            )
            
            if trend_reversal:
                hedge_ratio = self._calculate_hedge_ratio(position, market_data, indicators)
                return True, "Strong trend reversal detected", hedge_ratio
                
            # Check for divergence
            divergence = self._detect_divergence(position, data_5m, indicators[symbol]['5m'])
            if divergence:
                return True, "RSI divergence detected", 0.5  # Partial hedge
                
            return False, "", 0.0
            
        except Exception as e:
            self.logger.error(f"Error checking hedge conditions: {str(e)}")
            return False, "", 0.0
            
    def _detect_trend_reversal(
        self,
        position_direction: str,
        data_5m: pd.DataFrame,
        data_1h: pd.DataFrame,
        data_4h: pd.DataFrame,
        ind_5m: Dict,
        ind_1h: Dict,
        ind_4h: Dict
    ) -> bool:
        """Detect strong trend reversal signals."""
        try:
            # Check EMA crossovers
            ema_200_5m = ind_5m['ema_200'][-1]
            ema_200_1h = ind_1h['ema_200'][-1]
            ema_200_4h = ind_4h['ema_200'][-1]
            
            current_price = data_5m['close'].iloc[-1]
            
            if position_direction == 'long':
                bearish = (
                    current_price < ema_200_5m and
                    current_price < ema_200_1h and
                    ind_5m['rsi'][-1] < 30 and
                    ind_1h['macd_hist'][-1] < 0
                )
                return bearish
            else:
                bullish = (
                    current_price > ema_200_5m and
                    current_price > ema_200_1h and
                    ind_5m['rsi'][-1] > 70 and
                    ind_1h['macd_hist'][-1] > 0
                )
                return bullish
                
        except Exception as e:
            self.logger.error(f"Error detecting trend reversal: {str(e)}")
            return False
            
    def _detect_divergence(self, position: Position, data: pd.DataFrame, indicators: Dict) -> bool:
        """Detect RSI divergence."""
        try:
            price_data = data['close'].values[-20:]
            rsi_data = indicators['rsi'][-20:]
            
            if position.direction == 'long':
                # Bearish divergence
                price_making_higher_high = price_data[-1] > max(price_data[:-1])
                rsi_making_lower_high = rsi_data[-1] < max(rsi_data[:-1])
                return price_making_higher_high and rsi_making_lower_high
            else:
                # Bullish divergence
                price_making_lower_low = price_data[-1] < min(price_data[:-1])
                rsi_making_higher_low = rsi_data[-1] > min(rsi_data[:-1])
                return price_making_lower_low and rsi_making_higher_low
                
        except Exception as e:
            self.logger.error(f"Error detecting divergence: {str(e)}")
            return False
            
    def _calculate_hedge_ratio(self, position: Position, market_data: Dict, indicators: Dict) -> float:
        """Calculate optimal hedge ratio based on market conditions."""
        try:
            symbol = position.symbol
            
            # Get volatility measures
            atr = indicators[symbol]['5m']['atr'][-1]
            avg_atr = np.mean(indicators[symbol]['5m']['atr'][-20:])
            
            # Higher volatility = larger hedge
            volatility_factor = min(atr / avg_atr, 1.5)
            
            # Check trend strength
            trend_strength = abs(indicators[symbol]['1h']['adx'][-1])
            trend_factor = min(trend_strength / 25, 1.5)
            
            # Base hedge ratio
            base_ratio = 1.0
            
            # Adjust based on factors
            final_ratio = base_ratio * volatility_factor * trend_factor
            
            # Ensure ratio is between 0.5 and 1.5
            return max(0.5, min(1.5, final_ratio))
            
        except Exception as e:
            self.logger.error(f"Error calculating hedge ratio: {str(e)}")
            return 1.0
            
    def create_hedge(self, position: Position, hedge_ratio: float, reason: str) -> Optional[Position]:
        """Create a hedge position."""
        try:
            # Calculate hedge position size
            hedge_size = position.size * hedge_ratio
            
            # Create opposite position
            hedge_position = Position(
                symbol=position.symbol,
                direction='short' if position.direction == 'long' else 'long',
                entry_price=None,  # Will be filled by execution engine
                stop_loss=None,  # Will be calculated by execution engine
                take_profit=[],  # Will be calculated by execution engine
                size=hedge_size,
                entry_time=datetime.now(),
                timeframe='hedge',
                id=f"hedge_{position.id}"
            )
            
            # Store hedge relationship
            self.hedged_positions[position.id] = HedgePosition(
                original_position=position,
                hedge_position=hedge_position,
                hedge_ratio=hedge_ratio,
                creation_time=datetime.now(),
                hedge_reason=reason
            )
            
            return hedge_position
            
        except Exception as e:
            self.logger.error(f"Error creating hedge: {str(e)}")
            return None
            
    def manage_hedged_positions(self, market_data: Dict, indicators: Dict):
        """Manage existing hedged positions."""
        positions_to_remove = []
        
        for pos_id, hedge in self.hedged_positions.items():
            try:
                # Check if original position still exists
                if pos_id not in market_data['positions']:
                    positions_to_remove.append(pos_id)
                    continue
                    
                # Check if hedge should be closed
                if self._should_close_hedge(hedge, market_data, indicators):
                    positions_to_remove.append(pos_id)
                    
            except Exception as e:
                self.logger.error(f"Error managing hedged position {pos_id}: {str(e)}")
                
        # Clean up closed positions
        for pos_id in positions_to_remove:
            del self.hedged_positions[pos_id]
            
    def _should_close_hedge(self, hedge: HedgePosition, market_data: Dict, indicators: Dict) -> bool:
        """Determine if a hedge position should be closed."""
        try:
            # Minimum hedge duration
            if (datetime.now() - hedge.creation_time).total_seconds() < self.min_hedge_duration * 60:
                return False
                
            symbol = hedge.original_position.symbol
            
            # Check if trend reversal has played out
            if hedge.hedge_reason == "Strong trend reversal detected":
                if hedge.original_position.direction == 'long':
                    # Check if downtrend is weakening
                    return (
                        indicators[symbol]['1h']['macd_hist'][-1] > 0 and
                        indicators[symbol]['5m']['rsi'][-1] > 50
                    )
                else:
                    # Check if uptrend is weakening
                    return (
                        indicators[symbol]['1h']['macd_hist'][-1] < 0 and
                        indicators[symbol]['5m']['rsi'][-1] < 50
                    )
                    
            # For divergence-based hedges
            elif hedge.hedge_reason == "RSI divergence detected":
                # Close hedge if RSI normalizes
                rsi = indicators[symbol]['5m']['rsi'][-1]
                return 40 < rsi < 60
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking hedge closure: {str(e)}")
            return False
