import os
from utils.ai_commentary import generate_gpt_commentary
from dotenv import load_dotenv

# ...existing code...

def send_signal(self, signal_data, telegram_bot=None):
    """
    Sends a trading signal to Telegram and other destinations.
    """
    # ...existing code...
    
    # Extract relevant data for commentary
    asset = signal_data.get('symbol', 'Unknown')
    direction = signal_data.get('side', 'Unknown')
    strategy = signal_data.get('strategy', 'Unknown')
    
    # Compile indicators summary from available data
    indicators = []
    if 'rsi' in signal_data:
        indicators.append(f"RSI: {signal_data['rsi']}")
    if 'ema_cross' in signal_data and signal_data['ema_cross']:
        indicators.append("EMA Crossover")
    if 'macd' in signal_data and signal_data['macd'].get('crossover', False):
        indicators.append("MACD Crossover")
    if 'volume_spike' in signal_data and signal_data['volume_spike']:
        indicators.append("Volume Spike")
    
    indicators_summary = ", ".join(indicators) or "Technical analysis"
    
    # Generate AI commentary if enabled
    if os.getenv("ENABLE_COMMENTARY", "False").lower() == "true" and telegram_bot:
        comment = generate_gpt_commentary(asset, direction, strategy, indicators_summary)
        
        if comment:
            telegram_bot.send_message(
                chat_id=os.getenv("TELEGRAM_SIGNAL_CHAT_ID"),
                text=f"🧠 *Trade Commentary*\n{comment}",
                parse_mode="Markdown"
            )
    
    # ...existing code...
