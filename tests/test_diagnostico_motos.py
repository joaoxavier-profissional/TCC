"""Testes sem YOLO para a contagem de detecções por limiar."""
import unittest
from diagnostico_motos import resumir_limiares


class TestResumoDiagnostico(unittest.TestCase):
    def test_sem_deteccoes(self):
        resumo = resumir_limiares([])
        self.assertTrue(all(not contagens for contagens in resumo.values()))

    def test_limites_de_confianca(self):
        registros = [
            {"classe": "motocicleta", "confianca": 0.15},
            {"classe": "motocicleta", "confianca": 0.35},
            {"classe": "motocicleta", "confianca": 0.45},
            {"classe": "bicicleta", "confianca": 0.25},
        ]
        resumo = resumir_limiares(registros)
        self.assertEqual([resumo[l]["motocicleta"] for l in (0.1, 0.2, 0.3, 0.4)],
                         [3, 2, 2, 1])
        self.assertEqual(resumo[0.2]["bicicleta"], 1)
        self.assertEqual(resumo[0.3]["bicicleta"], 0)

    def test_classe_nao_informada_continua_contada(self):
        resumo = resumir_limiares([{"classe": "onibus", "confianca": 0.9}])
        self.assertEqual(resumo[0.4]["onibus"], 1)


if __name__ == "__main__":
    unittest.main()
