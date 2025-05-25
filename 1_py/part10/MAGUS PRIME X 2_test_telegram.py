from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update, ParseMode

# Initialize the notifier
notifier = TelegramNotifier()

if not notifier.enabled:
    print("Telegram notifier is not enabled. Please check your environment variables.")
    exit(1)

# Test message
message = """🔔 <b>TEST MESSAGE</b> 🔔

This is a test message from Magus Prime X.
Timestamp: {timestamp}
Status: ✅ Working!"""

# Send the message
try:
    result = notifier.bot.send_message(
        chat_id=notifier.channel_id,
        text=message,
        parse_mode="HTML"
    )
    print(f"Message sent successfully! Message ID: {result.message_id}")
except Exception as e:
    print(f"Error sending message: {str(e)}")
