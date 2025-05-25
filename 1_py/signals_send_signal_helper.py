"""
send_signal_helper.py — Full Refactored Version
- Consolidated imports
- Robust fallback for missing dependencies
- Environment-driven endpoints and API keys
- Clean function interfaces with type hints
- Error handling and logging
"""
from typing import Any, Dict, Optional, List
import os
import json
import logging
import time

import requests
from dotenv import load_dotenv

from config import CONFIG
from message_generator import generate_signal_message, get_signal_message

# Make these modules and types globally accessible for other files
GLOBAL_time = time
GLOBAL_List = List

# Initialize .env
load_dotenv()

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Fallback asset config
ASSET_CONFIG: Dict[str, Any] = getattr(CONFIG, "ASSET_CONFIG", {}) or {}

# Load endpoints and API key
SIGNAL_DISPATCHER_URL: str = os.getenv(
    "SIGNAL_DISPATCHER_URL", getattr(CONFIG, "dispatcher_url", "")
) or ""
API_KEY: str = os.getenv(
    "API_KEY", getattr(CONFIG, "api_key", "")
) or ""

__all__ = []


def send_signal_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Internal: send raw payload to dispatcher URL.
    Handles errors and returns JSON response or error dict.
    """
    if not SIGNAL_DISPATCHER_URL:
        logger.error("SIGNAL_DISPATCHER_URL not configured.")
        return {"error": "No dispatcher URL"}
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
    try:
        resp = requests.post(
            SIGNAL_DISPATCHER_URL,
            headers=headers,
            json=payload,
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"send_signal_payload error: {e}")
        return {"error": str(e)}


def send_signal(
    pair: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    tp2: Optional[float] = None,
    tp3: Optional[float] = None,
    timeframe: Optional[str] = None,
    mode: str = "SAFE_RECOVERY",
    type_: str = "Breakout",
    direction: Optional[str] = None,
    platform: str = "Capital.com",
    send_pre_signal: bool = True
) -> Dict[str, Any]:
    """
    Public: Build payload from parameters and send via dispatcher.
    Tries enhanced sender if available; falls back to HTTP.
    """
    # Normalize inputs
    pair = pair.upper()
    # Asset metadata
    asset_meta = ASSET_CONFIG.get(pair, {})

    # Inherit defaults
    timeframe = timeframe or asset_meta.get("timeframe", "30m")
    if type_ == "Breakout" and asset_meta.get("strategy"):
        type_ = asset_meta["strategy"]

    # Infer direction if missing
    if not direction:
        direction = "BUY" if entry > stop_loss else "SELL"

    # Build signal dict for message_generator
    signal_dict = {
        "pair": pair,
        "direction": direction,
        "entry": entry,
        "stop_loss": stop_loss,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "strategy": type_,
        "timeframe": timeframe,
        "platform": platform
    }

    # Build message using both generators
    msg_simple = generate_signal_message(signal=signal_dict)
    msg_formatted = get_signal_message(signal_dict)
    logger.info(f"Signal messages generated.")

    # Try enhanced if available
    try:
        try:
            from enhanced_signal_sender import send_signal as enhanced_send
        except ImportError:
            logger.error("Enhanced signal sender module not found.")
            raise
        logger.info("Using enhanced sender.")
        return enhanced_send(
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
            send_pre_signal=send_pre_signal
        )
    except ImportError:
        logger.info("Enhanced sender unavailable. Falling back.")

    # Build payload
    payload = {
        "pair": pair,
        "entry": entry,
        "stop_loss": stop_loss,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "timeframe": timeframe,
        "mode": mode,
        "strategy": type_,
        "direction": direction,
        "platform": platform,
        "send_pre_signal": send_pre_signal,
        "message": msg_simple,
        "formatted_message": msg_formatted
    }
    return send_signal_payload(payload)


def send_recap(
    signal_id: str,
    hit_tp1: bool = False,
    hit_tp2: bool = False,
    hit_tp3: bool = False,
    hit_sl: bool = False,
    pips: float = 0.0
) -> Dict[str, Any]:
    """
    Public: Send recap via enhanced or HTTP fallback.
    """
    payload = {
        "signal_id": signal_id,
        "hit_tp1": hit_tp1,
        "hit_tp2": hit_tp2,
        "hit_tp3": hit_tp3,
        "hit_sl": hit_sl,
        "pips": pips
    }
    # Enhanced recap if available
    try:
        try:
            from enhanced_signal_sender import send_recap as enhanced_recap
        except ImportError:
            logger.error(
                "Enhanced recap function not found in enhanced_signal_sender.")
            raise
        logger.info("Using enhanced recap.")
        return enhanced_recap(signal_id, hit_tp1, hit_tp2, hit_tp3, hit_sl, pips)
    except ImportError:
        logger.info("Enhanced recap unavailable. Falling back.")

    # HTTP fallback
    REC_URL = SIGNAL_DISPATCHER_URL.rstrip(
        '/') + '/api/send_recap' if SIGNAL_DISPATCHER_URL else ''
    if not REC_URL:
        logger.error("Dispatch URL missing for recap.")
        return {}
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
    try:
        resp = requests.post(REC_URL, headers=headers,
                             json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"send_recap error: {e}")
        return {}


# CLI test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    result = send_signal(
        pair="BTCUSD",
        entry=72000,
        stop_loss=71000,
        tp1=73000,
        tp2=73500,
        tp3=74000
    )
    print(json.dumps(result, indent=2))
