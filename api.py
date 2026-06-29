from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.db_manager import db
from handlers.chat import process_translator_mode, trigger_random_question
from loader import bot, dp

app = FastAPI(title="Telegram Mini App API")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eugene0408.github.io"
    ],  # frontend domen (use * for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Data schema for updating settings
class SettingsUpdate(BaseModel):
    user_id: int
    level: str | None = None
    temperature_frontend: int | None = None


@app.get("/api/settings/{user_id}")
async def get_settings(user_id: int):
    # Return data for the frontend.
    settings = db.get_user_settings(user_id)
    # Convert decimal values back to integers for frontend buttons.
    settings["temperature_frontend"] = int(settings["temperature"] * 10)
    return settings


@app.post("/api/settings/update")
async def update_settings(data: SettingsUpdate):
    if data.level:
        db.set_user_level_from_frontend(data.user_id, data.level)
        db.clear_history(data.user_id)
    if data.temperature_frontend is not None:
        db.set_user_temperature_from_frontend(data.user_id, data.temperature_frontend)
    return {"status": "success"}


class MiniAppAction(BaseModel):
    user_id: int
    action: str


@app.post("/api/bot/action")
async def handle_miniapp_action(data: MiniAppAction, background_tasks: BackgroundTasks):
    try:
        if data.action == "translator":
            # Create a state storage key for a specific user.
            state_key = StorageKey(
                bot_id=bot.id, chat_id=data.user_id, user_id=data.user_id
            )
            state = FSMContext(storage=dp.storage, key=state_key)
            # Run the translator activation function in the background.
            background_tasks.add_task(process_translator_mode, data.user_id, bot, state)
            return {"status": "accepted", "info": "Translator mode activating"}
        elif data.action == "ask_me":
            background_tasks.add_task(trigger_random_question, data.user_id, bot)
            return {"status": "accepted", "info": "Generation started in background"}

        return {"status": "error", "message": "unknown action"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
