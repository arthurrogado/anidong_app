from App.custom_bot import CustomBot
from telebot.types import CallbackQuery

class BaseComponent():
    def __init__(self, bot: CustomBot, userid: str | int, call: CallbackQuery = None) -> None:
        pass