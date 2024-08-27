from telebot import TeleBot
from App.Database.DB import DB

import datetime as dt

class Usuarios(DB):
    def __init__(self, bot: TeleBot = None):
        super().__init__(bot)

    def add_user(self, userid, nome: str = None):
        return self.insert(
            'usuarios',
            {
                'id': userid,
                'nome': nome,
            }
        )

    def get_usuario(self, userid):
        return self.select_one('usuarios', ['*'], f'id = {userid}')

    def esta_assinando(self, userid):
        usuario = self.get_usuario(userid)
        if not usuario.get('data_expiracao'):
            return False
        data_expiracao = dt.datetime.strptime(usuario.get('data_expiracao'), '%Y-%m-%d %H:%M:%S')
        return data_expiracao > dt.datetime.now()
        

