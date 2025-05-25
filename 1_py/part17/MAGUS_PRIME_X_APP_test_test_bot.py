import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch

import pandas as pd

from apy.bot_dev_backup import analyze_market, execute_trade


class TestBot(unittest.TestCase):
    @patch("apy.bot.get_market_data")
    def test_analyze_market(self, mock_get_market_data):
        mock_data = pd.DataFrame(
            {
                "closePrice": [100, 101, 102],
                "highPrice": [105, 106, 107],
                "lowPrice": [95, 96, 97],
            }
        )
        mock_get_market_data.return_value = mock_data
        result = analyze_market("BTCUSD")
        self.assertIsNotNone(result)
        # Add more assertions based on analyze_market logic

    @patch("apy.bot.authenticate")
    @patch("apy.bot.requests.post")
    def test_execute_trade(self, mock_post, mock_authenticate):
        mock_authenticate.return_value = ("mock_cst", "mock_x_security")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"dealReference": "mock_deal_ref"}

        result = execute_trade("BUY", "BTCUSD", 100)  # Match execute_trade signature
        self.assertIsNotNone(result)
        # Add more assertions based on execute_trade logic


if __name__ == "__main__":
    unittest.main()
