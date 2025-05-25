import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
from telegram import Bot, ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Updater

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends trading signals, warnings and updates to Telegram"""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            logger.warning(
                "Telegram bot token not found. Notifications will not be sent."
            )
            self.bot = None
            self.enabled = False
        else:
            self.bot = Bot(token=self.token)
            self.enabled = True

        self.channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        self.admin_ids = [
            int(id) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id
        ]
        self.user_ids = {}  # Maps user IDs to subscription status
        self.user_db_path = "telegram_users.json"
        self.load_users()

        # Signal formatting templates
        self.signal_template = """
🔔 <b>TRADING SIGNAL</b> 🔔

🪙 <b>{symbol}</b> {direction}

💰 Entry: {entry}
✅ Take Profit: {take_profit}
🛑 Stop Loss: {stop_loss}

Risk/Reward: {risk_reward}
Timeframe: {timeframe}
Confidence: {confidence}%

<i>{additional_info}</i>

⏰ {timestamp}
"""

        self.warning_template = """
⚠️ <b>WARNING</b> ⚠️

{warning_message}

Symbol: {symbol}
Timeframe: {timeframe}

⏰ {timestamp}
"""

        self.analysis_template = """
📊 <b>MARKET ANALYSIS</b> 📊

🪙 <b>{symbol}</b> ({timeframe})

<b>Current price:</b> {price}
<b>Trend:</b> {trend}
<b>Sentiment:</b> {sentiment}

💡 <b>Key Points:</b>
{key_points}

