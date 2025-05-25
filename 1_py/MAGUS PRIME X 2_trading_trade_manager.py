"""
Trade management module for MAGUS PRIME X trading bot.

This module handles opening, monitoring, and closing trades based on
strategy signals and risk management rules.
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable, Dict, Optional, Tuple

# Import the exit level calculator
from trading.exit_level_calculator import ExitLevelCalculator
from trading.trade_params import TradeExecutionParameters, TradeParameters


class TradeManager:
    """Manages all trade operations for the trading bot."""

    def __init__(
        self,
        api_client,
        telegram_sender: Optional[Callable] = None,
        risk_percent: float = 1.0,
        max_active_trades: int = 3,
    ):
        """Initialize the trade manager.

        Args:
            api_client: The API client for executing trades
            telegram_sender: Function to send Telegram notifications
            risk_percent: Percentage of account to risk per trade
            max_active_trades: Maximum number of concurrent open trades
        """
        self.api_client = api_client
        self.telegram_sender = telegram_sender
        self.risk_percent = risk_percent
        self.max_active_trades = max_active_trades

        # State tracking
        self.active_trades = {}
        self.last_trade_outcome = None

        # Initialize exit level calculator
        self.exit_calculator = ExitLevelCalculator()

    def open_trade(self, params: TradeParameters) -> bool:
        """Open a new trade based on a trading signal.

        Args:
            params: Trading parameters containing symbol, action, take_profit,
                   stop_loss, confidence, and source

        Returns:
            bool: True if trade was opened successfully
        """
        # Extract parameters for readability
        symbol = params.symbol
        action = params.action
        take_profit = params.take_profit
        stop_loss = params.stop_loss
        source = params.source
        risk_percent = params.risk_percent or self.risk_percent

        # Validate preconditions
        if not self._validate_trade_preconditions(symbol, action):
            return False

        # Get prerequisites: account info and current price
        account_info, current_price = self._get_trade_prerequisites(symbol)
        if not account_info or not current_price:
            return False

        # Prepare exit levels
        take_profit, stop_loss = self._prepare_exit_levels(
            action, current_price, take_profit, stop_loss
        )

        # Calculate position size
        position_size = self._calculate_position_size(
            account_info, action, current_price, stop_loss, risk_percent
        )
        if position_size <= 0:
            logging.error(f"Invalid position size calculated: {position_size}")
            return False

        # Prepare trade execution parameters
        execution_params = TradeExecutionParameters(
            symbol=symbol,
            action=action,
            position_size=position_size,
            take_profit=take_profit,
            stop_loss=stop_loss,
            current_price=current_price,
            source=source,
        )

        # Execute the trade and track it
        return self._execute_and_track_trade(execution_params)

    def _validate_trade_preconditions(self, symbol: str, action: str) -> bool:
        """Check if trade preconditions are met.

        Args:
            symbol: Market symbol to trade
            action: Trading action (BUY/SELL)

        Returns:
            bool: True if preconditions are met
        """
        if len(self.active_trades) >= self.max_active_trades:
            logging.info(
                f" "
Maximum active trades reached ({self.max + "_active_trades}). Skipping {symbol} {act + "ion}"
            )
            return False

        if symbol in self.active_trades:
            logging.info(f"Already have an active trade for {symbol}. Skipping.")
            return False

        return True

    def _get_trade_prerequisites(
        self, symbol: str
    ) -> Tuple[Optional[Dict], Optional[float]]:
        """Get account info and current price needed for trade.

        Args:
            symbol: Market symbol to trade

        Returns:
            tuple: (account_info, current_price) or (None, None) if error
        """
        # Get account info
        account_info = self.api_client.get_account_info()
        if not account_info or "balance" not in account_info:
            logging.error("Failed to get account info for position sizing")
            return None, None

        # Get current price
        current_price = self.api_client.get_current_price(symbol)
        if not current_price:
            logging.error(f"Failed to get current price for {symbol}")
            return None, None

        return account_info, current_price

    def _prepare_exit_levels(
        self,
        action: str,
        current_price: float,
        take_profit: Optional[float],
        stop_loss: Optional[float],
    ) -> Tuple[float, float]:
        """Prepare take profit and stop loss levels.

        Args:
            action: Trading action (BUY/SELL)
            current_price: Current market price
            take_profit: Provided take profit level (if any)
            stop_loss: Provided stop loss level (if any)

        Returns:
            tuple: (take_profit, stop_loss)
        """
        # Use provided levels if available, otherwise calculate
        if take_profit is None or stop_loss is None:
            calculated_tp, calculated_sl = self.exit_calculator.calculate_exit_levels(
                action, current_price
            )
            take_profit = take_profit or calculated_tp
            stop_loss = stop_loss or calculated_sl

        return take_profit, stop_loss

    def _calculate_position_size(
        self,
        account_info: Dict,
        action: str,
        current_price: float,
        stop_loss: float,
        risk_percent: float = None,
    ) -> float:
        """Calculate position size based on risk parameters.

        Args:
            account_info: Account information
            action: Trading action (BUY/SELL)
            current_price: Current market price
            stop_loss: Stop loss level
            risk_percent: Percentage of account to risk (overrides default)

        Returns:
            float: Position size or 0 if error
        """
        try:
            # Use provided risk percent or default
            risk_percent_to_use = risk_percent or self.risk_percent

            # Get account balance
            balance = float(account_info.get("balance", 0))
            if balance <= 0:
                logging.error("Invalid account balance")
                return 0

            # Calculate risk amount
            risk_amount = balance * (risk_percent_to_use / 100)

            # Calculate price distance to stop loss
            if action == "BUY":
                price_distance = abs(current_price - stop_loss)
            else:  # SELL
                price_distance = abs(stop_loss - current_price)

            # Calculate position size based on risk
            if price_distance > 0:
                position_size = risk_amount / price_distance
            else:
                logging.error("Stop loss is at the same level as current price")
                return 0

            # Apply minimum position size rules (example: 0.01)
            min_position = 0.01
            if position_size < min_position:
                position_size = min_position

            return position_size

        except Exception as e:
            logging.error(f"Error calculating position size: {e}")
            return 0

    def _execute_and_track_trade(self, params: TradeExecutionParameters) -> bool:
        """Execute trade and track it if successful.

        Args:
            params: Trade execution parameters

        Returns:
            bool: True if successful
        """
        # Execute the trade
        trade_result = self.api_client.open_position(
            symbol=params.symbol,
            direction=params.action,
            size=params.position_size,
            take_profit=params.take_profit,
            stop_loss=params.stop_loss,
        )

        if not trade_result or "dealId" not in trade_result:
            logging.error(f"Failed to open position for {params.symbol}")
            return False

        # Track the new trade
        self._track_new_trade(params, trade_result["dealId"])

        # Log success
        logging.info(
            f"Successfully opened {params.action} position for {params.symbol}"
        )

        return True

    def _track_new_trade(self, params: TradeExecutionParameters, deal_id: str) -> None:
        """Add a new trade to the active trades tracking.

        Args:
            params: Trade execution parameters
            deal_id: Deal ID from the broker
        """
        self.active_trades[params.symbol] = {
            "id": deal_id,
            "symbol": params.symbol,
            "action": params.action,
            "entry_price": params.current_price,
            "take_profit": params.take_profit,
            "stop_loss": params.stop_loss,
            "size": params.position_size,
            "open_time": datetime.now().isoformat(),
            "source": params.source,
        }

        # Send notification
        trade_message = (
            f"🟢 New {params.action} Trade: {params.symbol}\n"
            f"Entry: {params.current_price}\n"
            f"TP: {params.take_profit}\n"
            f"SL: {params.stop_loss}\n"
            f"Confidence: {params.confidence:.2f}"
        )

        if self.telegram_sender:
            asyncio.run(self.telegram_sender(trade_message))

    def close_trade(self, symbol: str, reason: str = "Manual") -> bool:
        """Close an active trade for a given symbol.

        Args:
            symbol: Market symbol to close the trade for
            reason: Reason for closing the trade

        Returns:
            bool: True if the trade was closed successfully
        """
        if symbol not in self.active_trades:
            logging.warning(f"No active trade found for {symbol}")
            return False

        try:
            # Get the trade details
            trade = self.active_trades[symbol]

            # Close the position
            result = self.api_client.close_position(trade["id"])

            if not result or not result.get("success"):
                logging.error(f"Failed to close position for {symbol}")
                return False

            # Calculate profit/loss
            close_price = result.get("close_price", 0)
            entry_price = trade["entry_price"]

            if trade["action"] == "BUY":
                pnl_percent = ((close_price / entry_price) - 1) * 100
            else:  # SELL
                pnl_percent = ((entry_price / close_price) - 1) * 100

            # Determine if this was a win or loss
            outcome = "WIN" if pnl_percent > 0 else "LOSS"

            # Save the outcome for reference
            self.last_trade_outcome = {
                "symbol": symbol,
                "action": trade["action"],
                "result": outcome,
                "pnl_percent": pnl_percent,
                "reason": reason,
                "close_time": datetime.now().isoformat(),
            }

            # Send notification
            close_message = (
                f"🔴 Closed {symbol} {trade['action']} Trade\n"
                f"Result: {outcome}\n"
                f"P/L: {pnl_percent:.2f}%\n"
                f"Reason: {reason}"
            )

            if self.telegram_sender:
                asyncio.run(self.telegram_sender(close_message))

            # Remove from active trades
            del self.active_trades[symbol]

            logging.info(
                f"Closed {symbol} trade: {outcome}, {pnl_percent:.2f}%, {reason}"
            )
            return True

        except Exception as e:
            logging.error(f"Error closing trade for {symbol}: {e}")
            return False

    def update_active_trades(self) -> None:
        """Update status of all active trades."""
        if not self.active_trades:
            return

        try:
            # Get current positions from API
            positions = self.api_client.get_open_positions()

            # Create a set of symbols with API-confirmed open positions
            open_position_symbols = {p["symbol"] for p in positions if "symbol" in p}

            # Find trades in our tracking that are no longer open in the API
            closed_trades = [
                symbol
                for symbol in self.active_trades
                if symbol not in open_position_symbols
            ]

            # Update our tracking for trades closed externally
            for symbol in closed_trades:
                logging.info(f"Trade for {symbol} was closed externally")

                # Create a record of the externally closed trade
                self.last_trade_outcome = {
                    "symbol": symbol,
                    "action": self.active_trades[symbol]["action"],
                    "result": "UNKNOWN",  # We don't know the outcome
                    "pnl_percent": 0,  # We don't know the P/L
                    "reason": "External",  # Closed outside our system
                    "close_time": datetime.now().isoformat(),
                }

                # Remove from active trades
                del self.active_trades[symbol]

            # Update trade details for still-open positions
            for position in positions:
                symbol = position.get("symbol")
                if symbol in self.active_trades:
                    # Update with latest data from API
                    self.active_trades[symbol].update(
                        {
                            "current_price": position.get("current_price", 0),
                            "profit_loss": position.get("profit_loss", 0),
                            "pnl_percent": position.get("pnl_percent", 0),
                        }
                    )

        except Exception as e:
            logging.error(f"Error updating active trades: {e}")

    def close_all_trades(self, reason: str = "System") -> int:
        """Close all active trades.

        Args:
            reason: Reason for closing all trades

        Returns:
            int: Number of trades closed successfully
        """
        if not self.active_trades:
            return 0

        closed_count = 0
        symbols = list(self.active_trades.keys())

        for symbol in symbols:
            if self.close_trade(symbol, reason):
                closed_count += 1

        return closed_count
