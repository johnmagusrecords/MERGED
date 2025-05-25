"""
bot_dev_backup.py — stubs so test_bot.py can import these functions.
"""

from typing import Optional, Dict, Any

def analyze_market(symbol: str) -> Dict[str, Any]:
    """
    Dummy stub for TestBot.test_analyze_market.
    """
    return {"signal": "BUY", "confidence": 0.5}

def execute_trade(side: str, symbol: str, price: float) -> Optional[str]:
    """
    Dummy stub for TestBot.test_execute_trade.
    """
    return "mock_deal_ref"
