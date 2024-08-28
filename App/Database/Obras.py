from telebot import TeleBot

from App.Database.DB import DB

class Obras(DB):
    def __init__(self, bot: TeleBot = None):
        super().__init__(bot)

    def get_obras(self, userid):
        return self.select('obras', ['*'], f'userid = {userid} limit 1000')

    def get_obra(self, id_obra):
        return self.select_one('obras', ['*'], f'id = {id_obra}')
    
    def pesquisar_obras(self, query):
        return self.select('obras', ['*'], f'nome like "%{query}%"', final = 'limit 10')

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
            WHERE obras_favoritas.id_usuario = {userid}
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

    def get_temporadas_ordenadas(self, obra_id: int):
        query = """
        WITH RECURSIVE cte AS (
            SELECT id, nome, id_temporada_anterior
            FROM temporadas
            WHERE id_temporada_anterior IS NULL AND id_obra = %s
            UNION ALL
            SELECT t.id, t.nome, t.id_temporada_anterior
            FROM temporadas t
            JOIN cte ON t.id_temporada_anterior = cte.id
        )
        SELECT * FROM cte;
        """
        self.cursor.execute(query, [obra_id])
        return self.dictify_query(self.cursor) #








    def ordenar_episodios(self, episodios) -> list[dict]:
        # Criar um dicionário para mapear cada episódio pelo seu ID
        # episodio_dict = {ep['id']: ep for ep in episodios}
        
        # Encontrar o primeiro episódio (aquele que não tem 'id_episodio_anterior')
        primeiro_episodio = None
        for episodio in episodios:
            if not episodio['id_episodio_anterior']:
                primeiro_episodio = episodio
                break
        
        # Construir a lista ordenada de episódios
        episodios_ordenados = []
        episodio_atual = primeiro_episodio
        while episodio_atual:
            episodios_ordenados.append(episodio_atual)
            proximo_id = episodio_atual['id']
            episodio_atual = next((ep for ep in episodios if ep['id_episodio_anterior'] == proximo_id), None)

        return episodios_ordenados
    
    def get_episodios_temporada(self, id_temporada: int):
        return self.ordenar_episodios(self.select('episodios', ['*'], f'id_temporada = {id_temporada}'))

