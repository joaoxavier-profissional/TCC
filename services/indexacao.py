"""Regras de agrupamento e persistência de detecções, independentes do YOLO."""
import sqlite3
from contextlib import closing
from collections import defaultdict
from pathlib import Path


def horario(segundo):
    segundo = int(segundo)
    return f"{segundo // 3600:02}:{segundo % 3600 // 60:02}:{segundo % 60:02}"


def agrupar_deteccoes(deteccoes, tolerancia=2):
    """Recebe pares (segundo, classe); devolve (classe, inicio, fim).

    Os intervalos são inclusivos; 2 segundos de diferença pertencem
    ao mesmo evento. Repetições no mesmo segundo são deduplicadas.
    """
    if tolerancia < 0:
        raise ValueError("Tolerância não pode ser negativa.")
    por_classe = defaultdict(set)
    for segundo, classe in deteccoes:
        if int(segundo) < 0:
            raise ValueError("Segundo negativo.")
        por_classe[str(classe)].add(int(segundo))
    eventos = []
    for classe, instantes in por_classe.items():
        instantes = sorted(instantes)
        if not instantes:
            continue
        inicio = ultimo = instantes[0]
        for instante in instantes[1:]:
            if instante - ultimo <= tolerancia:
                ultimo = instante
            else:
                eventos.append((classe, horario(inicio), horario(ultimo)))
                inicio = ultimo = instante
        eventos.append((classe, horario(inicio), horario(ultimo)))
    return sorted(eventos, key=lambda e: (e[1], e[0]))


def salvar_eventos(banco, nome_video, eventos):
    """Substitui somente eventos do vídeo informado, em transação SQLite.

    Em caso de falha durante a inserção, a transação é revertida.
    """
    nome = Path(nome_video).name
    if not nome or nome in (".", "..") or not nome.lower().endswith(".mp4"):
        raise ValueError("Nome de vídeo MP4 inválido.")
    registros = [(nome, classe, inicio, fim) for classe, inicio, fim in eventos]
    # O contexto do sqlite3 cuida da transação, mas NÃO fecha a conexão.
    # closing garante o fechamento também quando há exceções (Windows).
    with closing(sqlite3.connect(banco)) as con:
        with con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video TEXT NOT NULL,
                    classe TEXT NOT NULL,
                    inicio TEXT NOT NULL,
                    fim TEXT NOT NULL
                )
            """)
            con.execute("DELETE FROM eventos WHERE video = ?", (nome,))
            con.executemany(
                "INSERT INTO eventos (video, classe, inicio, fim) VALUES (?, ?, ?, ?)",
                registros,
            )
    return len(registros)
