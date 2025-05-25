import os
import time
import threading
import logging
import requests
import pandas as pd
import numpy as np
import talib
import json
import re
import uuid
import hashlib
import secrets
from flask import Flask, render_template_string, request, redirect, jsonify, send_from_directory, session, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from datetime import datetime, timedelta
import telegram
import asyncio
from collections import defaultdict

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Constants from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "1234")
STRATEGY_MODE = os.getenv("STRATEGY_MODE", "Balanced")

# User roles
ROLES = {
    "admin": {"can_change_strategy": True, "can_clear_history": True, "can_manage_users": True},
    "trader": {"can_change_strategy": True, "can_clear_history": False, "can_manage_users": False},
    "guest": {"can_change_strategy": False, "can_clear_history": False, "can_manage_users": False}
}

# Sample users (in production, this should be in a database)
USERS = {
    "admin": {
        "username": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "display_name": "Administrator"
    },
    "trader": {
        "username": "trader",
        "password": hashlib.sha256("trader123".encode()).hexdigest(),
        "role": "trader",
        "display_name": "Lead Trader"
    },
    "guest": {
        "username": "guest",
        "password": hashlib.sha256("guest123".encode()).hexdigest(),
        "role": "guest",
        "display_name": "Guest User"
    }
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username, role, display_name):
        self.id = username
        self.username = username
        self.role = role
        self.display_name = display_name
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_trader(self):
        return self.role == 'trader'
    
    def is_guest(self):
        return self.role == 'guest'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        user_data = USERS[user_id]
        return User(user_id, user_data['role'], user_data['display_name'])
    return None

# Initialize Telegram bot
telegram_bot = telegram.Bot(token=TELEGRAM_TOKEN)

async def send_telegram_async(message):
    """Async function to send Telegram messages"""
    try:
        await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {str(e)}")

def send_telegram_message(message):
    """Wrapper to run async Telegram message in sync context"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_telegram_async(message))
        loop.close()
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {str(e)}")

def load_trade_history():
    """Load trade history from CSV"""
    if os.path.exists("trade_history.csv"):
        df = pd.read_csv("trade_history.csv")
        df['Time'] = pd.to_datetime(df['Time'])
        return df
    return pd.DataFrame(columns=["Time", "Symbol", "Action", "Entry", "TP", "SL", "Result", "PnL"])

def calculate_metrics(trades_df):
    """Calculate trading metrics"""
    if trades_df.empty:
        return {
            'strategy': STRATEGY_MODE,
            'interval': '5 min',
            'paused': False,
            'total_trades': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'max_drawdown': 0,
            'daily_pnl': [],
            'cumulative_pnl': 0,
            'today_pnl': 0
        }

    # Calculate basic metrics
    wins = trades_df[trades_df['Result'] == 'win']
    losses = trades_df[trades_df['Result'] == 'loss']
    
    total_trades = len(trades_df)
    win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
    
    avg_win = wins['PnL'].mean() if not wins.empty else 0
    avg_loss = abs(losses['PnL'].mean()) if not losses.empty else 0
    
    # Calculate profit factor
    total_profit = wins['PnL'].sum() if not wins.empty else 0
    total_loss = abs(losses['PnL'].sum()) if not losses.empty else 0
    profit_factor = total_profit / total_loss if total_loss != 0 else float('inf')
    
    # Calculate drawdown
    trades_df['Cumulative'] = trades_df['PnL'].cumsum()
    trades_df['Peak'] = trades_df['Cumulative'].cummax()
    trades_df['Drawdown'] = trades_df['Peak'] - trades_df['Cumulative']
    max_drawdown = trades_df['Drawdown'].max()
    
    # Daily PnL
    daily_pnl = trades_df.groupby(trades_df['Time'].dt.date)['PnL'].sum()
    
    # Today's PnL
    today = datetime.now().date()
    today_pnl = daily_pnl.get(today, 0)
    
    return {
        'strategy': STRATEGY_MODE,
        'interval': '5 min',
        'paused': False,
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'profit_factor': round(profit_factor, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'max_drawdown': round(max_drawdown, 2),
        'daily_pnl': daily_pnl.to_dict(),
        'cumulative_pnl': round(trades_df['PnL'].sum(), 2),
        'today_pnl': round(today_pnl, 2)
    }

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Legacy web interface for the dashboard"""
    return redirect('/dashboard/react')

