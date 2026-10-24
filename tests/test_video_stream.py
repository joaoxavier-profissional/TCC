"""Testes do streaming de vídeo local, sem internet e sem MP4 reais."""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import unittest

from services.video_stream import url_video


class TestStreamingLocal(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.video = Path(self.tmp.name) / "amostra.mp4"
        self.conteudo = bytes(range(256)) * 8
        self.video.write_bytes(self.conteudo)
        self.url = url_video(self.video)

    def test_reutiliza_url_do_mesmo_video(self):
        self.assertEqual(url_video(self.video), self.url)

    def test_conteudo_completo(self):
        with urlopen(self.url, timeout=3) as resposta:
            self.assertEqual(resposta.status, 200)
            self.assertEqual(resposta.headers["Content-Type"], "video/mp4")
            self.assertEqual(resposta.headers["Accept-Ranges"], "bytes")
            self.assertEqual(resposta.read(), self.conteudo)

    def test_range_parcial(self):
        with urlopen(Request(self.url, headers={"Range": "bytes=10-19"}), timeout=3) as resposta:
            self.assertEqual(resposta.status, 206)
            self.assertEqual(resposta.headers["Content-Range"], "bytes 10-19/2048")
            self.assertEqual(resposta.read(), self.conteudo[10:20])

    def test_range_sufixo(self):
        with urlopen(Request(self.url, headers={"Range": "bytes=-5"}), timeout=3) as resposta:
            self.assertEqual(resposta.status, 206)
            self.assertEqual(resposta.read(), self.conteudo[-5:])

    def test_range_aberto(self):
        with urlopen(Request(self.url, headers={"Range": "bytes=2040-"}), timeout=3) as resposta:
            self.assertEqual(resposta.status, 206)
            self.assertEqual(resposta.read(), self.conteudo[2040:])

    def test_range_invalido(self):
        with self.assertRaises(HTTPError) as capturado:
            urlopen(Request(self.url, headers={"Range": "bytes=9999-"}), timeout=3)
        self.assertEqual(capturado.exception.code, 416)
        capturado.exception.close()

    def test_head_sem_corpo(self):
        with urlopen(Request(self.url, method="HEAD"), timeout=3) as resposta:
            self.assertEqual(resposta.headers["Content-Length"], "2048")
            self.assertEqual(resposta.read(), b"")

    def test_nao_aceita_arquivo_ausente(self):
        with self.assertRaises(FileNotFoundError):
            url_video(Path(self.tmp.name) / "inexistente.mp4")

    def test_nao_aceita_outros_formatos(self):
        arquivo = Path(self.tmp.name) / "segredo.txt"
        arquivo.write_text("exemplo")
        with self.assertRaises(ValueError):
            url_video(arquivo)


if __name__ == "__main__":
    unittest.main()
