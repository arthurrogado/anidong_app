from telebot import TeleBot
from telebot.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultPhoto,
    InlineQueryResultCachedPhoto
)

from App.Database.Episodios import Episodios
from App.Database.Obras import Obras
import requests
import io
from PIL import Image

from App.Database.Temporadas import Temporadas
from App.Utils.Markup import Markup

class Queries():
    def __init__(self, bot: TeleBot, userid: int = None, query: str = None, chat_type: str = None) -> list:
        self.userid = userid
        self.query = query
        self.bot = bot
        self.chat_type = chat_type
        self.deep_link_base = f"https://t.me/{self.bot.get_me().username}?start="

    def get_results(self):
        print(self.query)
        pesquisas = {
            'o:': self.pesquisar_obras,
            'oi:': self.get_obra_por_id,
            't: ': self.pesquisar_em_temporada,
            'of:': self.pesquisar_obras_favoritas,
            'ea:': self.pesquisar_obras_em_alta,
            'g: ': self.pesquisar_obras_genero
        }

        self.results = self.resultados_nao_encontrados()

        for key in pesquisas:
            if key in self.query:
                print('Achou a key:', key)
                self.results = pesquisas[key](self.query)
                break
        
        self.results = self.results[:50] # limitar a 50 resultados
        return self.results

    def get_size(self, url: str):
        # get thumbnail information (width and height)
        try:
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content))
            width, height = img.size
            return width, height
        except Exception as e:
            print(f"Error retrieving thumbnail information: {e}")
            return None, None
        
    def get_from(self, object, key):
        return str(object.get(key)) if object.get(key) is not None else ""
    

    def resultados_nao_encontrados(self, mensagem: str = 'Não encontrado'):
        return [
            InlineQueryResultArticle(
                id='1',
                title=mensagem,
                input_message_content=InputTextMessageContent(mensagem)
            )
        ]
    

    def get_text_link(self, text: str, url: str):
        return f"[{text}]({url})"
    

    def article_obra(self, obra):
        texto = f"ID:{obra.get('id')}" if self.chat_type == "sender" else f"🤖🎬 Assista agora à obra '{obra.get('nome')}'"
        return InlineQueryResultArticle(
            id=obra.get('id'),
            title=obra.get('nome'),
            input_message_content=InputTextMessageContent(
                self.get_text_link(texto, self.deep_link_base + 'Obra__visualizar__' + str(obra.get('id'))), 
                parse_mode='Markdown'
            ),
            description=obra.get('sinopse'),
            thumbnail_url=obra.get('thumbnail')
        )


    def get_obra_por_id(self, query: str):
        query = query.split('oi:')[1].strip() if query.startswith('oi:') else query
        if query.isnumeric() is False:
            return self.resultados_nao_encontrados('ID de obra deve ser um número')
        obra = Obras().get_obra(query)
        if obra is None:
            return self.resultados_nao_encontrados('Obra não encontrada')
        return [self.article_obra(obra)]

    def pesquisar_obras(self, query: str):
        query = query.split('o:')[1].strip() if query.startswith('o:') else query

        if query.isnumeric():
            return self.get_obra_por_id(query)

        obras = Obras().pesquisar_obras(query)
        results = []
        for obra in obras:
            if obra.get('thumbnail') is None:
                # obra['thumbnail'] = 'https://via.placeholder.com/150x300.png'
                obra['thumbnail'] = "https://i.imgur.com/mbFdfhs.png"
                width, height = 150, 150

            else:
                width, height = self.get_size(obra.get('thumbnail'))

            # descricao = obra.get('nomes_alternativos') or "" + " \n " + obra.get('ano') + Obras().get_qtd_temporadas(obra.get('id'))  + " \n " + obra.get('sinopse')
            # descricao = obra.get('nomes_alternativos') or "" + " | Isso aí"
            obra['qtd_temporadas'] = str(Obras().get_qtd_temporadas(obra.get('id')))
            descricao = self.get_from(obra, 'nomes_alternativos') + " | " + self.get_from(obra, 'ano') + " | " + obra.get('qtd_temporadas') + " | " + self.get_from(obra, 'sinopse')

            results.append(
                self.article_obra(obra)
                # InlineQueryResultArticle(
                #     id=obra.get('id'),
                #     title=obra.get('nome'),
                #     input_message_content=InputTextMessageContent('/Obra__visualizar__' + str(obra.get('id'))),
                #     thumbnail_url=obra.get('thumbnail'),
                #     description=descricao,
                #     reply_markup=Markup.generate_inline([[["Teste", "Teste"]]])
                # )
            )
        
        return results
    
    def pesquisar_em_temporada(self, query: str):
        # query = query.split('t:')[1].strip() if query.startswith('to:') else query
        query = query.split('t:')[1].strip()
        split_query = query.split(" ")
        id_temporada = split_query[0]
        if id_temporada.isnumeric() is False:
            return self.resultados_nao_encontrados('ID de temporada deve ser um número')
        
        ordem_temporada = Temporadas().get_ordem_temporada(id_temporada)
        if not ordem_temporada:
            return self.resultados_nao_encontrados('Temporada não encontrada')

        numero_episodio = split_query[1] if len(split_query) > 1 else None

        if numero_episodio and numero_episodio.isnumeric():
            numero_episodio = int(numero_episodio)
            episodio = Episodios().get_episodio_de_ordem(id_temporada, numero_episodio)
            if episodio is None:
                return self.resultados_nao_encontrados(f"{numero_episodio}º ep não encontrado")

            return [
                InlineQueryResultArticle(
                    id=episodio.get('id'),
                    title = f"{episodio.get('ordem')}º Episódio",
                    input_message_content=InputTextMessageContent('/Obra__assistir_episodio__' + str(episodio.get('id'))),
                    description = f"{episodio.get('nome')} • {ordem_temporada}º Temporada • {episodio.get('nome_obra')}"
                )
            ]
        episodios = Episodios().get_episodios_temporada(id_temporada)
        results = []
        for episodio in episodios:
            results.append(
                InlineQueryResultArticle(
                    id=episodio.get('id'),
                    title = f"{episodio.get('ordem')}º Episódio",
                    input_message_content=InputTextMessageContent('/Obra__assistir_episodio__' + str(episodio.get('id'))),
                    description = f"{episodio.get('nome')} • {ordem_temporada}º Temporada • {episodio.get('nome_obra')}"
                )
            )
        return results


    def pesquisar_obras_favoritas(self, query: str):
        query = query.split('of:')[1].strip() if query.startswith('of:') else query

        if query == "":
            print('Pesquisando obras favoritas:', query)
            obras = Obras().get_obras_favoritas_usuario(self.userid)
        else:
            obras = Obras().pesquisar_obras_favoritas(query, self.userid)
            
        results = []
        for obra in obras:
            results.append(
                InlineQueryResultArticle(
                    id=obra.get('id'),
                    title= "❤️" + obra.get('nome'),
                    input_message_content=InputTextMessageContent('/Obra__visualizar__' + str(obra.get('id'))),
                    description=obra.get('sinopse'),
                    thumbnail_url=obra.get('thumbnail')
                )
            )
        if len(results) == 0:
            return self.resultados_nao_encontrados("Você ainda não favoritou nenhuma obra...")
        return results


    def pesquisar_obras_em_alta(self, query: str):
        obras = Obras().get_obras_em_alta()
        results = []
        obras.reverse()
        for i, obra in enumerate(obras):
            results.append(
                InlineQueryResultArticle(
                    id=obra.get('id'),
                    title = f"{i+1}º - {obra.get('nome')}",
                    input_message_content=InputTextMessageContent('/Obra__visualizar__' + str(obra.get('id'))),
                    description=obra.get('sinopse'),
                    thumbnail_url=obra.get('thumbnail')
                )
            )
        if len(results) == 0:
            return self.resultados_nao_encontrados("Nenhuma obra em alta...")
        return results

    def pesquisar_obras_genero(self, query: str):
        # query = query.split('g: ')[1].strip() if query.startswith('g:') else query
        genero = query.split('g:')[1].strip()
        
        obras = Obras().get_obras_por_genero(genero)
        results = []
        for obra in obras:
            results.append(
                InlineQueryResultArticle(
                    id=obra.get('id'),
                    title=obra.get('nome'),
                    input_message_content=InputTextMessageContent('/Obra__visualizar__' + str(obra.get('id'))),
                    description=obra.get('sinopse'),
                    thumbnail_url=obra.get('thumbnail')
                )
            )
        if len(results) == 0:
            return self.resultados_nao_encontrados("Nenhuma obra encontrada...")
        return results
        