import os
import threading
import time
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_API_IDENTIFIER")
CAPITAL_API_URL = os.getenv(
    "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
)

EQUITY_CURVE_FILE = "equity_curve.csv"


class CapitalTracker:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.account_id = None
        self.last_api_call = 0  # Track when we last called the API for rate limiting
        self.tracking_thread = None
        self.stop_tracking = False
        self.login()

    def login(self, max_retries=3, retry_delay=5):
        """Login to Capital.com API with retry mechanism"""
        for attempt in range(max_retries):
            try:
                # Rate limiting - ensure at least 1 second between API calls
                self._wait_for_rate_limit()

                response = self.session.post(
                    f"{CAPITAL_API_URL}/session",
                    json={
                        "identifier": CAPITAL_IDENTIFIER,
                        "password": CAPITAL_API_PASSWORD,
                    },
                    headers={
                        "X-CAP-API-KEY": CAPITAL_API_KEY,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
                if response.status_code == 200:
                    self.auth_token = {
                        "CST": response.headers.get("CST"),
                        "X-SECURITY-TOKEN": response.headers.get("X-SECURITY-TOKEN"),
                    }
                    self.account_id = response.json().get("accountId")
                    print("✅ Capital Tracker: Logged in")
                    return True
                else:
                    print(
                        f"❌ Capital Tracker: Login failed (attempt {attempt+1}/{max_retries})",
                        response.text,
                    )
                    # Only wait and retry if not the last attempt
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
            except Exception as e:
                print(
                    f"❌ Capital Tracker: Exception during login (attempt {attempt+1}/{max_retries}): {str(e)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)

        return False

    def _wait_for_rate_limit(self, min_interval=1.0):
        """Ensure API calls are rate limited to avoid hitting API limits"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call

        if time_since_last_call < min_interval:
            # Wait until we've reached the minimum interval
            sleep_time = min_interval - time_since_last_call
            time.sleep(sleep_time)

        # Update the last API call time
        self.last_api_call = time.time()

    def get_balance(self, max_retries=3):
        """Get account balance with automatic retry on failure"""
        for attempt in range(max_retries):
            try:
                if not self.auth_token:
                    if not self.login():
                        return None

                # Apply rate limiting
                self._wait_for_rate_limit()

                headers = {
                    "X-CAP-API-KEY": CAPITAL_API_KEY,
                    "CST": self.auth_token["CST"],
                    "X-SECURITY-TOKEN": self.auth_token["X-SECURITY-TOKEN"],
                }

                account_url = f"{CAPITAL_API_URL}/accounts"
                response = self.session.get(account_url, headers=headers)

                if response.status_code == 200:
                    balance = response.json()["accounts"][0]["balance"]["balance"]
                    return round(float(balance), 2)
                elif response.status_code == 401:
                    # Auth expired, try to login again
                    print("❌ Capital Tracker: Auth expired, attempting login...")
                    if self.login() and attempt < max_retries - 1:
                        continue
                else:
                    print(
                        f"❌ Capital Tracker: Failed to fetch balance (attempt {attempt+1}/{max_retries}): {response.text}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(2)
            except Exception as e:
                print(
                    f"❌ Capital Tracker: Error getting balance (attempt {attempt+1}/{max_retries})",
                    str(e),
                )
                if attempt < max_retries - 1:
                    time.sleep(2)

        return None

    def log_equity(self):
        """Log current equity balance to CSV file"""
        balance = self.get_balance()
        if balance is None:
            return False

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        row = {"timestamp": timestamp, "balance": balance}

        df = pd.DataFrame([row])
        file_exists = os.path.exists(EQUITY_CURVE_FILE)

        df.to_csv(EQUITY_CURVE_FILE, mode="a", index=False, header=not file_exists)
        print(f"📈 Logged balance: {balance} AED at {timestamp}")
        return True

    def get_equity_data(self):
        """Get historical equity data from CSV file"""
        if os.path.exists(EQUITY_CURVE_FILE):
            return pd.read_csv(EQUITY_CURVE_FILE)
        return pd.DataFrame(columns=["timestamp", "balance"])

    def get_growth_percentage(self, starting_amount=333, target=1500):
        """Calculate growth percentage toward target"""
        current_balance = self.get_balance()
        if current_balance:
            progress = (
                (current_balance - starting_amount) / (target - starting_amount)
            ) * 100
            return round(progress, 2)
        return 0.0

    def start_tracking(self, interval_minutes=30):
        """Start background thread to track equity at regular intervals"""
        if self.tracking_thread and self.tracking_thread.is_alive():
            print("Tracking already running")
            return False

        self.stop_tracking = False

        def tracking_job():
            print(
                f"✅ Equity tracking started - logging every {interval_minutes} minutes"
            )
            while not self.stop_tracking:
                try:
                    self.log_equity()
                except Exception as e:
                    print(f"Error in equity tracking: {e}")

                # Sleep for the specified interval
                for _ in range(interval_minutes * 60):
                    if self.stop_tracking:
                        break
                    time.sleep(1)

        self.tracking_thread = threading.Thread(target=tracking_job, daemon=True)
        self.tracking_thread.start()
        return True

    def stop_tracking_equity(self):
        """Stop the background equity tracking thread"""
        self.stop_tracking = True
        if self.tracking_thread:
            self.tracking_thread.join(timeout=5.0)
            print("Equity tracking stopped")
            return True
        return False


# Example usage when module is run directly
if __name__ == "__main__":
    print("Capital.com Equity Tracker")
    print("-" * 50)

    tracker = CapitalTracker()

    # Get current balance
    balance = tracker.get_balance()
    if balance:
        print(f"Current balance: {balance}")

        # Check if we should start tracking
        start_tracking = input("Start automatic equity tracking? (y/n): ").lower()
        if start_tracking == "y":
            interval = input("Enter logging interval in minutes (default 30): ")
            try:
                interval = int(interval) if interval else 30
            except ValueError:
                interval = 30

            tracker.start_tracking(interval)

            print(f"Tracking started with {interval} minute intervals")
            print("Press Ctrl+C to stop")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping tracker...")
                tracker.stop_tracking_equity()
                print("Goodbye!")
    else:
        print("Could not retrieve balance. Check your API credentials.")
