# MAGUS PRIME X Trading Bot User Guide

## Introduction

Welcome to MAGUS PRIME X, an advanced AI-powered trading bot designed to help you make informed trading decisions. This guide will walk you through all the features of the system and how to use them effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Configuration](#configuration)
3. [Trading Features](#trading-features)
4. [AI Learning System](#ai-learning-system)
5. [ChatGPT Integration](#chatgpt-integration)
6. [Chart Analysis](#chart-analysis)
7. [Pine Script Indicators](#pine-script-indicators)
8. [Telegram Notifications](#telegram-notifications)
9. [Dynamic Range Profit Model](#dynamic-range-profit-model)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Capital.com API credentials
- OpenAI API key (for ChatGPT integration)
- Telegram Bot Token (for notifications)

### Installation

1. Clone the repository or download the source code
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys (see Configuration section)
4. Run the application:
   ```
   python app.py
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
# Capital.com API credentials
CAPITAL_API_KEY=your_capital_api_key
CAPITAL_ACCOUNT_ID=your_account_id

# OpenAI API key
OPENAI_API_KEY=your_openai_api_key

# Telegram configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
TELEGRAM_ADMIN_IDS=id1,id2,id3

# News API key
NEWS_API_KEY=your_news_api_key
```

## Trading Features

### Market Analysis

The bot analyzes markets using multiple methods:

1. **Technical Analysis**: Uses various indicators to identify trading opportunities.
2. **Machine Learning**: Predicts price movements based on historical data.
3. **News Analysis**: Evaluates market sentiment from news articles.
4. **AI Analysis**: Leverages ChatGPT for market insights.
5. **Chart Pattern Recognition**: Identifies candlestick patterns and key levels.

### Trading Signals

The bot generates trading signals with the following information:

- Entry point
- Take profit targets
- Stop loss level
- Risk/reward ratio
- Confidence score
- Additional context

### Risk Management

Built-in risk management features:

- Position sizing based on account balance
- Maximum drawdown protection
- Stop loss and take profit management
- Risk per trade limitation

## AI Learning System

The AI Learning System continuously improves the bot's trading decisions by:

1. **Recording Trades**: Logs all trading decisions and outcomes.
2. **Analyzing Mistakes**: Identifies patterns in losing trades.
3. **Reinforcement Learning**: Adjusts strategies based on success/failure.
4. **Performance Metrics**: Tracks improvement over time.

To view learning progress:

```
python ai_learning_system.py --metrics
```

## ChatGPT Integration

The ChatGPT integration provides:

1. **Market Analysis**: Natural language descriptions of market conditions.
2. **Trading Recommendations**: AI-generated insights about potential trades.
3. **Strategy Generation**: Creates Pine Script strategies based on current market conditions.
4. **News Interpretation**: Analyzes the potential impact of news events.

To get market analysis:

```
python chatgpt_analyst.py --analyze BTCUSD
```

## Chart Analysis

The Chart Analyzer identifies:

1. **Candlestick Patterns**: Recognizes over 60 different patterns.
2. **Support/Resistance**: Identifies key price levels.
3. **Trend Analysis**: Determines current trend direction and strength.
4. **Visual Charts**: Generates annotated charts with patterns and levels.

To analyze a symbol:

```
python chart_analyzer.py --symbol EURUSD --timeframe 1h
```

## Pine Script Indicators

Integrate TradingView indicators into your trading strategy:

1. **Indicator Import**: Import Pine Script indicators from TradingView.
2. **Parameter Customization**: Adjust indicator parameters.
3. **Signal Generation**: Generate trading signals based on indicators.
4. **Multiple Timeframes**: Apply indicators across different timeframes.

To add a new indicator:

```
python pine_script_integration.py --add indicator.pine
```

## Telegram Notifications

Receive trading alerts and updates via Telegram:

1. **Trading Signals**: Get notifications for new trading opportunities.
2. **Market Warnings**: Receive alerts about significant market events.
3. **Position Updates**: Be notified when trades are opened or closed.
4. **Custom Alerts**: Set up personalized alerts based on your criteria.

Commands available in the Telegram bot:

- `/start` - Subscribe to notifications.
- `/stop` - Unsubscribe from notifications.
- `/status` - Check bot status.
- `/help` - Display help message.

## Dynamic Range Profit Model

The bot uses a dynamic range profit model instead of subscription fees:

1. **Price Range Analysis**: Identifies optimal entry and exit points.
2. **Multiple Take Profit Levels**: Sets multiple profit targets for each trade.
3. **Dynamic Position Sizing**: Adjusts position size based on confidence.
4. **Compounding Logic**: Reinvests profits for exponential growth.

## Troubleshooting

### Common Issues

1. **API Connection Problems**
   - Check your API keys in the `.env` file.
   - Ensure internet connection is stable.
   - Verify API access hasn't been restricted.

2. **No Trading Signals**
   - Check market hours (some markets close on weekends/holidays).
   - Verify signal thresholds in configuration.
   - Ensure enough historical data is available.

3. **Telegram Notifications Not Working**
   - Verify your Telegram bot token.
   - Make sure you've started a chat with the bot.
   - Check that the bot has permission to send messages.

### Getting Help

For additional support:
- Check the documentation in the `docs` folder.
- Review the GitHub issues for known problems.
- Join our community Discord server.

## Advanced Configuration

For experienced users, advanced configuration options are available in `config.json`. This allows you to:

1. Customize indicator parameters.
2. Adjust risk management settings.
3. Configure AI learning parameters.
4. Set up custom trading rules.

---

Thank you for using MAGUS PRIME X! We're continuously improving the system to help you trade more effectively.
