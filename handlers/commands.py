from aiogram import Router, types
from aiogram.filters import CommandStart

from database.db_manager import db

router = Router()


# /start
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    db.clear_history(user_id)
    current_context = db.get_context(user_id)
    print(f"Контекст після очищення для {user_id}: {current_context}")
    await message.answer(
        "Hello! I've started a new session. I will remember our chat from now on. How are you today?"
    )
