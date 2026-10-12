import sqlite3

BANCO = "cftv.db"

conexao = sqlite3.connect(BANCO)
cursor = conexao.cursor()

print("=== BUSCA DE EVENTOS EM CFTV ===")
print()
print("Opções: pessoa, carro ou motocicleta")
print()

busca = input("O que você deseja procurar? ").strip().lower()

apelidos = {
    "moto": "motocicleta",
    "motocicletas": "motocicleta",
    "carros": "carro",
    "pessoas": "pessoa"
}

busca = apelidos.get(busca, busca)

cursor.execute(
    """
    SELECT video, classe, inicio, fim
    FROM eventos
    WHERE classe = ?
    ORDER BY inicio
    """,
    (busca,)
)

resultados = cursor.fetchall()

print()

if resultados:
    print(f"Resultados encontrados para '{busca}':")
    print()

    for video, classe, inicio, fim in resultados:
        if inicio == fim:
            print(f"{classe} encontrada em {inicio} no vídeo {video}")
        else:
            print(
                f"{classe} encontrada entre {inicio} e {fim} "
                f"no vídeo {video}"
            )
else:
    print(f"Nenhum resultado encontrado para '{busca}'.")

conexao.close()