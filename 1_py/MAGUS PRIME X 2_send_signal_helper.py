import json
import logging
import os
import time

import requests
from dotenv import load_dotenv

from config import ASSET_CONFIG, config

# Fix for the get_signal_message import
try:
    # Try the original import statement
    import get_signal_message
except ImportError:
    # Try importing from templates module (where it should be located)
    try:
        from templates import generate_signal_message as get_signal_message

        print("Successfully imported get_signal_message from templates module")
    except ImportError:
        # Try from enhanced_signal_sender (another possible location)
        try:
            from enhanced_signal_sender import (
                generate_signal_message as get_signal_message,
            )

            print(
                "Successfully imported get_signal_message from enhanced_signal_sender module"
            )
        except ImportError:
            # Create a fallback implementation to prevent errors
            print(
                "WARNING: Could not import get_signal_message, using fallback implementation"
            )

            def get_signal_message(
                pair,
                direction,
                entry,
                sl,
                tp1,
                tp2=None,
                tp3=None,
                timeframe=None,
                strategy=None,
            ):
                """Fallback implementation of get_signal_message"""
                return f"Signal: {direction} {pair} at {entry}, SL: {sl}, TP: {tp1}"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Signal dispatcher configuration
SIGNAL_DISPATCHER_URL = os.getenv(
    "SIGNAL_DISPATCHER_URL", config["signals"]["dispatcher_url"]
)
API_KEY = os.getenv("API_KEY", config["signals"]["api_key"])

# Flag to check if enhanced sender is available (will be set later)
ENHANCED_AVAILABLE = False
enhanced_send_signal = None


def send_signal_payload(payload):
    """
    Send a signal using a simple payload format

    Args:
        payload: Dictionary with signal parameters

    Returns:
        dict: Response from signal dispatcher
    """
    try:
        headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
        response = requests.post(SIGNAL_DISPATCHER_URL, json=payload, headers=headers)
        if response.ok:
            logger.info("Signal sent successfully ✅")
            return response.json()
        else:
            logger.warning(f"Failed to send signal: {response.text}")
            return response.json()
    except Exception as e:
        logger.error(f"Signal send error: {str(e)}")
        return {"error": str(e)}


def send_signal(
    pair,
    entry,
    stop_loss,
    tp1,
    tp2=None,
    tp3=None,
    timeframe=None,
    mode="SAFE_RECOVERY",
    type_="Breakout",
    direction=None,
    platform="Capital.com",
    send_pre_signal=True,
):
    """
    Helper function to send a signal via the signal dispatcher API

    Args:
        pair: Trading pair/symbol
        entry: Entry price
        stop_loss: Stop loss price
        tp1: Take profit 1 price
        tp2: Take profit 2 price (optional)
        tp3: Take profit 3 price (optional)
        timeframe: Chart timeframe (defaults to asset config)
        mode: Trading mode
        type_: Signal type/strategy
        direction: BUY or SELL (inferred if not provided)
        platform: Trading platform
        send_pre_signal: Whether to send a pre-signal alert

    Returns:
        dict: Response from signal dispatcher
    """
    global ENHANCED_AVAILABLE, enhanced_send_signal

    # Lazy import - only import enhanced_signal_sender when needed
    if enhanced_send_signal is None:
        try:
            from enhanced_signal_sender import send_signal as imported_send_signal

            enhanced_send_signal = imported_send_signal
            ENHANCED_AVAILABLE = True
            logger.info("Enhanced signal sender available")
        except ImportError:
            ENHANCED_AVAILABLE = False
            logger.warning("Enhanced signal sender not available, using basic sender")

    # Normalize pair
    pair = pair.upper()

    # Get asset config if available
    asset_meta = ASSET_CONFIG.get(pair, {})

    # Use timeframe from config if not provided
    if not timeframe:
        timeframe = asset_meta.get("timeframe", "30m")

    # Use strategy from config if not specified
    if type_ == "Breakout" and "strategy" in asset_meta:
        type_ = asset_meta["strategy"]

    # If direction not provided, infer from entry and stop loss
    if not direction:
        direction = "BUY" if float(entry) > float(stop_loss) else "SELL"

    # Try to use the enhanced signal sender if available
    if ENHANCED_AVAILABLE:
        return enhanced_send_signal(
            pair=pair,
            entry=entry,
            stop_loss=stop_loss,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            timeframe=timeframe,
            mode=mode,
            type_=type_,
            direction=direction,
            platform=platform,
        )

    # Otherwise, use the simple payload-based sender
    payload = {
        "pair": pair,
        "entry": entry,
        "stop_loss": stop_loss,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "timeframe": timeframe or "30m",
        "mode": mode,
        "strategy": type_,
        "direction": direction,
        "platform": platform,
        "send_pre_signal": send_pre_signal,
    }

    return send_signal_payload(payload)


