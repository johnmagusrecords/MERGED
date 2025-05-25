# enhanced_signal_sender.py
import logging
import asyncio
from dataclasses import dataclass
from typing import Optional, Any, Callable, Awaitable
import os
from telegram import Bot  # type: ignore
from indicators import calculate_rsi_safe, calculate_macd_safe, calculate_ema_safe

logger = logging.getLogger("EnhancedSignalSender")
logging.basicConfig(level=logging.INFO)


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    telegram_signal_chat_id: str

    @staticmethod
    def from_env() -> "Config":
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_SIGNAL_CHAT_ID")
        if not token or not chat_id:
            raise ConfigurationError(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_SIGNAL_CHAT_ID must be set in environment.")
        return Config(token, chat_id)


@dataclass
class TradeSignal:
    symbol: str
    direction: str
    entry: float
    stop_loss: float
    take_profits: list[float]
    strategy: str
    timeframe: str


class TradeNotification:
    """Stub for trade notification system."""

    async def notify(self, signal: TradeSignal) -> str:
        # ...implementation...
        return "notification_id"


class SentimentAnalyzer:
    """Stub for sentiment analyzer."""

    async def analyze(self, signal: TradeSignal) -> str:
        # ...implementation...
        return "neutral"


def telegram_bot_factory(token: str) -> Bot:
    """Factory for creating a Telegram Bot instance."""
    return Bot(token=token)


class EnhancedSignalSender:
    """
    Handles sending trade signals and notifications via Telegram and other channels.
    """

    def __init__(
        self,
        config: Config,
        telegram_bot_factory: Callable[[str], Bot],
        trade_notification: TradeNotification,
        sentiment_analyzer: SentimentAnalyzer,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        """
        Args:
            config: Configuration dataclass.
            telegram_bot_factory: Factory function to create a Telegram Bot.
            trade_notification: TradeNotification instance.
            sentiment_analyzer: SentimentAnalyzer instance.
            loop: Optional asyncio event loop.
        """
        self.config = config
        self.bot = telegram_bot_factory(config.telegram_bot_token)
        self.trade_notification = trade_notification
        self.sentiment_analyzer = sentiment_analyzer
        self.loop = loop or asyncio.get_event_loop()
        self._monitor_task: Optional[asyncio.Task] = None

    async def send_signal(self, signal: TradeSignal) -> str:
        """
        Formats and sends a trade signal to Telegram.

        Args:
            signal: TradeSignal dataclass.

        Returns:
            str: Signal ID or message ID.

        Raises:
            Exception: On Telegram API failure.
        """
        message = self._format_signal_message(signal)
        logger.info(f"Sending signal: {message}")
        try:
            sent = await self.loop.run_in_executor(
                None,
                lambda: self.bot.send_message(
                    chat_id=self.config.telegram_signal_chat_id,
                    text=message,
                    parse_mode="HTML"
                )
            )
            logger.info(f"Signal sent, message_id={sent.message_id}")
            return str(sent.message_id)
        except Exception as e:
            logger.error(f"Failed to send signal: {e}")
            raise

    async def send_trade_notification(self, signal: TradeSignal) -> str:
        """
        Sends a trade notification via the TradeNotification system.

        Args:
            signal: TradeSignal dataclass.

        Returns:
            str: Notification ID.

        Raises:
            Exception: On notification failure.
        """
        logger.info(f"Sending trade notification for {signal.symbol}")
        try:
            notification_id = await self.trade_notification.notify(signal)
            logger.info(f"Trade notification sent, id={notification_id}")
            return notification_id
        except Exception as e:
            logger.error(f"Failed to send trade notification: {e}")
            raise

    async def send_signal_with_context(
        self,
        signal: TradeSignal,
        commentary: Optional[str] = None
    ) -> str:
        """
        Sends a trade signal with optional contextual commentary.

        Args:
            signal: TradeSignal dataclass.
            commentary: Optional commentary string.

        Returns:
            str: Signal ID.

        Raises:
            Exception: On Telegram API failure.
        """
        message = self._format_signal_message(signal)
        if commentary:
            message += f"\n\n<b>Commentary:</b> {commentary}"
        logger.info(f"Sending signal with context: {message}")
        return await self.send_signal(signal)

    def _format_signal_message(self, signal: TradeSignal) -> str:
        """
        Formats a trade signal for Telegram.

        Args:
            signal: TradeSignal dataclass.

        Returns:
            str: Formatted message.
        """
        tp_str = ', '.join([str(tp) for tp in signal.take_profits])
        return (
            f"<b>Signal</b>\n"
            f"Symbol: {signal.symbol}\n"
            f"Direction: {signal.direction}\n"
            f"Entry: {signal.entry}\n"
            f"Stop Loss: {signal.stop_loss}\n"
            f"Take Profits: {tp_str}\n"
            f"Strategy: {signal.strategy}\n"
            f"Timeframe: {signal.timeframe}"
        )

    async def monitor_signals(self, poll_interval: float = 60.0) -> None:
        """
        Background task to monitor signals.

        Args:
            poll_interval: Time in seconds between polls.

        Raises:
            asyncio.CancelledError: If the task is cancelled.
        """
        logger.info("Started monitoring signals.")
        try:
            while True:
                # ...monitoring logic...
                await asyncio.sleep(poll_interval)
        except asyncio.CancelledError:
            logger.info("Signal monitoring cancelled.")
            raise

    def start_monitoring(self, poll_interval: float = 60.0) -> None:
        """
        Starts the background monitoring task.

        Args:
            poll_interval: Time in seconds between polls.
        """
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = self.loop.create_task(
                self.monitor_signals(poll_interval))
            logger.info("Monitoring task started.")

    async def shutdown(self) -> None:
        """
        Cancels the background monitoring task.
        """
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                logger.info("Monitoring task shutdown complete.")

# --- No side-effects at import ---


if __name__ == "__main__":
    async def main():
        config = Config.from_env()
        trade_notification = TradeNotification()
        sentiment_analyzer = SentimentAnalyzer()
        sender = EnhancedSignalSender(
            config,
            telegram_bot_factory,
            trade_notification,
            sentiment_analyzer
        )
        # Example usage:
        signal = TradeSignal(
            symbol="BTCUSDT",
            direction="LONG",
            entry=30000.0,
            stop_loss=29500.0,
            take_profits=[30500.0, 31000.0],
            strategy="Breakout",
            timeframe="1h"
        )
        await sender.send_signal(signal)
        sender.start_monitoring()
        # ...run for a while, then shutdown...
        await asyncio.sleep(5)
        await sender.shutdown()

    asyncio.run(main())
