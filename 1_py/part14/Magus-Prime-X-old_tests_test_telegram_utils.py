"""
Unit tests for the telegram utilities module.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.telegram_utils import (
    is_telegram_configured,
    send_trade_notification,
    send_trade_notification_async,
)


class TestTelegramUtils(unittest.TestCase):
    """Test cases for telegram utilities."""

    @patch("utils.telegram_utils.telegram_bot")
    @patch("utils.telegram_utils.telegram_config")
    def test_is_telegram_configured(self, mock_config, mock_bot):
        """Test the telegram configuration check."""
        # When bot is available and config is valid
        mock_bot.return_value = MagicMock()
        mock_config.is_configured = True
        mock_bot.is_configured = True

        # Since we've patched telegram_bot and telegram_config directly,
        # we need to make sure telegram_bot is not None for is_telegram_configured
        mock_bot.__bool__.return_value = True

        self.assertTrue(is_telegram_configured())

        # When bot is not available
        mock_bot.__bool__.return_value = False
        self.assertFalse(is_telegram_configured())

        # When config is invalid
        mock_bot.__bool__.return_value = True
        mock_config.is_configured = False
        self.assertFalse(is_telegram_configured())

    @patch("utils.telegram_utils.is_telegram_configured")
    @patch("utils.telegram_utils.TradeNotification.send_signal")
    def test_send_trade_notification_async(self, mock_send, mock_configured):
        """Test async trade notification with keyword arguments."""
        # Setup
        mock_configured.return_value = True

        # Test with minimal parameters
        asyncio.run(send_trade_notification_async(symbol="BTC/USD", action="BUY"))
        mock_send.assert_called_once()

        # Check that parameters were passed correctly
        args, _ = mock_send.call_args
        signal = args[0]
        self.assertEqual(signal.get("symbol"), "BTC/USD")
        self.assertEqual(signal.get("action"), "BUY")
        self.assertNotIn("take_profit", signal)  # Should not be included if None

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
        args, _ = mock_send.call_args
        signal = args[0]
        self.assertEqual(signal.get("symbol"), "ETH/USD")
        self.assertEqual(signal.get("action"), "SELL")
        self.assertEqual(signal.get("take_profit"), 1200.0)
        self.assertEqual(signal.get("stop_loss"), 1000.0)
        self.assertEqual(signal.get("confidence"), 0.85)

    @patch("utils.telegram_utils.send_trade_notification_async")
    def test_backwards_compatibility(self, mock_async):
        """Test that the old function signature still works."""
        # Setup
        mock_async.return_value = None

        # Test with positional arguments
        asyncio.run(send_trade_notification("BTC/USD", "BUY", 45000.0, 40000.0, 0.75))

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