@app.route('/dashboard/react')
@login_required
def dashboard_react():
    """Modern React dashboard that reads directly from CSV with Capital.com-style UI"""
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MAGUS PRIME X - Trading Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <link href="/static/css/style.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <!-- Loading Overlay -->
        <div class="loading-overlay" id="loadingOverlay">
            <img src="/static/images/logo.svg" alt="MAGUS PRIME X" class="logo-animation">
            <div class="text-gold mt-3">Loading Dashboard...</div>
        </div>
        
        <!-- Navbar -->
        <nav class="navbar navbar-expand-lg">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <img src="/static/images/logo.svg" alt="MAGUS PRIME X" class="navbar-logo">
                    <span>MAGUS PRIME X</span>
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item">
                            <a class="nav-link active" href="#"><i class="bi bi-graph-up-arrow"></i> Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#"><i class="bi bi-gear"></i> Settings</a>
                        </li>
                    </ul>
                    <div class="d-flex align-items-center">
                        <span class="me-3">
                            <span class="badge bg-success" id="connectionStatus">Connected</span>
                            <span class="ms-2">Auto-refresh <div class="refresh-indicator" id="refreshIndicator"></div></span>
                        </span>
                        <div class="user-profile">
                            <div class="user-avatar">{{ current_user.display_name[0] }}</div>
                            <div>
                                <div class="user-name">{{ current_user.display_name }}</div>
                                <div class="user-role">{{ current_user.role|capitalize }}</div>
                            </div>
                        </div>
                        <a href="/logout" class="btn btn-outline-light btn-sm ms-3">
                            <i class="bi bi-box-arrow-right"></i> Logout
                        </a>
                    </div>
                </div>
            </div>
        </nav>
        
        <!-- Main Content -->
        <div class="container-fluid py-4">
            <!-- Market Panel -->
            <div class="market-panel" id="marketPanel">
                <!-- Market items will be dynamically inserted here -->
            </div>
            
            <!-- Summary Cards -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-graph-up"></i> Win Rate
                        </div>
                        <div class="card-body text-center">
                            <div class="metrics-value" id="win-rate">0.00%</div>
                            <div class="metrics-label">Success Rate</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-cash"></i> Net PnL
                        </div>
                        <div class="card-body text-center">
                            <div class="metrics-value" id="net-pnl">$0.00</div>
                            <div class="metrics-label">Overall Performance</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-arrow-repeat"></i> Total Trades
                        </div>
                        <div class="card-body text-center">
                            <div class="metrics-value" id="trade-count">0</div>
                            <div class="metrics-label">Completed Trades</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-lightning"></i> Strategy
                        </div>
                        <div class="card-body text-center">
                            <div class="metrics-value" id="strategy-display">Balanced</div>
                            <div class="metrics-label">Current Mode</div>
                            
                            {% if current_user.has_permission('can_change_strategy') %}
                            <div class="mt-2">
                                <div class="btn-group btn-group-sm" role="group">
                                    <button type="button" class="btn btn-outline-success strategy-btn" data-strategy="Safe">Safe</button>
                                    <button type="button" class="btn btn-outline-primary strategy-btn" data-strategy="Balanced">Balanced</button>
                                    <button type="button" class="btn btn-outline-danger strategy-btn" data-strategy="Aggressive">Aggressive</button>
                                </div>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Chart and Trade Log -->
            <div class="row">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div><i class="bi bi-bar-chart-line"></i> Performance Chart</div>
                            <div>
                                <span class="badge bg-success">Take Profit</span>
                                <span class="badge bg-danger">Stop Loss</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div style="height: 400px;">
                                <canvas id="performanceChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div><i class="bi bi-journal-text"></i> Recent Trades</div>
                            {% if current_user.has_permission('can_clear_history') %}
                            <button class="btn btn-sm btn-outline-danger" id="clear-history-btn">
                                <i class="bi bi-trash"></i> Clear
                            </button>
                            {% endif %}
                        </div>
                        <div class="card-body p-0">
                            <table class="table table-hover mb-0">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Symbol</th>
                                        <th>Action</th>
                                        <th>Result</th>
                                    </tr>
                                </thead>
                                <tbody id="trade-table-body">
                                    <tr>
                                        <td colspan="4" class="text-center py-4 text-muted">No trades found</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Capital.com Integration Status -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-hdd-network"></i> Capital.com API Status
                        </div>
                        <div class="card-body">
                            <div class="alert alert-success" role="alert">
                                <i class="bi bi-check-circle-fill"></i> Connected to Capital.com API successfully
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="card bg-dark">
                                        <div class="card-body">
                                            <h5 class="card-title text-gold">Account Balance</h5>
                                            <h3 class="text-light" id="account-balance">$10,000.00</h3>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card bg-dark">
                                        <div class="card-body">
                                            <h5 class="card-title text-gold">Active Positions</h5>
                                            <h3 class="text-light" id="active-positions">0</h3>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card bg-dark">
                                        <div class="card-body">
                                            <h5 class="card-title text-gold">Daily PnL</h5>
                                            <h3 class="text-light" id="daily-pnl">$0.00</h3>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // MAGUS PRIME X Dashboard Integration with Auto-Refresh
            document.addEventListener('DOMContentLoaded', function() {
                // Initialize Chart.js
                const ctx = document.getElementById('performanceChart').getContext('2d');
                
                // Helper functions
                function formatDate(dateString) {
                    const date = new Date(dateString);
                    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
                }
                
                function calculateWinRate(trades) {
                    const completedTrades = trades.filter(t => t.result === "WIN" || t.result === "LOSS");
                    const wins = completedTrades.filter((t) => t.result === "WIN").length;
                    const total = completedTrades.length;
                    return total > 0 ? ((wins / total) * 100).toFixed(2) : "0.00";
                }
                
                function calculatePnL(trades) {
                    let pnl = 0;
                    for (const t of trades) {
                        if (t.result === "WIN") {
                            pnl += parseFloat(t.profit || 0);
                        } else if (t.result === "LOSS") {
                            pnl -= Math.abs(parseFloat(t.loss || 0));
                        }
                    }
                    return pnl.toFixed(2);
                }
                
                // Sample market data (will be replaced with real data in production)
                const marketData = [
                    { symbol: "EUR/USD", price: "1.0825", change: "+0.25%" },
                    { symbol: "GBP/USD", price: "1.2650", change: "-0.15%" },
                    { symbol: "USD/JPY", price: "149.85", change: "+0.42%" },
                    { symbol: "BTC/USD", price: "62,458.50", change: "+2.35%" },
                    { symbol: "ETH/USD", price: "3,225.75", change: "+1.85%" },
                    { symbol: "XAU/USD", price: "2,358.20", change: "+0.68%" },
                    { symbol: "NASDAQ", price: "17,650.80", change: "-0.12%" },
                    { symbol: "S&P 500", price: "5,245.75", change: "+0.33%" }
                ];
                
                // Populate market panel
                const marketPanel = document.getElementById('marketPanel');
                marketData.forEach(item => {
                    const isPositive = item.change.startsWith('+');
                    marketPanel.innerHTML += `
                        <div class="market-item">
                            <div class="market-symbol">${item.symbol}</div>
                            <div class="market-price">${item.price}</div>
                            <div class="market-change ${isPositive ? 'positive' : 'negative'}">${item.change}</div>
                        </div>
                    `;
                });
                
                // Create the performance chart
                let performanceChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [
                            {
                                label: 'Take Profit',
                                data: [],
                                borderColor: '#28a745',
                                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                                tension: 0.3,
                                fill: true
                            },
                            {
                                label: 'Stop Loss',
                                data: [],
                                borderColor: '#dc3545',
                                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                                tension: 0.3,
                                fill: true
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        plugins: {
                            legend: {
                                display: false,
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false,
                            }
                        },
                        scales: {
                            y: {
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)',
                                },
                                ticks: {
                                    color: '#aaa'
                                }
                            },
                            x: {
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)',
                                },
                                ticks: {
                                    color: '#aaa',
                                    maxRotation: 45,
                                    minRotation: 45
                                }
                            }
                        }
                    }
                });
                
                // Strategy change handler
                document.querySelectorAll('.strategy-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        const strategy = this.getAttribute('data-strategy');
                        
                        fetch('/api/strategy', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ strategy: strategy }),
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                // Update UI
                                document.querySelectorAll('.strategy-btn').forEach(btn => {
                                    btn.classList.remove('btn-success', 'btn-primary', 'btn-danger');
                                    btn.classList.add('btn-outline-secondary');
                                });
                                
                                this.classList.remove('btn-outline-secondary');
                                if (strategy === 'Safe') {
                                    this.classList.add('btn-success');
                                } else if (strategy === 'Balanced') {
                                    this.classList.add('btn-primary');
                                } else if (strategy === 'Aggressive') {
                                    this.classList.add('btn-danger');
                                }
                                
                                document.getElementById('strategy-display').textContent = strategy;
                            }
                        })
                        .catch(err => console.error('Error changing strategy:', err));
                    });
                });
                
                // Clear history handler
                const clearHistoryBtn = document.getElementById('clear-history-btn');
                if (clearHistoryBtn) {
                    clearHistoryBtn.addEventListener('click', function() {
                        if (confirm('Are you sure you want to clear trade history?')) {
                            fetch('/api/clear-history', { 
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    // Update table
                                    document.getElementById('trade-table-body').innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">No trades found</td></tr>';
                                    
                                    // Update chart
                                    performanceChart.data.labels = [];
                                    performanceChart.data.datasets[0].data = [];
                                    performanceChart.data.datasets[1].data = [];
                                    performanceChart.update();
                                    
                                    // Update summary
                                    document.getElementById('trade-count').textContent = '0';
                                    document.getElementById('win-rate').textContent = '0.00%';
                                    document.getElementById('net-pnl').textContent = '$0.00';
                                }
                            })
                            .catch(err => console.error('Error clearing history:', err));
                        }
                    });
                }
                
                // Auto-refresh functionality
                let refreshInterval = 10000; // 10 seconds
                let refreshTimer;
                let refreshIndicator = document.getElementById('refreshIndicator');
                
                function startAutoRefresh() {
                    refreshData();
                    refreshTimer = setInterval(refreshData, refreshInterval);
                    refreshIndicator.style.display = 'inline-block';
                }
                
                function stopAutoRefresh() {
                    clearInterval(refreshTimer);
                    refreshIndicator.style.display = 'none';
                }
                
                // Function to refresh data
                function refreshData() {
                    console.log('Refreshing data...');
                    Promise.all([
                        fetch('/trade-history').then(res => res.json()),
                        fetch('/api/metrics').then(res => res.json())
                    ])
                    .then(([trades, metrics]) => {
                        // Update chart data
                        if (trades.length > 0) {
                            performanceChart.data.labels = trades.map(t => new Date(t.Time).toLocaleTimeString());
                            performanceChart.data.datasets[0].data = trades.map(t => parseFloat(t.TP || 0));
                            performanceChart.data.datasets[1].data = trades.map(t => parseFloat(t.SL || 0));
                            performanceChart.update();
                        }
                        
                        // Update trade table
                        const tableBody = document.getElementById('trade-table-body');
                        if (trades.length > 0) {
                            tableBody.innerHTML = trades.slice(0, 10).map((t, idx) => `
                                <tr>
                                    <td>${new Date(t.Time).toLocaleTimeString()}</td>
                                    <td>${t.Symbol}</td>
                                    <td class="${t.Action === 'BUY' ? 'text-success' : 'text-danger'}">${t.Action}</td>
                                    <td>
                                        ${t.Result === 'WIN' 
                                            ? '<span class="win-badge">WIN</span>' 
                                            : t.Result === 'LOSS' 
                                                ? '<span class="loss-badge">LOSS</span>' 
                                                : '<span class="badge bg-secondary">OPEN</span>'}
                                    </td>
                                </tr>
                            `).join('');
                        } else {
                            tableBody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">No trades found</td></tr>';
                        }
                        
                        // Update summary
                        document.getElementById('trade-count').textContent = trades.length;
                        const winRate = calculateWinRate(trades);
                        document.getElementById('win-rate').textContent = winRate + '%';
                        document.getElementById('win-rate').className = 'metrics-value ' + (parseFloat(winRate) > 50 ? 'text-success' : 'text-danger');
                        
                        const pnl = calculatePnL(trades);
                        document.getElementById('net-pnl').textContent = '$' + pnl;
                        document.getElementById('net-pnl').className = 'metrics-value ' + (parseFloat(pnl) > 0 ? 'text-success' : 'text-danger');
                        
                        // Update Capital.com status
                        if (metrics) {
                            document.getElementById('account-balance').textContent = '$' + (metrics.account_balance || '10,000.00');
                            document.getElementById('active-positions').textContent = metrics.active_positions || '0';
                            document.getElementById('daily-pnl').textContent = '$' + (metrics.daily_pnl || '0.00');
                            document.getElementById('strategy-display').textContent = metrics.strategy || 'Balanced';
                        }
                    })
                    .catch(err => {
                        console.error('Error refreshing data:', err);
                        document.getElementById('connectionStatus').className = 'badge bg-danger';
                        document.getElementById('connectionStatus').textContent = 'Disconnected';
                    });
                }
                
                // Hide loading overlay after page is fully loaded
                setTimeout(function() {
                    const overlay = document.getElementById('loadingOverlay');
                    overlay.style.opacity = '0';
                    setTimeout(function() {
                        overlay.style.display = 'none';
                    }, 500);
                }, 1500);
                
                // Start auto-refresh when page loads
                startAutoRefresh();
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/trade-history')
@login_required
def trade_history():
    """API endpoint for direct CSV trade history"""
    if os.path.exists("trade_history.csv"):
        df = pd.read_csv("trade_history.csv").tail(100)
        return jsonify(df.to_dict(orient="records"))
    return jsonify([])

