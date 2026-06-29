from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types.base import TelegramObject


class OnlyTextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Check whether this event is actually a Message and whether it contains any text.
        if isinstance(event, Message):
            if not event.text:
                # If there is no text, stop bot!
                await event.answer("⚠️ Error: 🤖 I only understand text messages.")
                return

        # If ok continue handler
        return await handler(event, data)
