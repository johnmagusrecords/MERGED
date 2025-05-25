"""
Stubs for GPT commentary, sentiment analysis, and trade commentary.
"""


def generate_gpt_commentary(pair: str, direction: str, strategy: str) -> str:
    """Stub for generating GPT commentary."""
    return f"AI commentary for {pair} {direction} with strategy {strategy}."


def analyze_sentiment(text: str) -> str:
    """Stub for sentiment analysis."""
    return "neutral"


def get_trade_commentary(symbol: str, direction: str, entry: float, stop_loss: float, targets: list, strategy: str) -> str:
    """Stub for fetching trade commentary."""
    return "No trade commentary available."
