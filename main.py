import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from groq import Groq

# 1. Завантаження налаштувань
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default_properties=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY)


# 2. Логіка бази даних
class Database:
    def __init__(self, db_name="tutor_bot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Таблиця для зберігання повідомлень: id користувача, роль (user/assistant) і текст
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history
            (user_id INTEGER, role TEXT, content TEXT)
        """)
        self.conn.commit()

    def add_message(self, user_id, role, content):
        self.cursor.execute(
            "INSERT INTO history VALUES (?, ?, ?)", (user_id, role, content)
        )
        self.conn.commit()

    def get_context(self, user_id, limit=10):
        # Отримуємо останні 10 повідомлень для контексту
        self.cursor.execute(
            "SELECT role, content FROM history WHERE user_id = ? ORDER BY rowid DESC LIMIT ?",
            (user_id, limit),
        )
        rows = self.cursor.fetchall()
        # Повертаємо у правильному хронологічному порядку
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def clear_history(self, user_id):
        self.cursor.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        self.conn.commit()


db = Database()

# 3. Обробка повідомлень
SYSTEM_PROMPT = {
    "role": "system",
    "content": """You are an advanced, friendly AI English Tutor. Your goal is to help the user improve their conversational English through natural, real-life dialogue.

    ### CRITICAL INSTRUCTIONS:
    1. LANGUAGE: Always respond in English. Use natural, modern, conversational English.
    2. FORMATTING: You MUST use HTML tags for formatting.
       - Use <b>...</b> for bold.
       - Use <i>...</i> for italics.
       - Use <code>...</code> for specific words or phrases.
    3. STRUCTURE OF YOUR RESPONSE:
       - First, reply to the user's message naturally as a conversation partner. IMPORTANT: Do not ask any questions here. Just a statement or reaction.
       - Then, add a separator: ___
       - Then, provide a "Tutor Feedback" section using <b> tags.
       - Then, add another separator: ___
       - Then, ask question here
    4. ERROR CORRECTION: Gently correct mistakes (e.g., <b>Correction:</b> <s>[mistake]</s> -> <b>[fix]</b>).
    5. NATURAL ALTERNATIVES: Always suggest a "Natural way to say it".
    6. ENGAGEMENT: Always end with an open-ended question.

    ### FORMATTING EXAMPLE:
    That sounds like a great plan! Going to the park is always a good idea.
    ___
    💡 <b>Tutor Feedback:</b>
    • <b>Correction:</b> <s>I go to park</s> -> <b>I am going to the park</b> (Present Continuous for future plans).
    • <b>Natural way to say it:</b> "I'm heading to the park."
    ___
    ❔ What are you planning to do there?
   """,
}


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    db.clear_history(message.from_user.id)
    await message.answer(
        "Hello! I've started a new session. I will remember our chat from now on. How are you today?"
    )


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    # Зберігаємо повідомлення користувача
    db.add_message(user_id, "user", user_text)

    # Формуємо контекст для ШІ (системний промпт + історія з бази)
    history = db.get_context(user_id)
    messages = [SYSTEM_PROMPT] + history

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
        )

        full_response = chat_completion.choices[0].message.content

        # Зберігаємо відповідь бота в базу
        db.add_message(user_id, "assistant", full_response)

        # Розбиваємо відповідь бота на частини за роздільником ___
        parts = full_response.split("___")

        # Надсилаємо кожну частину окремим повідомленням
        for part in parts:
            clean_part = part.strip()
            if clean_part:
                await message.answer(clean_part, parse_mode="HTML")
                # коротка пауза щоб Telegram не блокував як спам
                await asyncio.sleep(0.6)

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("I'm sorry, I encountered an error. Please try again.")


async def main():
    print("Bot with SQLite memory is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
