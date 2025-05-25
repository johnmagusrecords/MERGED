"""
Unit tests for the telegram utilities module.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, PropertyMock, AsyncMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.telegram_utils import (
    is_telegram_configured,
    send_trade_notification,
    send_trade_notification_async,
    TradeNotification,
)


class TestTelegramUtils(unittest.TestCase):
    """Test cases for telegram utilities."""

    @patch("os.getenv")
    def test_is_telegram_configured(self, mock_getenv):
        """Test the telegram configuration check using environment variables."""
        # Simulate both variables present
        mock_getenv.side_effect = lambda key: {
            'TELEGRAM_BOT_TOKEN': 'dummy_token',
            'TELEGRAM_CHAT_ID': 'dummy_chat_id'
        }.get(key)
        self.assertTrue(is_telegram_configured())

        # Simulate missing TELEGRAM_BOT_TOKEN
        mock_getenv.side_effect = lambda key: {
            'TELEGRAM_BOT_TOKEN': None,
            'TELEGRAM_CHAT_ID': 'dummy_chat_id'
        }.get(key)
        self.assertFalse(is_telegram_configured())

        # Simulate missing TELEGRAM_CHAT_ID
        mock_getenv.side_effect = lambda key: {
            'TELEGRAM_BOT_TOKEN': 'dummy_token',
            'TELEGRAM_CHAT_ID': None
        }.get(key)
        self.assertFalse(is_telegram_configured())

    @patch("utils.telegram_utils.is_telegram_configured")
    @patch.object(TradeNotification, "send_signal", new_callable=AsyncMock)
    def test_send_trade_notification_async(self, mock_send, mock_configured):
        """Test async trade notification with keyword arguments."""
        # Setup
        mock_configured.return_value = True

        # Test with minimal parameters - use 0.0 instead of None for floats
        asyncio.run(send_trade_notification_async(symbol="BTC/USD", action="BUY", take_profit=0.0, stop_loss=0.0, confidence=0.0))
        mock_send.assert_called_once()

        # Check that parameters were passed correctly
        args, kwargs = mock_send.call_args
        chat_id_arg = args[0]
        message_arg = args[1]
        self.assertIsInstance(message_arg, str)
        self.assertIn("BTC/USD", message_arg)
        self.assertIn("BUY", message_arg)

        # Reset and test with all parameters
        mock_send.reset_mock()
        asyncio.run(
            send_trade_notification_async(
                symbol="ETH/USD",
                action="SELL",
                take_profit=1200.0,
                stop_loss=1000.0,
                confidence=0.85,
            )
        )

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        chat_id_arg = args[0]
        message_arg = args[1]
        self.assertIsInstance(message_arg, str)
        self.assertIn("ETH/USD", message_arg)
        self.assertIn("SELL", message_arg)
        self.assertIn("1200.0", message_arg)
        self.assertIn("1000.0", message_arg)
        self.assertIn("0.85", message_arg)

    @patch("utils.telegram_utils.send_trade_notification_async")
    def test_backwards_compatibility(self, mock_async):
        """Test that the old function signature still works."""
        # Setup
        async def async_return_none(*args, **kwargs):
            return None
        mock_async.side_effect = async_return_none

        # Test with positional arguments (added missing commas)
        coro = send_trade_notification("BTC/USD", "BUY", 45000.0, 40000.0, 0.75)
        if coro is not None:
            asyncio.run(coro)

        # Verify correct mapping to keyword arguments
        mock_async.assert_called_once_with(
            symbol="BTC/USD",
            action="BUY",
            take_profit=45000.0,
            stop_loss=40000.0,
            confidence=0.75,
        )


if __name__ == "__main__":
    unittest.main()
