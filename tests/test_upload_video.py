"""Testes de upload local sem rede, YOLO ou banco real."""
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from services.upload_video import guardar_upload, validar_nome


class TestUploadVideo(unittest.TestCase):
    def test_grava_mp4_com_conteudo(self):
        with TemporaryDirectory() as pasta:
            destino = guardar_upload(BytesIO(b"video ficticio"), "camera 1.mp4", pasta)
            self.assertEqual(destino.read_bytes(), b"video ficticio")

    def test_nao_sobrescreve_video_existente(self):
        with TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "existente.mp4"
            arquivo.write_bytes(b"original")
            with self.assertRaises(FileExistsError):
                guardar_upload(BytesIO(b"novo"), arquivo.name, pasta)
            self.assertEqual(arquivo.read_bytes(), b"original")

    def test_nao_aceita_caminho_de_pasta(self):
        for nome in ("../a.mp4", "videos/a.mp4", "..\\a.mp4", ".oculto.mp4", "a.txt"):
            with self.subTest(nome=nome):
                with self.assertRaises(ValueError):
                    validar_nome(nome)

    def test_recusa_arquivo_vazio(self):
        with TemporaryDirectory() as pasta:
            with self.assertRaises(ValueError):
                guardar_upload(BytesIO(b""), "vazio.mp4", pasta)
            self.assertEqual(list(Path(pasta).iterdir()), [])

    def test_recusa_arquivo_acima_do_limite_e_limpa_temporario(self):
        with TemporaryDirectory() as pasta:
            with self.assertRaises(ValueError):
                guardar_upload(BytesIO(b"abcdef"), "grande.mp4", pasta, tamanho_maximo=5)
            self.assertEqual(list(Path(pasta).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
