"""
Market analyzer module for MAGUS PRIME X trading bot.

This module handles all market analysis functions, including using the Chart Analyzer
module when available or falling back to basic technical analysis when it's not.
"""

import logging
from typing import Any, Dict, List, Tuple


class MarketAnalyzer:
    """Handles analysis of market data and determination of trading signals."""

    def __init__(self, chart_analyzer=None):
        """Initialize the market analyzer.

        Args:
            chart_analyzer: ChartAnalyzer instance (optional)
        """
        self.chart_analyzer = chart_analyzer
        self.last_analysis_cache = {}

    def analyze_market(
        self, symbol: str, prices: List[Dict], current_price: float
    ) -> Tuple[str, float, float, float]:
        """Analyze market conditions for a given symbol.

        Args:
            symbol: Market symbol to analyze
            prices: Historical price data
            current_price: Current market price

        Returns:
            tuple: (action, take_profit, stop_loss, confidence)
        """
        logging.debug(f"Analyzing market for {symbol} with {len(prices)} candles")

        # Check if we have valid market data
        if not self._validate_market_data(symbol, prices, current_price):
            return "NONE", 0, 0, 0

        # Use the Chart Analyzer if available, otherwise fallback
        if self.chart_analyzer:
            result = self._process_chart_analysis(symbol, prices, current_price)
        else:
            # Use fallback analysis
            from utils.price_formatter import PriceFormatter

            formatted_prices = PriceFormatter.format_prices_for_fallback_analysis(
                prices
            )
            result = self.perform_fallback_analysis(
                symbol, formatted_prices, current_price
            )

        # Extract the action and confidence from analysis result
        action = result.get("signal", "NONE")
        confidence = result.get("confidence", 0)

        # Calculate exit levels using standard method
        from trading.exit_level_calculator import ExitLevelCalculator

        # Use support/resistance levels if available from chart analysis
        sr_data = result.get("support_resistance")
        if sr_data:
            take_profit, stop_loss = ExitLevelCalculator.calculate_sr_exit_levels(
                action, current_price, sr_data
            )
        else:
            # Use standard calculation method
            take_profit, stop_loss = ExitLevelCalculator.calculate_exit_levels(
                action, current_price
            )

        return action, take_profit, stop_loss, confidence

    def _validate_market_data(
        self, symbol: str, prices: List[Dict], current_price: float
    ) -> bool:
        """Validate that we have sufficient market data for analysis.

        Args:
            symbol: Market symbol
            prices: Historical price data
            current_price: Current market price

        Returns:
            bool: True if the data is valid, False otherwise
        """
        if not prices:
            logging.warning(f"No price data available for {symbol}")
            return False

        if not current_price or current_price <= 0:
            logging.warning(f"Invalid current price for {symbol}: {current_price}")
            return False

        if len(prices) < 20:  # Minimum required for basic technical analysis
            logging.warning(
                f"Insufficient historical data for {symbol}: {len(prices)} candles"
            )
            return False

        return True

    def _process_chart_analysis(
        self, symbol: str, prices: List[Dict], current_price: float
    ) -> Dict[str, Any]:
        """Process market analysis using the Chart Analyzer.

        Args:
            symbol: Market symbol
            prices: Historical price data
            current_price: Current market price

        Returns:
            dict: Analysis result with signal and confidence
        """
        try:
            logging.info(f"Using Chart Analyzer for {symbol}")

            # Use the Chart Analyzer to analyze the market
            from utils.price_formatter import PriceFormatter

            formatted_data = PriceFormatter.format_prices_for_chart_analyzer(prices)

            # Perform the analysis with the Chart Analyzer
            analysis_result = self.chart_analyzer.analyze_chart(
                symbol, formatted_data, current_price
            )

            # Update the last analysis cache
            self.last_analysis_cache[symbol] = {
                "timestamp": (
                    formatted_data["timestamp"][-1]
                    if formatted_data["timestamp"]
                    else None
                ),
                "result": analysis_result,
            }

            return analysis_result

        except Exception as e:
            logging.error(f"Error in chart analysis for {symbol}: {e}")
            return {"signal": "NONE", "confidence": 0}

    def perform_fallback_analysis(
        self, symbol: str, formatted_prices: Dict[str, List], current_price: float
    ) -> Dict[str, Any]:
        """Perform basic technical analysis when chart analyzer is not available.

        Args:
            symbol: Market symbol to analyze
            formatted_prices: Formatted price data with close, high, low lists
            current_price: Current market price

        Returns:
            dict: Analysis result with signal and confidence
        """
        logging.info(f"Using fallback analysis for {symbol}")

        try:
            closes = formatted_prices.get("close", [])
            if not closes:
                logging.warning(
                    f"No valid price data for fallback analysis of {symbol}"
                )
                return {"signal": "NONE", "confidence": 0}

            # Simple moving averages
            short_ma = sum(closes[-5:]) / 5 if len(closes) >= 5 else current_price
            long_ma = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price

            # Determine if price is near support or resistance
            highs = formatted_prices.get("high", [])
            lows = formatted_prices.get("low", [])

            # Calculate potential support and resistance levels
            support_resistance = self._calculate_simple_sr_levels(
                highs, lows, current_price
            )

            # Determine trend direction
            if short_ma > long_ma * 1.01:  # 1% buffer
                signal = "BUY"
                confidence = self._calculate_signal_confidence(
                    closes, short_ma, long_ma
                )
            elif short_ma < long_ma * 0.99:  # 1% buffer
                signal = "SELL"
                confidence = self._calculate_signal_confidence(
                    closes, short_ma, long_ma
                )
            else:
                signal = "NONE"
                confidence = 0

            return {
                "signal": signal,
                "confidence": confidence,
                "analysis_type": "fallback",
                "short_ma": short_ma,
                "long_ma": long_ma,
                "support_resistance": support_resistance,
            }

        except Exception as e:
            logging.error(f"Error in fallback analysis for {symbol}: {e}")
            return {"signal": "NONE", "confidence": 0}

    def _calculate_signal_confidence(
        self, closes: List[float], short_ma: float, long_ma: float
    ) -> float:
        """Calculate confidence level for a trading signal.

        Args:
            closes: List of closing prices
            short_ma: Short-term moving average
            long_ma: Long-term moving average

        Returns:
            float: Confidence level between 0 and 1
        """
        # Base confidence
        base_confidence = 0.6

        # Calculate recent volatility
        if len(closes) >= 10:
            recent_prices = closes[-10:]
            price_range = max(recent_prices) - min(recent_prices)
            avg_price = sum(recent_prices) / len(recent_prices)

            # Normalize volatility (0-1 range)
            volatility = min(1.0, price_range / (avg_price * 0.1))

            # Adjust confidence based on volatility
            # Higher volatility slightly reduces confidence
            confidence = base_confidence * (1.0 - (volatility * 0.3))

            # Adjust confidence based on MA separation
            # Greater separation increases confidence
            ma_diff = abs(short_ma - long_ma) / ((short_ma + long_ma) / 2)
            ma_factor = min(1.5, 1.0 + (ma_diff * 10))

            confidence = confidence * ma_factor

            # Ensure confidence is between 0 and 1
            return min(0.95, max(0.0, confidence))

        return base_confidence

    def _calculate_simple_sr_levels(
        self, highs: List[float], lows: List[float], current_price: float
    ) -> Dict[str, List[float]]:
        """Calculate simple support and resistance levels.

        Args:
            highs: List of high prices
            lows: List of low prices
            current_price: Current market price

        Returns:
            dict: Support and resistance levels
        """
        # Check if we have enough data
        if not self._has_sufficient_price_data(highs, lows):
            return {}

        try:
            # Find local highs and lows
            resistance_levels, support_levels = self._identify_swing_points(highs, lows)

            # Filter levels that are too close to current price
            filtered_levels = self._filter_nearby_levels(
                resistance_levels, support_levels, current_price
            )

            return filtered_levels

        except Exception as e:
            logging.error(f"Error calculating support/resistance levels: {e}")
            return {}

    def _has_sufficient_price_data(self, highs: List[float], lows: List[float]) -> bool:
        """Check if there is sufficient price data for analysis.

        Args:
            highs: List of high prices
            lows: List of low prices

        Returns:
            bool: True if there is sufficient data
        """
        return highs and lows and len(highs) >= 10 and len(lows) >= 10

    def _identify_swing_points(
        self, highs: List[float], lows: List[float]
    ) -> Tuple[List[float], List[float]]:
        """Identify swing high and low points in price data.

        Args:
            highs: List of high prices
            lows: List of low prices

        Returns:
            tuple: (resistance_levels, support_levels)
        """
        resistance_levels = []
        support_levels = []

        # Use a simple algorithm to find swing highs and lows
        window_size = 5

        for i in range(window_size, len(highs) - window_size):
            # Check if this point is a local high
            if self._is_local_high(highs, i, window_size):
                resistance_levels.append(highs[i])

            # Check if this point is a local low
            if self._is_local_low(lows, i, window_size):
                support_levels.append(lows[i])

        # Remove duplicates and sort
        resistance_levels = sorted(list(set(resistance_levels)))
        support_levels = sorted(list(set(support_levels)))

        return resistance_levels, support_levels

    def _is_local_high(self, prices: List[float], index: int, window_size: int) -> bool:
        """Check if a point is a local high.

        Args:
            prices: List of prices
            index: Current index
            window_size: Window size for comparison

        Returns:
            bool: True if the point is a local high
        """
        return prices[index] == max(
            prices[index - window_size : index + window_size + 1]
        )

    def _is_local_low(self, prices: List[float], index: int, window_size: int) -> bool:
        """Check if a point is a local low.

        Args:
            prices: List of prices
            index: Current index
            window_size: Window size for comparison

        Returns:
            bool: True if the point is a local low
        """
        return prices[index] == min(
            prices[index - window_size : index + window_size + 1]
        )

    def _filter_nearby_levels(
        self,
        resistance_levels: List[float],
        support_levels: List[float],
        current_price: float,
    ) -> Dict[str, List[float]]:
        """Filter out levels that are too close to the current price.

        Args:
            resistance_levels: List of resistance levels
            support_levels: List of support levels
            current_price: Current market price

        Returns:
            dict: Filtered support and resistance levels
        """
        # Filter levels that are too close to current price
        min_distance = current_price * 0.005  # 0.5% minimum distance

        filtered_resistance = [
            r for r in resistance_levels if abs(r - current_price) > min_distance
        ]

        filtered_support = [
            s for s in support_levels if abs(s - current_price) > min_distance
        ]

        return {"resistance": filtered_resistance, "support": filtered_support}
