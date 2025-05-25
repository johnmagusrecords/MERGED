# Magus Prime X - AI Powered Trading Bot

![Magus Prime X Logo](logo.svg)

## Overview

Magus Prime X is a sophisticated AI-powered trading bot designed specifically for Capital.com integration. It combines advanced technical analysis with real-time market data to execute trades automatically while providing a modern, user-friendly dashboard interface.

## Features

- **Advanced Trading Algorithm**

  - RSI and MACD-based signal generation
  - Automated trade execution
  - Risk management with dynamic stop-loss
  - Multiple trading modes (Scalping/Swing)

- **Real-time Dashboard**

  - Live portfolio tracking
  - Active trades management
  - Trading signals display
  - Market news with sentiment analysis
  - Customizable TradingView charts

- **Capital.com Integration**

  - Direct API connection
  - Real-time order execution
  - Account management
  - Portfolio synchronization

- **Risk Management**
  - Automated stop-loss
  - Take-profit management
  - Position sizing
  - Risk percentage controls

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Capital.com API credentials

### Desktop App Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/magus-prime-x.git
cd magus-prime-x

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Build desktop application
npm run build

# The installer will be available in the dist folder
```

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run in development mode
npm run dev
```

## Configuration

1. Create a `.env` file in the root directory
2. Add your Capital.com API credentials:

```env
CAPITAL_API_KEY=your_api_key
CAPITAL_IDENTIFIER=your_email
CAPITAL_API_PASSWORD=your_api_password
```

## Usage

### Starting the Bot

1. Launch the Magus Prime X application
2. Connect your Capital.com account
3. Configure trading parameters (optional)
4. Click "Start Bot" to begin trading

### Dashboard Navigation

- **Dashboard**: Overview of portfolio performance and active trades
- **Trades**: Manage and monitor active positions
- **Assets**: View asset prices and performance
- **News**: Market news with AI sentiment analysis

### Trading Controls

- Start/Stop trading
- Edit position parameters
- Close positions manually
- View trading signals

## Safety Features

- Automatic stop-loss on all trades
- Maximum position size limits
- Risk percentage controls
- Emergency stop functionality

## Customization

### Trading Parameters

Edit `.env` file to customize:

- Risk percentage per trade
- Take-profit ratios
- Trading intervals
- Asset selection

### Technical Indicators

Modify `trading_bot.py` to adjust:

- RSI parameters
- MACD settings
- Additional indicators
- Trading logic

## Updates and Maintenance

The application includes automatic updates. When a new version is available, you'll be prompted to install it.

## Support

For issues and feature requests, please create an issue in the GitHub repository.

## License

MIT License - see LICENSE file for details

## Disclaimer

Trading cryptocurrencies carries a high level of risk and may not be suitable for all investors. Before deciding to trade, you should carefully consider your investment objectives, level of experience, and risk appetite.

## Author

Jean Ghanem

---

# MAGUS PRIME X Signal Bot - Final Deployment Guide

This is the final version of the MAGUS PRIME X Signal Dispatcher system.
It sends high-quality, MT5-compatible, GPT-enhanced trading signals to your Telegram group.

---

## ✅ Files & Their Purpose

| File                    | Purpose                                                           |
| ----------------------- | ----------------------------------------------------------------- |
| `signal_dispatcher.py`  | Flask API to receive & send signals + recaps                      |
| `news_monitor.py`       | Grabs sentiment & news from Alpha Vantage + RSS                   |
| `gpt_commentary.py`     | Uses GPT-4 to generate signal commentary                          |
| `send_signal_helper.py` | Easily send signals from bot.py or other modules                  |
| `assets_config.json`    | Custom config for each asset: type, hold, strategy                |
| `templates.py`          | Markdown-safe Telegram formatting                                 |
| `requirements.txt`      | Python packages needed for Render or local use                    |
| `openai_assistant.py`   | Integrates with MAGUS PRIMEX ASSISTANT for advanced AI commentary |

---

## 🧪 Local Testing

1. Create `.env` file:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=@your_group_or_channel
API_KEY=secure123
OPENAI_API_KEY=your_openai_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
```

2. Run locally:

```bash
pip install -r requirements.txt
python signal_dispatcher.py
```

---

## ☁️ Render Deployment

1. Push all files to your GitHub repository
2. Connect GitHub repo to [Render.com](https://render.com/)
3. Set Build Command:

```bash
pip install -r requirements.txt
```

4. Set Start Command:

```bash
python signal_dispatcher.py
```

5. Add environment variables (same as `.env`)
6. Deploy manually 🔥

---

## 🧠 GPT Assistant Integration (Optional)

You can now use GPT-4 to:

- Auto-explain signals
- Detect sentiment
- Suggest recovery trades

These are used automatically via `gpt_commentary.py`.

---

## 🤖 MAGUS PRIMEX ASSISTANT Integration

The system now integrates with OpenAI's Assistants API to provide:

- Advanced market analysis
- Professional trading commentary
- Custom-trained AI insights for your signals

To enable this feature:

1. Run `fix_assistant_imports.bat` to install dependencies
2. Make sure your OpenAI API key is in the `.env` file
3. Test with `run_assistant_test.bat`

---

## ✅ Final Output Format

Every signal includes:

- MT5-compatible symbol
- Asset type (Crypto, Indices, etc)
- Strategy explanation
- Trade mode (Swing, Scalping, etc)
- Holding time
- Market status (if closed)
- Sentiment & live news

---

## 🛠️ Helper Scripts

- `run_signal_dispatcher.bat` - Start the API server
- `test_enhanced_signals.py` - Test signal generation
- `test_openai_api.py` - Test OpenAI connection
- `run_telegram_bot.py` - Run Telegram bot in standalone mode
- `check_status.py` - Check system components status

---

## 📊 Assets Configuration

Edit `assets_config.json` to customize default settings for each trading instrument:

- Asset type (Crypto, Forex, Commodity, Index)
- Default strategy
- Recommended timeframe
- Expected hold duration

---

💬 Questions? Ask your assistant or contact the system developer.
