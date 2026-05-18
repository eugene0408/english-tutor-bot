from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from loader import CHANNEL_ID, CHANNEL_URL, bot


class CheckSubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # Пропускаємо команду /start, щоб користувач міг побачити привітання
        if event.text and event.text.startswith("/start"):
            return await handler(event, data)

        try:
            # Запитуємо у Телеграма статус користувача в каналу
            member = await bot.get_chat_member(
                chat_id=CHANNEL_ID, user_id=event.from_user.id
            )
            # Статуси 'left' (вийшов) та 'kicked' (забанений) означають, що підписки немає
            if member.status in ["left", "kicked"]:
                raise ValueError()  # Штучно викликаємо помилку, щоб перейти в блок керування доступом

            # Якщо користувач є в каналі (member, administrator, creator), продовжуємо виконання хендлера
            return await handler(event, data)

        except Exception:
            # Якщо підписки немає, блокуємо хендлер і надсилаємо кнопку підписки
            keybord = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📢 Subscribe to Channel", url=CHANNEL_URL
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
            # Повертаємо None
            return