@app.route('/api/metrics')
@login_required
def get_metrics():
    """API endpoint for metrics"""
    trades_df = load_trade_history()
    metrics = calculate_metrics(trades_df)
    return jsonify(metrics)

@app.route('/api/trades')
@login_required
def get_trades():
    """API endpoint for trades (legacy)"""
    # Redirect to new endpoint
    return redirect('/trade-history')

@app.route('/api/strategy', methods=['POST'])
@login_required
def change_strategy():
    """API endpoint to change trading strategy"""
    global STRATEGY_MODE
    
    try:
        data = request.json
        if not data or 'strategy' not in data:
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400
        
        strategy = data['strategy']
        if strategy not in ['Safe', 'Balanced', 'Aggressive']:
            return jsonify({'success': False, 'error': 'Invalid strategy'}), 400
        
        # Update environment variable
        STRATEGY_MODE = strategy
        
        # Update .env file
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as file:
                env_lines = file.readlines()
            
            with open(env_path, 'w') as file:
                strategy_updated = False
                for line in env_lines:
                    if line.startswith('STRATEGY_MODE='):
                        file.write(f'STRATEGY_MODE={strategy}\n')
                        strategy_updated = True
                    else:
                        file.write(line)
                
                # Add STRATEGY_MODE if it doesn't exist
                if not strategy_updated:
                    file.write(f'\nSTRATEGY_MODE={strategy}\n')
        
        # Reload environment variables
        load_dotenv()
        
        # Send notification
        send_telegram_message(f"🔄 Strategy changed to: {strategy}")
        
        return jsonify({'success': True, 'strategy': strategy})
    
    except Exception as e:
        logging.error(f"Error changing strategy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clear-history', methods=['POST'])
@login_required
def clear_history():
    """API endpoint to clear trade history"""
    try:
        # Check if trade history exists
        if os.path.exists("trade_history.csv"):
            # Create backup of trade history
            backup_path = f"trade_history_backup_{int(time.time())}.csv"
            os.rename("trade_history.csv", backup_path)
            
            # Create empty trade history file
            pd.DataFrame(columns=["Time", "Symbol", "Action", "Entry", "TP", "SL", "Result", "PnL"]).to_csv("trade_history.csv", index=False)
            
            # Send notification
            send_telegram_message(f"🗑️ Trade history cleared. Backup saved as {backup_path}")
            
            return jsonify({'success': True, 'backup': backup_path})
        
        return jsonify({'success': False, 'error': 'No trade history found'})
    
    except Exception as e:
        logging.error(f"Error clearing history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt for: {username}")
        
        # Hard-coded credentials for reliability
        if username == 'admin' and password == 'admin123':
            user = User('admin', 'admin', 'Administrator')
            login_user(user)
            print(f"Login successful for admin")
            return redirect('/dashboard/react')
        elif username == 'trader' and password == 'trader123':
            user = User('trader', 'trader', 'Lead Trader')
            login_user(user)
            print(f"Login successful for trader")
            return redirect('/dashboard/react')
        elif username == 'guest' and password == 'guest123':
            user = User('guest', 'guest', 'Guest User')
            login_user(user)
            print(f"Login successful for guest")
            return redirect('/dashboard/react')
        else:
            error_message = 'Invalid username or password'
            print(f"Login failed for {username}")
            return render_template_string(login_template(error=error_message))
    
    return render_template_string(login_template())

def login_template(error=None):
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MAGUS PRIME X - Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            body {
                background-color: #121212;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: 'Roboto', sans-serif;
                overflow: hidden;
            }
            .login-container {
                background-color: #1e1e1e;
                border-radius: 8px;
                padding: 30px;
                width: 400px;
                max-width: 90%;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
                position: relative;
                z-index: 1;
            }
            .login-logo {
                width: 80px;
                height: 80px;
                margin: 0 auto 20px;
                display: block;
            }
            .login-title {
                color: #ffc107;
                text-align: center;
                margin-bottom: 20px;
                font-size: 24px;
            }
            .btn-gold {
                background-color: #ffc107;
                border-color: #ffc107;
                color: #121212;
                font-weight: bold;
            }
            .btn-gold:hover {
                background-color: #d4af37;
                border-color: #d4af37;
                color: #121212;
            }
            .form-control {
                background-color: #333;
                border-color: #444;
                color: #fff;
            }
            .form-control:focus {
                background-color: #333;
                border-color: #ffc107;
                color: #fff;
                box-shadow: 0 0 0 0.25rem rgba(255, 193, 7, 0.25);
            }
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #121212;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                transition: opacity 0.5s ease-in-out;
            }
            .logo-animation {
                width: 120px;
                height: 120px;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% {
                    transform: scale(0.95);
                    filter: drop-shadow(0 0 5px rgba(212, 175, 55, 0.5));
                }
                70% {
                    transform: scale(1);
                    filter: drop-shadow(0 0 20px rgba(212, 175, 55, 0.8));
                }
                100% {
                    transform: scale(0.95);
                    filter: drop-shadow(0 0 5px rgba(212, 175, 55, 0.5));
                }
            }
            .text-gold {
                color: #ffc107;
                font-weight: 500;
            }
        </style>
    </head>
    <body>
        <div class="loading-overlay" id="loadingOverlay">
            <img src="/static/images/logo.svg" alt="MAGUS PRIME X" class="logo-animation">
            <div class="text-gold mt-3">Loading...</div>
        </div>
        
        <div class="login-container">
            <img src="/static/images/logo.svg" alt="MAGUS PRIME X" class="login-logo">
            <h2 class="login-title">MAGUS PRIME X</h2>
            
            {% if error %}
            <div class="alert alert-danger" role="alert">
                {{ error }}
            </div>
            {% endif %}
            
            <form action="/login" method="post" class="mt-4">
                <div class="mb-3">
                    <label for="username" class="form-label text-light">Username</label>
                    <input type="text" class="form-control" id="username" name="username" required>
                </div>
                <div class="mb-4">
                    <label for="password" class="form-label text-light">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <div class="d-grid">
                    <button type="submit" class="btn btn-gold">Login</button>
                </div>
                <div class="mt-3 text-center text-secondary">
                    <small>Default accounts: admin/admin123, trader/trader123, guest/guest123</small>
                </div>
            </form>
        </div>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Hide loading overlay after page is fully loaded
                setTimeout(function() {
                    const overlay = document.getElementById('loadingOverlay');
                    overlay.style.opacity = '0';
                    setTimeout(function() {
                        overlay.style.display = 'none';
                    }, 500);
                }, 1500);
            });
        </script>
    </body>
    </html>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == '__main__':
    try:
        # Send startup notification
        send_telegram_message("🚀 MAGUS PRIME X Bot Dashboard Started\n"
                             f"📊 Dashboard: http://localhost:5000/dashboard")
        
        # Get local IP for mobile access
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            send_telegram_message(f"📱 Mobile access: http://{local_ip}:5000/dashboard")
        except:
            pass
        
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Error starting server: {str(e)}")
        raise
