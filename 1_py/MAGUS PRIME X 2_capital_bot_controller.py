import logging
import os
import sys
import threading
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import the bot module for credentials and some functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bot_dev_backup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("capital_bot_controller.log"),
        logging.StreamHandler(),
    ],
)


class CapitalBotController:
    def __init__(self):
        self.active_trades = {}
        self.monitor_thread = None
        self.is_running = False

        # Strategy parameters
        self.risk_percent = 1.0
        self.atr_multiplier_tp = 2.5
        self.atr_multiplier_sl = 1.5
        self.breakeven_trigger = 0.01  # 1%
        self.tp_move_percent = 0.005  # 0.5%

        # API credentials from bot.py
        self.api_key = bot_dev_backup.CAPITAL_API_KEY
        self.api_url = bot_dev_backup.CAPITAL_API_URL
        self.identifier = bot_dev_backup.CAPITAL_IDENTIFIER
        self.api_password = bot_dev_backup.CAPITAL_API_PASSWORD

        # Session setup
        self.session = self.create_session()
        self.cst = None
        self.security_token = None

        logging.info("Capital Bot Controller initialized")

    def create_session(self):
        """Create a session with retry mechanism"""
        session = requests.Session()
        retry = Retry(total=5, backoff_factor=0.1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def authenticate(self):
        """Authenticate with Capital.com API"""
        url = f"{self.api_url}/session"
        headers = {"X-CAP-API-KEY": self.api_key}
        data = {"identifier": self.identifier, "password": self.api_password}

        try:
            response = self.session.post(url, headers=headers, json=data)
            if response.status_code == 200:
                data = response.json()
                self.cst = data.get("CST")
                self.security_token = data.get("X-SECURITY-TOKEN")
                logging.info("Authentication successful")
                return True
            else:
                logging.error(f"Authentication failed: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return False

    def get_auth_headers(self):
        """Get authentication headers for API requests"""
        if not self.cst or not self.security_token:
            if not self.authenticate():
                return None

        return {
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.security_token,
            "X-CAP-API-KEY": self.api_key,
        }

    def get_account_info(self):
        """Get account information from Capital.com"""
        headers = self.get_auth_headers()
        if not headers:
            return None

        try:
            response = self.session.get(f"{self.api_url}/accounts", headers=headers)
            if response.status_code == 200:
                accounts = response.json().get("accounts", [])
                if accounts:
                    account = accounts[0]  # Get the first account
                    return {
                        "id": account.get("accountId"),
                        "type": account.get("accountType"),
                        "currency": account.get("currency"),
                        "balance": float(account.get("balance", 0)),
                        "available": float(account.get("available", 0)),
                        "margin": float(account.get("margin", 0)),
                        "pnl": float(account.get("pnl", 0)),
                    }
            logging.error(f"Failed to get account info: {response.text}")
            return None
        except Exception as e:
            logging.error(f"Error getting account info: {str(e)}")
            return None

    def get_markets(self):
        """Get available markets from Capital.com"""
        headers = self.get_auth_headers()
        if not headers:
            return []

        try:
            response = self.session.get(f"{self.api_url}/markets", headers=headers)
            if response.status_code == 200:
                markets = response.json().get("markets", [])
                tradeable_markets = [
                    m for m in markets if m.get("marketStatus") == "TRADEABLE"
                ]
                logging.info(f"Found {len(tradeable_markets)} tradeable markets")
                return tradeable_markets
            logging.error(f"Failed to get markets: {response.text}")
            return []
        except Exception as e:
            logging.error(f"Error getting markets: {str(e)}")
            return []

    def get_market_details(self, epic):
        """Get market details for a specific market"""
        headers = self.get_auth_headers()
        if not headers:
            return None

        try:
            response = self.session.get(
                f"{self.api_url}/markets/{epic}", headers=headers
            )
            if response.status_code == 200:
                return response.json()
            logging.error(f"Failed to get market details: {response.text}")
            return None
        except Exception as e:
            logging.error(f"Error getting market details: {str(e)}")
            return None

    def get_positions(self):
        """Get open positions"""
        headers = self.get_auth_headers()
        if not headers:
            return []

        try:
            response = self.session.get(f"{self.api_url}/positions", headers=headers)
            if response.status_code == 200:
                positions = response.json().get("positions", [])
                logging.info(f"Found {len(positions)} open positions")
                return positions
            logging.error(f"Failed to get positions: {response.text}")
            return []
        except Exception as e:
            logging.error(f"Error getting positions: {str(e)}")
            return []

    def get_historical_prices(self, epic, resolution="MINUTE_15", limit=100):
        """Get historical price data for a market"""
        headers = self.get_auth_headers()
        if not headers:
            return None

        try:
            params = {"resolution": resolution, "max": limit}
            response = self.session.get(
                f"{self.api_url}/prices/{epic}", headers=headers, params=params
            )

            if response.status_code == 200:
                data = response.json()
                prices = data.get("prices", [])
                if not prices:
                    logging.warning(f"No price data found for {epic}")
                    return None

                import pandas as pd

                df = pd.DataFrame(
                    [
                        {
                            "timestamp": pd.to_datetime(p["snapshotTime"]),
                            "open": float(p["openPrice"]["bid"]),
                            "high": float(p["highPrice"]["bid"]),
                            "low": float(p["lowPrice"]["bid"]),
                            "close": float(p["closePrice"]["bid"]),
                            "volume": float(p.get("lastTradedVolume", 0)),
                        }
                        for p in prices
                        if "closePrice" in p
                    ]
                )

                if len(df) < 2:
                    logging.warning(f"Insufficient price data for {epic}")
                    return None

                df.set_index("timestamp", inplace=True)
                df.sort_index(inplace=True)

                return df

            logging.error(f"Failed to get historical prices: {response.text}")
            return None
        except Exception as e:
            logging.error(f"Error getting historical prices: {str(e)}")
            return None

    def calculate_atr(self, epic, period=14):
        """Calculate Average True Range for a market"""
        df = self.get_historical_prices(epic)
        if df is None or len(df) < period:
            return None

        try:
            import numpy as np

            high_low = df["high"] - df["low"]
            high_close = np.abs(df["high"] - df["close"].shift())
            low_close = np.abs(df["low"] - df["close"].shift())

            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(period).mean().iloc[-1]

            return atr
        except Exception as e:
            logging.error(f"Error calculating ATR: {str(e)}")
            return None

    def execute_trade(
        self, epic, direction, size=None, stop_level=None, profit_level=None
    ):
        """Execute a trade on Capital.com"""
        headers = self.get_auth_headers()
        if not headers:
            return None

        # Get market details if needed
        market = self.get_market_details(epic)
        if not market:
            logging.error(f"Failed to get market details for {epic}")
            return None

        # Calculate position size if not provided
        if size is None:
            account_info = self.get_account_info()
            if not account_info:
                logging.error("Failed to get account info for position sizing")
                return None

            balance = account_info["balance"]
            risk_amount = balance * (self.risk_percent / 100)

            # Calculate ATR for stop loss distance
            atr = self.calculate_atr(epic)
            if atr is None:
                logging.error(f"Failed to calculate ATR for {epic}")
                return None

            # Get current price
            current_price = None
            if "snapshot" in market and "bid" in market["snapshot"]:
                current_price = float(market["snapshot"]["bid"])

            if current_price is None:
                logging.error(f"Failed to get current price for {epic}")
                return None

            # Calculate stop loss distance
            sl_distance = atr * self.atr_multiplier_sl

            # Calculate position size
            size = risk_amount / sl_distance

            # Adjust to minimum deal size
            min_size = float(market.get("minDealSize", 0.1))
            size = max(min_size, size)

            # Calculate stop loss and take profit levels if not provided
            if stop_level is None:
                if direction == "BUY":
                    stop_level = current_price - sl_distance
                else:
                    stop_level = current_price + sl_distance

            if profit_level is None:
                tp_distance = atr * self.atr_multiplier_tp
                if direction == "BUY":
                    profit_level = current_price + tp_distance
                else:
                    profit_level = current_price - tp_distance

        # Prepare the request
        url = f"{self.api_url}/positions"
        data = {
            "epic": epic,
            "direction": direction,
            "size": str(round(size, 2)),
            "limitDistance": str(round(profit_level, 5)) if profit_level else None,
            "stopDistance": str(round(stop_level, 5)) if stop_level else None,
            "guaranteedStop": "false",
            "trailingStop": "false",
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        try:
            response = self.session.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                deal_reference = result.get("dealReference")
                logging.info(
                    f"Trade executed: {direction} {epic}, Size: {size}, Ref: {deal_reference}"
                )
                return deal_reference
            else:
                logging.error(f"Failed to execute trade: {response.text}")
                return None
        except Exception as e:
            logging.error(f"Error executing trade: {str(e)}")
            return None

    def close_position(self, dealId):
        """Close a position"""
        headers = self.get_auth_headers()
        if not headers:
            return False

        try:
            url = f"{self.api_url}/positions/{dealId}"
            response = self.session.delete(url, headers=headers)
            if response.status_code == 200:
                logging.info(f"Position closed: {dealId}")
                return True
            else:
                logging.error(f"Failed to close position: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Error closing position: {str(e)}")
            return False

    def update_stop_loss(self, dealId, new_level):
        """Update stop loss level for a position"""
        headers = self.get_auth_headers()
        if not headers:
            return False

        try:
            url = f"{self.api_url}/positions/{dealId}/stop-level"
            data = {"level": str(new_level)}
            response = self.session.put(url, headers=headers, json=data)
            if response.status_code == 200:
                logging.info(f"Stop loss updated for {dealId} to {new_level}")
                return True
            else:
                logging.error(f"Failed to update stop loss: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Error updating stop loss: {str(e)}")
            return False

    def update_take_profit(self, dealId, new_level):
        """Update take profit level for a position"""
        headers = self.get_auth_headers()
        if not headers:
            return False

        try:
            url = f"{self.api_url}/positions/{dealId}/limit-level"
            data = {"level": str(new_level)}
            response = self.session.put(url, headers=headers, json=data)
            if response.status_code == 200:
                logging.info(f"Take profit updated for {dealId} to {new_level}")
                return True
            else:
                logging.error(f"Failed to update take profit: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Error updating take profit: {str(e)}")
            return False

    def start_monitoring(self):
        """Start monitoring positions for trailing stop loss and breakeven"""
        if self.is_running:
            logging.warning("Monitoring already running")
            return False

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self.monitor_positions)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        logging.info("Position monitoring started")
        return True

    def stop_monitoring(self):
        """Stop monitoring positions"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        logging.info("Position monitoring stopped")
        return True

    def monitor_positions(self):
        """Monitor positions for trailing stop loss and breakeven updates"""
        while self.is_running:
            try:
                positions = self.get_positions()
                for position in positions:
                    # Check for breakeven and trailing take profit logic
                    self.check_position_management(position)

                # Sleep to avoid too frequent API calls
                time.sleep(30)
            except Exception as e:
                logging.error(f"Error in position monitoring: {str(e)}")
                time.sleep(60)  # Sleep longer on error

    def check_position_management(self, position):
        """Check if a position needs stop loss or take profit updates"""
        try:
            deal_id = position["dealId"]
            direction = position["direction"]
            open_level = float(position["openLevel"])
            current_level = float(position["level"])
            stop_level = float(position.get("stopLevel", 0))
            limit_level = float(position.get("limitLevel", 0))

            # Calculate profit percentage
            if direction == "BUY":
                profit_percent = (current_level - open_level) / open_level * 100
            else:
                profit_percent = (open_level - current_level) / open_level * 100

            # Breakeven logic
            if profit_percent >= (self.breakeven_trigger * 100):
                if direction == "BUY" and stop_level < open_level:
                    self.update_stop_loss(deal_id, open_level)
                elif direction == "SELL" and stop_level > open_level:
                    self.update_stop_loss(deal_id, open_level)

            # Trailing take profit logic
            if profit_percent >= (self.tp_move_percent * 100):
                tp_move = current_level * self.tp_move_percent
                if direction == "BUY" and limit_level < current_level + tp_move:
                    new_tp = limit_level + tp_move
                    self.update_take_profit(deal_id, new_tp)
                elif direction == "SELL" and limit_level > current_level - tp_move:
                    new_tp = limit_level - tp_move
                    self.update_take_profit(deal_id, new_tp)

        except Exception as e:
            logging.error(f"Error in position management: {str(e)}")

    def set_strategy(self, strategy_name):
        """Set trading strategy parameters"""
        if strategy_name.lower() == "safe":
            self.risk_percent = 1.0
            self.atr_multiplier_tp = 2.0
            self.atr_multiplier_sl = 1.0
            self.breakeven_trigger = 0.005  # 0.5%
            self.tp_move_percent = 0.003  # 0.3%
            logging.info("Strategy set to Safe")
            return True
        elif strategy_name.lower() == "balanced":
            self.risk_percent = 2.0
            self.atr_multiplier_tp = 2.5
            self.atr_multiplier_sl = 1.5
            self.breakeven_trigger = 0.01  # 1%
            self.tp_move_percent = 0.005  # 0.5%
            logging.info("Strategy set to Balanced")
            return True
        elif strategy_name.lower() == "aggressive":
            self.risk_percent = 3.0
            self.atr_multiplier_tp = 3.0
            self.atr_multiplier_sl = 1.5
            self.breakeven_trigger = 0.015  # 1.5%
            self.tp_move_percent = 0.01  # 1%
            logging.info("Strategy set to Aggressive")
            return True
        else:
            logging.error(f"Unknown strategy: {strategy_name}")
            return False


# Interactive console for bot control
def interactive_console():
    bot = CapitalBotController()

    print("\n=== MAGUS PRIME X Capital.com Bot Controller ===")
    print("Type 'help' for a list of commands")

    while True:
        try:
            command = input("\nCommand> ").strip().lower()

            if command == "help":
                print("\nAvailable commands:")
                print("  auth - Authenticate with Capital.com")
                print("  account - Show account information")
                print("  markets - Show available markets")
                print("  positions - Show open positions")
                print("  trade <symbol> <buy/sell> [size] - Execute a trade")
                print("  close <deal_id> - Close a position")
                print("  strategy <safe|balanced|aggressive> - Set strategy")
                print("  monitor start - Start position monitoring")
                print("  monitor stop - Stop position monitoring")
                print("  analyze <symbol> - Analyze a symbol with ATR")
                print("  exit - Exit the controller")

            elif command == "auth":
                if bot.authenticate():
                    print("Authentication successful")
                else:
                    print("Authentication failed")

            elif command == "account":
                account = bot.get_account_info()
                if account:
                    print("\nAccount Information:")
                    print(f"  ID: {account['id']}")
                    print(f"  Type: {account['type']}")
                    print(f"  Currency: {account['currency']}")
                    print(f"  Balance: ${account['balance']:.2f}")
                    print(f"  Available: ${account['available']:.2f}")
                    print(f"  Margin: ${account['margin']:.2f}")
                    print(f"  P/L: ${account['pnl']:.2f}")
                else:
                    print("Failed to get account information")

            elif command == "markets":
                markets = bot.get_markets()
                if markets:
                    print(f"\nFound {len(markets)} tradeable markets:")
                    for _i, market in enumerate(markets[:20]):  # Show only first 20
                        print(f"  {market['epic']}: {market['instrumentName']}")
                    if len(markets) > 20:
                        print(f"  ... and {len(markets) - 20} more")
                else:
                    print("No markets found or authentication failed")

            elif command == "positions":
                positions = bot.get_positions()
                if positions:
                    print(f"\nOpen Positions ({len(positions)}):")
                    for pos in positions:
                        direction = pos["direction"]
                        symbol = pos["epic"]
                        size = pos["size"]
                        open_level = pos["openLevel"]
                        current_level = pos["level"]
                        profit_loss = pos["profit"]
                        deal_id = pos["dealId"]
                        stop_level = pos.get("stopLevel", "None")
                        limit_level = pos.get("limitLevel", "None")

                        print(f"  {direction} {symbol} (ID: {deal_id})")
                        print(
                            f"    Size: {size}, Open: {open_level}, Current: {current_level}"
                        )
                        print(
                            f"    P/L: {profit_loss}, SL: {stop_level}, TP: {limit_level}"
                        )
                else:
                    print("No open positions found")

            elif command.startswith("trade "):
                parts = command.split()
                if len(parts) < 3:
                    print("Usage: trade <symbol> <buy/sell> [size]")
                else:
                    symbol = parts[1].upper()
                    direction = parts[2].upper()
                    size = float(parts[3]) if len(parts) > 3 else None

                    if direction not in ["BUY", "SELL"]:
                        print("Direction must be BUY or SELL")
                    else:
                        result = bot.execute_trade(symbol, direction, size)
                        if result:
                            print(f"Trade executed with reference: {result}")
                        else:
                            print("Failed to execute trade")

            elif command.startswith("close "):
                try:
                    deal_id = command.split()[1]
                    if bot.close_position(deal_id):
                        print(f"Position {deal_id} closed")
                    else:
                        print(f"Failed to close position {deal_id}")
                except IndexError:
                    print("Usage: close <deal_id>")

            elif command.startswith("strategy "):
                try:
                    strategy = command.split()[1]
                    if bot.set_strategy(strategy):
                        print(f"Strategy set to {strategy}")
                    else:
                        print(f"Unknown strategy: {strategy}")
                except IndexError:
                    print("Usage: strategy <safe|balanced|aggressive>")

            elif command == "monitor start":
                if bot.start_monitoring():
                    print("Position monitoring started")
                else:
                    print("Failed to start monitoring")

            elif command == "monitor stop":
                if bot.stop_monitoring():
                    print("Position monitoring stopped")
                else:
                    print("Failed to stop monitoring")

            elif command.startswith("analyze "):
                try:
                    symbol = command.split()[1].upper()
                    atr = bot.calculate_atr(symbol)
                    if atr:
                        print(f"\nAnalysis for {symbol}:")
                        print(f"  ATR: {atr:.5f}")

                        # Get current price
                        market = bot.get_market_details(symbol)
                        if market and "snapshot" in market:
                            current_price = float(market["snapshot"]["bid"])
                            print(f"  Current Price: {current_price:.5f}")

                            # Calculate potential SL and TP based on strategy
                            sl_buy = current_price - (atr * bot.atr_multiplier_sl)
                            sl_sell = current_price + (atr * bot.atr_multiplier_sl)
                            tp_buy = current_price + (atr * bot.atr_multiplier_tp)
                            tp_sell = current_price - (atr * bot.atr_multiplier_tp)

                            print(f"  Buy SL: {sl_buy:.5f}, TP: {tp_buy:.5f}")
                            print(f"  Sell SL: {sl_sell:.5f}, TP: {tp_sell:.5f}")
                    else:
                        print("Failed to analyze symbol")
                except IndexError:
                    print("Usage: analyze <symbol>")

            elif command == "exit":
                if bot.is_running:
                    bot.stop_monitoring()
                print("Exiting Capital.com Bot Controller")
                break

            else:
                print("Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\nExiting...")
            if bot.is_running:
                bot.stop_monitoring()
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    interactive_console()
