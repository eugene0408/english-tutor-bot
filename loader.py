import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CHANNEL_URL = os.getenv("CHANNEL_URL")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default_properties=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY)
