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

class Queries():
    def __init__(self, bot: TeleBot, query: str = None) -> list:
        self.query = query
        self.bot = bot

    def get_results(self):
        print(self.query)
        pesquisas = {
            'o:': self.pesquisar_obras,
            't: ': self.pesquisar_em_temporada
        }

        self.results = self.resultados_nao_encontrados()

        for key in pesquisas:
            if key in self.query:
                print('Achou a key:', key)
                self.results = pesquisas[key](self.query)
                self.results = self.results[:50] # limitar a 50 resultados
                break
        
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


    def pesquisar_obras(self, query: str):
        query = query.split('o:')[1].strip() if query.startswith('o:') else query
        obras = Obras().pesquisar_obras(query)
        results = []
        for obra in obras:

            print('\n\n Thumbnail:', obra.get('thumbnail'))

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
                InlineQueryResultArticle(
                    id=obra.get('id'),
                    title=obra.get('nome'),
                    input_message_content=InputTextMessageContent('/Obra__visualizar__' + str(obra.get('id'))),
                    thumbnail_url=obra.get('thumbnail'),
                    # thumbnail_height=width,
                    # thumbnail_width=height,
                    description=descricao
                )
            )
        
        return results
    
    def pesquisar_em_temporada(self, query: str):
        # query = query.split('t:')[1].strip() if query.startswith('to:') else query
        print('Pesquisando em temporada:', query)
        split_query = query.split('t: ')[1].split(' ')
        id_temporada = split_query[0]
        numero_episodio = split_query[1] if len(split_query) == 2 else None

        if numero_episodio:
            episodio = Episodios().get_episodio_de_ordem(id_temporada, numero_episodio)
            if episodio is None:
                return self.resultados_nao_encontrados()

            return [
                InlineQueryResultArticle(
                    id=episodio.get('id'),
                    title=episodio.get('nome'),
                    input_message_content=InputTextMessageContent('/Obra__assistir_episodio__' + str(episodio.get('id'))),
                    description=episodio.get('sinopse')
                )
            ]
        episodios = Episodios().get_episodios_temporada(id_temporada)
        results = []
        for episodio in episodios:
            results.append(
                InlineQueryResultArticle(
                    id=episodio.get('id'),
                    title=episodio.get('nome'),
                    input_message_content=InputTextMessageContent('/Obra__assistir_episodio__' + str(episodio.get('id'))),
                    description=episodio.get('sinopse')
                )
            )
        return results
