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
                SELECT id, nome, id_temporada_anterior, especial, 
                    CASE WHEN especial THEN nome ELSE 1 END AS ordem,
                    CASE WHEN especial THEN 0 ELSE 1 END AS ordem_continua
                FROM temporadas
                WHERE id_temporada_anterior IS NULL AND id_obra = %s
                UNION ALL
                SELECT t.id, t.nome, t.id_temporada_anterior, t.especial, 
                    CASE WHEN t.especial THEN t.nome ELSE cte.ordem_continua + 1 END,
                    CASE WHEN t.especial THEN cte.ordem_continua ELSE cte.ordem_continua + 1 END
                FROM temporadas t
                JOIN cte ON t.id_temporada_anterior = cte.id
            )
            SELECT id, nome, id_temporada_anterior, especial, ordem FROM cte;
        """
        self.cursor.execute(query, [obra_id])
        return self.dictify_query(self.cursor) #

    def get_qtd_temporadas(self, id_obra: int):
        query = f"SELECT COUNT(*) FROM temporadas WHERE id_obra = {id_obra}"
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]


    def favoritar(self, id_usuario: int, id_obra: int):
        return self.insert('obras_favoritas', {'id_usuario': id_usuario, 'id_obra': id_obra})
    
    def desfavoritar(self, id_usuario: int, id_obra: int):
        return self.delete('obras_favoritas', f'id_usuario = {id_usuario} AND id_obra = {id_obra}')
    
    def eh_favorita(self, id_usuario: int, id_obra: int):
        return self.select_one('obras_favoritas', ['*'], f'id_usuario = {id_usuario} AND id_obra = {id_obra}') is not None
    
    def get_obras_favoritas_usuario(self, id_usuario: int):
        sql = f"""
            SELECT o.* FROM obras o
            JOIN obras_favoritas of ON of.id_obra = o.id
            WHERE of.id_usuario = {id_usuario}
            ORDER BY of.created_at DESC
            limit 100
        """
        self.cursor.execute(sql)
        return self.dictify_query(self.cursor)
    
    def pesquisar_obras_favoritas(self, query: str, userid: int):
        sql = f"""
            SELECT o.* FROM obras o
            JOIN obras_favoritas of ON of.id_obra = o.id
            WHERE o.nome like "%{query}%" AND of.id_usuario = {userid}
            ORDER BY of.created_at DESC
            limit 100
        """
        self.cursor.execute(sql)
        return self.dictify_query(self.cursor)
    

    def get_obras_em_alta(self, dias: int = 7):
        """Seleciona obras em alta baseado em quantos usuários assistiram nos últimos dias"""
        sql = f"""
            SELECT o.*, COUNT( DISTINCT h.id_usuario) AS qtd_acessos 
            FROM obras o
            JOIN temporadas t ON t.id_obra = o.id
            JOIN episodios e ON e.id_temporada = t.id
            JOIN historico_episodios h ON h.id_episodio = e.id
            WHERE h.assistido_em >= DATE_SUB(NOW(), INTERVAL {dias} DAY)
            GROUP BY o.id
            ORDER BY qtd_acessos DESC
            limit 100
        """
        self.cursor.execute(sql)
        return self.dictify_query(self.cursor)


    def get_generos(self):
        sql = "SELECT genero FROM obras_generos GROUP BY genero"
        self.cursor.execute(sql)
        return self.dictify_query(self.cursor)
        # return self.select('generos', ['*'])

    def get_obras_por_genero(self, genero: int):
        sql = f"""
            SELECT o.* FROM obras o
            JOIN obras_generos og ON og.id_obra = o.id
            WHERE og.genero = '{genero}'
            limit 100
        """
        self.cursor.execute(sql)
        return self.dictify_query(self.cursor)
