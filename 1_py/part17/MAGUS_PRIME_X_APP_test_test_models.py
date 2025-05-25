"""
Unit tests for the trading models and utilities.
"""

import os
import shutil
import sys
import tempfile
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trading.models import (
    TradeParams,
    add_trade_record,
    calculate_profit_loss,
    calculate_trade_pl,
    calculate_trade_statistics,
    calculate_win_rate,
    get_trade_history,
    save_trade_history,
)


class TestTradeParams(unittest.TestCase):
    """Test cases for TradeParams class."""

    def test_init_valid_params(self):
        """Test initialization with valid parameters."""
        # Test with required parameters only
        trade = TradeParams(symbol="BTCUSD", direction="BUY")
        self.assertEqual(trade.symbol, "BTCUSD")
        self.assertEqual(trade.direction, "BUY")
        self.assertEqual(trade.quantity, 1.0)  # Default
        self.assertIsNone(trade.take_profit)
        self.assertIsNone(trade.stop_loss)

        # Test with all parameters
        trade = TradeParams(
            symbol="EURUSD",
            direction="SELL",
            quantity=2.5,
            take_profit=1.15,
            stop_loss=1.10,
        )
        self.assertEqual(trade.symbol, "EURUSD")
        self.assertEqual(trade.direction, "SELL")
        self.assertEqual(trade.quantity, 2.5)
        self.assertEqual(trade.take_profit, 1.15)
        self.assertEqual(trade.stop_loss, 1.10)

    def test_init_invalid_params(self):
        """Test initialization with invalid parameters."""
        # Test empty symbol
        with self.assertRaises(ValueError):
            TradeParams(symbol="", direction="BUY")

        # Test invalid direction
        with self.assertRaises(ValueError):
            TradeParams(symbol="BTCUSD", direction="INVALID")

        # Test negative quantity
        with self.assertRaises(ValueError):
            TradeParams(symbol="BTCUSD", direction="BUY", quantity=-1.0)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        trade = TradeParams(
            symbol="BTCUSD",
            direction="BUY",
            quantity=1.5,
            take_profit=50000.0,
            stop_loss=45000.0,
        )

        expected = {
            "symbol": "BTCUSD",
            "direction": "BUY",
            "quantity": 1.5,
            "take_profit": 50000.0,
            "stop_loss": 45000.0,
        }

        self.assertEqual(trade.to_dict(), expected)

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "symbol": "BTCUSD",
            "direction": "BUY",
            "quantity": 1.5,
            "take_profit": 50000.0,
            "stop_loss": 45000.0,
        }

        trade = TradeParams.from_dict(data)

        self.assertEqual(trade.symbol, "BTCUSD")
        self.assertEqual(trade.direction, "BUY")
        self.assertEqual(trade.quantity, 1.5)
        self.assertEqual(trade.take_profit, 50000.0)
        self.assertEqual(trade.stop_loss, 45000.0)

        # Test with missing optional fields
        data = {"symbol": "EURUSD", "direction": "SELL"}

        trade = TradeParams.from_dict(data)

        self.assertEqual(trade.symbol, "EURUSD")
        self.assertEqual(trade.direction, "SELL")
        self.assertEqual(trade.quantity, 1.0)  # Default
        self.assertIsNone(trade.take_profit)
        self.assertIsNone(trade.stop_loss)


