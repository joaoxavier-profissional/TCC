"""Testes do agrupamento temporal e da persistência SQLite por vídeo."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from services.indexacao import agrupar_deteccoes, salvar_eventos


class TestAgrupamento(unittest.TestCase):
    def test_sem_deteccoes(self):
        self.assertEqual(agrupar_deteccoes([]), [])

    def test_agrupa_lacunas_de_ate_dois_segundos(self):
        self.assertEqual(
            agrupar_deteccoes([(1, "pessoa"), (3, "pessoa"), (6, "pessoa")]),
            [("pessoa", "00:00:01", "00:00:03"), ("pessoa", "00:00:06", "00:00:06")],
        )

    def test_deduplica_e_separa_classes(self):
        self.assertEqual(
            agrupar_deteccoes([(2, "carro"), (2, "carro"), (2, "pessoa")]),
            [("carro", "00:00:02", "00:00:02"), ("pessoa", "00:00:02", "00:00:02")],
        )

    def test_rejeita_segundos_negativos(self):
        with self.assertRaises(ValueError):
            agrupar_deteccoes([(-1, "pessoa")])


class TestBanco(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.banco = Path(self.tmp.name) / "testes.db"

    def consultar(self):
        with sqlite3.connect(self.banco) as con:
            return con.execute(
                "SELECT video, classe, inicio, fim FROM eventos ORDER BY video, inicio"
            ).fetchall()

    def test_preserva_eventos_dos_outros_videos(self):
        salvar_eventos(self.banco, "a.mp4", [("pessoa", "00:00:01", "00:00:02")])
        salvar_eventos(self.banco, "b.mp4", [("carro", "00:00:04", "00:00:05")])
        self.assertEqual(len(self.consultar()), 2)

    def test_reindexacao_nao_duplica(self):
        evento = [("pessoa", "00:00:01", "00:00:02")]
        salvar_eventos(self.banco, "a.mp4", evento)
        salvar_eventos(self.banco, "a.mp4", evento)
        self.assertEqual(len(self.consultar()), 1)

    def test_reindexacao_substitui_apenas_video_alvo(self):
        salvar_eventos(self.banco, "a.mp4", [("pessoa", "00:00:01", "00:00:02")])
        salvar_eventos(self.banco, "b.mp4", [("carro", "00:00:04", "00:00:05")])
        salvar_eventos(self.banco, "a.mp4", [("motocicleta", "00:00:08", "00:00:09")])
        self.assertEqual([r[1] for r in self.consultar()], ["motocicleta", "carro"])

    def test_arquivo_sem_deteccoes_remove_apenas_eventos_antigos_desse_video(self):
        salvar_eventos(self.banco, "a.mp4", [("pessoa", "00:00:01", "00:00:02")])
        salvar_eventos(self.banco, "b.mp4", [("carro", "00:00:03", "00:00:04")])
        salvar_eventos(self.banco, "a.mp4", [])
        self.assertEqual([r[0] for r in self.consultar()], ["b.mp4"])

    def test_reverte_exclusao_se_insercao_falhar(self):
        original = ("pessoa", "00:00:01", "00:00:02")
        salvar_eventos(self.banco, "a.mp4", [original])
        # SQLite rejeita NULL em coluna NOT NULL, e deve desfazer o DELETE anterior.
        with self.assertRaises(sqlite3.IntegrityError):
            salvar_eventos(self.banco, "a.mp4", [(None, "00:00:03", "00:00:04")])
        self.assertEqual(self.consultar(), [("a.mp4", *original)])


if __name__ == "__main__":
    unittest.main()
