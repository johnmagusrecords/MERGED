import threading
import queue
import json
from datetime import datetime
import pandas as pd
import numpy as np
from flask_socketio import SocketIO

class WebSocketHandler:
    def __init__(self, socketio):
        self.socketio = socketio
        self.update_queue = queue.Queue()
        self.running = True
        
    def start_background_thread(self):
        """Start the background update thread"""
        thread = threading.Thread(target=self.background_updates)
        thread.daemon = True
        thread.start()
        
    def format_number(self, num):
        """Format number with 2 decimal places and commas"""
        return f"{num:,.2f}"
        
    def get_performance_metrics(self, trade_history_file):
        """Calculate performance metrics from trade history"""
        try:
            trades = pd.read_csv(trade_history_file)
            
            if len(trades) == 0:
                return {
                    'win_rate': 0,
                    'net_profit': 0,
                    'sharpe_ratio': 0,
                    'max_drawdown': 0,
                    'total_trades': 0
                }
                
            # Calculate metrics
            winning_trades = trades[trades['Result'] == 'WIN']
            total_trades = len(trades)
            win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate P&L
            trades['PnL'] = trades.apply(lambda x: float(x['TP']) if x['Result'] == 'WIN' else -float(x['SL']), axis=1)
            net_profit = trades['PnL'].sum()
            
            # Calculate Sharpe ratio (assuming daily returns)
            daily_returns = trades.groupby(pd.to_datetime(trades['Time']).dt.date)['PnL'].sum()
            sharpe_ratio = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if len(daily_returns) > 1 else 0
            
            # Calculate max drawdown
            cumulative = daily_returns.cumsum()
            rolling_max = cumulative.expanding().max()
            drawdowns = (cumulative - rolling_max) / rolling_max * 100
            max_drawdown = drawdowns.min() if len(drawdowns) > 0 else 0
            
            return {
                'win_rate': self.format_number(win_rate),
                'net_profit': self.format_number(net_profit),
                'sharpe_ratio': self.format_number(sharpe_ratio),
                'max_drawdown': self.format_number(max_drawdown),
                'total_trades': total_trades
            }
            
        except Exception as e:
            print(f"Error calculating performance metrics: {str(e)}")
            return {
                'win_rate': 0,
                'net_profit': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'total_trades': 0
            }
            
    def get_strategy_performance(self, trades):
        """Calculate performance metrics for each strategy"""
        try:
            rsi_trades = trades[trades['Strategy'] == 'RSI']
            macd_trades = trades[trades['Strategy'] == 'MACD']
            ai_trades = trades[trades['Strategy'] == 'AI']
            
            def calc_strategy_metrics(strategy_trades):
                if len(strategy_trades) == 0:
                    return {'winRate': 0, 'profit': 0}
                    
                wins = len(strategy_trades[strategy_trades['Result'] == 'WIN'])
                win_rate = (wins / len(strategy_trades)) * 100
                profit = strategy_trades['PnL'].sum()
                return {
                    'winRate': round(win_rate, 2),
                    'profit': round(profit, 2)
                }
                
            return {
                'rsi': calc_strategy_metrics(rsi_trades),
                'macd': calc_strategy_metrics(macd_trades),
                'ai': calc_strategy_metrics(ai_trades)
            }
            
        except Exception as e:
            print(f"Error calculating strategy performance: {str(e)}")
            return {
                'rsi': {'winRate': 0, 'profit': 0},
                'macd': {'winRate': 0, 'profit': 0},
                'ai': {'winRate': 0, 'profit': 0}
            }
            
    def background_updates(self):
        """Background thread for sending real-time updates"""
        while self.running:
            try:
                # Get current performance metrics
                performance = self.get_performance_metrics('trade_history.csv')
                
                metrics = {
                    'type': 'metrics',
                    'data': {
                        'winRate': performance['win_rate'],
                        'netProfit': performance['net_profit'],
                        'sharpeRatio': performance['sharpe_ratio'],
                        'maxDrawdown': performance['max_drawdown']
                    }
                }
                
                # Get active trades
                trades = pd.read_csv('trade_history.csv') if os.path.exists('trade_history.csv') else pd.DataFrame()
                active_trades = {
                    'type': 'trades',
                    'data': trades.tail(5).to_dict('records')
                }
                
                # Get strategy performance
                strategy_perf = {
                    'type': 'strategy',
                    'data': self.get_strategy_performance(trades)
                }
                
                # Emit updates via WebSocket
                self.socketio.emit('update', metrics)
                self.socketio.emit('update', active_trades)
                self.socketio.emit('update', strategy_perf)
                
                # Update equity curve
                if len(trades) > 0:
                    equity_data = {
                        'type': 'chart',
                        'data': {
                            'time': datetime.now().isoformat(),
                            'value': float(performance['net_profit'])
                        }
                    }
                    self.socketio.emit('update', equity_data)
                
            except Exception as e:
                print(f"Error in background updates: {str(e)}")
            
            self.socketio.sleep(5)  # Update every 5 seconds
            
    def stop(self):
        """Stop the background thread"""
        self.running = False
