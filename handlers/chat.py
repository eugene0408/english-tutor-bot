import asyncio

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from database.db_manager import db
from utils.ai_logic import generate_tutor_response
from utils.prompts import ASK_ME_PROMPT, TRANSLATOR_PROMPT
from utils.states import TranslatorStates

router = Router()


# ХЕНДЛЕР КНОПКИ "🎲 Ask Me"
@router.message(lambda message: message.text == "🎲 Ask Me")
async def handle_ask_me(message: types.Message):
    """
    Очищує базу, запускає Groq з промптом ASK_ME_PROMPT,
    зберігає відповідь у базу та надсилає у чат
    """
    user_id = message.from_user.id
    # очищує базу даних
    db.clear_history(user_id)
    # отримує пустий контекст
    history = db.get_context(user_id)

    try:
        full_response, parts = await generate_tutor_response(
            history, custom_prompt=ASK_ME_PROMPT
        )
        # Зберігає питання у базу
        db.add_message(user_id, "assistant", full_response)
        # Отримує відформатоване питання
        ai_question = (
            parts[0]
            if parts
            else "I'm sorry, I couldn't think of a question. Please try again."
        )
        await message.answer(ai_question, parse_mode="HTML")
    except Exception as e:
        print(f"Error in ask handler: {e}")
        await message.answer(
            "I'm sorry, I couldn't think of a question. Please try again."
        )


# ХЕНДЛЕР КНОПКИ "Translator 🌐"
@router.message(lambda message: message.text == "Translator 🌐")
async def start_translation(message: types.Message, state: FSMContext):
    # Вмикає стан очікування тексту для перекладу
    await state.set_state(TranslatorStates.waiting_for_ukrainian_text)
    await message.answer("⏬ Пишіть українською 🇺🇦 ")


# БОТ ПЕРЕХОПЛЮЄ ТЕКСТ ДЛЯ ПЕРЕКЛАДУ (тільки коли увімкнено стан)
@router.message(TranslatorStates.waiting_for_ukrainian_text)
async def process_translation(message: types.Message, state: FSMContext):
    uk_text = message.text
    # записує текст який потрібно перекласти у тимчасову історію
    temporary_history = [{"role": "user", "content": uk_text}]

    # Виклик Groq з промптом для перекладу
    _, parts = await generate_tutor_response(
        history=temporary_history, custom_prompt=TRANSLATOR_PROMPT
    )

    # Переклад
    en_translation = parts[0] if parts else "Sorry, couldn't translate."

    # Відправляє переклад користувачу
    await message.answer(f"<code>{en_translation}</code>", parse_mode="HTML")

    # ВАЖЛИВО: скидання стану щоб бот повернувася в режим звичайного чату
    await state.clear()


# ЗВИЧАЙНИЙ ЧАТ
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
            await asyncio.sleep(0.8)

    except Exception as e:
        print(f"Error in chat handler: {e}")
        await message.answer("I'm sorry, I encountered an error. Please try again.")
