from telebot import TeleBot
from App.Database.DB import DB

class Episodios(DB):
    def __init__(self, bot: TeleBot = None):
        super().__init__(bot)

    def get_episodio(self, id_episodio: int):
        sql = """
            SELECT e.*, o.nome AS nome_obra
            FROM episodios e
            JOIN temporadas t ON e.id_temporada = t.id
            JOIN obras o ON t.id_obra = o.id
            WHERE e.id = %s
            LIMIT 1;
        """
        self.cursor.execute(sql, [id_episodio])
        result = self.dictify_query(self.cursor, ['id', 'id_temporada', 'id_episodio_anterior', 'msg_id', 'created_at', 'link', 'deleted_at', 'nome', 'nome_obra'])
        if result and len(result) > 0:
            return result[0]
        else:
            return {}
        # return self.select_one('episodios', ['*'], f'id = {id_episodio}')

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
            episodio_atual['ordem'] = len(episodios_ordenados) + 1
            episodios_ordenados.append(episodio_atual)
            proximo_id = episodio_atual['id']
            episodio_atual = next((ep for ep in episodios if ep['id_episodio_anterior'] == proximo_id), None)

        return episodios_ordenados
    
    def get_episodios_temporada(self, id_temporada: int):
        sql = """SELECT e.*, o.nome AS nome_obra
            FROM episodios e
            JOIN temporadas t ON e.id_temporada = t.id
            JOIN obras o ON t.id_obra = o.id
            WHERE e.id_temporada = %s
        """
        self.cursor.execute(sql, [id_temporada])
        result = self.dictify_query(self.cursor, ['id', 'id_temporada', 'id_episodio_anterior', 'msg_id', 'created_at', 'link', 'deleted_at', 'nome', 'nome_obra'])
        return self.ordenar_episodios(result)
    
    def get_episodio_com_ordem(self, id_episodio: int):
        episodio = self.get_episodio(id_episodio)
        episodios = self.get_episodios_temporada(episodio.get('id_temporada'))
        i = 1
        for ep in episodios:
            if str(ep.get('id')) == str(id_episodio):
                break
            i += 1
        episodio['ordem'] = i
        return episodio

    def get_episodio_de_ordem(self, id_temporada: int, ordem: int):
        episodios = self.get_episodios_temporada(id_temporada)
        for episodio in episodios:
            if episodio['ordem'] == ordem:
                return episodio
        return None

    def get_ultimo_episodio_assistido(self, id_usuario: int, id_obra: int):
        # colunas de historico_episodios: id_usuario, id_episodio e created_at
        sql = f"""
            SELECT e.*, h.*
            FROM historico_episodios h
            JOIN episodios e ON h.id_episodio = e.id
            JOIN temporadas t ON e.id_temporada = t.id
            WHERE h.id_usuario = {id_usuario} AND t.id_obra = {id_obra}
            ORDER BY h.assistido_em DESC
            LIMIT 1;
        """
        columns = []
        columns.append(self.get_all_columns('episodios'))
        columns.append(self.get_all_columns('historico_episodios'))
        self.cursor.execute(sql)
        result = self.dictify_query(self.cursor)
        if result and len(result) > 0:
            return result[0]
        else:
            return {}
        # return self.cursor.fetchone()
    
    def get_proximo_episodio_historico_usuario(self, id_usuario: int, id_obra: int):
        # Pega automaticamente qual o próximo episódio a ser assistido pelo usuário, baseado no último episódio assistido
        ultimo_episodio = self.get_ultimo_episodio_assistido(id_usuario, id_obra)
        if ultimo_episodio is None:
            return None
        
        # Encontrar o próximo episódio
        episodios = self.get_episodios_temporada(ultimo_episodio['id_temporada'])
        proximo_episodio = None
        for i, episodio in enumerate(episodios):
            if episodio['id'] == ultimo_episodio['id']:
                proximo_episodio = episodios[i + 1] if i + 1 < len(episodios) else None
                break
        
        return proximo_episodio
    
    def get_proximo_episodio(self, id_episodio: int):
        return self.select_one('episodios', ['*'], f'id_episodio_anterior = {id_episodio}')

    def adicionar_historico(self, id_usuario: int, id_episodio: int):
        return self.insert('historico_episodios', {'id_usuario': id_usuario, 'id_episodio': id_episodio})