class TestTradeHistory(unittest.TestCase):
    """Test cases for trade history functions."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        from trading.models import clear_trade_history

        clear_trade_history()

        # Create temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Patch the TRADE_HISTORY_FILE path
        self.original_file = os.environ.get("TRADE_HISTORY_FILE")
        os.environ["TRADE_HISTORY_FILE"] = os.path.join(
            self.test_dir, "test_trade_history.json"
        )

        # Sample trade data
        self.sample_trades = [
            {
                "Timestamp": "2023-01-01T12:00:00",
                "Symbol": "BTCUSD",
                "Action": "BUY",
                "TP": 50000.0,
                "SL": 45000.0,
                "Result": "WIN",
                "PL": 500.0,
            },
            {
                "Timestamp": "2023-01-02T14:30:00",
                "Symbol": "EURUSD",
                "Action": "SELL",
                "TP": 1.05,
                "SL": 1.10,
                "Result": "LOSS",
                "PL": -200.0,
            },
        ]

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

        # Restore original path
        if self.original_file:
            os.environ["TRADE_HISTORY_FILE"] = self.original_file
        else:
            del os.environ["TRADE_HISTORY_FILE"]

    def test_save_and_get_trade_history(self):
        """Test saving and retrieving trade history."""
        # Save sample trades to in-memory list
        for trade in self.sample_trades:
            add_trade_record(trade)

        # Save trade history to file
        self.assertIsNone(save_trade_history(os.environ["TRADE_HISTORY_FILE"]))

        # Retrieve trades
        trades = get_trade_history()

        # Check results
        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[0]["Symbol"], "BTCUSD")
        self.assertEqual(trades[1]["Symbol"], "EURUSD")

    def test_add_trade_record(self):
        """Test adding a trade record."""
        # Add first trade
        new_trade = {"Symbol": "GOLD", "Action": "BUY", "TP": 2000.0, "SL": 1900.0}

        self.assertTrue(add_trade_record(new_trade))

        # Check that record was added with timestamp
        trades = get_trade_history()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["Symbol"], "GOLD")
        self.assertIn("Timestamp", trades[0])

        # Add another trade
        another_trade = {
            "Symbol": "OIL",
            "Action": "SELL",
            "TP": 70.0,
            "SL": 75.0,
            "Timestamp": "2023-01-03T10:00:00",  # Explicit timestamp
        }

        self.assertTrue(add_trade_record(another_trade))

        # Check that both records exist
        trades = get_trade_history()
        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[1]["Symbol"], "OIL")
        self.assertEqual(trades[1]["Timestamp"], "2023-01-03T10:00:00")


class TestTradeStatistics(unittest.TestCase):
    """Test cases for trade statistics functions."""

    def setUp(self):
        """Set up test data."""
        self.winning_trades = [
            {"Symbol": "BTCUSD", "Result": "WIN", "TP": 50000, "SL": 45000, "PL": 500},
            {"Symbol": "ETHUSD", "Result": "WIN", "TP": 3000, "SL": 2800, "PL": 300},
        ]

        self.losing_trades = [
            {"Symbol": "EURUSD", "Result": "LOSS", "TP": 1.05, "SL": 1.10, "PL": -250},
            {"Symbol": "GOLD", "Result": "LOSS", "TP": 2000, "SL": 1900, "PL": -400},
        ]

        self.mixed_trades = self.winning_trades + self.losing_trades

    def test_calculate_win_rate(self):
        """Test win rate calculation."""
        # Test with all winning trades
        self.assertEqual(calculate_win_rate(self.winning_trades), 100.0)

        # Test with all losing trades
        self.assertEqual(calculate_win_rate(self.losing_trades), 0.0)

        # Test with mixed trades (50% win rate)
        self.assertEqual(calculate_win_rate(self.mixed_trades), 50.0)

        # Test with empty list
        self.assertEqual(calculate_win_rate([]), 0.0)

    def test_calculate_profit_loss(self):
        """Test profit/loss calculation."""
        # Test with all winning trades
        self.assertEqual(calculate_profit_loss(self.winning_trades), 800.0)

        # Test with all losing trades
        self.assertEqual(calculate_profit_loss(self.losing_trades), -650.0)

        # Test with mixed trades
        self.assertEqual(calculate_profit_loss(self.mixed_trades), 150.0)

        # Test with empty list
        self.assertEqual(calculate_profit_loss([]), 0.0)

    def test_calculate_trade_pl(self):
        """Test individual trade P/L calculation."""
        # Test winning trade with explicit PL
        trade = {"Symbol": "BTCUSD", "Result": "WIN", "PL": 500}
        self.assertEqual(calculate_trade_pl(trade, "WIN"), 500.0)

        # Test winning trade with TP/SL
        trade = {"Symbol": "ETHUSD", "Result": "WIN", "TP": 3000, "SL": 2800}
        self.assertEqual(calculate_trade_pl(trade, "WIN"), 200.0)

        # Test losing trade with explicit PL
        trade = {"Symbol": "EURUSD", "Result": "LOSS", "PL": -250}
        self.assertEqual(calculate_trade_pl(trade, "LOSS"), -250.0)

        # Test losing trade with TP/SL
        trade = {"Symbol": "GOLD", "Result": "LOSS", "TP": 2000, "SL": 1900}
        self.assertEqual(calculate_trade_pl(trade, "LOSS"), -100.0)

    def test_calculate_trade_statistics(self):
        """Test the main statistics function."""
        # Test with mixed trades
        win_rate, pnl = calculate_trade_statistics(self.mixed_trades)
        self.assertEqual(win_rate, 50.0)
        self.assertEqual(pnl, 150.0)

        # Test with empty list
        win_rate, pnl = calculate_trade_statistics([])
        self.assertEqual(win_rate, 0.0)
        self.assertEqual(pnl, 0.0)


if __name__ == "__main__":
    unittest.main()