def should_trigger_recovery(last_result):
    """
    Determine if we should send a recovery signal based on the last trade.
    """
    if not last_result:
        return False
    return (
        last_result.get("result") == "SL"
        and os.getenv("ENABLE_RECOVERY_MODE", "true").lower() == "true"
    )


def prepare_recovery_signal(last_trade):
    """
    Prepare a recovery signal based on the last failed trade.
    This creates a counter-trend signal when SL is hit, using the SL level
    as the new entry point and the original entry as the new SL.

    Args:
        last_trade (dict): Data from the last trade that hit SL

    Returns:
        dict: Recovery signal parameters or None if unable to create
    """
    try:
        # Extract trade details
        entry = float(last_trade["entry"])
        sl = float(last_trade["stop_loss"])
        direction = last_trade["direction"]

        # Calculate recovery parameters (opposite direction)
        recovery_direction = "BUY" if direction == "SELL" else "SELL"
        recovery_entry = round(sl, 4)
        recovery_sl = round(entry, 4)

        # Set take profit targets with expanded risk-to-reward
        risk = abs(recovery_entry - recovery_sl)
        if recovery_direction == "BUY":
            tp1 = round(recovery_entry + (risk * 1.5), 4)
            tp2 = round(recovery_entry + (risk * 2.5), 4)
            tp3 = round(recovery_entry + (risk * 4.0), 4)
        else:  # SELL
            tp1 = round(recovery_entry - (risk * 1.5), 4)
            tp2 = round(recovery_entry - (risk * 2.5), 4)
            tp3 = round(recovery_entry - (risk * 4.0), 4)

        # Create recovery signal
        return {
            "symbol": last_trade["symbol"],
            "entry": recovery_entry,
            "stop_loss": recovery_sl,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "direction": recovery_direction,
            "strategy": "Recovery Bounce",
            "timeframe": last_trade.get("timeframe", "30m"),
            "platform": "Capital.com",
        }

    except Exception as e:
        print(f"❌ Failed to generate recovery signal: {e}")
        return None


def send_recap(
    signal_id, hit_tp1=False, hit_tp2=False, hit_tp3=False, hit_sl=False, pips=0
):
    """
    Helper function to send a signal recap via the signal dispatcher API

    Args:
        signal_id: ID of the signal to recap
        hit_tp1: Whether TP1 was hit
        hit_tp2: Whether TP2 was hit
        hit_tp3: Whether TP3 was hit
        hit_sl: Whether SL was hit
        pips: Pips/points gained or lost

    Returns:
        dict: Response from signal dispatcher
    """
    # Prepare the payload
    payload = {
        "signal_id": signal_id,
        "hit_tp1": hit_tp1,
        "hit_tp2": hit_tp2,
        "hit_tp3": hit_tp3,
        "hit_sl": hit_sl,
        "pips": pips,
    }

    # Use the local dispatcher if running in the same process
    try:
        # Lazy import - only import when needed
        from enhanced_signal_sender import send_recap as local_send_recap

        # Log that we're using local dispatcher
        logger.info(f"Using local signal dispatcher for recap {signal_id}")

        # Call the function directly
        return local_send_recap(signal_id, hit_tp1, hit_tp2, hit_tp3, hit_sl, pips)

    except ImportError:
        # Use the API if local dispatcher not available
        logger.info(f"Using remote signal dispatcher API for recap {signal_id}")

        headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

        # Determine if we're using localhost or remote API
        api_url = SIGNAL_DISPATCHER_URL
        if "localhost" not in api_url and "127.0.0.1" not in api_url:
            # Use external URL
            api_url = f"{SIGNAL_DISPATCHER_URL}/api/send_recap"
        else:
            # Use localhost
            api_url = "http://localhost:5001/api/send_recap"

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Error sending recap: {response.status_code} - {response.text}"
                )
                return {
                    "error": f"API error: {response.status_code}",
                    "details": response.text,
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}


if __name__ == "__main__":
    # Simple test if run directly
    logging.basicConfig(level=logging.INFO)

    print("Testing Signal Helper")
    print("-" * 50)

    # Test sending a signal
    result = send_signal(
        pair="BTCUSD",
        entry=72000,
        stop_loss=71000,
        tp1=73000,
        tp2=73500,
        tp3=74000,
        timeframe="1h",
        type_="Breakout",
        direction="BUY",
    )

    print(f"Signal result: {json.dumps(result, indent=2)}")

    # Test sending a recap if signal succeeded
    if result.get("success") and "signal_id" in result:
        time.sleep(5)  # Wait a moment

        recap_result = send_recap(
            signal_id=result["signal_id"],
            hit_tp1=True,
            hit_tp2=False,
            hit_tp3=False,
            hit_sl=False,
            pips=100,
        )

        print(f"Recap result: {json.dumps(recap_result, indent=2)}")
