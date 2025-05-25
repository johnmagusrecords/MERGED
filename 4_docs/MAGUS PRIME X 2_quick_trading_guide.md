# MAGUS PRIME X Trading Bot - Quick Guide

## Access Points

- **Dashboard**: http://127.0.0.1:5000/dashboard
- **API Documentation**: http://127.0.0.1:5000/docs

## Common Commands

### Via Telegram

- `/status` - Get bot status and current positions
- `/signal SYMBOL` - Get trading signal for a specific symbol
- `/forcebuy SYMBOL [TP] [SL]` - Force a buy order
- `/forcesell SYMBOL [TP] [SL]` - Force a sell order
- `/pause` - Pause all trading
- `/resume` - Resume trading

### Via Dashboard

1. Login with your dashboard password (default: 1234)
2. View active positions and performance metrics
3. Use the control panel to:
   - Start/stop automated trading
   - Search for trading signals
   - Manually execute trades
   - Adjust risk parameters

## Trading Signal Examples

Send a trading signal using the send_signal helper:

```python
from send_signal_helper import send_signal

# Example GOLD signal
send_signal(
    pair="GOLD",
    entry=3110.50,
    stop_loss=3095.75,
    tp1=3125.25,
    tp2=3140.00,
    tp3=3160.50,
    timeframe="1h",
    type_="Breakout"
)

# Example BTC signal
send_signal(
    pair="BTCUSD",
    entry=71250.50,
    stop_loss=69950.75,
    tp1=73250.25,
    timeframe="4h",
    type_="Trend Following"
)
```

## Troubleshooting

- If authentication fails, run `python auth_diagnostic.py`
- For signal sending issues, run `python test_enhanced_signals.py`
- Check the log files in the project directory for error details
