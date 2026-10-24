"""Recepção segura de MP4 para a biblioteca local de gravações."""
from pathlib import Path
import re
import secrets

MAX_UPLOAD_BYTES = 250 * 1024 * 1024
_NOME = re.compile(r"^[\w .()\-]+\.mp4$", re.IGNORECASE | re.UNICODE)


def validar_nome(nome):
    """Aceita nomes simples MP4, sem separadores e sem nomes especiais."""
    if (not isinstance(nome, str) or not nome or nome in (".", "..")
            or "/" in nome or "\\" in nome or not _NOME.fullmatch(nome)
            or nome.startswith(".")):
        raise ValueError("Nome inválido. Use um nome simples terminado em .mp4.")
    return nome


def guardar_upload(arquivo, nome, pasta, tamanho_maximo=MAX_UPLOAD_BYTES):
    """Salva upload em blocos; nunca sobrescreve arquivos existentes.

    O envio deve ser limitado no Streamlit também. Faz escrita temporária e
    vincula o destino de forma exclusiva para não substituir outro MP4.
    """
    nome = validar_nome(nome)
    raiz = Path(pasta)
    raiz.mkdir(parents=True, exist_ok=True)
    destino = raiz / nome
    if destino.exists():
        raise FileExistsError(f"Já existe um vídeo chamado {nome}.")
    temporario = raiz / (".upload-" + secrets.token_hex(16) + ".part")
    total = 0
    try:
        with temporario.open("xb") as saida:
            while True:
                bloco = arquivo.read(1024 * 1024)
                if not bloco:
                    break
                total += len(bloco)
                if total > tamanho_maximo:
                    raise ValueError("Arquivo excede o limite de 250 MB.")
                saida.write(bloco)
        if total == 0:
            raise ValueError("O arquivo está vazio.")
        # Link exclusivo: se o destino surgir durante o upload, não substitui.
        import os
        os.link(temporario, destino)
        return destino
    finally:
        temporario.unlink(missing_ok=True)
