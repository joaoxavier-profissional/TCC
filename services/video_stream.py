"""Servidor HTTP local para reproduzir MP4 com suporte a solicitações Range.

Escuta somente em 127.0.0.1. Cada arquivo cadastrado recebe token aleatório.
Não expõe listagem de diretórios nem aceita caminhos fornecidos pelo cliente.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock, Thread
from urllib.parse import urlsplit
import re
import secrets

_INTERVALO = re.compile(r"^bytes=(\d*)-(\d*)$")
_BLOCO = 256 * 1024


class _Servidor(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, endereco):
        super().__init__(endereco, _Handler)
        self.arquivos = {}
        self.trava = Lock()


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, formato, *args):
        pass

    def do_GET(self):
        self._responder(False)

    def do_HEAD(self):
        self._responder(True)

    def _responder(self, somente_cabecalhos):
        rota = urlsplit(self.path).path
        if not rota.startswith("/video/"):
            self.send_error(404)
            return
        token = rota[len("/video/"):]
        with self.server.trava:
            arquivo = self.server.arquivos.get(token)
        if arquivo is None or not arquivo.is_file():
            self.send_error(404)
            return

        try:
            tamanho = arquivo.stat().st_size
        except OSError:
            self.send_error(404)
            return

        cabecalho = self.headers.get("Range")
        inicio, fim = 0, tamanho - 1
        parcial = cabecalho is not None
        if parcial:
            match = _INTERVALO.fullmatch(cabecalho.strip())
            if not match or (not match[1] and not match[2]) or tamanho == 0:
                self._intervalo_invalido(tamanho)
                return
            try:
                if not match[1]:  # bytes=-N
                    quantidade = int(match[2])
                    if quantidade <= 0:
                        raise ValueError()
                    inicio = max(tamanho - quantidade, 0)
                else:
                    inicio = int(match[1])
                    fim = int(match[2]) if match[2] else tamanho - 1
                if inicio >= tamanho or fim < inicio:
                    raise ValueError()
                fim = min(fim, tamanho - 1)
            except ValueError:
                self._intervalo_invalido(tamanho)
                return

        comprimento = max(0, fim - inicio + 1)
        self.send_response(206 if parcial else 200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(comprimento))
        self.send_header("Cache-Control", "private, no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if parcial:
            self.send_header("Content-Range", f"bytes {inicio}-{fim}/{tamanho}")
        self.end_headers()
        if somente_cabecalhos:
            return
        try:
            with arquivo.open("rb") as conteudo:
                conteudo.seek(inicio)
                restante = comprimento
                while restante:
                    bloco = conteudo.read(min(restante, _BLOCO))
                    if not bloco:
                        break
                    self.wfile.write(bloco)
                    restante -= len(bloco)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _intervalo_invalido(self, tamanho):
        self.send_response(416)
        self.send_header("Content-Range", f"bytes */{tamanho}")
        self.send_header("Content-Length", "0")
        self.end_headers()


_instancia = None
_trava_instancia = Lock()


def _obter_servidor():
    global _instancia
    with _trava_instancia:
        if _instancia is None:
            servidor = _Servidor(("127.0.0.1", 0))
            Thread(target=servidor.serve_forever, daemon=True).start()
            _instancia = servidor
        return _instancia


def url_video(caminho):
    """Registra arquivo local existente e devolve sua URL temporária."""
    arquivo = Path(caminho).resolve(strict=True)
    if not arquivo.is_file() or arquivo.suffix.lower() != ".mp4":
        raise ValueError("O arquivo precisa ser um vídeo MP4.")
    servidor = _obter_servidor()
    with servidor.trava:
        # Reutiliza o token ao reconstruir o player no Streamlit.
        for token, existente in servidor.arquivos.items():
            if existente == arquivo:
                break
        else:
            token = secrets.token_urlsafe(24)
            servidor.arquivos[token] = arquivo
    porta = servidor.server_address[1]
    return f"http://127.0.0.1:{porta}/video/{token}"
