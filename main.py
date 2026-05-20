import asyncio
import logging

from handlers import chat_router, commands_router
from loader import bot, dp
from middlewares.check_sub import CheckSubscriptionMiddleware


async def main():
    # Loging to display errors and logs in console
    logging.basicConfig(level=logging.INFO)

    # Subscription check
    chat_router.message.middleware(CheckSubscriptionMiddleware())

    # IMPORTANT: commands first than chat
    dp.include_router(commands_router)
    dp.include_router(chat_router)

    print("Bot with SQLite memory and subscription check is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
