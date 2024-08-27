from App.Components.BaseComponent import BaseComponent
from telebot import TeleBot
from telebot.types import CallbackQuery

from App.Database.Obras import Obras
from App.Utils.Markup import Markup

class ObrasFavoritas(BaseComponent):
    def __init__(self, bot: TeleBot, userid: int, call: CallbackQuery = None):
        super().__init__(bot=bot, userid=userid, call=call)
        self.bot = bot
        self.userid = userid
        self.start()

    def start(self):
        self.listar()

    def listar(self):
        obras_favoritas = Obras().get_obras_favoritas(self.userid)
        texto = "📚 Suas obras favoritas\n\n"
        
        markup = Markup.generate_inline([
            [['🔍 Pesquisar', 'obras__pesquisar'], ['📈 Em alta', 'obras__em_alta']],
            [['📂 Categorias', 'obras_categorias']]
        ])

        for obra in obras_favoritas:
            info_obra = f"📖 **{obra.get('nome')}** - /visualizar_obra_{obra.get(id)} \n"
            if len(texto) + info_obra > 4096:
                self.bot.send_message(self.userid, texto, reply_markup=markup, parse_mode='Markdown')
                texto = "2º parte\n\n" + info_obra
            texto += info_obra
        self.bot.send_message(self.userid, texto, reply_markup=markup, parse_mode='Markdown')

