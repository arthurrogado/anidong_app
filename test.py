from App.Core.Cobranca import Cobranca
import json

cobranca = Cobranca()
result = cobranca.criar_cobranca(10.00, 'Teste de cobrança')

print(json.dumps(result, indent=4))