from App.Config.secrets import MERCADO_PAGO_TOKEN

import mercadopago
from datetime import datetime, timedelta, timezone

class Cobranca:
    def __init__(self):
        self.sdk = mercadopago.SDK(MERCADO_PAGO_TOKEN)
        pass

    def criar_cobranca(self, valor: float, descricao: str = None, horas_expiracao: int = 24):
        # return {'valor': valor, 'descricao': descricao, 'codigo': 'teste1'}

        # Defina o fuso horário desejado, por exemplo, UTC-4
        tz = timezone(timedelta(hours=-4))

        # Obtenha a data e hora atuais no fuso horário especificado
        dt = datetime.now(tz) + timedelta(hours=horas_expiracao)

        # Formate a data e hora até os segundos
        date_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
        date_of_expiration = f"{date_str}.000-04:00"

        payment_data = {
            "transaction_amount": valor,
            "description": descricao,
            "payment_method_id": "pix",
            "installments": 1,
            "payer": {
                "email": "arthurogadoreis@gmail.com"
            },
            "date_of_expiration": date_of_expiration
        }
        result = self.sdk.payment().create(payment_data)
        if result.get('status') == 201:
            return result.get('response')
        return False
    
    def verificar_cobranca(self, codigo: str):
        return self.sdk.payment().get(codigo)

    def liquidar_cobranca(self, codigo: str):
        pass
