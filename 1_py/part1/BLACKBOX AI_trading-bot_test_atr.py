import pandas as pd
import numpy as np
from src.technical_indicators import calculate_atr

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
    
    print("Sample Data:")
    print(df)
    print("\nCalculated ATR values:")
    print(atr)

if __name__ == "__main__":
    test_atr()
