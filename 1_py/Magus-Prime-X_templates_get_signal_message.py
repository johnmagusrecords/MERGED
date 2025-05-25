def get_signal_message(symbol, direction, entry, stop_loss, tp1, tp2, tp3,
                       timeframe, type_, strategy_name, hold_time, platform,
                       commentary, category):
    """
    Format the trading signal message with all provided details.

    Args:
        symbol (str): Trading pair
        direction (str): BUY or SELL
        entry (float): Entry price
        stop_loss (float): SL
        tp1, tp2, tp3 (float): Take profit levels
        timeframe (str): Timeframe
        type_ (str): Strategy type
        strategy_name (str): Name of the strategy
        hold_time (str): Expected duration
        platform (str): Broker/platform
        commentary (dict): Additional insights
        category (str): Asset type

    Returns:
        str: Formatted message
    """
    message = f"""
    🚀 Signal Alert 🚀
    Pair: {symbol}
    Direction: {direction}
    Entry: {entry}
    Stop Loss: {stop_loss}
    Take Profits: {tp1}, {tp2}, {tp3}
    Timeframe: {timeframe}
    Strategy: {type_} ({strategy_name})
    Hold Time: {hold_time}
    Platform: {platform}
    Category: {category}
    """
    if commentary:
        message += f"\nCommentary: {commentary.get('technical_insights', 'N/A')}"

    return message.strip()
