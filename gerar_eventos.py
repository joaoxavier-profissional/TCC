import csv

ARQUIVO_ENTRADA = "deteccoes.csv"
ARQUIVO_SAIDA = "eventos.csv"

# Se o mesmo objeto voltar a aparecer com no máximo
# 2 segundos de diferença, consideramos parte do mesmo evento.
TOLERANCIA_SEGUNDOS = 2


def timestamp_para_segundos(timestamp):
    horas, minutos, segundos = map(int, timestamp.split(":"))
    return horas * 3600 + minutos * 60 + segundos


def segundos_para_timestamp(total_segundos):
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    return f"{horas:02}:{minutos:02}:{segundos:02}"


# Lê as detecções criadas pelo indexar_video.py
deteccoes_por_classe = {}

with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as arquivo:
    leitor = csv.DictReader(arquivo)

    for linha in leitor:
        classe = linha["classe"]
        segundo = timestamp_para_segundos(linha["timestamp"])

        if classe not in deteccoes_por_classe:
            deteccoes_por_classe[classe] = []

        deteccoes_por_classe[classe].append(segundo)


eventos = []

# Agrupa detecções próximas em eventos
for classe, segundos in deteccoes_por_classe.items():

    segundos = sorted(set(segundos))

    if not segundos:
        continue

    inicio = segundos[0]
    ultimo = segundos[0]

    for segundo in segundos[1:]:

        if segundo - ultimo <= TOLERANCIA_SEGUNDOS:
            ultimo = segundo

        else:
            eventos.append([
                classe,
                segundos_para_timestamp(inicio),
                segundos_para_timestamp(ultimo)
            ])

            inicio = segundo
            ultimo = segundo

    eventos.append([
        classe,
        segundos_para_timestamp(inicio),
        segundos_para_timestamp(ultimo)
    ])


# Ordena pelo horário inicial
eventos.sort(
    key=lambda evento: timestamp_para_segundos(evento[1])
)


# Salva os eventos
with open(ARQUIVO_SAIDA, "w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.writer(arquivo)

    escritor.writerow(["classe", "inicio", "fim"])
    escritor.writerows(eventos)


print("Eventos encontrados:")
print()

for classe, inicio, fim in eventos:

    if inicio == fim:
        print(f"{classe} | {inicio}")
    else:
        print(f"{classe} | {inicio} até {fim}")

print()
print("Processamento concluído.")
print("Arquivo eventos.csv criado.")