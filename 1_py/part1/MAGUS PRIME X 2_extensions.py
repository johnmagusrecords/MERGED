import logging
import os
import threading
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_API_IDENTIFIER")
CAPITAL_API_URL = os.getenv(
    "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
)

# Additional trading configuration
USE_GUARANTEED_SL = os.getenv("USE_GUARANTEED_SL", "True").lower() == "true"
MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", "10"))
TRAILING_ACTIVATION = float(os.getenv("TRAILING_ACTIVATION", "1")) / 100
EXTENSIONS_ENABLED = os.getenv("ENABLE_EXTENSIONS", "True").lower() == "true"

# Global state for position tracking
active_positions = {}
breakeven_positions = set()
verification_threads = {}


class TradeExecutor:
    def __init__(self, bot_instance=None):
        """
        Initialize with an optional reference to the main bot instance
        """
        self.bot = bot_instance
        self.initialize_extension()

    def initialize_extension(self):
        """Set up the extension and start any required threads"""
        logging.info("🧩 Trade Executor Extension initialized")

        # Start position monitoring thread if not already running
        self.position_thread = threading.Thread(
            target=self.monitor_positions_loop, daemon=True
        )
        self.position_thread.start()
        logging.info("📊 Position monitoring thread started")

    def execute_trade(self, symbol, action, tp, sl, risk_percent=None):
        """
        Execute a trade with proper position sizing based on risk.

        Args:
            symbol (str): The symbol to trade
            action (str): "BUY" or "SELL"
            tp (float): Take profit price
            sl (float): Stop loss price
            risk_percent (float, optional): Risk percentage to use

        Returns:
            bool: Success or failure
        """
        try:
            # Check if we're at max positions
            if len(active_positions) >= MAX_POSITIONS:
                logging.warning(
                    f"Max positions reached ({MAX_POSITIONS}). Not executing new trade."
                )
                return False

            # Check if already in position for this symbol
            if symbol in active_positions:
                logging.warning(
                    f"Already in position for {symbol}. Not executing duplicate trade."
                )
                return False

            # Get current price
            current_price = self.get_current_price(symbol)
            if not current_price or current_price <= 0:
                logging.error(f"Could not get current price for {symbol}")
                return False

            # Get account info for position sizing
            account_info = self.get_account_info()
            if not account_info:
                logging.error("Could not get account info for position sizing")
                return False

            balance = account_info.get("balance", 0)
            if balance <= 0:
                logging.error(f"Invalid account balance: {balance}")
                return False

            # Risk calculation
            from bot_dev_backup import RISK_PERCENT as DEFAULT_RISK

            actual_risk_percent = (
                risk_percent if risk_percent is not None else DEFAULT_RISK
            )
            risk_amount = balance * (actual_risk_percent / 100)

            risk_distance = abs(current_price - sl)
            if risk_distance <= 0:
                logging.error(f"Invalid risk distance: {risk_distance}")
                return False

            position_size = risk_amount / risk_distance

            # Ensure minimum position size
            min_size = self.get_minimum_position_size(symbol)
            position_size = max(position_size, min_size)
            position_size = round(position_size, 2)

            # Place the order
            deal_reference = self.place_order(symbol, action, position_size, tp, sl)

            if not deal_reference:
                logging.error(f"Failed to execute {action} order for {symbol}")
                return False

            # Track the position
            active_positions[symbol] = {
                "symbol": symbol,
                "action": action,
                "entry_price": current_price,
                "position_size": position_size,
                "tp": tp,
                "sl": sl,
                "open_time": datetime.now(),
                "deal_reference": deal_reference,
            }

            # Record in trade history
            from bot_dev_backup import save_trade_to_csv

            save_trade_to_csv(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                action=action,
                tp=tp,
                sl=sl,
            )

            # Send notification
            self.send_trade_notification(
                symbol, action, current_price, tp, sl, position_size
            )

            logging.info(
                f"Executed {action} trade for {symbol} at {current_price}, Size: {position_size}"
            )
            return True

        except Exception as e:
            logging.error(f"Error executing trade for {symbol}: {str(e)}")
            return False

    def get_current_price(self, symbol):
        """
        Get the current price for a symbol.
        Uses bot's get_market_data if available, otherwise makes a direct API call.
        """
        try:
            # Try to use bot's cached market data if available
            if self.bot:
                data = self.bot.get_market_data(symbol)
                if data is not None and not data.empty:
                    return float(data["close"].iloc[-1])

            # Otherwise, make direct API call
            # Find the epic for the symbol
            from bot_dev_backup import find_market_match

            available_markets = self.bot.available_markets if self.bot else []
            market = find_market_match(symbol, available_markets)
            if market:
                epic = market.get("epic")
                if epic:
                    # Make a price request
                    cst, sec = self.authenticate()
                    if not cst or not sec:
                        return None

                    url = f"{CAPITAL_API_URL}/markets/{epic}"
                    headers = {
                        "X-CAP-API-KEY": CAPITAL_API_KEY,
                        "CST": cst,
                        "X-SECURITY-TOKEN": sec,
                    }

                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        offer_price = data.get("offer")
                        if offer_price:
                            return float(offer_price)

            logging.error(f"Could not get price for {symbol}")
            return None
        except Exception as e:
            logging.error(f"Error getting current price for {symbol}: {str(e)}")
            return None

    def get_account_info(self):
        """Fetch account balance information"""
        try:
            # Use bot's method if available
            if self.bot and hasattr(self.bot, "get_account_info"):
                return self.bot.get_account_info()

            # Otherwise make direct API call
            cst, sec = self.authenticate()
            if not cst or not sec:
                return None

            url = f"{CAPITAL_API_URL}/accounts"
            headers = {
                "X-CAP-API-KEY": CAPITAL_API_KEY,
                "CST": cst,
                "X-SECURITY-TOKEN": sec,
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                if accounts:
                    return {
                        "balance": float(accounts[0].get("balance", 0)),
                        "currency": accounts[0].get("currency", "USD"),
                    }

            return None
        except Exception as e:
            logging.error(f"Error getting account info: {str(e)}")
            return None

    def get_minimum_position_size(self, symbol):
        """Get minimum position size for a symbol"""
        try:
            if self.bot and hasattr(self.bot, "get_minimum_position_size"):
                return self.bot.get_minimum_position_size(symbol)

            # Default to 0.1 if we can't determine
            return 0.1
        except Exception as e:
            logging.error(f"Error getting minimum position size: {str(e)}")
            return 0.1

    def place_order(self, symbol, direction, size, tp=None, sl=None):
        """Place a market order with Capital.com API"""
        try:
            cst, sec = self.authenticate()
            if not cst or not sec:
                return None

            # Find market data for the symbol
            from bot_dev_backup import find_market_match

            available_markets = self.bot.available_markets if self.bot else []
            market = find_market_match(symbol, available_markets)
            epic = market.get("epic") if market else None

            if not epic:
                logging.error(f"Could not find epic for {symbol}")
                return None

            # Prepare order
            payload = {
                "epic": epic,
                "direction": direction,
                "size": str(size),
                "orderType": "MARKET",
                "guaranteedStop": USE_GUARANTEED_SL,
                "forceOpen": True,
            }

            # Add TP/SL if provided
            if tp is not None:
                payload["limitLevel"] = str(tp)
            if sl is not None:
                payload["stopLevel"] = str(sl)

            # Execute the order
            url = f"{CAPITAL_API_URL}/positions"
            headers = {
                "X-CAP-API-KEY": CAPITAL_API_KEY,
                "CST": cst,
                "X-SECURITY-TOKEN": sec,
                "Content-Type": "application/json",
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                if "dealReference" in data:
                    # Start a thread to verify the position was created properly
                    verification_thread = threading.Thread(
                        target=self.verify_position,
                        args=(data["dealReference"], symbol, direction),
                    )
                    verification_thread.daemon = True
                    verification_thread.start()

                    verification_threads[data["dealReference"]] = verification_thread
                    return data["dealReference"]

            logging.error(
                f"Failed to place order: {response.status_code} - {response.text}"
            )
            return None

        except Exception as e:
            logging.error(f"Error placing order: {str(e)}")
            return None

    def verify_position(self, deal_reference, symbol, direction, max_retries=5):
        """Verify a position was created and update with deal ID"""
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Wait before checking
                time.sleep(2 * (retry_count + 1))

                cst, sec = self.authenticate()
                if not cst or not sec:
                    retry_count += 1
                    continue

                # Check the deal confirmation
                url = f"{CAPITAL_API_URL}/confirms/{deal_reference}"
                headers = {
                    "X-CAP-API-KEY": CAPITAL_API_KEY,
                    "CST": cst,
                    "X-SECURITY-TOKEN": sec,
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    # Update the active position with deal ID
                    if symbol in active_positions and "dealId" in data:
                        active_positions[symbol]["deal_id"] = data["dealId"]
                        logging.info(
                            f"Position verified for {symbol}: dealId {data['dealId']}"
                        )
                        return

                # Try again
                retry_count += 1

            except Exception as e:
                logging.error(f"Error verifying position for {symbol}: {str(e)}")
                retry_count += 1

        logging.warning(
            f"Could not verify position for {symbol} after {max_retries} attempts"
        )

    def close_position(self, symbol):
        """Close an open position"""
        try:
            if symbol not in active_positions:
                logging.warning(f"No open position found for {symbol}")
                return False

            position = active_positions[symbol]
            deal_id = position.get("deal_id")

            if not deal_id:
                logging.error(f"No deal ID found for {symbol}")
                return False

            cst, sec = self.authenticate()
            if not cst or not sec:
                return False

            url = f"{CAPITAL_API_URL}/positions/{deal_id}"
            headers = {
                "X-CAP-API-KEY": CAPITAL_API_KEY,
                "CST": cst,
                "X-SECURITY-TOKEN": sec,
            }

            response = requests.delete(url, headers=headers)

            if response.status_code == 200:
                # Process the result
                data = response.json()

                # Determine if win/loss
                direction = position.get("action")
                entry = float(position.get("entry_price", 0))
                close_level = float(data.get("level", 0))

                result = None
                if direction == "BUY":
                    result = "WIN" if close_level > entry else "LOSS"
                else:  # SELL
                    result = "WIN" if close_level < entry else "LOSS"

                # Update PnL
                position_size = position.get("position_size", 0)
                if direction == "BUY":
                    pnl = (close_level - entry) * position_size
                else:
                    pnl = (entry - close_level) * position_size

                if hasattr(self.bot, "daily_pnl"):
                    self.bot.daily_pnl += pnl

                # Record result
                from bot_dev_backup import save_trade_to_csv

                save_trade_to_csv(
                    timestamp=datetime.now().isoformat(),
                    symbol=symbol,
                    action=f"CLOSE_{direction}",
                    tp=position.get("tp", 0),
                    sl=position.get("sl", 0),
                    result=result,
                )

                # Remove from active positions
                del active_positions[symbol]

                logging.info(
                    f"Closed position for {symbol} with result: {result}, PnL: {pnl:.2f}"
                )
                return True

            logging.error(
                f"Failed to close position: {response.status_code} - {response.text}"
            )
            return False

        except Exception as e:
            logging.error(f"Error closing position: {str(e)}")
            return False

    def close_all_positions(self, reason="Manual close"):
        """Close all active positions"""
        for symbol in list(active_positions.keys()):
            self.close_position(symbol)
            logging.info(f"Closed position for {symbol}: {reason}")

    def update_position(self, deal_id, sl=None, tp=None):
        """Update stop loss and/or take profit for a position"""
        try:
            cst, sec = self.authenticate()
            if not cst or not sec:
                return False

            payload = {}
            if sl is not None:
                payload["stopLevel"] = str(sl)
            if tp is not None:
                payload["limitLevel"] = str(tp)

            if not payload:
                return False

            url = f"{CAPITAL_API_URL}/positions/{deal_id}"
            headers = {
                "X-CAP-API-KEY": CAPITAL_API_KEY,
                "CST": cst,
                "X-SECURITY-TOKEN": sec,
                "Content-Type": "application/json",
            }

            response = requests.put(url, headers=headers, json=payload)

            if response.status_code == 200:
                logging.info(f"Updated position {deal_id}: SL={sl}, TP={tp}")
                return True

            logging.error(
                f"Failed to update position: {response.status_code} - {response.text}"
            )
            return False

        except Exception as e:
            logging.error(f"Error updating position: {str(e)}")
            return False

    def monitor_positions_loop(self):
        """Background loop to monitor and manage open positions"""
        while True:
            try:
                # Check each active position
                for symbol, position in list(active_positions.items()):
                    try:
                        # Get current price
                        current_price = self.get_current_price(symbol)
                        if not current_price:
                            continue

                        direction = position.get("action")
                        entry_price = position.get("entry_price")
                        position.get("sl")
                        deal_id = position.get("deal_id")

                        if not deal_id:
                            continue

                        # Calculate profit percentage
                        if direction == "BUY":
                            profit_pct = (
                                (current_price - entry_price) / entry_price * 100
                            )
                        else:  # SELL
                            profit_pct = (
                                (entry_price - current_price) / entry_price * 100
                            )

                        # Check for breakeven condition
                        if (
                            deal_id not in breakeven_positions
                            and profit_pct >= TRAILING_ACTIVATION * 100
                        ):
                            new_sl = entry_price
                            if self.update_position(deal_id, new_sl, None):
                                breakeven_positions.add(deal_id)
                                position["sl"] = new_sl
                                logging.info(f"Moved SL to breakeven for {symbol}")

                    except Exception as e:
                        logging.error(
                            f"Error monitoring position for {symbol}: {str(e)}"
                        )

                # Check for daily limits
                from bot_dev_backup import CLOSE_HOUR, DAILY_LOSS_LIMIT, DAILY_PROFIT_LIMIT

                if hasattr(self.bot, "daily_pnl"):
                    if self.bot.daily_pnl <= DAILY_LOSS_LIMIT:
                        logging.warning(
                            f"Daily loss limit reached: ${self.bot.daily_pnl:.2f}"
                        )
                        self.close_all_positions("Daily loss limit reached")

                    if self.bot.daily_pnl >= DAILY_PROFIT_LIMIT:
                        logging.info(
                            f"Daily profit target reached: ${self.bot.daily_pnl:.2f}"
                        )
                        self.close_all_positions("Daily profit target reached")

                # Check for end-of-day close
                current_hour = datetime.now().hour
                if CLOSE_HOUR >= 0 and current_hour == CLOSE_HOUR:
                    logging.info("End of day close hour reached.")
                    self.close_all_positions("End of day close time reached")

            except Exception as e:
                logging.error(f"Error in position monitoring loop: {str(e)}")

            # Sleep before next check
            time.sleep(60)

    def send_trade_notification(self, symbol, direction, price, tp, sl, size):
        """Send notification when a trade is executed"""
        message = (
            f"🚨 {direction} Signal for {symbol}\n\n"
            f"💰 Entry: {price:.5f}\n"
            f"🛑 Stop Loss: {sl:.5f}\n"
            f"✅ Take Profit: {tp:.5f}\n"
            f"📊 Position Size: {size}\n"
            f"📈 Risk/Reward: {abs(tp-price)/abs(price-sl):.2f}\n\n"
            f"🤖 Generated by Magus Prime X"
        )

        from bot_dev_backup import (
            is_telegram_async,
            send_telegram_message_async,
            send_telegram_message_sync,
        )

        if is_telegram_async:
            import asyncio

            asyncio.run(send_telegram_message_async(message))
        else:
            send_telegram_message_sync(message)

    def authenticate(self):
        """Authenticate with Capital.com API, using bot's method if available"""
        if self.bot and hasattr(self.bot, "authenticate"):
            return self.bot.authenticate()

        # Simplified authentication for standalone use
        try:
            url = f"{CAPITAL_API_URL}/session"
            headers = {"X-CAP-API-KEY": CAPITAL_API_KEY}
            data = {"identifier": CAPITAL_IDENTIFIER, "password": CAPITAL_API_PASSWORD}

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                resp_data = response.json()
                cst = resp_data.get("CST")
                security = resp_data.get("X-SECURITY-TOKEN")
                return cst, security
            else:
                logging.error(f"Authentication failed: {response.text}")
                return None, None
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return None, None


# Create global trade executor instance
trade_executor = None


def init_extensions(bot_instance=None):
    """Initialize all extensions"""
    global trade_executor

    if not EXTENSIONS_ENABLED:
        logging.info("Extensions disabled via configuration.")
        return

    logging.info("Initializing MAGUS PRIME X extensions...")

    # Initialize trade executor
    trade_executor = TradeExecutor(bot_instance)

    logging.info("Extensions initialized successfully!")


# Functions to expose to the main bot
def execute_trade(symbol, action, tp, sl, risk_percent=None):
    """Execute a trade using the trade executor"""
    if not EXTENSIONS_ENABLED or not trade_executor:
        logging.warning("Extensions are disabled or not initialized.")
        return False

    return trade_executor.execute_trade(symbol, action, tp, sl, risk_percent)


def close_position(symbol):
    """Close a position using the trade executor"""
    if not EXTENSIONS_ENABLED or not trade_executor:
        logging.warning("Extensions are disabled or not initialized.")
        return False

    return trade_executor.close_position(symbol)


def close_all_positions(reason="Manual close"):
    """Close all positions using the trade executor"""
    if not EXTENSIONS_ENABLED or not trade_executor:
        logging.warning("Extensions are disabled or not initialized.")
        return

    trade_executor.close_all_positions(reason)


def get_active_positions():
    """Get a list of all active positions"""
    return list(active_positions.values())
