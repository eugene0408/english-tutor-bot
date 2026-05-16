from aiogram import Router, types
from aiogram.filters import CommandStart

from database.db_manager import db

router = Router()


# /start
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    # Очищає базу при перезапуску бота командою /start
    db.clear_history(message.from_user.id)
    await message.answer(
        "Hello! I've started a new session. I will remember our chat from now on. How are you today?"
    )
