from App.Components.BaseComponent import BaseComponent
from telebot import TeleBot
from telebot.types import CallbackQuery

from App.Database.Obras import Obras
from App.Utils.Markup import Markup

class Visualizar(BaseComponent):
    def __init__(self, bot: TeleBot, userid: int, call: CallbackQuery = None):
        super().__init__(bot=bot, userid=userid, call=call)
        self.bot = bot
        self.userid = userid
        self.start()

    def visualizar(self, id_obra):
        obra = Obras().get_obra(id_obra)
        if obra is None:
            self.bot.send_message(self.userid, 'Obra não encontrada')
            return
        
        texto = f"🎬 **{obra.get('nome')}**\n\n"
        texto += f"📚 **Sinopse**: {obra.get('sinopse')}"
        markup = Markup.generate_inline([
            [['👁️ Assistir', f'Obras___start__{id_obra}']],
            [['🔖 Favoritar', f'Obras__favoritar__{id_obra}']]
        ])

        if obra.get('thumbnail') is not None:
            self.bot.send_photo(self.userid, obra.get('thumbnail'), caption=texto, reply_markup=markup)
        else:
            self.bot.send_message(self.userid, texto, reply_markup=markup)
