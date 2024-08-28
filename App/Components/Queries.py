from telebot import TeleBot
from telebot.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultPhoto,
    InlineQueryResultCachedPhoto
)

from App.Database.Obras import Obras

class Queries():
    def __init__(self, bot: TeleBot, query: str = None):
        self.query = query
        self.bot = bot

    def pesquisar_obras(self, query: str):
        query = query.split('nome_obra:')[1].strip() if query.startswith('nome_obra:') else query
        obras = Obras().pesquisar_obras(query)
        print('\n\n Obras:', obras)
        results = []
        for obra in obras:

            if obra.get('thumbnail') is None:
                obra['thumbnail'] = 'https://via.placeholder.com/150'


            results.append(
                InlineQueryResultArticle(
                    id=obra.get('id'),
                    title=obra.get('nome'),
                    input_message_content=InputTextMessageContent('/Obra__visualizar__' + str(obra.get('id'))),
                    thumbnail_url=obra.get('thumbnail')
                )
            )
        
        return results