⏰ {timestamp}
"""

        # Start the background thread for handling asynchronous events
        if self.enabled:
            self.event_thread = threading.Thread(
                target=self.run_event_loop, daemon=True
            )
            self.event_thread.start()

    def load_users(self) -> None:
        """Load registered users from JSON file"""
        try:
            if os.path.exists(self.user_db_path):
                with open(self.user_db_path, "r") as f:
                    self.user_ids = json.load(f)
                logger.info(f"Loaded {len(self.user_ids)} users from database")
        except Exception as e:
            logger.error(f"Error loading users: {str(e)}")
            self.user_ids = {}

    def save_users(self) -> None:
        """Save registered users to JSON file"""
        try:
            with open(self.user_db_path, "w") as f:
                json.dump(self.user_ids, f)
        except Exception as e:
            logger.error(f"Error saving users: {str(e)}")

    def run_event_loop(self) -> None:
        """Run the asyncio event loop in a separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Test connection
        try:
            loop.run_until_complete(
                self.send_message_to_admins(
                    "Trading bot notification system is online."
                )
            )
            logger.info("Telegram notification system initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Telegram notification system: {str(e)}")

        try:
            loop.run_forever()
        except Exception as e:
            logger.error(f"Error in Telegram event loop: {str(e)}")
        finally:
            loop.close()

    async def send_message(
        self, chat_id: str, message: str, parse_mode: str = ParseMode.HTML
    ) -> bool:
        """Send a message to a specific chat"""
        if not self.enabled or not self.bot:
            logger.warning("Telegram notifications disabled or bot not initialized")
            return False

        try:
            await self.bot.send_message(
                chat_id=chat_id, text=message, parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False

    async def send_message_to_channel(self, message: str) -> bool:
        """Send a message to the configured channel"""
        if not self.channel_id:
            logger.warning("No Telegram channel configured")
            return False

        return await self.send_message(self.channel_id, message)

    async def send_message_to_admins(self, message: str) -> bool:
        """Send a message to all admin users"""
        if not self.admin_ids:
            logger.warning("No Telegram admins configured")
            return False

        success = True
        for admin_id in self.admin_ids:
            if not await self.send_message(admin_id, message):
                success = False

        return success

    async def send_message_to_all_users(self, message: str) -> Dict[str, int]:
        """Send a message to all subscribed users"""
        if not self.user_ids:
            logger.warning("No Telegram users registered")
            return {"success": 0, "failed": 0}

        success_count = 0
        failed_count = 0

        for user_id, user_data in self.user_ids.items():
            # Only send to subscribed users
            if user_data.get("subscribed", False):
                if await self.send_message(user_id, message):
                    success_count += 1
                else:
                    failed_count += 1

        return {"success": success_count, "failed": failed_count}

    def send_signal(
        self,
        symbol: str,
        direction: str,
        entry: float,
        take_profit: float,
        stop_loss: float,
        timeframe: str,
        confidence: float,
        additional_info: str = "",
    ) -> None:
        """Send a trading signal to all channels"""
        if not self.enabled:
            return

        # Calculate risk/reward ratio
        if direction.lower() == "buy":
            risk = entry - stop_loss
            reward = take_profit - entry
        else:
            risk = stop_loss - entry
            reward = entry - take_profit

        risk_reward = round(reward / risk, 2) if risk > 0 else "N/A"

        # Format the signal message
        message = self.signal_template.format(
            symbol=symbol,
            direction="🟢 BUY" if direction.lower() == "buy" else "🔴 SELL",
            entry=entry,
            take_profit=take_profit,
            stop_loss=stop_loss,
            risk_reward=risk_reward,
            timeframe=timeframe,
            confidence=int(confidence * 100),
            additional_info=additional_info,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Send warning about incoming signal first
        self.send_warning(
            f"Incoming {direction.upper()} signal for {symbol} in 10 seconds",
            symbol,
            timeframe,
        )

        # Wait 10 seconds before sending the actual signal
        def delayed_signal():
            time.sleep(10)
            asyncio.run(self.send_message_to_channel(message))
            asyncio.run(self.send_message_to_all_users(message))

        threading.Thread(target=delayed_signal).start()

    def send_warning(
        self, warning_message: str, symbol: str = "", timeframe: str = ""
    ) -> None:
        """Send a warning message"""
        if not self.enabled:
            return

        message = self.warning_template.format(
            warning_message=warning_message,
            symbol=symbol or "All Markets",
            timeframe=timeframe or "All Timeframes",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        asyncio.run(self.send_message_to_channel(message))
        asyncio.run(self.send_message_to_all_users(message))

    def send_market_analysis(
        self,
        symbol: str,
        timeframe: str,
        price: float,
        trend: str,
        sentiment: str,
        key_points: List[str],
    ) -> None:
        """Send market analysis update"""
        if not self.enabled:
            return

        # Format key points as bullet points
        formatted_key_points = "\n".join([f"• {point}" for point in key_points])

        message = self.analysis_template.format(
            symbol=symbol,
            timeframe=timeframe,
            price=price,
            trend=trend,
            sentiment=sentiment,
            key_points=formatted_key_points,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        asyncio.run(self.send_message_to_channel(message))
        asyncio.run(self.send_message_to_all_users(message))

    def send_custom_notification(
        self, title: str, message: str, importance: str = "normal"
    ) -> None:
        """Send a custom notification"""
        if not self.enabled:
            return

        emoji_map = {"high": "🔴", "normal": "🔵", "low": "⚪"}

        emoji = emoji_map.get(importance.lower(), "🔵")

        formatted_message = f"""
{emoji} <b>{title}</b> {emoji}

{message}

⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        asyncio.run(self.send_message_to_channel(formatted_message))
        asyncio.run(self.send_message_to_all_users(formatted_message))

    def register_user(self, user_id: str, username: str = None) -> bool:
        """Register a new user for notifications"""
        try:
            str_user_id = str(user_id)
            if str_user_id not in self.user_ids:
                self.user_ids[str_user_id] = {
                    "username": username,
                    "registered_at": datetime.now().isoformat(),
                    "subscribed": True,
                }
            else:
                self.user_ids[str_user_id]["subscribed"] = True

            self.save_users()
            return True
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False

    def unregister_user(self, user_id: str) -> bool:
        """Unregister a user from notifications"""
        try:
            str_user_id = str(user_id)
            if str_user_id in self.user_ids:
                self.user_ids[str_user_id]["subscribed"] = False
                self.save_users()
            return True
        except Exception as e:
            logger.error(f"Error unregistering user: {str(e)}")
            return False

    def get_subscribers_count(self) -> int:
        """Get the number of subscribed users"""
        return sum(
            1
            for user_data in self.user_ids.values()
            if user_data.get("subscribed", False)
        )

    def setup_bot_commands(self, updater: Updater) -> None:
        """Setup command handlers for the Telegram bot"""
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", self.cmd_start))
        dp.add_handler(CommandHandler("stop", self.cmd_stop))
        dp.add_handler(CommandHandler("help", self.cmd_help))
        dp.add_handler(CommandHandler("status", self.cmd_status))

        # Admin commands
        dp.add_handler(CommandHandler("broadcast", self.cmd_broadcast))
        dp.add_handler(CommandHandler("subscribers", self.cmd_subscribers))

        logger.info("Telegram bot commands initialized")

    # Bot command handlers
    async def cmd_start(self, update: Update, context: CallbackContext) -> None:
        """Handle the /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username

        self.register_user(user_id, username)

        await update.message.reply_text(
            "Welcome to the Trading Bot notifications!\n\n"
            "You're now subscribed to receive trading signals and market updates.\n"
            "Use /help to see available commands."
        )

    async def cmd_stop(self, update: Update, context: CallbackContext) -> None:
        """Handle the /stop command"""
        user_id = update.effective_user.id

        self.unregister_user(user_id)

        await update.message.reply_text(
            "You've been unsubscribed from trading notifications.\n"
            "You can use /start to subscribe again anytime."
        )

    async def cmd_help(self, update: Update, context: CallbackContext) -> None:
        """Handle the /help command"""
        await update.message.reply_text(
            "Available commands:\n\n"
            "/start - Subscribe to notifications\n"
            "/stop - Unsubscribe from notifications\n"
            "/status - Check bot status\n"
            "/help - Show this help message"
        )

    async def cmd_status(self, update: Update, context: CallbackContext) -> None:
        """Handle the /status command"""
        await update.message.reply_text(
            "Trading Bot Status: Online\n\n"
            f"Subscribers: {self.get_subscribers_count()}\n"
            f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    async def cmd_broadcast(self, update: Update, context: CallbackContext) -> None:
        """Handle the /broadcast command (admin only)"""
        user_id = update.effective_user.id

        if str(user_id) not in [str(id) for id in self.admin_ids]:
            await update.message.reply_text(
                "Sorry, this command is only available to administrators."
            )
            return

        # Get the message to broadcast
        if not context.args:
            await update.message.reply_text("Usage: /broadcast <message>")
            return

        message = " ".join(context.args)

        # Send to all subscribers
        results = await self.send_message_to_all_users(message)

        await update.message.reply_text(
            f"Broadcast sent to {results['success']} users.\n"
            f"Failed: {results['failed']}"
        )

    async def cmd_subscribers(self, update: Update, context: CallbackContext) -> None:
        """Handle the /subscribers command (admin only)"""
        user_id = update.effective_user.id

        if str(user_id) not in [str(id) for id in self.admin_ids]:
            await update.message.reply_text(
                "Sorry, this command is only available to administrators."
            )
            return

        # Count active subscribers
        count = self.get_subscribers_count()

        await update.message.reply_text(f"Current subscribers: {count}")
