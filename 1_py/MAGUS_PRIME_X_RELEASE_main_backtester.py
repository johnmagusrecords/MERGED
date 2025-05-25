import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import talib
from datetime import datetime
import plotly.graph_objects as go
from dataclasses import dataclass
import joblib
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from statsmodels.stats.stattools import sharpe_ratio

@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity_curve: pd.Series
    win_rate: float
    profit_factor: float
    sharpe: float
    max_drawdown: float
    net_profit: float
    total_trades: int

class Strategy:
    def __init__(self, params: Dict = None):
        self.params = params or {}
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        raise NotImplementedError

class RSIStrategy(Strategy):
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        rsi = talib.RSI(data['close'].values, timeperiod=self.params.get('period', 14))
        signals = pd.Series(index=data.index, data=0)
        signals[rsi < self.params.get('oversold', 30)] = 1  # Buy
        signals[rsi > self.params.get('overbought', 70)] = -1  # Sell
        return signals

class MACDStrategy(Strategy):
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        macd, signal, _ = talib.MACD(
            data['close'].values,
            fastperiod=self.params.get('fast_period', 12),
            slowperiod=self.params.get('slow_period', 26),
            signalperiod=self.params.get('signal_period', 9)
        )
        signals = pd.Series(index=data.index, data=0)
        signals[macd > signal] = 1  # Buy
        signals[macd < signal] = -1  # Sell
        return signals

class BBStrategy(Strategy):
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        upper, middle, lower = talib.BBANDS(
            data['close'].values,
            timeperiod=self.params.get('period', 20),
            nbdevup=self.params.get('std_dev', 2),
            nbdevdn=self.params.get('std_dev', 2)
        )
        signals = pd.Series(index=data.index, data=0)
        signals[data['close'] < lower] = 1  # Buy
        signals[data['close'] > upper] = -1  # Sell
        return signals

class AIStrategy(Strategy):
    def __init__(self, params: Dict = None):
        super().__init__(params)
        self.model = self._build_model()
        self.scaler = StandardScaler()
        
    def _build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, input_shape=(20, 5)),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        return model
        
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        features = []
        for i in range(20, len(data)):
            window = data.iloc[i-20:i][['open', 'high', 'low', 'close', 'volume']].values
            features.append(window)
        return np.array(features)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        X = self._prepare_features(data)
        if len(X) == 0:
            return pd.Series(index=data.index, data=0)
        
        X = self.scaler.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
        predictions = self.model.predict(X)
        
        signals = pd.Series(index=data.index, data=0)
        signals.iloc[20:] = np.where(predictions > 0.5, 1, -1)
        return signals

class Backtester:
    def __init__(self, data: pd.DataFrame, strategies: List[Strategy], 
                 initial_capital: float = 10000):
        self.data = data
        self.strategies = strategies
        self.initial_capital = initial_capital
        
    def _calculate_metrics(self, trades: pd.DataFrame) -> BacktestResult:
        if len(trades) == 0:
            return BacktestResult(
                trades=trades,
                equity_curve=pd.Series([self.initial_capital]),
                win_rate=0.0,
                profit_factor=0.0,
                sharpe=0.0,
                max_drawdown=0.0,
                net_profit=0.0,
                total_trades=0
            )
            
        # Calculate P&L and equity curve
        trades['pnl'] = trades['exit_price'] - trades['entry_price']
        trades['pnl'] = trades['pnl'] * trades['position']  # Adjust for short positions
        equity_curve = (trades['pnl'].cumsum() + self.initial_capital)
        
        # Calculate metrics
        winning_trades = trades[trades['pnl'] > 0]
        losing_trades = trades[trades['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(trades) if len(trades) > 0 else 0
        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 else float('inf')
        
        # Calculate Sharpe ratio (assuming daily data)
        returns = trades['pnl'] / self.initial_capital
        sharpe = sharpe_ratio(returns) if len(returns) > 1 else 0
        
        # Calculate maximum drawdown
        peak = equity_curve.expanding(min_periods=1).max()
        drawdown = (equity_curve - peak) / peak
        max_drawdown = drawdown.min()
        
        return BacktestResult(
            trades=trades,
            equity_curve=equity_curve,
            win_rate=win_rate * 100,
            profit_factor=profit_factor,
            sharpe=sharpe,
            max_drawdown=max_drawdown * 100,
            net_profit=equity_curve.iloc[-1] - self.initial_capital,
            total_trades=len(trades)
        )
    
    def run(self) -> BacktestResult:
        combined_signal = pd.Series(index=self.data.index, data=0)
        
        # Combine signals from all strategies
        for strategy in self.strategies:
            combined_signal += strategy.generate_signals(self.data)
            
        # Normalize signals
        combined_signal = np.sign(combined_signal)
        
        # Generate trades
        trades = []
        position = 0
        entry_price = 0
        entry_time = None
        
        for i in range(len(self.data)):
            if combined_signal.iloc[i] != 0 and position == 0:
                # Enter position
                position = combined_signal.iloc[i]
                entry_price = self.data['close'].iloc[i]
                entry_time = self.data.index[i]
            elif (combined_signal.iloc[i] == -position or i == len(self.data)-1) and position != 0:
                # Exit position
                exit_price = self.data['close'].iloc[i]
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': self.data.index[i],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'position': position
                })
                position = 0
        
        trades_df = pd.DataFrame(trades)
        return self._calculate_metrics(trades_df)
    
    def plot_results(self, result: BacktestResult) -> go.Figure:
        fig = go.Figure()
        
        # Plot equity curve
        fig.add_trace(go.Scatter(
            x=result.equity_curve.index,
            y=result.equity_curve.values,
            mode='lines',
            name='Equity Curve'
        ))
        
        # Plot trade entries and exits
        for _, trade in result.trades.iterrows():
            color = 'green' if trade['pnl'] > 0 else 'red'
            
            # Entry point
            fig.add_trace(go.Scatter(
                x=[trade['entry_time']],
                y=[self.data.loc[trade['entry_time'], 'close']],
                mode='markers',
                marker=dict(color=color, symbol='triangle-up' if trade['position'] > 0 else 'triangle-down', size=10),
                name=f"{'Buy' if trade['position'] > 0 else 'Sell'} Entry"
            ))
            
            # Exit point
            fig.add_trace(go.Scatter(
                x=[trade['exit_time']],
                y=[self.data.loc[trade['exit_time'], 'close']],
                mode='markers',
                marker=dict(color=color, symbol='x', size=10),
                name='Exit'
            ))
            
        fig.update_layout(
            title='Backtest Results',
            xaxis_title='Date',
            yaxis_title='Portfolio Value',
            showlegend=True
        )
        
        return fig

def save_backtest_result(result: BacktestResult, filename: str):
    """Save backtest result to file"""
    joblib.dump(result, filename)

def load_backtest_result(filename: str) -> BacktestResult:
    """Load backtest result from file"""
    return joblib.load(filename)
