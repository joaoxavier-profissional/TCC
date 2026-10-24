"""Testes de regressão dos filtros de eventos de CFTV."""
import unittest

from services.busca import filtrar_eventos


EVENTOS = [
    ("cam1.mp4", "pessoa", "00:00:05", "00:00:12"),
    ("cam1.mp4", "carro", "00:00:10", "00:00:20"),
    ("cam2.mp4", "pessoa", "00:00:30", "00:00:40"),
    ("cam2.mp4", "moto", "00:01:00", "00:01:10"),
]


class TestFiltrarEventos(unittest.TestCase):
    def test_sem_filtros_retorna_todos_em_ordem_crescente(self):
        self.assertEqual(filtrar_eventos(EVENTOS), EVENTOS)

    def test_filtra_por_classe(self):
        resultado = filtrar_eventos(EVENTOS, classe="pessoa")
        self.assertEqual([e[1] for e in resultado], ["pessoa", "pessoa"])

    def test_filtra_por_video(self):
        resultado = filtrar_eventos(EVENTOS, video="cam2.mp4")
        self.assertEqual(len(resultado), 2)
        self.assertTrue(all(e[0] == "cam2.mp4" for e in resultado))

    def test_combina_classe_video_e_intervalo(self):
        resultado = filtrar_eventos(
            EVENTOS, classe="pessoa", video="cam1.mp4", inicio=8, fim=9
        )
        self.assertEqual(resultado, [EVENTOS[0]])

    def test_inclui_eventos_que_cruzam_a_janela(self):
        resultado = filtrar_eventos(EVENTOS, inicio=11, fim=15)
        self.assertEqual(resultado, [EVENTOS[0], EVENTOS[1]])

    def test_limites_da_janela_sao_inclusivos(self):
        resultado = filtrar_eventos(EVENTOS, inicio=20, fim=30)
        self.assertEqual(resultado, [EVENTOS[1], EVENTOS[2]])

    def test_intervalo_sem_correspondencias(self):
        self.assertEqual(filtrar_eventos(EVENTOS, inicio=100, fim=110), [])

    def test_intervalo_invertido_gera_erro(self):
        with self.assertRaises(ValueError):
            filtrar_eventos(EVENTOS, inicio=20, fim=10)

    def test_descendente(self):
        resultado = filtrar_eventos(EVENTOS, ordenacao="Horário (decrescente)")
        self.assertEqual(resultado, list(reversed(EVENTOS)))

    def test_ordenacao_por_classe(self):
        resultado = filtrar_eventos(EVENTOS, ordenacao="Classe (A–Z)")
        self.assertEqual([e[1] for e in resultado], ["carro", "moto", "pessoa", "pessoa"])

    def test_ordenacao_por_gravacao(self):
        resultado = filtrar_eventos(EVENTOS, ordenacao="Gravação (A–Z)")
        self.assertEqual([e[0] for e in resultado], ["cam1.mp4", "cam1.mp4", "cam2.mp4", "cam2.mp4"])

    def test_descarta_eventos_com_horario_invalido(self):
        eventos = EVENTOS + [("cam3.mp4", "pessoa", "indefinido", "00:00:15")]
        self.assertEqual(filtrar_eventos(eventos), EVENTOS)


if __name__ == "__main__":
    unittest.main()
