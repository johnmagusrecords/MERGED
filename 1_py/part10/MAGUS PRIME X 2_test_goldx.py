from signal_sender import SignalSender


def test_gold_signal():
    print("Sending test GOLD signal to Telegram...")
    sender = SignalSender()

    response = sender.send_signal(
        pair="GOLD",
        entry=3110.50,
        stop_loss=3095.75,
        tp1=3125.25,
        tp2=3140.00,
        tp3=3160.50,
        timeframe="1h",
        mode="SAFE_RECOVERY",
        signal_type="BUY Test Signal",
    )

    if "error" in response:
        print(f"❌ Error: {response.get('error')}")
        return False
    else:
        print("✅ Signal sent successfully!")
        return True


if __name__ == "__main__":
    test_gold_signal()
    print("\nCheck your Telegram for the message!")
