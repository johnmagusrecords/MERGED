"""
Unit tests for the Capital.com API client.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apy.capital_api import CapitalAPI


class TestCapitalAPI(unittest.TestCase):
    """Test cases for the Capital.com API client."""

    def setUp(self):
        """Set up test environment."""
        # Create API client with mock credentials
        self.api = CapitalAPI(
            api_key="test_key",
            identifier="test_id",
            password="test_pass",
            api_url="https://test.capital.com/api/v1",
        )
        # Mock authentication tokens
        setattr(self.api, "_auth_token", "test_token")
        setattr(self.api, "_cst", "test_cst")
        setattr(self.api, "_authenticated", True)

    @patch("apy.capital_api.requests.Session")
    def test_initialization(self, mock_session):
        """Test API client initialization."""
        # Test with explicit credentials
        api = CapitalAPI(
            api_key="custom_key",
            identifier="custom_id",
            password="custom_pass",
            api_url="https://custom.capital.com/api/v1",
        )

        # Check that credentials were stored correctly
        self.assertEqual(api.api_key, "custom_key")
        self.assertEqual(api.identifier, "custom_id")
        self.assertEqual(api.password, "custom_pass")
        self.assertEqual(api.api_url, "https://custom.capital.com/api/v1")

        # Check that session was created
        mock_session.assert_called_once()

    @patch.object(CapitalAPI, "_make_api_request")
    def test_execute_trade(self, mock_request):
        """Test trade execution."""
        # Setup successful response
        mock_request.return_value = (True, {"dealId": "123456", "status": "SUCCESS"})

        # Execute trade with valid parameters
        result = self.api.execute_trade(
            {
                "symbol": "BTCUSD",
                "direction": "BUY",
                "quantity": 1.0,
                "take_profit": 50000.0,
                "stop_loss": 45000.0,
            }
        )

        # Check result
        if result is not None:
            deal_id = result["dealId"]
        else:
            deal_id = None
        self.assertIsNotNone(deal_id)
        self.assertEqual(deal_id, "123456")

        # Check API request
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "trades")
        self.assertEqual(kwargs.get("method"), "POST")
        self.assertEqual(args[1]["epic"], "BTCUSD")
        self.assertEqual(args[1]["side"], "BUY")

        # Test with invalid parameters
        with self.assertRaises(ValueError):
            self.api.execute_trade({"symbol": "", "direction": "INVALID"})

    @patch.object(CapitalAPI, "_make_api_request")
    def test_close_trade(self, mock_request):
        """Test closing a trade."""
        # Setup successful response
        mock_request.return_value = (True, {"status": "CLOSED"})

        # Close a trade
        result = self.api.close_trade("123456")

        # Check result
        self.assertTrue(result)

        # Check API request
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "positions/123456/close")
        self.assertEqual(kwargs.get("method"), "POST")
        self.assertEqual(kwargs, {"method": "POST"})

        # Test with invalid parameters
        with self.assertRaises(ValueError):
            self.api.close_trade("")

    @patch.object(CapitalAPI, "_make_api_request")
    def test_get_active_trades(self, mock_request):
        """Test getting active trades."""
        # Setup mock data
        mock_positions = [
            {"dealId": "123", "epic": "BTCUSD", "direction": "BUY"},
            {"dealId": "456", "epic": "ETHUSD", "direction": "SELL"},
        ]
        mock_request.return_value = (True, {"positions": mock_positions})

        # Get active trades
        positions = self.api.get_active_trades()

        # Check result
        if positions is not None:
            count = len(positions)
        else:
            count = None
        self.assertEqual(count, 2)
        self.assertEqual(positions[0]["dealId"], "123")
        self.assertEqual(positions[1]["dealId"], "456")

        # Check API request
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "trades/active")
        self.assertEqual(kwargs.get("method"), "GET")
        self.assertEqual(kwargs, {"method": "GET"})

    @patch.object(CapitalAPI, "_make_api_request")
    def test_error_handling(self, mock_request):
        """Test error handling in API calls."""
        # Setup failed response
        mock_request.return_value = (
            False,
            {"status": "ERROR", "message": "Invalid request"},
        )

        # Try to execute trade
        result = self.api.execute_trade(
            {"symbol": "BTCUSD", "direction": "BUY", "quantity": 1.0}
        )

        # Check that result is None on error
        if result is not None:
            error_message = result["message"]
        else:
            error_message = None
        self.assertIsNone(error_message)


if __name__ == "__main__":
    unittest.main()
