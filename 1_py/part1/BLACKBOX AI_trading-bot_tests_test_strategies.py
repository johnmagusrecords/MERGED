# Tests for the trading strategies
import unittest
from src.strategies import strategy_one, strategy_two

class TestStrategies(unittest.TestCase):
    def test_strategy_one(self):
        result = strategy_one()
        self.assertIsNotNone(result)  # Ensure strategy_one returns a value
        # Add more assertions to validate the output of strategy_one

    def test_strategy_two(self):
        result = strategy_two()
        self.assertIsNotNone(result)  # Ensure strategy_two returns a value
        # Add more assertions to validate the output of strategy_two


if __name__ == '__main__':
    unittest.main()
