def generate_signal_message(
    symbol: str,
    direction: str,
    entry: float,
    stop_loss: float,
    take_profits: list,
    strategy: str = None,
    timeframe: str = None,
    commentary: str = None
) -> str:
    """
    Generate a trade signal message formatted for MetaTrader 5 and Telegram.

    Args:
        symbol (str): Trading symbol (e.g., "XAUUSD").
        direction (str): Trade direction ("BUY" or "SELL").
        entry (float): Entry price.
        stop_loss (float): Stop-loss price.
        take_profits (list): List of take-profit prices.
        strategy (str, optional): Strategy name or description.
        timeframe (str, optional): Timeframe for the trade.
        commentary (str, optional): Additional commentary.

    Returns:
        str: Formatted trade signal message.
    """
    tp_lines = "\n".join(
        [f"🎯 TP{i+1}: {tp}" for i, tp in enumerate(take_profits)])

    strategy_line = f"\n📊 Strategy: {strategy}" if strategy else ""
    timeframe_line = f"\n🕒 Timeframe: {timeframe}" if timeframe else ""
    commentary_line = f"\n💬 {commentary}" if commentary else ""

    message_en = (
        f"📢 TRADE SIGNAL\n"
        f"📈 {symbol} - {direction.upper()}\n"
        f"📍 Entry: {entry}\n"
        f"🛡️ SL: {stop_loss}\n"
        f"{tp_lines}"
        f"{strategy_line}"
        f"{timeframe_line}"
        f"{commentary_line}\n"
        f"🔔 Optimized for Capital.com"
    )

    message_ar = (
        f"📢 إشارة تداول\n"
        f"📈 {symbol} - {direction.upper()}\n"
        f"📍 دخول: {entry}\n"
        f"🛡️ وقف الخسارة: {stop_loss}\n"
        f"{tp_lines.replace('🎯 TP', '🎯 الهدف')}"
        f"{strategy_line.replace('📊 Strategy', '📊 الاستراتيجية')}"
        f"{timeframe_line.replace('🕒 Timeframe', '🕒 الإطار الزمني')}"
        f"{commentary_line.replace('💬', '💬 تعليق')}\n"
        f"🔔 محسّن لـ Capital.com"
    )

    return f"{message_en}\n\n{message_ar}"
# ...existing code...
