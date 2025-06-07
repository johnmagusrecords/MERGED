import os
from importlib.machinery import SourceFileLoader
import pandas as pd
import numpy as np

# Load the calculate_atr function directly from the sibling module
module_path = os.path.join(os.path.dirname(__file__), "BLACKBOX AI_trading-bot_src_technical_indicators.py")
technical_indicators = SourceFileLoader("technical_indicators", module_path).load_module()
calculate_atr = technical_indicators.calculate_atr

def test_atr():
    # Create sample price data
    data = {
        'high': [100, 102, 104, 103, 105],
        'low': [98, 97, 99, 98, 101],
        'close': [99, 101, 102, 100, 103]
    }
    df = pd.DataFrame(data)
    
    # Calculate ATR with period=3
    atr = calculate_atr(df['high'], df['low'], df['close'], period=3)

    expected = np.array([2, 3, 3, 3, 3])

    # Ensure the result is a numpy array with the expected values
    assert isinstance(atr, np.ndarray)
    assert np.array_equal(atr, expected)

if __name__ == "__main__":
    raise SystemExit("Run this test using pytest or unittest, not as a script")
