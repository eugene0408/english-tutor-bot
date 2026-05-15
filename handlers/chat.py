import asyncio

from aiogram import Router, types

from database.db_manager import db
from utils.ai_logic import generate_tutor_response

router = Router()


@router.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    # Зберігаємо повідомлення користувача
    db.add_message(user_id, "user", user_text)

    # Отримуємо історію для передачі AI
    history = db.get_context(user_id)

    try:
        # Викликаємо логіку AI
        full_response, parts = await generate_tutor_response(history)

        # Зберігаємо повну відповідь бота в базу для контексту
        db.add_message(user_id, "assistant", full_response)

        # Надсилаємо кожну частину окремим повідомленням у Telegram
        for part in parts:
            await message.answer(part, parse_mode="HTML")
            # коротка пауза, щоб Telegram не блокував як спам
            await asyncio.sleep(0.6)

    except Exception as e:
        print(f"Error in chat handler: {e}")
        await message.answer("I'm sorry, I encountered an error. Please try again.")
