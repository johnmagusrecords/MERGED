import unittest
from trading_bot.api.trading_api import TradingAPI

class TestTradingAPI(unittest.TestCase):
    """Test cases for TradingAPI class"""
    
    def setUp(self):
        self.api = TradingAPI()
        
    def test_authentication(self):
        """Test API authentication"""
        self.assertTrue(self.api.authenticate(), "Authentication failed")
        
    def test_get_market_data(self):
        """Test market data retrieval"""
        symbol = "BTCUSD"
        data = self.api.get_market_data(symbol)
        self.assertIsNotNone(data, f"Failed to fetch market data for {symbol}")
        self.assertIn("prices", data, "Missing prices in market data")
        
    def test_get_min_distance(self):
        """Test minimum distance retrieval"""
        symbol = "BTCUSD"
        min_distance = self.api.get_min_distance(symbol)
        self.assertIsNotNone(min_distance, f"Failed to fetch min distance for {symbol}")
        self.assertIsInstance(min_distance, float, "Min distance is not a float")

if __name__ == "__main__":
    unittest.main()
