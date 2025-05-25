"""
Risk management module for MAGUS PRIME X trading bot.

This module handles risk calculations, position sizing, and risk adjustment
based on market conditions and trading performance.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List


class RiskManager:
    """Manages risk-related calculations for the trading bot."""

    def __init__(
        self,
        default_risk_percent: float = 1.0,
        max_daily_risk: float = 5.0,
        max_drawdown_limit: float = 10.0,
    ):
        """Initialize the risk manager.

        Args:
            default_risk_percent: Default percentage of account to risk per trade
            max_daily_risk: Maximum percentage of account to risk per day
            max_drawdown_limit: Maximum drawdown percentage before reducing risk
        """
        self.default_risk_percent = default_risk_percent
        self.max_daily_risk = max_daily_risk
        self.max_drawdown_limit = max_drawdown_limit

        # Trade history tracking
        self.trades_today = []
        self.last_trades = []  # Keep track of last 20 trades
        self.daily_risk_used = 0.0
        self.last_reset_date = datetime.now().date()

    def calculate_position_size(
        self, account_balance: float, risk_amount: float, stop_distance: float
    ) -> float:
        """Calculate position size based on risk parameters.

        Args:
            account_balance: Current account balance
            risk_amount: Amount to risk in account currency
            stop_distance: Distance to stop loss in price terms

        Returns:
            float: Position size to use for the trade
        """
        if stop_distance <= 0:
            logging.error(f"Invalid stop distance: {stop_distance}")
            return 0

        # Basic position sizing formula: Risk Amount / Stop Distance
        position_size = risk_amount / stop_distance

        # Ensure position size is reasonable and not zero
        if position_size <= 0:
            logging.warning(
                "Calculated position size was zero or negative, using minimum"
            )
            position_size = 0.01  # Minimum position size

        return position_size

    def calculate_trade_risk(
        self, confidence: float, consecutive_losses: int = 0
    ) -> float:
        """Calculate risk percentage for a trade based on confidence and history.

        Args:
            confidence: Signal confidence (0-1)
            consecutive_losses: Number of consecutive losing trades

        Returns:
            float: Adjusted risk percentage for this trade
        """
        # Start with default risk
        adjusted_risk = self.default_risk_percent

        # Adjust based on signal confidence
        if confidence >= 0.8:
            # High confidence signal - can use full risk
            confidence_factor = 1.0
        elif confidence >= 0.6:
            # Medium confidence - reduce risk slightly
            confidence_factor = 0.8
        else:
            # Lower confidence - reduce risk more
            confidence_factor = 0.5

        adjusted_risk *= confidence_factor

        # Adjust for consecutive losses (martingale-like approach)
        if consecutive_losses == 0:
            # No recent losses, use standard risk
            pass
        elif consecutive_losses == 1:
            # One recent loss, reduce risk
            adjusted_risk *= 0.7
        else:
            # Multiple consecutive losses, reduce risk significantly
            adjusted_risk *= 0.5

        # Ensure we don't exceed daily risk limit
        if self.daily_risk_used + adjusted_risk > self.max_daily_risk:
            remaining_risk = max(0, self.max_daily_risk - self.daily_risk_used)
            logging.warning(
                f" "
Daily risk limit nearly reached. Adjusti + "ng risk from {adjusted_risk}% to {remain + "ing_risk}%"
            )
            adjusted_risk = remaining_risk

        return adjusted_risk

    def update_trade_history(self, trade_result: Dict[str, Any]) -> None:
        """Update trade history with a new trade result.

        Args:
            trade_result: Dictionary with trade outcome details
        """
        # Reset daily counters if it's a new day
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.trades_today = []
            self.daily_risk_used = 0.0
            self.last_reset_date = current_date

        # Add to today's trades
        self.trades_today.append(trade_result)

        # Update daily risk used
        self.daily_risk_used += trade_result.get("risk_percent", 0)

        # Update recent trades list (keep last 20)
        self.last_trades.append(trade_result)
        if len(self.last_trades) > 20:
            self.last_trades.pop(0)

    def get_consecutive_losses(self) -> int:
        """Get the number of consecutive losing trades.

        Returns:
            int: Number of consecutive losses
        """
        count = 0

        # Iterate through recent trades in reverse (newest first)
        for trade in reversed(self.last_trades):
            if trade.get("result") == "LOSS":
                count += 1
            else:
                # Streak broken by a win
                break

        return count

    def get_win_rate(self) -> float:
        """Calculate the current win rate based on recent trades.

        Returns:
            float: Win rate as percentage (0-100)
        """
        if not self.last_trades:
            return 0

        wins = sum(1 for trade in self.last_trades if trade.get("result") == "WIN")
        return (wins / len(self.last_trades)) * 100

    def calculate_drawdown(self, balance_history: List[float]) -> float:
        """Calculate the current drawdown percentage.

        Args:
            balance_history: List of account balance values

        Returns:
            float: Current drawdown as percentage
        """
        if not balance_history:
            return 0

        peak = max(balance_history)
        current = balance_history[-1]

        if peak == 0:
            return 0

        drawdown = ((peak - current) / peak) * 100
        return drawdown

    def should_stop_trading(self, drawdown: float) -> bool:
        """Determine if trading should be paused based on risk metrics.

        Args:
            drawdown: Current drawdown percentage

        Returns:
            bool: True if trading should be paused
        """
        # Stop if drawdown exceeds limit
        if drawdown >= self.max_drawdown_limit:
            logging.warning(
                f"Maximum drawdown limit reached: {drawdown:.2f}% >= {self.max_drawdown_limit}%"
            )
            return True

        # Stop if daily risk is exhausted
        if self.daily_risk_used >= self.max_daily_risk:
            logging.warning(
                f"Daily risk limit reached: {self.daily_risk_used:.2f}% >= {self.max_daily_risk}%"
            )
            return True

        # Continue trading
        return False
