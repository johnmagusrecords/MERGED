import backtrader as bt
import pandas_ta as ta
import pandas as pd
import ccxt
import time

# Define your trading strategy
class MyStrategy(bt.Strategy):
    # Define your indicators and parameters here
    def __init__(self):
        self.rsi = ta.rsi(self.data.close, length=14)  # RSI Indicator
        
    def next(self):
        # Simple trading strategy: Buy if RSI is under 30, Sell if over 70
        if self.rsi[-1] < 30:
            if not self.position:
                self.buy()
        elif self.rsi[-1] > 70:
            if self.position:
                self.sell()

# Set up the backtesting environment
def run_backtest():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MyStrategy)
    
    # Load historical data (you can replace this with real-time data if needed)
    data = bt.feeds.PandasData(dataname=pd.read_csv('historical_data.csv'))
    cerebro.adddata(data)

    # Set up initial capital and commission
    cerebro.broker.set_cash(10000)
    cerebro.broker.set_commission(commission=0.001)

    # Run the backtest
    cerebro.run()

    # Print the final portfolio value
    print(f'Final Portfolio Value: {cerebro.broker.getvalue()}')

# Run backtest
run_backtest()
import backtrader as bt
import pandas as pd

# Load the CSV file into a pandas DataFrame
data_path = r'C:\Users\djjoh\OneDrive\Desktop\bitcoin_data.csv'

# Backtrader needs to know the date format, so we'll make sure it's correct
df = pd.read_csv(data_path, parse_dates=True, index_col='Date')

# Convert the DataFrame to Backtrader's data feed
data = bt.feeds.PandasData(dataname=df)

# Set up the backtesting environment
cerebro = bt.Cerebro()
cerebro.adddata(data)

# Define your strategy (you can replace this with your own strategy)
class MyStrategy(bt.Strategy):
    def __init__(self):
        # Define indicators, like moving averages or others
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)

    def next(self):
        if self.data.close[0] > self.sma[0]:
            if not self.position:
                self.buy()
        elif self.data.close[0] < self.sma[0]:
            if self.position:
                self.sell()

# Add the strategy to the cerebro engine
cerebro.addstrategy(MyStrategy)

# Run the backtest
cerebro.run()

# Plot the results (optional)
cerebro.plot()
