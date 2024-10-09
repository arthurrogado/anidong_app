from App.custom_bot import CustomBot
from telebot.types import CallbackQuery

class BaseComponent():
    def __init__(self, bot: CustomBot, userid: str | int, call: CallbackQuery = None) -> None:
        self.bot = bot
        self.userid = userid
        self.call = call
        self.bot.send_chat_action(self.userid, 'typing')

    def cancel(self, call):
        self.bot.answer_callback_query(call.id, '❌ Cancelled')
        self.bot.delete_message(call.message.chat.id, call.message.message_id)
        self.bot.clear_step_handler_by_chat_id(call.message.chat.id)
        # self.bot.clear_callback_handlers_by_chat_id(call.message.chat.id)

    def set_callback_query_handler(self, handler_function, call_data):
        # Set callback query handler to custom markup that has a specific call_data and is not registered in main bot
        self.bot.register_callback_query_handler(handler_function, lambda call: call.data == call_data)