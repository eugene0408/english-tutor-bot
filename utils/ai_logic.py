import asyncio
from typing import cast

from groq.types.chat import ChatCompletionMessageParam

from loader import groq_client
from utils.prompts import SYSTEM_PROMPT


async def generate_tutor_response(
    history: list[ChatCompletionMessageParam], custom_prompt: str = SYSTEM_PROMPT
) -> tuple:
    """
    Forms a request to the AI, receives a response and breaks it into parts.
    Returns the full response to the database and a list of formatted messages.
    """
    system_message = cast(
        ChatCompletionMessageParam, {"role": "system", "content": custom_prompt}
    )
    messages: list[ChatCompletionMessageParam] = [system_message] + history

    # Run groq_client in a separate thread
    loop = asyncio.get_event_loop()
    chat_completion = await loop.run_in_executor(
        None,
        lambda: groq_client.chat.completions.create(
            messages=messages, model="llama-3.3-70b-versatile", temperature=0.8
        ),
    )
    # AI response of empty string if no response
    full_response = chat_completion.choices[0].message.content or ""
    # Inserts invisible characters to preserve paragraphs in Telegram chat
    formated_response = full_response.replace("\n\n", "\n\u200e\n")
    # Splits the answer into parts by separator ___
    parts = formated_response.split("___")
    # Remove empty parts and extra spaces
    clean_parts = [part.strip() for part in parts if part.strip]

    return full_response, clean_parts
