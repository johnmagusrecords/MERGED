"""
Notification module for MAGUS PRIME X trading bot.

This module handles sending notifications via Telegram and other channels.
"""

import asyncio
import logging
from typing import Optional

import telegram

from trading.trade_params import NotificationParameters


class Notifier:
    """Handles notifications for the trading bot."""

    def __init__(
        self,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
    ):
        """Initialize the notifier.

        Args:
            telegram_token: Telegram bot token
            telegram_chat_id: Telegram chat ID
        """
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_bot = None

        # Initialize Telegram bot if credentials are provided
        if self.telegram_token and self.telegram_chat_id:
            try:
                self.telegram_bot = telegram.Bot(token=self.telegram_token)
                logging.info("Telegram bot initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Telegram bot: {e}")
                self.telegram_bot = None

    async def send_telegram_message(self, message: str) -> bool:
        """Send a message to Telegram.

        Args:
            message: Message to send

        Returns:
            bool: True if message was sent successfully
        """
        if not self.telegram_bot or not self.telegram_chat_id:
            logging.warning("Telegram not configured, skipping notification")
            return False

        try:
            await self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            return True
        except Exception as e:
            logging.error(f"Failed to send Telegram message: {e}")
            return False

    def send_telegram_message_sync(self, message: str) -> bool:
        """Send a Telegram message synchronously.

        Args:
            message: Message to send

        Returns:
            bool: True if message was sent successfully
        """
        return asyncio.run(self.send_telegram_message(message))

    def send_notification(self, message: str, notification_type: str = "info") -> bool:
        """Send a notification via all available channels.

        Args:
            message: Message to send
            notification_type: Type of notification (info, warning, error)

        Returns:
            bool: True if notification was sent successfully via any channel
        """
        # Log the message
        if notification_type == "warning":
            logging.warning(message)
        elif notification_type == "error":
            logging.error(message)
        else:
            logging.info(message)

        # Send via Telegram if available
        telegram_success = False
        if self.telegram_bot:
            telegram_success = self.send_telegram_message_sync(message)

        # Add other notification channels here as needed

        return telegram_success

    def send_trade_notification(self, params: NotificationParameters) -> bool:
        """Send a trade notification.

        Args:
            params: Trade notification parameters

        Returns:
            bool: True if notification was sent successfully
        """
        emoji = "🟢" if params.action == "BUY" else "🔴"
        message = (
            f"{emoji} New {params.action} Trade: {params.symbol}\n"
            f"Entry: {params.entry_price:.5f}\n"
            f"TP: {params.take_profit:.5f}\n"
            f"SL: {params.stop_loss:.5f}\n"
            f"Confidence: {params.confidence:.2f}"
        )

        return self.send_notification(message)

    def send_trade_closed_notification(
        self, symbol: str, action: str, profit_loss: float, reason: str
    ) -> bool:
        """Send a trade closed notification.

        Args:
            symbol: Market symbol
            action: Trading action (BUY/SELL)
            profit_loss: Profit/loss percentage
            reason: Reason for closing the trade

        Returns:
            bool: True if notification was sent successfully
        """
        emoji = "✅" if profit_loss > 0 else "❌"
        result = "WIN" if profit_loss > 0 else "LOSS"

        message = (
            f"{emoji} Closed {symbol} {action} Trade\n"
            f"Result: {result}\n"
            f"P/L: {profit_loss:.2f}%\n"
            f"Reason: {reason}"
        )

        return self.send_notification(message)

    def send_error_notification(self, error_message: str) -> bool:
        """Send an error notification.

        Args:
            error_message: Error message

        Returns:
            bool: True if notification was sent successfully
        """
        message = f"⚠️ ERROR: {error_message}"
        return self.send_notification(message, notification_type="error")
