from telebot import TeleBot

from App.Components.BaseComponent import BaseComponent
from App.Config.config import CLOUD_ID
from App.Database.Episodios import Episodios
from App.Database.Obras import Obras
from App.Database.Temporadas import Temporadas
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

        opcoes_markup = [
            [['👁️ Assistir de onde parou', f'Obra__assistir__{id_obra}']],
            [['❤️ Favoritar', f'Obras__favoritar__{id_obra}']]
        ]

        temporadas = Obras().get_temporadas_ordenadas(id_obra)
        for temporada in temporadas:
            opcoes_markup.append([[f'🎬 Temporada ' + str(temporada.get('ordem')), f'switch_inline_query_current_chat=t: ']])

        markup = Markup.generate_inline(opcoes_markup)            

        if obra.get('thumb_msg_id') is not None:
            self.bot.copy_message(self.userid, from_chat_id=CLOUD_ID, message_id=obra.get('thumb_msg_id'), caption=texto, reply_markup=markup, parse_mode='Markdown')
        else:
            self.bot.send_message(self.userid, texto, reply_markup=markup, parse_mode='Markdown')


    def assistir(self, id_obra):
        obra = Obras().get_obra(id_obra)
        if obra is None:
            self.bot.send_message(self.userid, 'Obra não encontrada')
            return
        
        # Buscar a temporada onde o usuário parou, isto é, o último episódio assistido do histórico
        ultimo_episodio = Episodios().get_ultimo_episodio_assistido(self.userid, id_obra)
        if ultimo_episodio is not None:
            self.assistir_episodio(ultimo_episodio.get('id'))
            return
        
        primeira_temporada = Obras().get_temporadas_ordenadas(id_obra)[0] if Obras().get_temporadas_ordenadas(id_obra) else None
        if primeira_temporada is None:
            self.bot.send_message(self.userid, 'Obra sem temporadas ainda...')
            return
        
        episodios = Episodios().get_episodios_temporada(primeira_temporada.get('id'))
        if len(episodios) == 0:
            self.bot.send_message(self.userid, 'Obra sem episódios ainda...')
            return
        
        primeiro_episodio = episodios[0]
        self.assistir_episodio(primeiro_episodio.get('id'))


    def assistir_episodio(self, id_episodio):
        episodio = Episodios().get_episodio_com_ordem(id_episodio)
        if episodio is None:
            self.bot.send_message(self.userid, 'Episódio não encontrado')
            return
        elif episodio.get('msg_id') is None:
            self.bot.send_message(self.userid, 'Episódio não postado ainda...')
            return
        
        ordem_temporada = Temporadas().get_ordem_temporada(episodio.get('id_temporada'))
        
        proximo_episodio = Episodios().get_proximo_episodio(id_episodio)
        print('Proximo episodio:', proximo_episodio)
        
        controle = []
        if episodio.get('id_episodio_anterior') is not None:
            controle.append(['◀️', f"Obra__assistir_episodio__{episodio.get('id_episodio_anterior')}"])
        if proximo_episodio is not None:
            controle.append(['▶️', f"Obra__assistir_episodio__{proximo_episodio.get('id')}"])

        markup_controles = Markup.generate_inline([
            controle,
            [
                ['Temporadas', f'Obra__temporadas__{episodio.get("id_obra")}']
            ]
        ])

        caption = f"🎬 Obra: {episodio.get('nome_obra')} \n > Temporada: {ordem_temporada} \n > Episódio {episodio.get('ordem')}"
        
        self.bot.copy_message(self.userid, from_chat_id=CLOUD_ID, message_id=episodio.get('msg_id'), reply_markup=markup_controles, caption=caption)
        Episodios().adicionar_historico(self.userid, episodio.get('id'))



