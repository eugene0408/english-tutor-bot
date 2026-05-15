import asyncio

from loader import groq_client
from utils.prompts import SYSTEM_PROMPT


async def generate_tutor_response(history: list) -> list:
    """
    Формує запит до AI, отримує відповідь та розбиває її на частини.
    Повертає повну відповідь для бази та список очищених повідомлень.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    # Запускаємо groq_client в окремому потоці
    loop = asyncio.get_event_loop()
    chat_completion = await loop.run_in_executor(
        None,
        lambda: groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
        ),
    )
    # Відповідь AI
    full_response = chat_completion.choices[0].message.content
    # Розбиваємо відповідь на частини за роздільником ___
    parts = full_response.split("___")
    # Фільтруємо порожні частини та прибираємо зайві пробіли
    clean_parts = [part.strip() for part in parts if part.strip]
    # Повертаємо повну відповідь та частини
    return full_response, clean_parts
