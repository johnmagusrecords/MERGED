# Features

<!-- ...existing code... -->

## AI Trade Commentary

MAGUS PRIME X can generate AI-powered explanations for trade signals using OpenAI's GPT-4 model. This helps traders understand the reasoning behind each signal.

### Configuration

1. Add your OpenAI API key to the `.env` file:

   ```
   OPENAI_API_KEY=your_api_key_here
   ENABLE_COMMENTARY=True
   ```

2. The system will automatically generate commentary for each signal and send it to your Telegram channel.

### Example Output

```
🧠 Trade Commentary
Strong BUY signal for BTC/USDT triggered by RSI reversal from oversold territory and MACD crossover indicating bullish momentum (87% confidence)
```

## Telegram Trade Commands

Control your trading bot directly through Telegram with these commands:

| Command             | Description                                                |
| ------------------- | ---------------------------------------------------------- |
| `/pausebot`         | Pause all trading operations                               |
| `/resumebot`        | Resume automated trading                                   |
| `/closeall`         | Close all open positions                                   |
| `/forcebuy SYMBOL`  | Force a buy order for SYMBOL (e.g., `/forcebuy BTCUSDT`)   |
| `/forcesell SYMBOL` | Force a sell order for SYMBOL (e.g., `/forcesell ETHUSDT`) |

### Setup

1. These commands are automatically registered when the bot starts.
2. Only authorized Telegram users (as configured in your .env) can use these commands.
3. All command executions are logged in the application logs.

## Auto-Recovery Mode

MAGUS PRIME X includes an intelligent recovery system that can automatically detect failed trades (like Stop Loss hits) and attempt to re-enter the market when conditions are favorable.

### How it works

1. When a Stop Loss is triggered, the recovery system is activated
2. The bot monitors the asset for favorable re-entry conditions
3. Up to 3 attempts are made (configurable) to find a valid setup
4. When a valid pattern is detected, a new "Recovery Trade" is executed with improved parameters

### Recovery Signal Validation

Recovery trades are only executed when specific confirmation criteria are met:

- Trend reversal patterns on multiple timeframes
- Volume confirmation
- RSI indicator validation
- Market direction alignment

### Configuration

Enable recovery mode in your `.env` file:

```
ENABLE_RECOVERY_MODE=True
RECOVERY_MAX_ATTEMPTS=3
RECOVERY_WAIT_MINUTES=5
```

### Example Output

```
🔄 Recovery Trade Monitoring
🔹 Asset: BTC/USDT
🔹 Direction: BUY

✅ Recovery Trade Confirmed
🔹 Asset: BTC/USDT
🔹 Direction: BUY
🔹 Reason: Bullish reversal with volume confirmation
🛑 SL: -2.50%
✅ TP: 3.75%
```

<!-- ...existing code... -->
