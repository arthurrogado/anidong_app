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
    
    

    def info_assinatura(self, userid):
        # tabela de pagamentos mostra o histórico de comprar de assinatura
        # retornar o última cobranca paga e a data de expiração
        # ultimo_pagamento = self.select_one("cobrancas", ['*'], f'userid = {userid}', where="data_recebimento IS NOT NULL" , final='ORDER BY data_recebimento DESC')
        # if not ultimo_pagamento:
        #     return False
        
        sql = f"""
        SELECT c.*, u.data_expiracao 
        FROM usuarios u 
        LEFT JOIN cobrancas c ON c.id_usuario = u.id AND c.data_recebimento IS NOT NULL 
        WHERE u.id = {userid} 
        ORDER BY c.data_recebimento DESC 
        LIMIT 1
        """
        colunas = self.get_all_columns('cobrancas').append('data_expiracao')
        self.cursor.execute(sql)
        # result = self.dictify_result(self.cursor, self.cursor.fetchone())
        result = self.dictify_query(self.cursor, colunas)
        if result:
            return result[0]
        return False
        

    def esta_assinando(self, userid):
        usuario = self.get_usuario(userid)
        if not usuario.get('data_expiracao'):
            return False
        # data_expiracao = dt.datetime.strptime(usuario.get('data_expiracao'), '%Y-%m-%d %H:%M:%S')
        data_expiracao = usuario.get('data_expiracao')
        return data_expiracao > dt.datetime.now()
    
        

    def add_cobranca(self, userid, valor, codigo, qtd_dias, descricao = None):
        return self.insert(
            "cobrancas",
            {
                'id_usuario': userid,
                'valor': valor,
                'codigo': codigo,
                'qtd_dias': qtd_dias,
                'descricao': descricao
            }
        )
    
    def get_cobranca(self, codigo):
        return self.select_one('cobrancas', ['*'], f'codigo = "{codigo}"')
    
    def liquidar_cobranca(self, codigo, data_recebimento: dt.datetime = None):
        if data_recebimento is None:
            data_recebimento = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        status = self.update('cobrancas', {'data_recebimento': data_recebimento}, f'codigo = "{codigo}"')
        if status:
            cobranca = self.get_cobranca(codigo)
            data_expiracao = dt.datetime.now() + dt.timedelta(days=cobranca.get('qtd_dias'))
            self.update('usuarios', {'data_expiracao': data_expiracao.strftime('%Y-%m-%d %H:%M:%S')}, f'id = {cobranca.get("id_usuario")}')
            return True
        return False
        