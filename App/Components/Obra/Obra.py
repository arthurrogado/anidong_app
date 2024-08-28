from telebot import TeleBot

from App.Components.BaseComponent import BaseComponent
from App.Config.config import CLOUD_ID
from App.Database.Obras import Obras
from App.Utils.Markup import Markup

class Obra(BaseComponent):
    def __init__(self, bot: TeleBot, userid, call = None):
        super().__init__(bot=bot, userid=userid, call=call)
        self.bot = bot
        self.userid = userid
        self.start()

    def start(self):
        pass


    def visualizar(self, id_obra):
        obra = Obras().get_obra(id_obra)
        if obra is None:
            self.bot.send_message(self.userid, 'Obra não encontrada')
            return
        
        texto = f"🎬 **{obra.get('nome')}**\n\n"
        texto += f"📚 **Sinopse**: {obra.get('sinopse')}"
        markup = Markup.generate_inline([
            [['👁️ Assistir', f'Obra__assistir__{id_obra}']],
            [['🔖 Favoritar', f'Obras__favoritar__{id_obra}']]
        ])

        if obra.get('thumb_msg_id') is not None:
            self.bot.copy_message(self.userid, from_chat_id=CLOUD_ID, message_id=obra.get('thumb_msg_id'), caption=texto, reply_markup=markup, parse_mode='Markdown')
        else:
            self.bot.send_message(self.userid, texto, reply_markup=markup, parse_mode='Markdown')


    def assistir(self, id_obra):
        obra = Obras().get_obra(id_obra)
        if obra is None:
            self.bot.send_message(self.userid, 'Obra não encontrada')
            return
        
        primeira_temporada = Obras().get_temporadas_ordenadas(id_obra)[0] if Obras().get_temporadas_ordenadas(id_obra) else None
        if primeira_temporada is None:
            self.bot.send_message(self.userid, 'Obra sem temporadas ainda...')
            return
        
        episodios = Obras().get_episodios_temporada(primeira_temporada.get('id'))
        if len(episodios) == 0:
            self.bot.send_message(self.userid, 'Obra sem episódios ainda...')
            return
        
        primeiro_episodio = episodios[0]
        markup_controles = Markup.generate_inline([
            [
                ['⏪', f'Obra__assistir__episodio__{primeiro_episodio.get("id")}'],
                ['◀️', f'Obra__assistir__anterior__{primeiro_episodio.get("id")}'], 
                ['▶️', f'Obra__assistir__proximo__{primeiro_episodio.get("id")}'],
                ['⏩', f'Obra__assistir__episodio__{primeiro_episodio.get("id")}']
            ],
            [
                ['Temporadas', f'Obra__assistir__temporadas__{id_obra}']
            ]
        ])

        self.bot.copy_message(self.userid, from_chat_id=CLOUD_ID, message_id=primeiro_episodio.get('msg_id'), reply_markup=markup_controles)
