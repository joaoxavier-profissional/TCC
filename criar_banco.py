import csv
import sqlite3

ARQUIVO_CSV = "eventos.csv"
BANCO = "cftv.db"
VIDEO = "teste.mp4"

# Conecta ao banco de dados.
# Se ele ainda não existir, o SQLite cria automaticamente.
conexao = sqlite3.connect(BANCO)
cursor = conexao.cursor()

# Cria a tabela de eventos
cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video TEXT NOT NULL,
    classe TEXT NOT NULL,
    inicio TEXT NOT NULL,
    fim TEXT NOT NULL
)
""")

# Limpa registros anteriores para evitar duplicação nos testes
cursor.execute("DELETE FROM eventos")

# Lê o arquivo eventos.csv
with open(ARQUIVO_CSV, "r", encoding="utf-8") as arquivo:
    leitor = csv.DictReader(arquivo)

    for linha in leitor:
        cursor.execute(
            """
            INSERT INTO eventos (video, classe, inicio, fim)
            VALUES (?, ?, ?, ?)
            """,
            (
                VIDEO,
                linha["classe"],
                linha["inicio"],
                linha["fim"]
            )
        )

conexao.commit()

print("Eventos armazenados no banco:")
print()

cursor.execute("""
SELECT id, video, classe, inicio, fim
FROM eventos
ORDER BY inicio
""")

for evento in cursor.fetchall():

    id_evento, video, classe, inicio, fim = evento

    if inicio == fim:
        print(f"{id_evento} | {classe} | {inicio} | {video}")
    else:
        print(f"{id_evento} | {classe} | {inicio} até {fim} | {video}")

conexao.close()

print()
print("Banco de dados criado com sucesso.")
print("Arquivo cftv.db criado.")