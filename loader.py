import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

# Load data from .env file
load_dotenv()


class Settings(BaseModel):
    TELEGRAM_TOKEN: str
    GROQ_API_KEY: str
    CHANNEL_ID: int
    CHANNEL_URL: str


settings = Settings.model_validate(dict(os.environ))


bot = Bot(
    token=settings.TELEGRAM_TOKEN,
    default_properties=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()
groq_client = Groq(api_key=settings.GROQ_API_KEY)
