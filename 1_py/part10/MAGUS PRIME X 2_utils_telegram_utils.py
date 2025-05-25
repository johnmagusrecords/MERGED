"""
Telegram Notification Utilities

This module provides functionality for sending notifications to Telegram.
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional, Tuple

import telegram
from telegram.constants import ParseMode

# Environment variables for configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Global bot instance
telegram_bot = None


class TelegramConfig:
    """Configuration class for Telegram notifications."""

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        """Initialize Telegram configuration.

        Args:
            token: Telegram bot token (defaults to env var)
            chat_id: Telegram chat ID (defaults to env var)
        """
        self.token = token or TELEGRAM_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.is_configured = bool(self.token and self.chat_id)


# Default configuration from environment variables
telegram_config = TelegramConfig()


def is_telegram_configured() -> bool:
    """Check if Telegram is properly configured.

    Returns:
        bool: True if Telegram is configured, False otherwise
    """
    global telegram_bot
    return bool(telegram_config.is_configured and telegram_bot is not None)


if telegram_config.is_configured:
    telegram_bot = telegram.Bot(token=telegram_config.token)
    # Check if asyncio support is available
    try:
        import telegram.ext

        is_telegram_async = True
    except ImportError:
        is_telegram_async = False


async def send_telegram_message(message):
    """Send a message to the Telegram chat.

    Args:
        message: Text message to send
    """
    if not is_telegram_configured():
        return

    try:
        await telegram_bot.send_message(chat_id=telegram_config.chat_id, text=message)
        logging.info(f"Telegram message sent: {message[:50]}...")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")


def send_message_sync(message):
    """Synchronous wrapper for sending Telegram messages.

    Args:
        message: Text message to send
    """
    if not is_telegram_configured():
        return

    try:
        asyncio.run(send_telegram_message(message))
    except Exception as e:
        logging.error(f"Failed to send Telegram message (sync): {e}")


class TradeNotification:
    """Class to format and send trade notifications."""

    @staticmethod
    def _extract_signal_data(
        trade_signal: Dict[str, Any],
    ) -> Tuple[Optional[str], Optional[str]]:
        """Extract essential data from trade signal.

        Args:
            trade_signal: Dictionary with trade signal details

        Returns:
            Tuple of (symbol, action) or (None, None) if missing
        """
        symbol = trade_signal.get("symbol") or trade_signal.get("asset")
        action = trade_signal.get("action") or trade_signal.get("direction")

        return symbol, action

    @staticmethod
    def _format_trade_message(
        trade_signal: Dict[str, Any], symbol: str, action: str
    ) -> str:
        """Format trade notification message.

        Args:
            trade_signal: Dictionary with trade signal details
            symbol: Trading symbol
            action: Trade action

        Returns:
            Formatted message string
        """
        # Format the message
        emoji = "🔴" if action == "SELL" else "🟢"
        message = f"{emoji} *TRADE SIGNAL*\n\n"
        message += f"*{symbol}*: {action}\n"

        # Add optional parameters if present
        if trade_signal.get("take_profit"):
            message += f"Take Profit: {trade_signal['take_profit']}\n"

        if trade_signal.get("stop_loss"):
            message += f"Stop Loss: {trade_signal['stop_loss']}\n"

        if trade_signal.get("confidence"):
            confidence = float(trade_signal["confidence"])
            message += f"Confidence: {confidence*100:.0f}%\n"

        if trade_signal.get("source"):
            message += f"Source: {trade_signal['source']}\n"

        return message

    @staticmethod
    async def send_signal(trade_signal: Dict[str, Any]) -> None:
        """Send a notification for a new trading signal.

        Args:
            trade_signal: Dictionary with trade signal details
        """
        if not is_telegram_configured():
            return

        try:
            # Extract essential data
            symbol, action = TradeNotification._extract_signal_data(trade_signal)

            if not symbol or not action:
                logging.error("Missing required trade signal parameters")
                return

            # Format message
            message = TradeNotification._format_trade_message(
                trade_signal, symbol, action
            )

            # Send the message
            await telegram_bot.send_message(
                chat_id=telegram_config.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
            )
            logging.info(f"Trade notification sent for {symbol}")
        except Exception as e:
            logging.error(f"Failed to send trade notification: {e}")

    @staticmethod
    async def send_closed(close_data: Dict[str, Any]) -> None:
        """Send a notification for a closed trade.

        Args:
            close_data: Dictionary with trade close details
        """
        if not is_telegram_configured():
            return

        try:
            symbol = close_data.get("symbol")
            reason = close_data.get("reason", "Manual close")
            profit_loss = close_data.get("profit_loss")

            if not symbol:
                logging.error("Missing symbol in trade close notification")
                return

            # Format the message
            message = "🔔 *TRADE CLOSED*\n\n"
            message += f"*{symbol}*\n"
            message += f"Reason: {reason}\n"

            if profit_loss is not None:
                emoji = "✅" if float(profit_loss) > 0 else "❌"
                message += f"{emoji} P/L: {float(profit_loss):.2f}\n"

            await telegram_bot.send_message(
                chat_id=telegram_config.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
            )
            logging.info(f"Trade closed notification sent for {symbol}")
        except Exception as e:
            logging.error(f"Failed to send trade closed notification: {e}")


# For backward compatibility
async def send_trade_notification_async(**kwargs) -> None:
    """Legacy function for sending trade notifications with keyword arguments.

    Keyword Args:
        symbol: Trading symbol
        action: Trade action (BUY/SELL)
        take_profit: Take profit level
        stop_loss: Stop loss level
        confidence: Trade confidence level (0-1)
    """
    await TradeNotification.send_signal(kwargs)


# Old function signature maintained for backwards compatibility
async def send_trade_notification(symbol: str, action: str, **kwargs) -> None:
    """Legacy function for sending trade notifications.

    Args:
        symbol: Trading symbol
        action: Trade action (BUY/SELL)

    Keyword Args:
        take_profit: Take profit level
        stop_loss: Stop loss level
        confidence: Trade confidence level (0-1)
    """
    # Convert parameters to the expected dictionary format
    trade_signal = {
        "symbol": symbol,
        "action": action,
        "take_profit": kwargs.get("take_profit"),
        "stop_loss": kwargs.get("stop_loss"),
        "confidence": kwargs.get("confidence", 0.0),
    }

    await TradeNotification.send_signal(trade_signal)


async def send_trade_closed_notification(
    symbol: str, reason: str, profit_loss: Optional[float] = None
) -> None:
    """Legacy function for sending trade closed notifications.

    Args:
        symbol: Trading symbol
        reason: Reason for closing the trade
        profit_loss: Profit/loss amount if available
    """
    trade_info = {"symbol": symbol, "reason": reason, "profit_loss": profit_loss}
    await TradeNotification.send_closed(trade_info)


def check_telegram_setup() -> bool:
    """Check if Telegram notification is properly configured.

    Returns:
        bool: True if configured, False otherwise
    """
    return is_telegram_configured()
