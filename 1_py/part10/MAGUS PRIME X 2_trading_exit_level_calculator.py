"""
Exit level calculator for MAGUS PRIME X trading bot.

This module handles the calculation of exit levels (take profit and stop loss)
using both standard calculations and support/resistance levels.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union


class ExitLevelCalculator:
    """Calculator for determining appropriate exit levels for trades."""

    @staticmethod
    def calculate_exit_levels(action: str, current_price: float) -> Tuple[float, float]:
        """Calculate standard exit levels based on the action and current price.

        Args:
            action: Trading action ('BUY' or 'SELL')
            current_price: Current market price

        Returns:
            tuple: (take_profit, stop_loss)
        """
        if action == "BUY":
            take_profit = current_price * 1.02  # 2% profit target
            stop_loss = current_price * 0.985  # 1.5% stop loss
        elif action == "SELL":
            take_profit = current_price * 0.98  # 2% profit target
            stop_loss = current_price * 1.015  # 1.5% stop loss
        else:
            return 0, 0

        return round(take_profit, 5), round(stop_loss, 5)

    @staticmethod
    def convert_levels_to_float(levels: List[Union[str, float]]) -> List[float]:
        """Convert level values to float if they're strings.

        Args:
            levels: List of level values that might be strings or floats

        Returns:
            list: Converted float values
        """
        result = []
        for level in levels:
            try:
                result.append(float(level))
            except (ValueError, TypeError):
                logging.warning(f"Invalid level value: {level}")
        return result

    @staticmethod
    def find_higher_levels(price: float, levels: List[float]) -> List[float]:
        """Find all levels above a given price.

        Args:
            price: Reference price
            levels: List of level values

        Returns:
            list: Levels above the price
        """
        return [level for level in levels if level > price]

    @staticmethod
    def find_lower_levels(price: float, levels: List[float]) -> List[float]:
        """Find all levels below a given price.

        Args:
            price: Reference price
            levels: List of level values

        Returns:
            list: Levels below the price
        """
        return [level for level in levels if level < price]

    @classmethod
    def find_nearest_level(
        cls, price: float, levels: List[Union[str, float]], above: bool
    ) -> Optional[float]:
        """Find the nearest support/resistance level.

        Args:
            price: Current price
            levels: List of support or resistance levels
            above: Whether to find the nearest level above (True) or below (False)

        Returns:
            float: Nearest level or None if no suitable level found
        """
        if not levels:
            return None

        # Convert levels to float if they're strings
        float_levels = cls.convert_levels_to_float(levels)

        # Find appropriate levels based on direction
        filtered_levels = (
            cls.find_higher_levels(price, float_levels)
            if above
            else cls.find_lower_levels(price, float_levels)
        )

        # Return the closest level if any found
        if filtered_levels:
            return min(filtered_levels) if above else max(filtered_levels)

        return None

    @classmethod
    def calculate_sr_exit_levels(
        cls, params: ExitLevelParameters
    ) -> Tuple[float, float]:
        """Calculate exit levels using support/resistance if available.

        Args:
            params: Exit level calculation parameters

        Returns:
            tuple: (take_profit, stop_loss)
        """
        # Default to standard calculation if no support/resistance or no action
        if params.action not in ("BUY", "SELL") or not params.support_resistance:
            return cls.calculate_exit_levels(params.action, params.current_price)

        # Extract support and resistance levels
        resistance_levels = cls._get_resistance_levels(params.support_resistance)
        support_levels = cls._get_support_levels(params.support_resistance)

        # Find appropriate exit levels based on action
        take_profit, stop_loss = cls._get_action_based_levels(
            params.action, params.current_price, support_levels, resistance_levels
        )

        # Return found levels or fall back to standard calculation
        if take_profit and stop_loss:
            return take_profit, stop_loss

        # Fallback to standard calculation
        return cls.calculate_exit_levels(params.action, params.current_price)

    @classmethod
    def _get_resistance_levels(
        cls, support_resistance: Dict[str, List[Union[str, float]]]
    ) -> List[float]:
        """Extract and convert resistance levels.

        Args:
            support_resistance: Support/resistance data

        Returns:
            list: Resistance levels as floats
        """
        resistance_levels = support_resistance.get("resistance", [])
        return cls.convert_levels_to_float(resistance_levels)

    @classmethod
    def _get_support_levels(
        cls, support_resistance: Dict[str, List[Union[str, float]]]
    ) -> List[float]:
        """Extract and convert support levels.

        Args:
            support_resistance: Support/resistance data

        Returns:
            list: Support levels as floats
        """
        support_levels = support_resistance.get("support", [])
        return cls.convert_levels_to_float(support_levels)

    @classmethod
    def _get_action_based_levels(
        cls, action, current_price, support_levels, resistance_levels
    ):
        """Get appropriate exit levels based on action type.

        Args:
            action: Trading action (BUY/SELL)
            current_price: Current market price
            support_levels: List of support levels
            resistance_levels: List of resistance levels

        Returns:
            tuple: (take_profit, stop_loss) or (None, None) if not found
        """
        if action == "BUY":
            # For buy: take profit is nearest resistance above, stop loss is nearest support below
            take_profit = cls.find_nearest_level(
                current_price, resistance_levels, above=True
            )
            stop_loss = cls.find_nearest_level(
                current_price, support_levels, above=False
            )

        elif action == "SELL":
            # For sell: take profit is nearest support below, stop loss is nearest resistance above
            take_profit = cls.find_nearest_level(
                current_price, support_levels, above=False
            )
            stop_loss = cls.find_nearest_level(
                current_price, resistance_levels, above=True
            )

        else:
            return None, None

        return take_profit, stop_loss
