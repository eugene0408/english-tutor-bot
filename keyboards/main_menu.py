from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    # кнопки в один ряд пишуться через кому
    builder.row(KeyboardButton(text="🎲 Ask Me"), KeyboardButton(text="Translator 🌐"))
    # щоб додати ще один ряд
    # builder.row(...)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Type here ..."
    )
