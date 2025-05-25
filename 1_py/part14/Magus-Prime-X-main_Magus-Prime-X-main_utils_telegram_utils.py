import os
import asyncio


def is_telegram_configured() -> bool:
    return bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"))


class TradeNotification:
    def __init__(self):
        import telegram
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.bot = telegram.Bot(token=token)

    async def send_signal(self, chat_id: str, message: str) -> None:
        await self.bot.send_message(chat_id=chat_id, text=message)

    async def send_plain_message(self, chat_id: str, message: str) -> None:
        await self.bot.send_message(chat_id=chat_id, text=message)


async def send_trade_notification_async(
    symbol: str,
    action: str,
    take_profit: float,
    stop_loss: float,
    confidence: float
) -> None:
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    msg = (
        f"Trade Signal\n"
        f"Symbol: {symbol}\n"
        f"Action: {action}\n"
        f"Take Profit: {take_profit}\n"
        f"Stop Loss: {stop_loss}\n"
        f"Confidence: {confidence:.2f}"
    )
    tn = TradeNotification()
    loop = asyncio.get_running_loop()
    await tn.send_signal(chat_id, msg)


def send_trade_notification(symbol, action, take_profit, stop_loss, confidence):
    asyncio.run(
        send_trade_notification_async(
            symbol=symbol,
            action=action,
            take_profit=take_profit,
            stop_loss=stop_loss,
            confidence=confidence
        )
    )


async def send_plain_message_async(chat_id: str, message: str) -> None:
    tn = TradeNotification()
    loop = asyncio.get_running_loop()
    await tn.send_plain_message(chat_id, message)


def send_plain_message(chat_id: str, message: str) -> None:
    asyncio.run(send_plain_message_async(chat_id, message))
