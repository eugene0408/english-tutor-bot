from aiogram.types import Message


def get_user_id(message: Message) -> int | None:
    if message.from_user is None:
        return None
    return message.from_user.id
