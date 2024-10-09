import mercadopago
from App.Config.secrets import MERCADO_PAGO_TOKEN

sdk = mercadopago.SDK(MERCADO_PAGO_TOKEN)

def liquidar_cobranca(codigo):
    update_request = {
        "status": "approved"
    }
    result = sdk.payment().update(codigo, update_request)
    return result


if __name__ == '__main__':
    codigo = 1319729802
    print(liquidar_cobranca(codigo))