from App.Database.DB import DB
import datetime as dt

class Temporadas(DB):
    def __init__(self, bot = None):
        super().__init__(bot)
        self.table = 'obras'
    
    def get_temporada(self, temporada_id: int):
        return self.select_one('temporadas', ['*'], f'id = {temporada_id}')
    
    def get_temporada_depois_de(self, temporada_anterior_id: int):
        return self.select_one('temporadas', ['*'], f'id_temporada_anterior = {temporada_anterior_id}')
    
    def get_ordem_temporada(self, id_temporada: int):
        temporada = self.get_temporada(id_temporada)

        if len(temporada) == 0:
            return False

        if temporada.get('especial') == '1':
            return temporada.get('nome')
        
        if not temporada.get('id_temporada_anterior'):
            return 1
        
        return self.get_ordem_temporada(temporada.get('id_temporada_anterior')) + 1

    def get_primeira_temporada(self, id_obra: int):
        return self.select_one('temporadas', ['*'], f'id_obra = {id_obra} AND id_temporada_anterior IS NULL')
    
    def get_temporadas_ordenadas(self, id_obra: int):
        query = """
        WITH RECURSIVE cte AS (
            SELECT id, nome, id_temporada_anterior, especial
            FROM temporadas
            WHERE id_temporada_anterior IS NULL AND id_obra = %s
            UNION ALL
            SELECT t.id, t.nome, t.id_temporada_anterior
            FROM temporadas t
            JOIN cte ON t.id_temporada_anterior = cte.id
        )
        SELECT * FROM cte;
        """
        self.cursor.execute(query, [id_obra])
        return self.dictify_query(self.cursor) #