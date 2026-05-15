import asyncio
import logging

from handlers import chat_router, commands_router
from loader import bot, dp


async def main():
    # Логування щоб бачити помилки або статус бота в консолі Railway
    logging.basicConfig(level=logging.INFO)

    # ПІДКЛЮЧАЄМО РОУТЕРИ
    # Важливо: спочатку команди, потім звичайний чат!
    dp.include_router(commands_router)
    dp.include_router(chat_router)

    print("Bot with SQLite memory is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
