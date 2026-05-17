from aiogram.fsm.state import State, StatesGroup


class TranslatorStates(StatesGroup):
    waiting_for_ukrainian_text = State()
