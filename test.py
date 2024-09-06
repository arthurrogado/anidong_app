string = 't: 1 25'
# 't: 1' ou 't: 1 25'
# temporada 1 episodio 25
split_string = string.split('t: ')[1].split(' ')
id_temporada = split_string[0]
numero_episodio = split_string[1] if len(split_string) == 2 else None
print(id_temporada, numero_episodio)