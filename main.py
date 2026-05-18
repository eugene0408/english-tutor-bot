import asyncio
import logging

from handlers import chat_router, commands_router
from loader import bot, dp
from middlewares.check_sub import CheckSubscriptionMiddleware


async def main():
    # Логування для відображення помилок та статусу бота в консолі
    logging.basicConfig(level=logging.INFO)

    # Перевірка підписки
    chat_router.message.middleware(CheckSubscriptionMiddleware())

    # Важливо: спочатку команди, потім чат
    dp.include_router(commands_router)
    dp.include_router(chat_router)

    print("Bot with SQLite memory and subscription check is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
