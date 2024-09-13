from telebot.types import CallbackQuery, Message

from App.Components.BaseComponent import BaseComponent
from App.Config.config import ADMIN_IDS
from App.Database.Usuarios import Usuarios
from App.Utils.Markup import Markup
from App.custom_bot import CustomBot

class _MainMenu(BaseComponent):
    def __init__(self, bot: CustomBot, userid: int, call: CallbackQuery = None):
        super().__init__(bot=bot, userid=userid, call=call)
        self.bot = bot
        self.userid = userid
        self.call = call
        self.usuario = None
        self.start()

    def start(self):

        self.usuario = Usuarios().get_usuario(self.userid)

        if not self.usuario:
            tg_user = self.bot.get_chat(chat_id=self.userid)
            nome_usuario = tg_user.first_name if tg_user.first_name else "Usuário"
            print(f"\n\n Nome do usuário: {nome_usuario}\n\n")
            Usuarios().add_user(userid=self.userid, nome=nome_usuario)
            self.usuario = Usuarios().get_usuario(self.userid)
            if self.usuario == None: 
                self.usuario = {'nome': nome_usuario}

        if self.userid in ADMIN_IDS or Usuarios().esta_assinando(self.userid):
            self.menu_assinantes()
        else:
            self.menu_inicial()


    def menu_inicial(self):
        texto = f"Olá, {self.usuario.get('nome')}! Eu sou o bot Anidong! 🤖 \n\n Deseja comprar uma assinatura?"
        markup = Markup.generate_inline([
            [['📝 Comprar assinatura', 'assinatura__comprar']]
        ])
        self.bot.send_message(self.userid, texto, reply_markup=markup)


    def menu_assinantes(self):
        texto = f"Olá, {self.usuario.get('nome')}! 🤖 \n\n O que deseja fazer?"
        markup = Markup().generate_inline([
            [['✅ Visualizar assinatura', 'assinatura__visualizar']],
            [['⭐ Favoritas', 'switch_inline_query_current_chat=of: '], ['🔍 Pesquisar', 'switch_inline_query_current_chat=o: ']],
            [['📈 Em alta', 'switch_inline_query_current_chat=ea: '], ['📂 Gêneros', 'Obra__ver_generos']]
        ])
        self.bot.send_message(self.userid, texto, reply_markup=markup)
