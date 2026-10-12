"""Acesso aos eventos armazenados no SQLite."""
import sqlite3
from services.config import BANCO

def carregar_eventos():
    """

    Consulta a tabela eventos do SQLite.

    """
    if not BANCO.is_file():
        return ([], 'Banco de dados não encontrado.')
    try:
        with sqlite3.connect(BANCO) as con:
            dados = con.execute('\n\n                SELECT video, classe, inicio, fim\n\n                FROM eventos\n\n                ORDER BY video, inicio\n\n                ').fetchall()
        return (dados, None)
    except sqlite3.Error as erro:
        return ([], f'Erro no SQLite: {erro}')
