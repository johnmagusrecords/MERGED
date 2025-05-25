from signal_sender import SignalSender


# Create an example function that your main bot might use
def send_trade_signal(symbol, entry_price, stop_loss, targets, timeframe):
    """
    Function to integrate in your main bot that sends signals when trades are detected
    """
    # Create Signal Sender instance
    sender = SignalSender()

    # Send the signal
    response = sender.send_signal(
        pair=symbol,
        entry=entry_price,
        stop_loss=stop_loss,
        tp1=targets[0],
        tp2=targets[1] if len(targets) > 1 else None,
        tp3=targets[2] if len(targets) > 2 else None,
        timeframe=timeframe,
        mode="SAFE_RECOVERY",
        signal_type="Breakout",
    )

    # Check response
    if "error" in response:
        print(f"⚠️ Error sending signal: {response['error']}")
        return False
    else:
        print(f"✅ Signal sent successfully for {symbol}")
        return True


# Example usage in your main bot
if __name__ == "__main__":
    print("Example of how to integrate signal sending in your main bot")

    # This would normally be called when your trading algorithm detects a signal
    send_trade_signal(
        symbol="GOLD",
        entry_price=3110.50,
        stop_loss=3095.75,
        targets=[3125.25, 3140.00, 3160.50],
        timeframe="1h",
    )
