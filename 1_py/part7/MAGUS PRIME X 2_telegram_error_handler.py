import asyncio
import logging
import traceback

from telegram import Update
from telegram.error import BadRequest, ChatMigrated, Conflict, NetworkError, TimedOut
from telegram.ext import ContextTypes

# Configure logging
logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Telegram errors gracefully"""
    # Log the error before we do anything else
    error = context.error

    # Get traceback information
    tb_list = traceback.format_exception(None, error, error.__traceback__)
    tb_string = "".join(tb_list)

    # Detailed error message for logging
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    error_msg = (
        f"Exception while handling an update:\n"
        f"update = {update_str}\n\n"
        f"error = {tb_string}"
    )

    # Log the error
    logger.error(error_msg)

    # Handle different types of errors specifically
    if isinstance(error, BadRequest):
        if "chat not found" in str(error):
            logger.error(
                "Telegram Chat ID is invalid or the bot doesn't have access to the chat."
            )
            logger.error("Please check your TELEGRAM_CHAT_ID in the .env file.")
            logger.error("To get your chat ID, message @userinfobot on Telegram.")
        elif "group chat was upgraded to a supergroup" in str(error):
            logger.warning("Group was upgraded to supergroup. Chat ID has changed.")
        else:
            logger.error(f"BadRequest error: {error}")

    elif isinstance(error, TimedOut):
        logger.warning(f"Telegram request timed out: {error}")

    elif isinstance(error, NetworkError):
        logger.error(f"Network error communicating with Telegram: {error}")
        logger.info("Waiting 10 seconds before retrying")
        await asyncio.sleep(10)

    elif isinstance(error, ChatMigrated):
        logger.warning(f"Chat ID migrated to: {error.new_chat_id}")

    elif isinstance(error, Conflict):
        logger.error(f"Telegram conflict error: {error}")

    else:
        logger.error(f"Unhandled Telegram error: {type(error).__name__}: {error}")

    # Inform developer/admin about the error if it's serious
    try:
        # Only for serious errors, you might want to notify an admin
        if not isinstance(
            error, (TimedOut, NetworkError)
        ) and "chat not found" not in str(error):
            pass
            # You could add admin notification here if needed
            # await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Serious error: {type(error).__name__}")
    except Exception as e:
        logger.error(f"Failed to notify admin about error: {e}")


# Helper function to register this handler
def register_error_handler(application):
    """Register the error handler with a Telegram application"""
    application.add_error_handler(error_handler)
    logger.info("Telegram error handler registered")
