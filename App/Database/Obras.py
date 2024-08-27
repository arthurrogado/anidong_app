from telebot import TeleBot

from App.Database.DB import DB

class Obras(DB):
    def __init__(self, bot: TeleBot = None):
        super().__init__(bot)

    def get_obras(self, userid):
        return self.select('obras', ['*'], f'userid = {userid} limit 1000')

    def get_obra(self, obra_id):
        return self.select_one('obras', ['*'], f'obra_id = {obra_id}')

    def get_obras_em_alta(self):
        # pegar obras com maiores buscas ou starts em algum histórico
        # historico_obras: id_usuario, id_obra, data_acesso
        # então pegar as obras mais acessadas nos últimos 7 dias limitando a 100
        pass

    def get_obras_favoritas(self, userid):
        # tabela intermediaria: obras_favoritas
        sql = f"""
            SELECT obras.* FROM obras
            JOIN obras_favoritas ON obras_favoritas.id_obra = obras.id
            WHERE obras_favoritas.userid = {userid}
            limit 100
        """
        self.cursor.execute(sql)
        return self.dictify_query(self.cursor)

    def get_obras_por_categoria(self, categoria):
        # tabela intermediaria: obras_categorias
        sql = f"""
            SELECT obras.* FROM obras
            JOIN obras_categorias ON obras_categorias.id_obra = obras.id
            WHERE obras_categorias.categoria = {categoria}
            limit 100
        """
        self.cursor.execute(sql)
        return self.dictify_query(self.cursor)
