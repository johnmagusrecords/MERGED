def get_signal_message(signal_data, symbol=None, direction=None, **kwargs):
    symbol = symbol or signal_data.get("symbol", "")
    direction = direction or signal_data.get("direction", "")
    entry = signal_data.get("entry")
    stop_loss = signal_data.get("stop_loss")
    take_profits = signal_data.get("take_profits", [])
    asset_type = signal_data.get("asset_type", "Unknown")
    strategy = signal_data.get("strategy", "Unknown")
    hold_time = signal_data.get("hold_time", "Unknown")
    commentary = signal_data.get("commentary", "")

    return f"""📣 *Trade Signal Alert* 📣

🔹 *Asset*: {symbol.upper()} ({asset_type})
🔹 *Direction*: {direction.upper()}
🔹 *Entry*: `{entry}`
🔹 *Stop Loss*: `{stop_loss}`
🔹 *Take Profits*: {', '.join(str(tp) for tp in take_profits)}

🧠 *Strategy*: {strategy}
⏳ *Holding Time*: {hold_time}
💬 *Commentary*: {commentary}

#MAGUS_PRIME_X
"""
