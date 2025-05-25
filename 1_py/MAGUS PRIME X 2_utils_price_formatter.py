"""
Price data formatting utilities for MAGUS PRIME X trading bot.

This module handles conversion and formatting of price data between
different formats required by various components of the system.
"""

import logging
from typing import Any, Dict, List


class PriceFormatter:
    """Utility class for formatting price data."""

    @staticmethod
    def format_prices_for_chart_analyzer(
        prices: List[Dict[str, Any]],
    ) -> Dict[str, List]:
        """Format price data for the Chart Analyzer module.

        Args:
            prices: Raw price data from API

        Returns:
            dict: Formatted price data for the Chart Analyzer
        """
        try:
            # Convert the prices to the format expected by Chart Analyzer
            formatted_data = {
                "timestamp": [],
                "open": [],
                "high": [],
                "low": [],
                "close": [],
                "volume": [],
            }

            for price in prices:
                if all(
                    k in price
                    for k in [
                        "snapshotTime",
                        "openPrice",
                        "highPrice",
                        "lowPrice",
                        "closePrice",
                    ]
                ):
                    formatted_data["timestamp"].append(price["snapshotTime"])
                    formatted_data["open"].append(float(price["openPrice"]))
                    formatted_data["high"].append(float(price["highPrice"]))
                    formatted_data["low"].append(float(price["lowPrice"]))
                    formatted_data["close"].append(float(price["closePrice"]))
                    formatted_data["volume"].append(float(price.get("volume", 0)))

            return formatted_data

        except Exception as e:
            logging.error(f"Error formatting prices for chart analyzer: {e}")
            return {}

    @staticmethod
    def format_prices_for_fallback_analysis(
        prices: List[Dict[str, Any]],
    ) -> Dict[str, List]:
        """Format price data for the fallback analysis.

        Args:
            prices: Raw price data from API

        Returns:
            dict: Formatted price data for fallback analysis
        """
        try:
            # Extract just the closing prices for simpler analysis
            close_prices = [
                float(price["closePrice"]) for price in prices if "closePrice" in price
            ]

            # High and low prices for range calculation
            high_prices = [
                float(price["highPrice"]) for price in prices if "highPrice" in price
            ]

            low_prices = [
                float(price["lowPrice"]) for price in prices if "lowPrice" in price
            ]

            return {"close": close_prices, "high": high_prices, "low": low_prices}

        except Exception as e:
            logging.error(f"Error formatting prices for fallback analysis: {e}")
            return {"close": [], "high": [], "low": []}
