import asyncio

from loader import groq_client
from utils.prompts import SYSTEM_PROMPT


async def generate_tutor_response(
    history: list, custom_prompt: str = SYSTEM_PROMPT
) -> tuple:
    """
    Формує запит до AI, отримує відповідь та розбиває її на частини.
    Повертає повну відповідь для бази та список оформлених повідомлень.
    """
    messages = [{"role": "system", "content": custom_prompt}] + history

    # Запускає groq_client в окремому потоці
    loop = asyncio.get_event_loop()
    chat_completion = await loop.run_in_executor(
        None,
        lambda: groq_client.chat.completions.create(
            messages=messages, model="llama-3.3-70b-versatile", temperature=0.8
        ),
    )
    # Відповідь AI
    full_response = chat_completion.choices[0].message.content
    # Вставляє невидимі символи щоб зберегти абзаци у Telegram
    formated_response = full_response.replace("\n\n", "\n\u200e\n")
    # Розбиває відповідь на частини за роздільником ___
    parts = formated_response.split("___")
    # Фільтрує порожні частини та прибирає зайві пробіли
    clean_parts = [part.strip() for part in parts if part.strip]
    # Повертає повну відповідь для бази та частини для повідомленнь
    return full_response, clean_parts
