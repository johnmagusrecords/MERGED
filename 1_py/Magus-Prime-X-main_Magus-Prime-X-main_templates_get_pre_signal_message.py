def get_pre_signal_message(pair, direction=None, strategy=None, timeframe=None):
    """
    Generate a pre-signal message for a trading alert.

    Args:
        pair (str): Trading pair/symbol.
        direction (str, optional): Direction of the trade (BUY or SELL).
        strategy (str, optional): Trading strategy.
        timeframe (str, optional): Timeframe for the trade.

    Returns:
        str: Formatted pre-signal message.
    """
    alert_text = f"🚨 *Incoming Signal Alert*\nPreparing high-accuracy trade setup for *{pair}*..."
    
    if direction:
        alert_text += f"\nDirection: *{direction}*"
    
    if strategy:
        alert_text += f"\nStrategy: *{strategy}*"
    
    if timeframe:
        alert_text += f"\nTimeframe: *{timeframe}*"
    
    return alert_text.strip()
