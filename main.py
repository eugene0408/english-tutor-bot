import asyncio
import logging

import uvicorn

from api import app
from handlers import chat_router, commands_router
from loader import bot, dp
from middlewares.check_sub import CheckSubscriptionMiddleware
from middlewares.only_text import OnlyTextMiddleware


async def start_fastapi():
    # Start web server at 8000 port
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def start_bot():
    # Loging to display errors and logs in console
    logging.basicConfig(level=logging.INFO)

    # Subscription check
    chat_router.message.middleware(CheckSubscriptionMiddleware())
    # Message has text check
    chat_router.message.middleware(OnlyTextMiddleware())

    # IMPORTANT: commands first than chat
    dp.include_router(commands_router)
    dp.include_router(chat_router)

    print("Bot with SQLite memory and subscription check is running...")
    await dp.start_polling(bot)


async def main():
    # Run both processes in parallel.
    await asyncio.gather(start_fastapi(), start_bot())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
