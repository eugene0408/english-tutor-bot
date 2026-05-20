from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types.base import TelegramObject

from loader import bot, settings


class CheckSubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Skip check any other event except Message
        if not isinstance(event, Message):
            return await handler(event, data)
        # Skip check command /start, so user can see greeting message
        if event.text and event.text.startswith("/start"):
            return await handler(event, data)

        try:
            # Check user status in channel
            if event.from_user is None:
                return
            member = await bot.get_chat_member(
                chat_id=settings.CHANNEL_ID, user_id=event.from_user.id
            )
            # left or kicked means user is not subscripted
            if member.status in ["left", "kicked"]:
                raise ValueError()  # Artificially induce an error to enter the access control unit

            # If user is subscripted (member, administrator, creator), continue handler
            return await handler(event, data)

        except Exception:
            # If no subscription block handler and send subscription button
            keybord = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📢 Subscribe to Channel", url=settings.CHANNEL_URL
                        )
                    ]
                ]
            )

            await event.answer(
                "⚠️ <b>Access Denied!</b>\n\n"
                "To use this English tutor bot, you must be subscribed to channel. ",
                parse_mode="HTML",
                reply_markup=keybord,
            )
            # Return None
            return
