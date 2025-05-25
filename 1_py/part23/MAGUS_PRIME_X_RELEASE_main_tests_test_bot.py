import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch
from bot import execute_trade, analyze_market
import pandas as pd

class TestBot(unittest.TestCase):
    @patch('bot.get_market_data')
    def test_analyze_market(self, mock_get_market_data):
        mock_data = pd.DataFrame({
            'closePrice': [100, 101, 102],
            'highPrice': [105, 106, 107],
            'lowPrice': [95, 96, 97]
        })
        mock_get_market_data.return_value = mock_data
        result = analyze_market('BTCUSD')
        self.assertIsNotNone(result)
        # Add more assertions based on analyze_market logic

    @patch('bot.authenticate')
    @patch('bot.requests.post')
    def test_execute_trade(self, mock_post, mock_authenticate):
        mock_authenticate.return_value = ('mock_cst', 'mock_x_security')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'dealReference': 'mock_deal_ref'}
        
        result = execute_trade('BUY', 'BTCUSD', 100)  # price instead of risk_percent
        self.assertIsNotNone(result)
        # Add more assertions based on execute_trade logic

if __name__ == '__main__':
    unittest.main()
