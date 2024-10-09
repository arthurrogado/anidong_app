from App.Components.BaseComponent import BaseComponent
from App.Core.Cobranca import Cobranca
from App.Database.Usuarios import Usuarios

import datetime as dt

from App.Utils.Markup import Markup

class Assinatura(BaseComponent):
    def __init__(self, bot, userid, call):
        super().__init__(bot=bot, userid=userid, call=call)
        self.bot = bot
        self.userid = userid
        self.call = call

        self.planos_dias_valor = [
            [3, 5.00],
            [7, 10.00],
            [30, 30.00, "🔥 Mais popular"],
            [60, 80.00]
        ]

    
    def visualizar(self):
        dados_assinatura = Usuarios().info_assinatura(self.userid)
        if not dados_assinatura:
            self.bot.send_message(self.userid, '☹️ Você não possui assinatura ativa.', reply_markup=Markup.generate_inline([[["📝 Comprar assinatura", "Assinatura__comprar"]]]))
            return
        
        data_expiracao: dt.datetime = dados_assinatura.get('data_expiracao')
        data_expiracao_formatada = data_expiracao.strftime('%d/%m/%Y %H:%M:%S')
        texto = f"📅 Data de expiração: {data_expiracao_formatada}\n"
        tempo_restante: dt.datetime = data_expiracao - dt.datetime.now()
        tempo_restante_formatado = f"{tempo_restante.days} dias, {tempo_restante.seconds // 3600} horas e {(tempo_restante.seconds // 60) % 60} minutos"
        texto += f"📆 Tempo restante: {tempo_restante_formatado}\n\n"

        data_recebimento = dados_assinatura.get('data_recebimento')
        valor_recebimento = dados_assinatura.get('valor')
        qtd_dias = dados_assinatura.get('qtd_dias')
        descricao = dados_assinatura.get('descricao')
        if data_recebimento == None or valor_recebimento == None or qtd_dias == None:
            texto += "💰 Último pagamento: Não encontrado."
        else:
            texto += f"💰 Último pagamento: {data_recebimento} - R$ {valor_recebimento} - por {qtd_dias} dias. \n <strong>Descrição:</strong> {descricao}"
        

        markup = Markup.generate_inline([
            [["🔄️ Renovar assinatura", "Assinatura__comprar"]]
        ])

        self.bot.send_message(self.userid, texto, reply_markup=markup, parse_mode='html')


    def comprar(self):
        texto = "⭐ **Comprar assinatura**\n\n Escolha quantos dias você quer!"

        markup_data = []

        for plano in self.planos_dias_valor:
            texto_markup = f"📅 {plano[0]} dias - R$ {plano[1]}"
            if len(plano) == 3:
                texto_markup += " - " + plano[2]

            markup_data.append([[texto_markup, f"Assinatura__fazer_pedido__{plano[0]}"]])

        markup = Markup.generate_inline(markup_data)
        self.bot.send_message(self.userid, texto, reply_markup=markup, parse_mode='markdown')


    def fazer_pedido(self, qtd_dias):
        valor = [plano[1] for plano in self.planos_dias_valor if plano[0] == int(qtd_dias)][0]

        cobranca = Cobranca().criar_cobranca(valor, f"Assinatura de {qtd_dias} dias")
        if not cobranca:
            self.bot.send_message(self.userid, '☹️ Erro ao criar cobrança. Fala com o admin!')
            return
        
        import json
        print(json.dumps(cobranca, indent=4))
        
        codigo = cobranca['id']
        Usuarios().add_cobranca(self.userid, valor, codigo, qtd_dias)

        markup = Markup.generate_inline([
            [["Já paguei", f"Assinatura__verificar_pagamento__{codigo}"]]
        ])

        qr_code = cobranca['point_of_interaction']['transaction_data']['qr_code']
        self.bot.send_message(self.userid, f'🪙 Cobrança criada com sucesso! Código: {codigo}. PIX Copia e cola: \n\n <code>{qr_code}</code>', parse_mode='html', reply_markup=markup)


    def verificar_pagamento(self, codigo):
        cobranca = Cobranca().verificar_cobranca(codigo)
        if not cobranca:
            self.bot.send_message(self.userid, 'Cobrança não encontrada.')
            return
        
        try:
            if cobranca.get('status') == 'approved':
                Usuarios().liquidar_cobranca(codigo)
            else:
                self.bot.send_message(self.userid, 'Cobrança não aprovada. Espera um pouco e tenta novamente.')
        except Exception as e:
            self.bot.send_message(self.userid, 'Erro ao verificar cobrança. Conversa com o admin.')
            print(e)



    def liquidar_cobranca(self, codigo):
        cobranca = Usuarios().get_cobranca(codigo)
        if not cobranca:
            self.bot.send_message(self.userid, 'Cobrança não encontrada.')
            return

        Usuarios().liquidar_cobranca(codigo)
        self.bot.send_message(self.userid, f"Cobrança liquidada com sucesso!")
        self.visualizar()
