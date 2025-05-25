import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_gpt_commentary(asset, direction, strategy, indicators_summary):
    """
    Uses OpenAI to generate a short explanation of the signal.
    
    Args:
        asset (str): The trading asset/pair (e.g., "BTC/USDT")
        direction (str): "BUY" or "SELL"
        strategy (str): Name of the strategy that generated the signal
        indicators_summary (str): Summary of indicator values that triggered the signal
        
    Returns:
        str: A one-line explanation with confidence level
    """
    try:
        # Check if commentary is enabled
        if os.getenv("ENABLE_COMMENTARY", "False").lower() != "true":
            return None
            
        prompt = (
            f"Explain this {direction} trade signal for {asset} based on the following:\n"
            f"Strategy: {strategy}\n"
            f"Indicators Summary: {indicators_summary}\n"
            f"Output a 1-line explanation with a confidence level (e.g., 85%)."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150,
        )
        commentary = response['choices'][0]['message']['content']
        return commentary.strip()

    except Exception as e:
        return f"GPT Commentary unavailable: {str(e)}"
