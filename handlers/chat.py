import asyncio
import random
from typing import cast

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from groq.types.chat import ChatCompletionMessageParam

from database.db_manager import db
from utils.ai_logic import generate_tutor_response
from utils.constants import EVERYDAY_TOPICS
from utils.prompts import ASK_ME_PROMPT, TRANSLATOR_PROMPT
from utils.states import TranslatorStates
from utils.user import get_user_id

router = Router()


# "🎲 Ask Me" button handler
@router.message(lambda message: message.text == "🎲 Ask Me")
async def handle_ask_me(message: types.Message):
    """
    Clear database, launch Groq with ASK_ME_PROMPT
    and randomly selected topic from EVERYDAY_TOPICS,
    save response to base and send it to chat
    """
    user_id = get_user_id(message)
    if user_id is None:
        return
    # Clear datebase for user
    db.clear_history(user_id)
    # get empty history
    history = db.get_context(user_id)

    chosen_topic = random.choice(EVERYDAY_TOPICS)
    final_prompt = ASK_ME_PROMPT.format(topic=chosen_topic)

    try:
        full_response, parts = await generate_tutor_response(
            history, custom_prompt=final_prompt
        )
        # Save AI question to base
        db.add_message(user_id, "assistant", full_response)
        # Get formated question
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


# "Translator 🌐" button handler
@router.message(lambda message: message.text == "Translator 🌐")
async def start_translation(message: types.Message, state: FSMContext):
    # Set waiting for text state
    await state.set_state(TranslatorStates.waiting_for_ukrainian_text)
    await message.answer("⏬ Пишіть українською 🇺🇦 ")


# BOT CAPTURES TEXT FOR TRANSLATION (only when the state is enabled)
@router.message(TranslatorStates.waiting_for_ukrainian_text)
async def process_translation(message: types.Message, state: FSMContext):
    uk_text = message.text
    # Create temp history for text to translate
    temporary_history = cast(
        ChatCompletionMessageParam, {"role": "user", "content": uk_text}
    )

    # Run Groq with TRANSLATOR_PROMPT
    _, parts = await generate_tutor_response(
        history=[temporary_history], custom_prompt=TRANSLATOR_PROMPT
    )

    # Translated text
    en_translation = parts[0] if parts else "Sorry, couldn't translate."

    # Send translated text to chat
    await message.answer(f"<code>{en_translation}</code>", parse_mode="HTML")

    # IMPORTANT: reset the state so the bot returns to normal chat mode
    await state.clear()


# CHAT MODE
@router.message()
async def handle_message(message: types.Message):
    user_id = get_user_id(message)
    if user_id is None:
        return
    user_text = message.text

    # Save user message
    db.add_message(user_id, "user", user_text)

    # Get history for AI
    history = db.get_context(user_id)

    try:
        # Run AI logic
        full_response, parts = await generate_tutor_response(history)

        # Save full response for AI context
        db.add_message(user_id, "assistant", full_response)

        # Send each part in separate message to Telegram chat
        for part in parts:
            await message.answer(part, parse_mode="HTML")
            # short break so Telegram doest block it as spam
            await asyncio.sleep(0.8)

    except Exception as e:
        print(f"Error in chat handler: {e}")
        await message.answer("I'm sorry, I encountered an error. Please try again.")
