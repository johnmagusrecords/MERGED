def generate_recap_message(pair, result, exit_price, notes=None, entry=None, targets_hit=None):
    """
    Generate a recap message for a trading signal.

    Args:
        pair (str): Trading pair/symbol.
        result (str): Trade result ("WIN", "LOSS", "BREAK EVEN").
        exit_price (float): Exit price.
        notes (str, optional): Additional notes.
        entry (float, optional): Entry price.
        targets_hit (dict, optional): Dictionary indicating which targets were hit.

    Returns:
        str: Formatted recap message.
    """
    recap_msg = f"📈 Recap for {pair}:\n"
    recap_msg += f"Result: {result}\n"
    recap_msg += f"Exit Price: {exit_price:.2f}\n"
    
    if entry is not None:
        recap_msg += f"Entry Price: {entry:.2f}\n"
    
    if targets_hit:
        recap_msg += "Targets Hit:\n"
        for target, hit in targets_hit.items():
            recap_msg += f" - {target}: {'✅' if hit else '❌'}\n"
    
    if notes:
        recap_msg += f"Notes: {notes}\n"
    
    return recap_msg.strip()
