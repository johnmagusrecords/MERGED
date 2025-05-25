import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
import talib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CandlePattern:
    name: str
    bullish: bool
    strength: float  # 0.0 to 1.0
    description: str
    start_index: int
    end_index: int


@dataclass
class Support:
    price: float
    strength: float  # 0.0 to 1.0
    type: str  # 'support' or 'resistance'
    touches: int
    time_period: List[datetime]


class ChartAnalyzer:
    """Advanced chart and candlestick pattern analyzer"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.patterns = {}
        self.key_levels = {}
        self.chart_images_dir = "chart_images"

        # Ensure chart images directory exists
        os.makedirs(self.chart_images_dir, exist_ok=True)

        # Map of pattern IDs to names
        self.pattern_names = {
            talib.CDL2CROWS: "Two Crows",
            talib.CDL3BLACKCROWS: "Three Black Crows",
            talib.CDL3INSIDE: "Three Inside Up/Down",
            talib.CDL3LINESTRIKE: "Three-Line Strike",
            talib.CDL3OUTSIDE: "Three Outside Up/Down",
            talib.CDL3STARSINSOUTH: "Three Stars In The South",
            talib.CDL3WHITESOLDIERS: "Three Advancing White Soldiers",
            talib.CDLABANDONEDBABY: "Abandoned Baby",
            talib.CDLADVANCEBLOCK: "Advance Block",
            talib.CDLBELTHOLD: "Belt-hold",
            talib.CDLBREAKAWAY: "Breakaway",
            talib.CDLCLOSINGMARUBOZU: "Closing Marubozu",
            talib.CDLCONCEALBABYSWALL: "Concealing Baby Swallow",
            talib.CDLCOUNTERATTACK: "Counterattack",
            talib.CDLDARKCLOUDCOVER: "Dark Cloud Cover",
            talib.CDLDOJI: "Doji",
            talib.CDLDOJISTAR: "Doji Star",
            talib.CDLDRAGONFLYDOJI: "Dragonfly Doji",
            talib.CDLENGULFING: "Engulfing Pattern",
            talib.CDLEVENINGDOJISTAR: "Evening Doji Star",
            talib.CDLEVENINGSTAR: "Evening Star",
            talib.CDLGAPSIDESIDEWHITE: "Up/Down-gap side-by-side white lines",
            talib.CDLGRAVESTONEDOJI: "Gravestone Doji",
            talib.CDLHAMMER: "Hammer",
            talib.CDLHANGINGMAN: "Hanging Man",
            talib.CDLHARAMI: "Harami Pattern",
            talib.CDLHARAMICROSS: "Harami Cross Pattern",
            talib.CDLHIGHWAVE: "High-Wave Candle",
            talib.CDLHIKKAKE: "Hikkake Pattern",
            talib.CDLHIKKAKEMOD: "Modified Hikkake Pattern",
            talib.CDLHOMINGPIGEON: "Homing Pigeon",
            talib.CDLIDENTICAL3CROWS: "Identical Three Crows",
            talib.CDLINNECK: "In-Neck Pattern",
            talib.CDLINVERTEDHAMMER: "Inverted Hammer",
            talib.CDLKICKING: "Kicking",
            talib.CDLKICKINGBYLENGTH: "Kicking - bull/bear determined by length",
            talib.CDLLADDERBOTTOM: "Ladder Bottom",
            talib.CDLLONGLEGGEDDOJI: "Long Legged Doji",
            talib.CDLLONGLINE: "Long Line Candle",
            talib.CDLMARUBOZU: "Marubozu",
            talib.CDLMATCHINGLOW: "Matching Low",
            talib.CDLMATHOLD: "Mat Hold",
            talib.CDLMORNINGDOJISTAR: "Morning Doji Star",
            talib.CDLMORNINGSTAR: "Morning Star",
            talib.CDLONNECK: "On-Neck Pattern",
            talib.CDLPIERCING: "Piercing Pattern",
            talib.CDLRICKSHAWMAN: "Rickshaw Man",
            talib.CDLRISEFALL3METHODS: "Rising/Falling Three Methods",
            talib.CDLSHOOTINGSTAR: "Shooting Star",
            talib.CDLSHORTLINE: "Short Line Candle",
            talib.CDLSPINNINGTOP: "Spinning Top",
            talib.CDLSTALLEDPATTERN: "Stalled Pattern",
            talib.CDLSTICKSANDWICH: "Stick Sandwich",
            talib.CDLTAKURI: "Takuri (Dragonfly Doji with very long lower shadow)",
            talib.CDLTASUKIGAP: "Tasuki Gap",
            talib.CDLTHRUSTING: "Thrusting Pattern",
            talib.CDLTRISTAR: "Tristar Pattern",
            talib.CDLUNIQUE3RIVER: "Unique 3 River",
            talib.CDLUPSIDEGAP2CROWS: "Upside Gap Two Crows",
            talib.CDLXSIDEGAP3METHODS: "Upside/Downside Gap Three Methods",
        }

        # Pattern bullishness mapping (1 = bullish, -1 = bearish, 0 = neutral)
        self.pattern_bullishness = {
            "Two Crows": -1,
            "Three Black Crows": -1,
            "Three Inside Up/Down": 0,
            "Three-Line Strike": 0,
            "Three Outside Up/Down": 0,
            "Three Stars In The South": 1,
            "Three Advancing White Soldiers": 1,
            "Abandoned Baby": 0,
            "Advance Block": -1,
            "Belt-hold": 0,
            "Breakaway": 0,
            "Closing Marubozu": 0,
            "Concealing Baby Swallow": 1,
            "Counterattack": 0,
            "Dark Cloud Cover": -1,
            "Doji": 0,
            "Doji Star": 0,
            "Dragonfly Doji": 1,
            "Engulfing Pattern": 0,
            "Evening Doji Star": -1,
            "Evening Star": -1,
            "Up/Down-gap side-by-side white lines": 0,
            "Gravestone Doji": -1,
            "Hammer": 1,
            "Hanging Man": -1,
            "Harami Pattern": 0,
            "Harami Cross Pattern": 0,
            "High-Wave Candle": 0,
            "Hikkake Pattern": 0,
            "Modified Hikkake Pattern": 0,
            "Homing Pigeon": 1,
            "Identical Three Crows": -1,
            "In-Neck Pattern": -1,
            "Inverted Hammer": 1,
            "Kicking": 0,
            "Kicking - bull/bear determined by length": 0,
            "Ladder Bottom": 1,
            "Long Legged Doji": 0,
            "Long Line Candle": 0,
            "Marubozu": 0,
            "Matching Low": 1,
            "Mat Hold": 1,
            "Morning Doji Star": 1,
            "Morning Star": 1,
            "On-Neck Pattern": -1,
            "Piercing Pattern": 1,
            "Rickshaw Man": 0,
            "Rising/Falling Three Methods": 0,
            "Separating Lines": 0,
            "Shooting Star": -1,
            "Short Line Candle": 0,
            "Spinning Top": 0,
            "Stalled Pattern": -1,
            "Stick Sandwich": 1,
            "Takuri": 1,
            "Tasuki Gap": 0,
            "Thrusting Pattern": -1,
            "Tristar Pattern": 0,
            "Unique 3 River": 1,
            "Upside Gap Two Crows": -1,
            "Upside/Downside Gap Three Methods": 0,
        }

        # Pattern strength mapping (0.0 to 1.0)
        self.pattern_strength = {
            "Three Black Crows": 0.9,
            "Three White Soldiers": 0.9,
            "Morning Star": 0.8,
            "Evening Star": 0.8,
            "Engulfing Pattern": 0.7,
            "Hammer": 0.7,
            "Shooting Star": 0.7,
            "Doji": 0.5,
            "Harami Pattern": 0.6,
        }

    def analyze_candles(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Analyze candlestick patterns in the data"""
        try:
            # Ensure we have OHLCV data
            if not all(x in data.columns for x in ["open", "high", "low", "close"]):
                raise ValueError("Data must contain OHLC columns")

            open_prices = data["open"].values
            high_prices = data["high"].values
            low_prices = data["low"].values
            close_prices = data["close"].values

            # Store patterns found
            patterns_found = []

            # Check for all candlestick patterns using TA-Lib
            for pattern_func, pattern_name in self.pattern_names.items():
                # Calculate pattern
                result = pattern_func(
                    open_prices, high_prices, low_prices, close_prices
                )

                # Find where pattern is detected (non-zero values)
                pattern_indices = np.nonzero(result)[0]

                for idx in pattern_indices:
                    # Get pattern strength
                    strength = self.pattern_strength.get(pattern_name, 0.6)

                    # Determine if pattern is bullish or bearish based on its nature and current trend
                    bullish = False
                    if self.pattern_bullishness[pattern_name] == 1:
                        bullish = True
                    elif self.pattern_bullishness[pattern_name] == -1:
                        bullish = False
                    else:
                        # For neutral patterns, detect based on result value
                        bullish = result[idx] > 0

                    # Create pattern object
                    pattern = CandlePattern(
                        name=pattern_name,
                        bullish=bullish,
                        strength=strength,
                        description=self._get_pattern_description(pattern_name),
                        start_index=max(0, idx - 2),
                        end_index=idx,
                    )

                    patterns_found.append(pattern)

            # Sort patterns by their position (end_index) and strength
            patterns_found.sort(key=lambda x: (x.end_index, -x.strength))

            # Calculate overall sentiment based on patterns
            bullish_count = sum(1 for p in patterns_found if p.bullish)
            bearish_count = len(patterns_found) - bullish_count

            if len(patterns_found) == 0:
                sentiment = "neutral"
                sentiment_strength = 0.5
            else:
                sentiment = "bullish" if bullish_count > bearish_count else "bearish"
                sentiment_strength = abs(bullish_count - bearish_count) / len(
                    patterns_found
                )

            # Store patterns for this symbol
            self.patterns[symbol] = patterns_found

            return {
                "symbol": symbol,
                "patterns": [vars(p) for p in patterns_found],
                "patterns_count": len(patterns_found),
                "sentiment": sentiment,
                "sentiment_strength": sentiment_strength,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(
                f"Error analyzing candlestick patterns for {symbol}: {str(e)}"
            )
            return {
                "symbol": symbol,
                "error": str(e),
                "patterns": [],
                "patterns_count": 0,
                "sentiment": "neutral",
                "sentiment_strength": 0.5,
                "timestamp": datetime.now().isoformat(),
            }

    def _get_pattern_description(self, pattern_name: str) -> str:
        """Get a description for the candlestick pattern"""
        descriptions = {
            "Doji": "Indicates indecision in the market. Open and close prices are nearly equal.",
            "Hammer": " "
Bullish reversal pattern with a small bo + "dy and long lower shadow, indicating pot + "ential trend reversal.",
            "Shooting Star": " "
Bearish reversal pattern with a small bo + "dy and long upper shadow, signaling pote + "ntial downtrend.",
            "Engulfing Pattern": " "
A two-candle pattern where the second ca + "ndle completely engulfs the body of the  + "first.",
            "Morning Star": " "
Bullish reversal pattern consisting of t + "hree candles, indicating a potential upt + "rend.",
            "Evening Star": " "
Bearish reversal pattern consisting of t + "hree candles, indicating a potential dow + "ntrend.",
            "Three Black Crows": " "
Bearish reversal pattern with three cons + "ecutive declining candles, suggesting a  + "downtrend.",
            "Three White Soldiers": " "
Bullish reversal pattern with three cons + "ecutive advancing candles, suggesting an + " uptrend.",
        }

        return descriptions.get(
            pattern_name, f"A {pattern_name.lower()} pattern was detected."
        )

    def analyze_trend(
        self, symbol: str, data: pd.DataFrame, timeframes: List[str] = None
    ) -> Dict:
        """
        Analyze market trend across multiple timeframes

        Args:
            symbol: Trading symbol
            data: Dict of dataframes indexed by timeframe
            timeframes: List of timeframes to analyze

        Returns:
            Dictionary with trend analysis
        """
        try:
            # Initialize results
            trend_analysis = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "timeframes": {},
            }

            # Analyze all available timeframes
            for tf, tf_data in data.items():
                # Skip if timeframes specified and this one not included
                if timeframes and tf not in timeframes:
                    continue

                close_prices = tf_data["close"].values

                # Calculate various moving averages
                sma20 = talib.SMA(close_prices, timeperiod=20)
                sma50 = talib.SMA(close_prices, timeperiod=50)
                sma200 = talib.SMA(close_prices, timeperiod=200)
                ema20 = talib.EMA(close_prices, timeperiod=20)

                # Calculate ADX for trend strength
                adx = talib.ADX(
                    tf_data["high"].values,
                    tf_data["low"].values,
                    close_prices,
                    timeperiod=14,
                )

                # Current price and moving averages
                current_price = close_prices[-1]
                current_sma20 = sma20[-1]
                current_sma50 = sma50[-1]
                current_sma200 = sma200[-1]
                current_ema20 = ema20[-1]
                current_adx = adx[-1]

                # Determine trend
                trend = "neutral"
                trend_strength = 0.5

                # Strong uptrend: price > EMA20 > SMA20 > SMA50 > SMA200
                if (
                    current_price
                    > current_ema20
                    > current_sma20
                    > current_sma50
                    > current_sma200
                ):
                    trend = "strong_uptrend"
                    trend_strength = min(1.0, current_adx / 100 + 0.5)

                # Uptrend: price > SMA20 > SMA50
                elif current_price > current_sma20 > current_sma50:
                    trend = "uptrend"
                    trend_strength = min(1.0, current_adx / 100 + 0.3)

                # Strong downtrend: price < EMA20 < SMA20 < SMA50 < SMA200
                elif (
                    current_price
                    < current_ema20
                    < current_sma20
                    < current_sma50
                    < current_sma200
                ):
                    trend = "strong_downtrend"
                    trend_strength = min(1.0, current_adx / 100 + 0.5)

                # Downtrend: price < SMA20 < SMA50
                elif current_price < current_sma20 < current_sma50:
                    trend = "downtrend"
                    trend_strength = min(1.0, current_adx / 100 + 0.3)

                # Possible reversal: price crossed above/below SMA20
                elif current_price > current_sma20 and close_prices[-2] < sma20[-2]:
                    trend = "possible_upward_reversal"
                    trend_strength = 0.6

                elif current_price < current_sma20 and close_prices[-2] > sma20[-2]:
                    trend = "possible_downward_reversal"
                    trend_strength = 0.6

                # Store results for this timeframe
                trend_analysis["timeframes"][tf] = {
                    "trend": trend,
                    "strength": trend_strength,
                    "adx": current_adx,
                    "price_sma20_ratio": current_price / current_sma20 - 1,
                    "price_sma50_ratio": current_price / current_sma50 - 1,
                    "price_sma200_ratio": current_price / current_sma200 - 1,
                    "sma20_sma50_ratio": current_sma20 / current_sma50 - 1,
                    "sma20_cross": (
                        True
                        if (close_prices[-2] - sma20[-2])
                        * (current_price - current_sma20)
                        < 0
                        else False
                    ),
                }

            # Calculate overall trend based on weighted timeframes
            # Weight shorter timeframes less than longer ones
            if trend_analysis["timeframes"]:
                timeframe_weights = {
                    "1m": 0.1,
                    "5m": 0.2,
                    "15m": 0.3,
                    "30m": 0.4,
                    "1h": 0.6,
                    "4h": 0.8,
                    "1d": 1.0,
                    "1w": 1.2,
                }

                uptrend_score = 0
                downtrend_score = 0
                total_weight = 0

                for tf, analysis in trend_analysis["timeframes"].items():
                    weight = timeframe_weights.get(tf, 0.5)
                    total_weight += weight

                    if "uptrend" in analysis["trend"]:
                        uptrend_score += weight * analysis["strength"]
                    elif "downtrend" in analysis["trend"]:
                        downtrend_score += weight * analysis["strength"]

                if total_weight > 0:
                    if uptrend_score > downtrend_score:
                        trend_analysis["overall_trend"] = "uptrend"
                        trend_analysis["overall_strength"] = (
                            uptrend_score / total_weight
                        )
                    elif downtrend_score > uptrend_score:
                        trend_analysis["overall_trend"] = "downtrend"
                        trend_analysis["overall_strength"] = (
                            downtrend_score / total_weight
                        )
                    else:
                        trend_analysis["overall_trend"] = "neutral"
                        trend_analysis["overall_strength"] = 0.5

            return trend_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing trend for {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "timeframes": {},
                "overall_trend": "neutral",
                "overall_strength": 0.5,
            }

    def _identify_support_resistance(
        self, data: pd.DataFrame, window_size: int = 10, threshold: float = 0.01
    ) -> List[Support]:
        """
        Identify support and resistance levels from price data

        Args:
            data: DataFrame with OHLC data
            window_size: Size of the window to look for local min/max
            threshold: Minimum price difference threshold (as % of price)

        Returns:
            List of Support objects with price levels and strengths
        """
        try:
            levels = []

            # Get high and low prices
            highs = data["high"].values
            lows = data["low"].values

            # Find local maxima and minima
            for i in range(window_size, len(data) - window_size):
                # Check if this point is a local high
                if all(
                    highs[i] > highs[i - j] for j in range(1, window_size + 1)
                ) and all(highs[i] > highs[i + j] for j in range(1, window_size + 1)):
                    # Found a resistance level
                    levels.append(
                        Support(
                            price=highs[i],
                            strength=0.0,  # Will be calculated later
                            type="resistance",
                            touches=0,
                            time_period=[data.index[i]],
                        )
                    )

                # Check if this point is a local low
                if all(
                    lows[i] < lows[i - j] for j in range(1, window_size + 1)
                ) and all(lows[i] < lows[i + j] for j in range(1, window_size + 1)):
                    # Found a support level
                    levels.append(
                        Support(
                            price=lows[i],
                            strength=0.0,  # Will be calculated later
                            type="support",
                            touches=0,
                            time_period=[data.index[i]],
                        )
                    )

            # If we don't have many levels, reduce the criteria
            if len(levels) < 4:
                # Try with a smaller window
                return self._identify_support_resistance(
                    data, window_size=5, threshold=threshold
                )

            # Group nearby levels (within threshold %)
            grouped_levels = []
            levels.sort(key=lambda x: x.price)

            current_group = [levels[0]]
            for i in range(1, len(levels)):
                # Check if this level is close to the current group average
                group_avg = sum(level.price for level in current_group) / len(
                    current_group
                )
                price_diff_pct = abs(levels[i].price - group_avg) / group_avg

                if price_diff_pct <= threshold:
                    # Add to current group
                    current_group.append(levels[i])
                else:
                    # Create a new grouped level from the current group
                    avg_price = sum(level.price for level in current_group) / len(
                        current_group
                    )

                    # Determine type (majority vote)
                    supports = sum(
                        1 for level in current_group if level.type == "support"
                    )
                    resistances = len(current_group) - supports
                    level_type = "support" if supports > resistances else "resistance"

                    # Combine time periods
                    time_periods = []
                    for level in current_group:
                        time_periods.extend(level.time_period)

                    grouped_levels.append(
                        Support(
                            price=avg_price,
                            strength=0.0,  # Will be calculated
                            type=level_type,
                            touches=0,  # Will be calculated
                            time_period=time_periods,
                        )
                    )

                    # Start a new group
                    current_group = [levels[i]]

            # Add the last group
            if current_group:
                avg_price = sum(level.price for level in current_group) / len(
                    current_group
                )
                supports = sum(1 for level in current_group if level.type == "support")
                resistances = len(current_group) - supports
                level_type = "support" if supports > resistances else "resistance"

                time_periods = []
                for level in current_group:
                    time_periods.extend(level.time_period)

                grouped_levels.append(
                    Support(
                        price=avg_price,
                        strength=0.0,
                        type=level_type,
                        touches=0,
                        time_period=time_periods,
                    )
                )

            # Count touches and calculate strength
            for i, level in enumerate(grouped_levels):
                touches = 0
                # Check each candle for touches
                for j in range(len(data)):
                    # Define touch range based on price volatility
                    touch_range = data["high"].iloc[j] - data["low"].iloc[j]
                    touch_threshold = max(touch_range * 0.2, level.price * threshold)

                    # Check if candle touches this level
                    if (
                        abs(data["high"].iloc[j] - level.price) <= touch_threshold
                        or abs(data["low"].iloc[j] - level.price) <= touch_threshold
                    ):
                        touches += 1
                        # Add to time periods if not already there
                        if data.index[j] not in level.time_period:
                            level.time_period.append(data.index[j])

                # Update touches
                grouped_levels[i].touches = touches

                # Calculate strength based on touches and recency
                recency_weight = 0.7
                touch_weight = 0.3

                # More recent levels are stronger
                latest_touch = (
                    max(level.time_period) if level.time_period else data.index[0]
                )
                days_since = (
                    (data.index[-1] - latest_touch).days
                    if hasattr(latest_touch, "days")
                    else 0
                )
                recency_score = max(
                    0.0, 1.0 - (days_since / 30)
                )  # Scale to 0-1, 0 means 30+ days old

                # More touches means stronger level
                max_touches = 10  # Cap at 10 touches
                touch_score = min(1.0, touches / max_touches)

                # Combined strength score
                strength = (recency_weight * recency_score) + (
                    touch_weight * touch_score
                )
                grouped_levels[i].strength = strength

            # Sort by strength
            grouped_levels.sort(key=lambda x: x.strength, reverse=True)

            # Limit to top N strongest levels
            return grouped_levels[:8]  # Top 8 levels

        except Exception as e:
            self.logger.error(f"Error identifying support/resistance: {str(e)}")
            return []

    def _generate_pattern_chart(
        self,
        data: pd.DataFrame,
        patterns: List[CandlePattern],
        support_resistance: List[Support],
        chart_patterns: List[Dict] = None,
        filename: str = None,
    ) -> Optional[str]:
        """
        Generate a candlestick chart with patterns and support/resistance levels

        Args:
            data: DataFrame with OHLC data
            patterns: List of candlestick patterns detected
            support_resistance: List of support and resistance levels
            chart_patterns: List of chart patterns (double tops, head and shoulders, etc.)
            filename: Output filename for the chart image

        Returns:
            Path to the saved chart image if successful, None otherwise
        """
        try:
            # Create a copy of the data
            plot_data = data.copy()

            if "date" not in plot_data.columns and not isinstance(
                plot_data.index, pd.DatetimeIndex
            ):
                # Create a date index if not present
                plot_data = plot_data.set_index(
                    pd.date_range(start="2023-01-01", periods=len(plot_data))
                )

            # Set up the plot
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.subplots_adjust(bottom=0.2)

            # Plot candlesticks
            mpf.plot(plot_data, type="candle", style="yahoo", ax=ax)

            # Track pattern annotations for legend
            pattern_annotations = {}

            # Highlight candlestick patterns
            for pattern in patterns:
                # Get indices for the pattern
                start_idx = max(0, pattern.start_index)
                end_idx = min(len(plot_data) - 1, pattern.end_index)

                # Determine color based on bullish/bearish
                color = "green" if pattern.bullish else "red"

                # Create rectangle highlighting the pattern
                dates = plot_data.index[start_idx : end_idx + 1]
                min_price = (
                    plot_data.loc[plot_data.index[start_idx : end_idx + 1], "low"].min()
                    * 0.99
                )
                max_price = (
                    plot_data.loc[
                        plot_data.index[start_idx : end_idx + 1], "high"
                    ].max()
                    * 1.01
                )

                rect = patches.Rectangle(
                    (dates[0], min_price),
                    dates[-1] - dates[0],
                    max_price - min_price,
                    linewidth=1,
                    edgecolor=color,
                    facecolor=color,
                    alpha=0.1,
                )
                ax.add_patch(rect)

                # Add pattern name
                mid_idx = start_idx + (end_idx - start_idx) // 2
                mid_price = (min_price + max_price) / 2

                if pattern.name not in pattern_annotations:
                    pattern_annotations[pattern.name] = {
                        "color": color,
                        "bullish": pattern.bullish,
                    }

                ax.text(
                    plot_data.index[mid_idx],
                    mid_price,
                    pattern.name,
                    color="black",
                    bbox=dict(facecolor=color, alpha=0.3),
                )

            # Add support and resistance levels
            for level in support_resistance:
                color = "green" if level.type == "support" else "red"
                linestyle = "-" if level.strength > 0.6 else "--"

                ax.axhline(
                    y=level.price,
                    color=color,
                    linestyle=linestyle,
                    alpha=min(1.0, 0.3 + level.strength * 0.7),
                    label=f"{level.type.capitalize()} ({level.price:.2f})",
                )

            # Add chart patterns (if provided)
            if chart_patterns:
                for pattern in chart_patterns:
                    if "position" in pattern and len(pattern["position"]) >= 2:
                        # Get color based on bias
                        color = "green" if pattern.get("bias") == "bullish" else "red"
                        if pattern.get("bias") == "neutral":
                            color = "blue"

                        # Get positions
                        positions = pattern["position"]

                        # Create different visualizations based on pattern type
                        pattern_name = pattern.get("name", "")

                        if "Double Top" in pattern_name:
                            # Draw lines connecting peaks
                            start, end = positions[0], positions[1]
                            peak1_y = plot_data.loc[plot_data.index[start], "high"]
                            peak2_y = plot_data.loc[plot_data.index[end], "high"]

                            # Draw line connecting peaks
                            ax.plot(
                                [plot_data.index[start], plot_data.index[end]],
                                [peak1_y, peak2_y],
                                color=color,
                                linewidth=2,
                                linestyle="-",
                            )

                            # Highlight pattern area
                            rect = patches.Rectangle(
                                (
                                    plot_data.index[start],
                                    plot_data.loc[
                                        plot_data.index[start:end], "low"
                                    ].min()
                                    * 0.99,
                                ),
                                plot_data.index[end] - plot_data.index[start],
                                peak1_y * 1.01
                                - plot_data.loc[plot_data.index[start:end], "low"].min()
                                * 0.99,
                                linewidth=1,
                                edgecolor=color,
                                facecolor=color,
                                alpha=0.1,
                            )
                            ax.add_patch(rect)

                        elif "Double Bottom" in pattern_name:
                            # Draw lines connecting troughs
                            start, end = positions[0], positions[1]
                            trough1_y = plot_data.loc[plot_data.index[start], "low"]
                            trough2_y = plot_data.loc[plot_data.index[end], "low"]

                            # Draw line connecting troughs
                            ax.plot(
                                [plot_data.index[start], plot_data.index[end]],
                                [trough1_y, trough2_y],
                                color=color,
                                linewidth=2,
                                linestyle="-",
                            )

                            # Highlight pattern area
                            rect = patches.Rectangle(
                                (plot_data.index[start], trough1_y * 0.99),
                                plot_data.index[end] - plot_data.index[start],
                                plot_data.loc[plot_data.index[start:end], "high"].max()
                                * 1.01
                                - trough1_y * 0.99,
                                linewidth=1,
                                edgecolor=color,
                                facecolor=color,
                                alpha=0.1,
                            )
                            ax.add_patch(rect)

                        elif "Head and Shoulders" in pattern_name:
                            # Draw lines for head and shoulders pattern
                            left, head, right = positions[0], positions[1], positions[2]

                            # Get y values
                            if "Inverse" in pattern_name:
                                # Inverse H&S (looking at lows)
                                left_y = plot_data.loc[plot_data.index[left], "low"]
                                head_y = plot_data.loc[plot_data.index[head], "low"]
                                right_y = plot_data.loc[plot_data.index[right], "low"]

                                # Get neckline
                                left_peak = plot_data.loc[
                                    plot_data.index[left:head], "high"
                                ].max()
                                right_peak = plot_data.loc[
                                    plot_data.index[head:right], "high"
                                ].max()
                                neckline = (left_peak + right_peak) / 2

                                # Plot neckline
                                ax.plot(
                                    [plot_data.index[left], plot_data.index[right]],
                                    [neckline, neckline],
                                    color=color,
                                    linewidth=2,
                                    linestyle="--",
                                )
                            else:
                                # Regular H&S (looking at highs)
                                left_y = plot_data.loc[plot_data.index[left], "high"]
                                head_y = plot_data.loc[plot_data.index[head], "high"]
                                right_y = plot_data.loc[plot_data.index[right], "high"]

                                # Get neckline
                                left_trough = plot_data.loc[
                                    plot_data.index[left:head], "low"
                                ].min()
                                right_trough = plot_data.loc[
                                    plot_data.index[head:right], "low"
                                ].min()
                                neckline = (left_trough + right_trough) / 2

                                # Plot neckline
                                ax.plot(
                                    [plot_data.index[left], plot_data.index[right]],
                                    [neckline, neckline],
                                    color=color,
                                    linewidth=2,
                                    linestyle="--",
                                )

                            # Draw lines connecting shoulders and head
                            ax.plot(
                                [
                                    plot_data.index[left],
                                    plot_data.index[head],
                                    plot_data.index[right],
                                ],
                                [left_y, head_y, right_y],
                                color=color,
                                linewidth=2,
                                marker="o",
                            )

                        elif "Triangle" in pattern_name:
                            start, end = positions[0], positions[1]

                            if "Ascending" in pattern_name:
                                # Plot horizontal resistance line
                                resistance = plot_data.loc[
                                    plot_data.index[start:end], "high"
                                ].max()
                                ax.axhline(
                                    y=resistance,
                                    xmin=start / len(plot_data),
                                    xmax=end / len(plot_data),
                                    color=color,
                                    linestyle="--",
                                    linewidth=2,
                                )

                                # Plot ascending support line
                                first_low = plot_data.loc[plot_data.index[start], "low"]
                                last_low = plot_data.loc[plot_data.index[end], "low"]
                                ax.plot(
                                    [plot_data.index[start], plot_data.index[end]],
                                    [first_low, last_low],
                                    color=color,
                                    linewidth=2,
                                    linestyle="-",
                                )

                            elif "Descending" in pattern_name:
                                # Plot horizontal support line
                                support = plot_data.loc[
                                    plot_data.index[start:end], "low"
                                ].min()
                                ax.axhline(
                                    y=support,
                                    xmin=start / len(plot_data),
                                    xmax=end / len(plot_data),
                                    color=color,
                                    linestyle="--",
                                    linewidth=2,
                                )

                                # Plot descending resistance line
                                first_high = plot_data.loc[
                                    plot_data.index[start], "high"
                                ]
                                last_high = plot_data.loc[plot_data.index[end], "high"]
                                ax.plot(
                                    [plot_data.index[start], plot_data.index[end]],
                                    [first_high, last_high],
                                    color=color,
                                    linewidth=2,
                                    linestyle="-",
                                )

                        elif "Channel" in pattern_name:
                            start, end = positions[0], positions[1]

                            # Get price data for the range
                            range_highs = plot_data.loc[
                                plot_data.index[start:end], "high"
                            ]
                            range_lows = plot_data.loc[
                                plot_data.index[start:end], "low"
                            ]

                            # Fit lines
                            x = np.arange(start, end + 1)
                            x_dates = [
                                plot_data.index[i] for i in range(start, end + 1)
                            ]

                            # Calculate slopes and intercepts
                            high_slope, high_intercept = np.polyfit(
                                x, range_highs.values, 1
                            )
                            low_slope, low_intercept = np.polyfit(
                                x, range_lows.values, 1
                            )

                            # Plot channel lines
                            upper_line = high_intercept + high_slope * x
                            lower_line = low_intercept + low_slope * x

                            ax.plot(
                                x_dates,
                                upper_line,
                                color=color,
                                linewidth=2,
                                linestyle="-",
                            )
                            ax.plot(
                                x_dates,
                                lower_line,
                                color=color,
                                linewidth=2,
                                linestyle="-",
                            )

                            # Add shaded region
                            ax.fill_between(
                                x_dates, upper_line, lower_line, color=color, alpha=0.1
                            )

            # Set plot title and labels
            symbol = data.get(
                "symbol",
                (
                    plot_data.columns.name
                    if hasattr(plot_data.columns, "name")
                    else "Price"
                ),
            )
            title = f"Chart Analysis for {symbol}"
            ax.set_title(title)
            ax.set_xlabel("Date")
            ax.set_ylabel("Price")

            # Format x-axis date labels
            fig.autofmt_xdate()

            # Add grid
            ax.grid(True, alpha=0.3)

            # Add legend for candlestick patterns
            pattern_handles = []
            for name, props in pattern_annotations.items():
                handle = patches.Patch(
                    color=props["color"],
                    alpha=0.3,
                    label=f"{name} ({'Bullish' if props['bullish'] else 'Bearish'})",
                )
                pattern_handles.append(handle)

            # Create legend
            if pattern_handles:
                ax.legend(handles=pattern_handles, loc="upper left")

            # Save figure if filename is provided
            if filename:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                plt.savefig(filename, dpi=100, bbox_inches="tight")
                plt.close(fig)
                return filename
            else:
                plt.show()
                plt.close(fig)
                return None

        except Exception as e:
            self.logger.error(f"Error generating chart: {str(e)}")
            return None

    def detect_chart_patterns(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        Detect common chart patterns like head and shoulders, double tops, etc.

        Args:
            symbol: Trading symbol
            data: DataFrame with OHLC data

        Returns:
            Dictionary with detected patterns and confidence levels
        """
        try:
            # Ensure we have enough data
            if len(data) < 30:
                return {
                    "symbol": symbol,
                    "patterns": [],
                    "message": "Insufficient data for chart pattern detection",
                }

            # Extract price data
            close_prices = data["close"].values
            high_prices = data["high"].values
            low_prices = data["low"].values

            # Results container
            patterns_found = []

            # Detect double tops and bottoms
            double_top = self._detect_double_top(high_prices, close_prices)
            if double_top:
                patterns_found.append(double_top)

            double_bottom = self._detect_double_bottom(low_prices, close_prices)
            if double_bottom:
                patterns_found.append(double_bottom)

            # Detect head and shoulders
            head_shoulders = self._detect_head_and_shoulders(
                high_prices, low_prices, close_prices
            )
            if head_shoulders:
                patterns_found.append(head_shoulders)

            # Detect triangles
            ascending_triangle = self._detect_ascending_triangle(
                high_prices, low_prices
            )
            if ascending_triangle:
                patterns_found.append(ascending_triangle)

            descending_triangle = self._detect_descending_triangle(
                high_prices, low_prices
            )
            if descending_triangle:
                patterns_found.append(descending_triangle)

            # Detect channels
            channel = self._detect_channel(high_prices, low_prices, close_prices)
            if channel:
                patterns_found.append(channel)

            # Determine overall bias based on detected patterns
            if patterns_found:
                bullish_patterns = sum(
                    1 for p in patterns_found if p.get("bias") == "bullish"
                )
                bearish_patterns = sum(
                    1 for p in patterns_found if p.get("bias") == "bearish"
                )

                if bullish_patterns > bearish_patterns:
                    overall_bias = "bullish"
                    confidence = min(1.0, bullish_patterns / len(patterns_found) + 0.2)
                elif bearish_patterns > bullish_patterns:
                    overall_bias = "bearish"
                    confidence = min(1.0, bearish_patterns / len(patterns_found) + 0.2)
                else:
                    overall_bias = "neutral"
                    confidence = 0.5
            else:
                overall_bias = "neutral"
                confidence = 0.5

            return {
                "symbol": symbol,
                "patterns": patterns_found,
                "overall_bias": overall_bias,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error detecting chart patterns for {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "error": str(e),
                "patterns": [],
                "overall_bias": "neutral",
                "confidence": 0.0,
            }

    def _detect_double_top(
        self, high_prices, close_prices, threshold=0.03, min_gap=5
    ) -> Optional[Dict]:
        """Detect double top pattern"""
        try:
            n = len(high_prices)
            for i in range(min_gap, n - min_gap):
                # Look for first peak
                if (
                    high_prices[i] > high_prices[i - 1]
                    and high_prices[i] > high_prices[i + 1]
                ):
                    first_peak = i
                    first_peak_value = high_prices[i]

                    # Look for second peak
                    for j in range(first_peak + min_gap, n - 1):
                        if (
                            high_prices[j] > high_prices[j - 1]
                            and high_prices[j] > high_prices[j + 1]
                        ):
                            second_peak = j
                            second_peak_value = high_prices[j]

                            # Check if peaks are at similar heights
                            price_diff = (
                                abs(first_peak_value - second_peak_value)
                                / first_peak_value
                            )
                            if price_diff < threshold:
                                # Check for confirmation (price breaking below the trough)
                                trough = min(close_prices[first_peak:second_peak])
                                first_peak + np.argmin(
                                    close_prices[first_peak:second_peak]
                                )

                                if (
                                    second_peak + 1 < n
                                    and close_prices[second_peak + 1] < trough
                                ):
                                    confidence = 0.7 * (1 - price_diff / threshold)

                                    return {
                                        "name": "Double Top",
                                        "bias": "bearish",
                                        "position": [first_peak, second_peak],
                                        "confidence": confidence,
                                        "target": trough - (first_peak_value - trough),
                                    }
            return None

        except Exception as e:
            self.logger.error(f"Error detecting double top: {str(e)}")
            return None

    def _detect_double_bottom(
        self, low_prices, close_prices, threshold=0.03, min_gap=5
    ) -> Optional[Dict]:
        """Detect double bottom pattern"""
        try:
            n = len(low_prices)
            for i in range(min_gap, n - min_gap):
                # Look for first trough
                if (
                    low_prices[i] < low_prices[i - 1]
                    and low_prices[i] < low_prices[i + 1]
                ):
                    first_trough = i
                    first_trough_value = low_prices[i]

                    # Look for second trough
                    for j in range(first_trough + min_gap, n - 1):
                        if (
                            low_prices[j] < low_prices[j - 1]
                            and low_prices[j] < low_prices[j + 1]
                        ):
                            second_trough = j
                            second_trough_value = low_prices[j]

                            # Check if troughs are at similar heights
                            price_diff = (
                                abs(first_trough_value - second_trough_value)
                                / first_trough_value
                            )
                            if price_diff < threshold:
                                # Check for confirmation (price breaking above the peak)
                                peak = max(close_prices[first_trough:second_trough])
                                first_trough + np.argmax(
                                    close_prices[first_trough:second_trough]
                                )

                                if (
                                    second_trough + 1 < n
                                    and close_prices[second_trough + 1] > peak
                                ):
                                    confidence = 0.7 * (1 - price_diff / threshold)

                                    return {
                                        "name": "Double Bottom",
                                        "bias": "bullish",
                                        "position": [first_trough, second_trough],
                                        "confidence": confidence,
                                        "target": peak + (peak - first_trough_value),
                                    }
            return None

        except Exception as e:
            self.logger.error(f"Error detecting double bottom: {str(e)}")
            return None

    def _detect_head_and_shoulders(
        self, high_prices, low_prices, close_prices, threshold=0.03, min_gap=3
    ) -> Optional[Dict]:
        """Detect head and shoulders pattern (regular and inverse)"""
        try:
            n = len(high_prices)

            # Check for regular head and shoulders
            for i in range(min_gap, n - 2 * min_gap):
                # Look for left shoulder
                if (
                    high_prices[i] > high_prices[i - 1]
                    and high_prices[i] > high_prices[i + 1]
                ):
                    left_shoulder = i
                    left_shoulder_value = high_prices[i]

                    # Look for head
                    for j in range(left_shoulder + min_gap, n - min_gap):
                        if (
                            high_prices[j] > high_prices[j - 1]
                            and high_prices[j] > high_prices[j + 1]
                        ):
                            head = j
                            head_value = high_prices[j]

                            # Head should be higher than left shoulder
                            if head_value > left_shoulder_value:
                                # Look for right shoulder
                                for k in range(head + min_gap, n - 1):
                                    if (
                                        high_prices[k] > high_prices[k - 1]
                                        and high_prices[k] > high_prices[k + 1]
                                    ):
                                        right_shoulder = k
                                        right_shoulder_value = high_prices[k]

                                        # Right shoulder should be similar height to left shoulder
                                        shoulder_diff = (
                                            abs(
                                                left_shoulder_value
                                                - right_shoulder_value
                                            )
                                            / left_shoulder_value
                                        )

                                        if (
                                            shoulder_diff < threshold
                                            and right_shoulder_value < head_value
                                        ):
                                            # Find neckline
                                            left_trough = min(
                                                low_prices[left_shoulder:head]
                                            )
                                            right_trough = min(
                                                low_prices[head:right_shoulder]
                                            )
                                            neckline = (left_trough + right_trough) / 2

                                            # Check for confirmation
                                            if (
                                                right_shoulder + 1 < n
                                                and close_prices[right_shoulder + 1]
                                                < neckline
                                            ):
                                                confidence = 0.8 * (
                                                    1 - shoulder_diff / threshold
                                                )

                                                return {
                                                    "name": "Head and Shoulders",
                                                    "bias": "bearish",
                                                    "position": [
                                                        left_shoulder,
                                                        head,
                                                        right_shoulder,
                                                    ],
                                                    "confidence": confidence,
                                                    "target": neckline
                                                    - (head_value - neckline),
                                                }

            # Check for inverse head and shoulders
            for i in range(min_gap, n - 2 * min_gap):
                # Look for left shoulder (trough)
                if (
                    low_prices[i] < low_prices[i - 1]
                    and low_prices[i] < low_prices[i + 1]
                ):
                    left_shoulder = i
                    left_shoulder_value = low_prices[i]

                    # Look for head (lower trough)
                    for j in range(left_shoulder + min_gap, n - min_gap):
                        if (
                            low_prices[j] < low_prices[j - 1]
                            and low_prices[j] < low_prices[j + 1]
                        ):
                            head = j
                            head_value = low_prices[j]

                            # Head should be lower than left shoulder
                            if head_value < left_shoulder_value:
                                # Look for right shoulder
                                for k in range(head + min_gap, n - 1):
                                    if (
                                        low_prices[k] < low_prices[k - 1]
                                        and low_prices[k] < low_prices[k + 1]
                                    ):
                                        right_shoulder = k
                                        right_shoulder_value = low_prices[k]

                                        # Right shoulder should be similar height to left shoulder
                                        shoulder_diff = (
                                            abs(
                                                left_shoulder_value
                                                - right_shoulder_value
                                            )
                                            / left_shoulder_value
                                        )

                                        if (
                                            shoulder_diff < threshold
                                            and right_shoulder_value > head_value
                                        ):
                                            # Find neckline
                                            left_peak = max(
                                                high_prices[left_shoulder:head]
                                            )
                                            right_peak = max(
                                                high_prices[head:right_shoulder]
                                            )
                                            neckline = (left_peak + right_peak) / 2

                                            # Check for confirmation
                                            if (
                                                right_shoulder + 1 < n
                                                and close_prices[right_shoulder + 1]
                                                > neckline
                                            ):
                                                confidence = 0.8 * (
                                                    1 - shoulder_diff / threshold
                                                )

                                                return {
                                                    "name": "Inverse Head and Shoulders",
                                                    "bias": "bullish",
                                                    "position": [
                                                        left_shoulder,
                                                        head,
                                                        right_shoulder,
                                                    ],
                                                    "confidence": confidence,
                                                    "target": neckline
                                                    + (neckline - head_value),
                                                }
            return None

        except Exception as e:
            self.logger.error(f"Error detecting head and shoulders: {str(e)}")
            return None

    def _detect_ascending_triangle(
        self, high_prices, low_prices, min_touches=3, threshold=0.03
    ) -> Optional[Dict]:
        """Detect ascending triangle pattern"""
        try:
            n = len(high_prices)

            # Find potential resistance line (flat top)
            for i in range(n - min_touches * 5):
                # Find a high point
                if (
                    high_prices[i] > high_prices[i - 1]
                    and high_prices[i] > high_prices[i + 1]
                ):
                    resistance_level = high_prices[i]

                    # Count number of times price approaches this level
                    touches = 0
                    lows = []

                    for j in range(i, n):
                        # Check if price approaches resistance
                        if (
                            abs(high_prices[j] - resistance_level) / resistance_level
                            < threshold
                        ):
                            touches += 1

                        # Track lows for trend line
                        if (
                            j > i
                            and low_prices[j] < low_prices[j - 1]
                            and low_prices[j] < low_prices[j + 1]
                            if j + 1 < n
                            else True
                        ):
                            lows.append((j, low_prices[j]))

                    # Need at least 3 touches and 2 higher lows
                    if touches >= min_touches and len(lows) >= 2:
                        # Check if lows are making higher lows (ascending)
                        ascending = True
                        for k in range(1, len(lows)):
                            if lows[k][1] <= lows[k - 1][1]:
                                ascending = False
                                break

                        if ascending:
                            # Calculate confidence based on number of touches
                            confidence = min(0.9, 0.5 + touches * 0.1)

                            # Estimate target
                            height = resistance_level - lows[0][1]
                            target = resistance_level + height

                            return {
                                "name": "Ascending Triangle",
                                "bias": "bullish",
                                "position": [i, lows[-1][0]],
                                "confidence": confidence,
                                "target": target,
                            }
            return None

        except Exception as e:
            self.logger.error(f"Error detecting ascending triangle: {str(e)}")
            return None

    def _detect_descending_triangle(
        self, high_prices, low_prices, min_touches=3, threshold=0.03
    ) -> Optional[Dict]:
        """Detect descending triangle pattern"""
        try:
            n = len(low_prices)

            # Find potential support line (flat bottom)
            for i in range(n - min_touches * 5):
                # Find a low point
                if (
                    low_prices[i] < low_prices[i - 1]
                    and low_prices[i] < low_prices[i + 1]
                ):
                    support_level = low_prices[i]

                    # Count number of times price approaches this level
                    touches = 0
                    highs = []

                    for j in range(i, n):
                        # Check if price approaches support
                        if (
                            abs(low_prices[j] - support_level) / support_level
                            < threshold
                        ):
                            touches += 1

                        # Track highs for trend line
                        if (
                            j > i
                            and high_prices[j] > high_prices[j - 1]
                            and high_prices[j] > high_prices[j + 1]
                            if j + 1 < n
                            else True
                        ):
                            highs.append((j, high_prices[j]))

                    # Need at least 3 touches and 2 lower highs
                    if touches >= min_touches and len(highs) >= 2:
                        # Check if highs are making lower highs (descending)
                        descending = True
                        for k in range(1, len(highs)):
                            if highs[k][1] >= highs[k - 1][1]:
                                descending = False
                                break

                        if descending:
                            # Calculate confidence based on number of touches
                            confidence = min(0.9, 0.5 + touches * 0.1)

                            # Estimate target
                            height = highs[0][1] - support_level
                            target = support_level - height

                            return {
                                "name": "Descending Triangle",
                                "bias": "bearish",
                                "position": [i, highs[-1][0]],
                                "confidence": confidence,
                                "target": target,
                            }
            return None

        except Exception as e:
            self.logger.error(f"Error detecting descending triangle: {str(e)}")
            return None

    def _detect_channel(
        self, high_prices, low_prices, close_prices, min_touches=3, threshold=0.05
    ) -> Optional[Dict]:
        """Detect price channels (ascending, descending, or horizontal)"""
        try:
            n = len(high_prices)
            window = min(20, n // 3)

            # Find potential channel by checking multiple segments
            for start in range(0, n - window, window // 2):
                end = start + window

                # Calculate linear regression for high prices
                x = np.array(range(start, end))
                y_high = high_prices[start:end]
                high_slope, high_intercept = np.polyfit(x, y_high, 1)

                # Calculate linear regression for low prices
                y_low = low_prices[start:end]
                low_slope, low_intercept = np.polyfit(x, y_low, 1)

                # Check if slopes are similar
                if (
                    abs(high_slope - low_slope)
                    > 0.001 * abs(high_slope + low_slope) / 2
                ):
                    continue

                # Count how many touches to each line
                upper_touches = 0
                lower_touches = 0

                for i in range(start, end):
                    upper_line = high_intercept + high_slope * i
                    lower_line = low_intercept + low_slope * i

                    # Check upper touches
                    if abs(high_prices[i] - upper_line) / upper_line < threshold:
                        upper_touches += 1

                    # Check lower touches
                    if abs(low_prices[i] - lower_line) / lower_line < threshold:
                        lower_touches += 1

                # Need enough touches on both lines
                if upper_touches >= min_touches and lower_touches >= min_touches:
                    # Determine channel type
                    if high_slope > 0.001:
                        channel_type = "Ascending Channel"
                        bias = "bullish"
                    elif high_slope < -0.001:
                        channel_type = "Descending Channel"
                        bias = "bearish"
                    else:
                        channel_type = "Horizontal Channel"
                        bias = "neutral"

                    # Calculate confidence based on touches and cleanness
                    confidence = min(0.9, 0.5 + (upper_touches + lower_touches) * 0.05)

                    # Estimate breakout target
                    upper_line_end = high_intercept + high_slope * (end - 1)
                    lower_line_end = low_intercept + low_slope * (end - 1)
                    channel_height = upper_line_end - lower_line_end

                    # Target depends on which side we're closer to
                    last_close = close_prices[end - 1]
                    if abs(last_close - upper_line_end) < abs(
                        last_close - lower_line_end
                    ):
                        # Closer to upper line, target is upward breakout
                        target = upper_line_end + channel_height
                    else:
                        # Closer to lower line, target is downward breakout
                        target = lower_line_end - channel_height

                    return {
                        "name": channel_type,
                        "bias": bias,
                        "position": [start, end - 1],
                        "confidence": confidence,
                        "target": target,
                    }
            return None

        except Exception as e:
            self.logger.error(f"Error detecting channel: {str(e)}")
            return None

    def comprehensive_analysis(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        Perform a comprehensive analysis of the given data

        Args:
            symbol: Trading symbol
            data: DataFrame with OHLC data

        Returns:
            Dictionary with comprehensive analysis results
        """
        try:
            # Analyze candlestick patterns
            pattern_analysis = self.analyze_candles(symbol, data)

            # Identify support and resistance levels
            support_resistance = self._identify_support_resistance(data)

            # Detect chart patterns
            chart_patterns = self.detect_chart_patterns(symbol, data)

            # Generate chart with patterns and support/resistance levels
            filename = f"{self.chart_images_dir}/{symbol}_chart.png"
            self._generate_pattern_chart(
                data,
                pattern_analysis["patterns"],
                support_resistance,
                chart_patterns["patterns"],
                filename,
            )

            # Combine results
            results = {
                "symbol": symbol,
                "pattern_analysis": pattern_analysis,
                "support_resistance": support_resistance,
                "chart_patterns": chart_patterns,
                "chart_image": filename,
            }

            return results

        except Exception as e:
            self.logger.error(
                f"Error performing comprehensive analysis for {symbol}: {str(e)}"
            )
            return {"symbol": symbol, "error": str(e)}

    def calculate_technical_indicators(
        self, data: pd.DataFrame
    ) -> Dict[str, np.ndarray]:
        """
        Calculate common technical indicators for the given data

        Args:
            data: DataFrame with OHLC data

        Returns:
            Dictionary of technical indicators
        """
        try:
            # Ensure we have OHLCV data
            if not all(x in data.columns for x in ["open", "high", "low", "close"]):
                raise ValueError("Data must contain OHLC columns")

            # Extract price data
            close_prices = data["close"].values
            high_prices = data["high"].values
            low_prices = data["low"].values
            data["open"].values

            # Dictionary to store indicators
            indicators = {}

            # Calculate moving averages
            indicators["sma_20"] = talib.SMA(close_prices, timeperiod=20)
            indicators["sma_50"] = talib.SMA(close_prices, timeperiod=50)
            indicators["sma_200"] = talib.SMA(close_prices, timeperiod=200)
            indicators["ema_9"] = talib.EMA(close_prices, timeperiod=9)
            indicators["ema_21"] = talib.EMA(close_prices, timeperiod=21)

            # Calculate Bollinger Bands
            indicators["bb_upper"], indicators["bb_middle"], indicators["bb_lower"] = (
                talib.BBANDS(
                    close_prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
                )
            )

            # Calculate RSI (Relative Strength Index)
            indicators["rsi_14"] = talib.RSI(close_prices, timeperiod=14)

            # Calculate MACD (Moving Average Convergence Divergence)
            indicators["macd"], indicators["macd_signal"], indicators["macd_hist"] = (
                talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
            )

            # Calculate Stochastic Oscillator
            indicators["slowk"], indicators["slowd"] = talib.STOCH(
                high_prices,
                low_prices,
                close_prices,
                fastk_period=5,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=3,
                slowd_matype=0,
            )

            # Calculate ADX (Average Directional Index)
            indicators["adx"] = talib.ADX(
                high_prices, low_prices, close_prices, timeperiod=14
            )

            # Calculate ATR (Average True Range)
            indicators["atr"] = talib.ATR(
                high_prices, low_prices, close_prices, timeperiod=14
            )

            # Calculate OBV (On Balance Volume)
            if "volume" in data.columns:
                indicators["obv"] = talib.OBV(close_prices, data["volume"].values)

            # Calculate Ichimoku Cloud
            indicators["tenkan_sen"] = self._calculate_ichimoku_tenkan_sen(
                high_prices, low_prices
            )
            indicators["kijun_sen"] = self._calculate_ichimoku_kijun_sen(
                high_prices, low_prices
            )
            indicators["senkou_span_a"] = self._calculate_ichimoku_senkou_span_a(
                indicators["tenkan_sen"], indicators["kijun_sen"]
            )
            indicators["senkou_span_b"] = self._calculate_ichimoku_senkou_span_b(
                high_prices, low_prices
            )
            indicators["chikou_span"] = np.append(
                np.array([np.nan] * 26), close_prices[:-26]
            )

            return indicators

        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}

    def _calculate_ichimoku_tenkan_sen(self, high_prices, low_prices, period=9):
        """Calculate Tenkan-sen (Conversion Line) for Ichimoku Cloud"""
        tenkan_sen = np.zeros_like(high_prices)
        for i in range(period - 1, len(high_prices)):
            period_high = high_prices[i - period + 1 : i + 1].max()
            period_low = low_prices[i - period + 1 : i + 1].min()
            tenkan_sen[i] = (period_high + period_low) / 2
        return tenkan_sen

    def _calculate_ichimoku_kijun_sen(self, high_prices, low_prices, period=26):
        """Calculate Kijun-sen (Base Line) for Ichimoku Cloud"""
        kijun_sen = np.zeros_like(high_prices)
        for i in range(period - 1, len(high_prices)):
            period_high = high_prices[i - period + 1 : i + 1].max()
            period_low = low_prices[i - period + 1 : i + 1].min()
            kijun_sen[i] = (period_high + period_low) / 2
        return kijun_sen

    def _calculate_ichimoku_senkou_span_a(self, tenkan_sen, kijun_sen):
        """Calculate Senkou Span A (Leading Span A) for Ichimoku Cloud"""
        return (tenkan_sen + kijun_sen) / 2

    def _calculate_ichimoku_senkou_span_b(self, high_prices, low_prices, period=52):
        """Calculate Senkou Span B (Leading Span B) for Ichimoku Cloud"""
        senkou_span_b = np.zeros_like(high_prices)
        for i in range(period - 1, len(high_prices)):
            period_high = high_prices[i - period + 1 : i + 1].max()
            period_low = low_prices[i - period + 1 : i + 1].min()
            senkou_span_b[i] = (period_high + period_low) / 2
        return senkou_span_b

    def analyze_market(
        self,
        symbol: str,
        data: pd.DataFrame,
        timeframe: str = "daily",
        save_chart: bool = True,
    ) -> Dict:
        """
        Perform a comprehensive market analysis using all available tools

        Args:
            symbol: Trading symbol
            data: DataFrame with OHLC data
            timeframe: Timeframe of the data (e.g., "daily", "hourly")
            save_chart: Whether to save the chart image

        Returns:
            Dictionary with comprehensive analysis results and trading signals
        """
        try:
            self.logger.info(
                f"Performing comprehensive market analysis for {symbol} on {timeframe} timeframe"
            )

            # Calculate technical indicators
            indicators = self.calculate_technical_indicators(data)

            # Analyze candlestick patterns
            pattern_analysis = self.analyze_candles(symbol, data)

            # Identify support and resistance levels
            support_resistance = self._identify_support_resistance(data)

            # Detect chart patterns
            chart_patterns = self.detect_chart_patterns(symbol, data)

            # Analyze trend
            trend_analysis = self.analyze_trend(symbol, data)

            # Generate chart if requested
            chart_path = None
            if save_chart:
                filename = os.path.join(
                    self.chart_images_dir,
                    f"{symbol.replace('/', '_')}_{timeframe}_chart.png",
                )
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                chart_path = self._generate_pattern_chart(
                    data,
                    self.patterns.get(symbol, []),
                    support_resistance,
                    chart_patterns.get("patterns", []),
                    filename,
                )

            # Determine overall market bias
            bullish_signals = 0
            bearish_signals = 0
            neutral_signals = 0

            # Count candlestick pattern signals
            if pattern_analysis.get("sentiment") == "bullish":
                bullish_signals += 1
            elif pattern_analysis.get("sentiment") == "bearish":
                bearish_signals += 1
            else:
                neutral_signals += 1

            # Count chart pattern signals
            if chart_patterns.get("overall_bias") == "bullish":
                bullish_signals += 1
            elif chart_patterns.get("overall_bias") == "bearish":
                bearish_signals += 1
            else:
                neutral_signals += 1

            # Count trend signals
            if trend_analysis.get("trend") == "uptrend":
                bullish_signals += 1
            elif trend_analysis.get("trend") == "downtrend":
                bearish_signals += 1
            else:
                neutral_signals += 1

            # Technical indicators analysis
            # Check for bullish/bearish crossovers in moving averages
            if (
                indicators.get("sma_20", np.array([]))[-1]
                > indicators.get("sma_50", np.array([]))[-1]
                and indicators.get("sma_20", np.array([]))[-2]
                <= indicators.get("sma_50", np.array([]))[-2]
            ):
                bullish_signals += 1
            elif (
                indicators.get("sma_20", np.array([]))[-1]
                < indicators.get("sma_50", np.array([]))[-1]
                and indicators.get("sma_20", np.array([]))[-2]
                >= indicators.get("sma_50", np.array([]))[-2]
            ):
                bearish_signals += 1

            # Check RSI
            last_rsi = indicators.get("rsi_14", np.array([]))[-1]
            if not np.isnan(last_rsi):
                if last_rsi > 70:
                    bearish_signals += 1
                elif last_rsi < 30:
                    bullish_signals += 1

            # Check MACD
            last_macd = indicators.get("macd", np.array([]))[-1]
            last_macd_signal = indicators.get("macd_signal", np.array([]))[-1]
            if not np.isnan(last_macd) and not np.isnan(last_macd_signal):
                if last_macd > last_macd_signal:
                    bullish_signals += 1
                elif last_macd < last_macd_signal:
                    bearish_signals += 1

            # Determine overall bias
            total_signals = bullish_signals + bearish_signals + neutral_signals
            if total_signals > 0:
                if bullish_signals > bearish_signals:
                    overall_bias = "bullish"
                    confidence = bullish_signals / total_signals
                elif bearish_signals > bullish_signals:
                    overall_bias = "bearish"
                    confidence = bearish_signals / total_signals
                else:
                    overall_bias = "neutral"
                    confidence = neutral_signals / total_signals
            else:
                overall_bias = "neutral"
                confidence = 0.5

            # Generate trading signals
            trading_signal = "hold"  # Default signal

            if overall_bias == "bullish" and confidence > 0.6:
                trading_signal = "buy"
            elif overall_bias == "bearish" and confidence > 0.6:
                trading_signal = "sell"

            # Check for strong reversal patterns that might override the bias
            for pattern in pattern_analysis.get("patterns", []):
                if (
                    pattern.get("name")
                    in ["Hammer", "Morning Star", "Bullish Engulfing"]
                    and pattern.get("strength", 0) > 0.7
                ):
                    trading_signal = "buy"
                    break
                elif (
                    pattern.get("name")
                    in ["Shooting Star", "Evening Star", "Bearish Engulfing"]
                    and pattern.get("strength", 0) > 0.7
                ):
                    trading_signal = "sell"
                    break

            # Compile final result
            result = {
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat(),
                "chart_path": chart_path,
                "candlestick_patterns": pattern_analysis,
                "chart_patterns": chart_patterns,
                "support_resistance": [vars(level) for level in support_resistance],
                "trend_analysis": trend_analysis,
                "technical_indicators": {
                    "last_price": data["close"].iloc[-1] if len(data) > 0 else None,
                    "rsi": float(last_rsi) if not np.isnan(last_rsi) else None,
                    "macd": {
                        "value": float(last_macd) if not np.isnan(last_macd) else None,
                        "signal": (
                            float(last_macd_signal)
                            if not np.isnan(last_macd_signal)
                            else None
                        ),
                        "histogram": (
                            float(indicators.get("macd_hist", np.array([]))[-1])
                            if len(indicators.get("macd_hist", np.array([]))) > 0
                            and not np.isnan(
                                indicators.get("macd_hist", np.array([]))[-1]
                            )
                            else None
                        ),
                    },
                    "moving_averages": {
                        "sma_20": (
                            float(indicators.get("sma_20", np.array([]))[-1])
                            if len(indicators.get("sma_20", np.array([]))) > 0
                            and not np.isnan(indicators.get("sma_20", np.array([]))[-1])
                            else None
                        ),
                        "sma_50": (
                            float(indicators.get("sma_50", np.array([]))[-1])
                            if len(indicators.get("sma_50", np.array([]))) > 0
                            and not np.isnan(indicators.get("sma_50", np.array([]))[-1])
                            else None
                        ),
                        "sma_200": (
                            float(indicators.get("sma_200", np.array([]))[-1])
                            if len(indicators.get("sma_200", np.array([]))) > 0
                            and not np.isnan(
                                indicators.get("sma_200", np.array([]))[-1]
                            )
                            else None
                        ),
                    },
                },
                "market_summary": {
                    "overall_bias": overall_bias,
                    "confidence": confidence,
                    "trading_signal": trading_signal,
                    "key_levels": {
                        "nearest_support": (
                            min(
                                [
                                    level.price
                                    for level in support_resistance
                                    if level.type == "support"
                                ]
                                or [0],
                                key=lambda x: abs(x - data["close"].iloc[-1]),
                            )
                            if len(data) > 0
                            else None
                        ),
                        "nearest_resistance": (
                            min(
                                [
                                    level.price
                                    for level in support_resistance
                                    if level.type == "resistance"
                                ]
                                or [float("inf")],
                                key=lambda x: abs(x - data["close"].iloc[-1]),
                            )
                            if len(data) > 0
                            else None
                        ),
                    },
                },
            }

            return result

        except Exception as e:
            self.logger.error(
                f"Error in comprehensive market analysis for {symbol}: {str(e)}"
            )
            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "trading_signal": "hold",  # Default to hold on error
            }
