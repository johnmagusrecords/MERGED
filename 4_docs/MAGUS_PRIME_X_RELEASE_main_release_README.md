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
