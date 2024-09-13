string = 't: 1 25'
# 't: 1' ou 't: 1 25'
# temporada 1 episodio 25
string = string.split('t:')[1].strip()
split_string = string.split(' ')
id_temporada = split_string[0]
numero_episodio = split_string[1] if len(split_string) > 1 else None
print(id_temporada, numero_episodio)