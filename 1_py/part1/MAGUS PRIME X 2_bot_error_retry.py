import asyncio
import logging
import threading
import time
from functools import wraps

logger = logging.getLogger(__name__)


def with_retry(max_retries=3, retry_delay=5):
    """Decorator to retry a function on exception"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise
                    logger.warning(f"Retry {retries}/{max_retries} after error: {e}")
                    time.sleep(retry_delay)

        return wrapper

    return decorator


class SafeEventLoop:
    """Safely manage an asyncio event loop in a thread"""

    def __init__(self):
        self.loop = None
        self._lock = threading.Lock()

    def get_loop(self):
        """Get the current thread's event loop or create a new one"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                logger.warning("Existing event loop is closed, creating new one")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop
        except RuntimeError:
            # No event loop in this thread
            logger.info("Creating new event loop for thread")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def run_coroutine(self, coro):
        """Safely run a coroutine in the event loop"""
        with self._lock:
            self.loop = self.get_loop()
            try:
                return self.loop.run_until_complete(coro)
            except Exception as e:
                logger.error(f"Error running coroutine: {e}")
                raise

    def close(self):
        """Safely close the event loop"""
        with self._lock:
            if self.loop and not self.loop.is_closed():
                # Cancel all running tasks
                tasks = asyncio.all_tasks(self.loop)
                if tasks:
                    for task in tasks:
                        task.cancel()
                    try:
                        self.loop.run_until_complete(
                            asyncio.gather(*tasks, return_exceptions=True)
                        )
                    except Exception as e:
                        logger.error(f"Error cancelling tasks: {e}")

                # Close the loop
                self.loop.close()
                logger.info("Event loop closed safely")


# Global instance
safe_loop = SafeEventLoop()


# For use in threaded environments
@with_retry(max_retries=3)
def run_telegram_with_retry(telegram_app):
    """Run Telegram app with retry on failure"""
    try:
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Start the bot
        telegram_app.run_polling(allowed_updates=None, close_loop=False)

        # Cleanup
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()

        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

        loop.close()
        return True
    except Exception as e:
        logger.error(f"Error in Telegram bot: {e}")
        raise
