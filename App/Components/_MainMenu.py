from telebot.types import CallbackQuery

from App.Components.BaseComponent import BaseComponent
from App.custom_bot import CustomBot

import asyncio

class _MainMenu(BaseComponent):
    def __init__(self, bot: CustomBot, userid: int, call: CallbackQuery = None):
        super().__init__(bot=bot, userid=userid, call=call)
        self.bot = bot
        self.userid = userid
        self.call = call
        self.start()

    def start(self):
        # veriticar permissão, caso usuário esteja com assinatura ativa, mostrar menu de assinatura

        texto = "Olá, eu sou o bot Anidong! 🤖\n\n Qual seu nome?"
        msg = self.bot.send_message(self.userid, texto)
        response = asyncio.run(self.get_response(msg))
        print("Response: ", response)

    async def get_response(self, msg):
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def callback(message):
            future.set_result(message.text)

        self.bot.register_next_step_handler(msg, callback)
        return await future
            