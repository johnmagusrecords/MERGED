import os
import hmac
from flask import Flask, request, jsonify
from threading import Lock
from functools import wraps

app = Flask(__name__)

class State:
    def __init__(self):
        self.signal_history = []
        self.history_lock = Lock()

state = State()

def validate_api_key(request_api_key):
    api_key = os.getenv("API_KEY")
    return hmac.compare_digest(request_api_key or "", api_key or "")

def validate_env_vars():
    required_vars = ["TELEGRAM_BOT_TOKEN", "CAPITAL_API_KEY", "API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

@app.route("/ignore-signal", methods=["POST"])
def ignore_signal():
    data = request.json
    with state.history_lock:
        state.signal_history.append({"signal": data, "status": "ignored"})
    return jsonify({"status": "ignored"})

def dispatch_signal(signal):
    # Consolidated dispatch logic
    # ...send to Telegram, log, etc...
    with state.history_lock:
        state.signal_history.append({"signal": signal, "status": "dispatched"})
    return True

def clear_expired_signals():
    # Implement expiration logic if needed
    with state.history_lock:
        state.signal_history = [
            s for s in state.signal_history if not is_expired(s)
        ]

def is_expired(signal_entry):
    # Placeholder: implement expiration check
    return False

@app.before_first_request
def start_background_tasks():
    # Example: start news monitor or other background jobs
    pass

if __name__ == "__main__":
    validate_env_vars()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
