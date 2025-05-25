# MAGUS PRIME X - Developer Documentation

## System Architecture

MAGUS PRIME X is built using a hybrid architecture combining:
- Electron.js for the desktop application wrapper
- HTML/CSS/JavaScript for the frontend interface
- Python for trading algorithms and advanced analysis

### Key Components

1. **Chart Analyzer Module**
   - Location: `chart_analyzer.py`
   - Provides comprehensive technical indicator support
   - Handles candlestick pattern detection
   - Implements chart pattern recognition
   - Identifies support/resistance levels
   - Connects with the frontend via the `analyze_market` method

2. **Capital.com API Integration**
   - Location: `capital_com_trader.py`
   - Manages broker connection and authentication
   - Handles order execution and position management
   - Processes market data feeds

3. **Frontend Interface**
   - Main file: `magus_prime_x_unified.html`
   - Styling: `css/complete-styles.css`
   - JavaScript: `js/complete-app.js`
   - Integrates Project-Bolt UI elements with existing functionality

4. **Electron Configuration**
   - Main file: `electron.js`
   - Package configuration: `package.json`

## Development Environment

To set up the development environment:

1. Clone the repository
2. Install Node.js dependencies: `npm install`
3. Install Python dependencies: `pip install -r requirements.txt`
4. Run in development mode: `npm run dev`

## API Reference

### Chart Analyzer API

The Chart Analyzer module exposes these primary methods:

```python
def analyze_market(symbol, timeframe, indicators=None):
    """
    Provides consolidated analysis results and clear trading signals
    
    Args:
        symbol (str): Trading pair or asset symbol
        timeframe (str): Chart timeframe (e.g., '1h', '4h', '1d')
        indicators (list, optional): List of indicators to include
        
    Returns:
        dict: Analysis results including signals and visualization data
    """
```

### Capital.com API

The Capital.com integration is handled through:

```python
def connect_broker(api_key, api_password, api_identifier, api_url):
    """
    Establishes connection to Capital.com
    
    Args:
        api_key (str): Your Capital.com API key
        api_password (str): Your API password
        api_identifier (str): Your API identifier
        api_url (str): API endpoint URL
        
    Returns:
        bool: Connection status
    """
```

## Building and Distribution

To build the application:

1. Update version in `package.json`
2. Run: `npm run build`
3. Distribute the contents of the `dist/win-unpacked` folder

## Project Structure

- `/js`: JavaScript files
- `/css`: Stylesheet files
- `/assets`: Icons and images
- `/python`: Trading algorithms and analysis tools
- `/templates`: HTML templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

---

© 2025 MAGUS PRIME X. All rights reserved.
