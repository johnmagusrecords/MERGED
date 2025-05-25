# MAGUS PRIME X - AI Trading Bot

An advanced algorithmic trading bot with AI-powered decision making.

## Features

- Multiple trading strategies
- Risk management system
- Real-time market analysis
- Telegram integration
- Comprehensive testing suite

## Setup

1. Install dependencies:
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`:
   - `VITE_SUPABASE_URL`: Your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anonymous key
   - `VITE_TELEGRAM_TOKEN`: Your Telegram bot token
   - `VITE_TELEGRAM_CHAT_ID`: Your Telegram chat ID
   - `VITE_CAPITAL_API_KEY`: Your Capital.com API key
   - `VITE_CAPITAL_API_IDENTIFIER`: Your Capital.com API identifier
   - `VITE_CAPITAL_API_PASSWORD`: Your Capital.com API password
   - Other trading-related variables as specified in `.env.example`

3. Deploy Supabase Edge Functions:
   - Navigate to your Supabase project
   - Deploy the Telegram edge function from `/supabase/functions/telegram`
   - Set the required environment variables in Supabase dashboard

4. Run the bot:
   ```bash
   # Start web interface
   npm run dev
   
   # Start trading bot
   python bot.py
   ```

## Project Structure

- `bot.py`: Main AI bot logic
- `config.py`: Configuration settings
- `strategies/`: Trading strategies
- `risk_management/`: Risk management modules
- `data/`: Market data storage
- `tests/`: Unit tests
- `src/`: React frontend application

## Testing

Run frontend tests:
```bash
npm test
```

Run backend tests:
```bash
pytest tests/
```

## Dependencies

- @babel/runtime: For async/await support
- regenerator-runtime: For generator functions
- Other dependencies as listed in package.json and requirements.txt

## Troubleshooting

If you encounter issues with the Capital.com API or Telegram integration:

1. Check that your API credentials are correct in the `.env` file
2. Verify that your Supabase Edge Function is deployed correctly
3. For development, the application uses mock data by default

## License

Proprietary software. All rights reserved.