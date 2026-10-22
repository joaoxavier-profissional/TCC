"""Testes das funções auxiliares de tempo e arquivos de vídeo."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services import video


class TestSegundos(unittest.TestCase):
    def test_converte_hora_minuto_segundo(self):
        self.assertEqual(video.segundos("01:02:03"), 3723)

    def test_converte_inicio_da_gravacao(self):
        self.assertEqual(video.segundos("00:00:00"), 0)

    def test_rejeita_formato_invalido(self):
        for valor in ("01:30", "texto", "", "01:02:03:04"):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    video.segundos(valor)


class TestArquivosVideo(unittest.TestCase):
    def test_caminho_video_usa_apenas_nome_do_arquivo(self):
        with patch.object(video, "VIDEOS", Path("/gravacoes")):
            self.assertEqual(
                video.caminho_video("../outra_pasta/cam1.mp4"),
                Path("/gravacoes/cam1.mp4"),
            )

    def test_lista_apenas_mp4_e_em_ordem(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            for nome in ("b.mp4", "a.mp4", "nota.txt"):
                (raiz / nome).touch()
            with patch.object(video, "VIDEOS", raiz):
                self.assertEqual(
                    [p.name for p in video.listar_videos()],
                    ["a.mp4", "b.mp4"],
                )

    def test_pasta_inexistente_retorna_lista_vazia(self):
        with tempfile.TemporaryDirectory() as pasta:
            with patch.object(video, "VIDEOS", Path(pasta) / "ausente"):
                self.assertEqual(video.listar_videos(), [])


if __name__ == "__main__":
    unittest.main()
