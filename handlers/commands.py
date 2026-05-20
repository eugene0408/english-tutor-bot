from aiogram import Router, types
from aiogram.filters import CommandStart

from database.db_manager import db
from keyboards.main_menu import get_main_keyboard
from utils.user import get_user_id

router = Router()


# /start
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = get_user_id(message)
    if user_id is None:
        return
    # Clear datebase for user
    db.clear_history(user_id)

    await message.answer(
        "Hello! I've started a new session. I will remember our chat from now on. How are you today?",
        reply_markup=get_main_keyboard(),  # buttons
    )
