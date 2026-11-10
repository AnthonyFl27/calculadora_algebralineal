"""Pruebas del método de Regula Falsi (falsa posición)."""

import unittest

from metodos.biseccion import biseccion
from metodos.falsa_posicion import (
    falsa_posicion,
    procedimiento_texto,
    punto_secante,
)

POLINOMIO = "x^4 - 5x^3 + 0.5x^2 - 11x + 10"


class SecanteTests(unittest.TestCase):

    def test_punto_secante(self):
        # f(x) = x² − 2 en [1, 2]: la secante pasa por (1, −1) y (2, 2).
        self.assertAlmostEqual(punto_secante(1, 2, -1, 2), 4 / 3)

    def test_en_una_recta_la_raiz_sale_en_una_iteracion(self):
        r = falsa_posicion("2x - 3", 0, 5, "0.0001")
        self.assertAlmostEqual(r["pasos"][0]["c"], 1.5)
        self.assertEqual(r["pasos"][0]["fc"], 0)
        self.assertEqual(r["resultado"]["motivo"], "raiz_exacta")
        self.assertEqual(r["resultado"]["iteraciones"], 1)


class RaizCuadradaTests(unittest.TestCase):

    def setUp(self):
        self.r = falsa_posicion("x^2 - 2", 1, 2, "0.0001")

    def test_resultado(self):
        res = self.r["resultado"]
        self.assertEqual(res["iteraciones"], 6)
        self.assertAlmostEqual(res["raiz"], 2 ** 0.5, places=4)
        self.assertTrue(res["convergio"])
        self.assertEqual(self.r["operacion"], "falsa_posicion")
        self.assertFalse(self.r["bloqueada"])
        self.assertNotIn("cota_iteraciones", self.r)

    def test_primeras_iteraciones(self):
        pasos = self.r["pasos"]
        self.assertAlmostEqual(pasos[0]["c"], 4 / 3)
        self.assertAlmostEqual(pasos[1]["c"], 1.4)
        self.assertIsNone(pasos[0]["error"])
        self.assertAlmostEqual(pasos[1]["error"], 100 * (1.4 - 4 / 3) / 1.4)
        self.assertEqual(pasos[0]["decision"], "derecha")
        self.assertEqual(pasos[1]["a"], pasos[0]["a_nuevo"])

    def test_c_es_el_corte_de_la_secante(self):
        for p in self.r["pasos"]:
            self.assertAlmostEqual(
                p["c"], (p["a"] * p["fb"] - p["b"] * p["fa"])
                / (p["fb"] - p["fa"]))
            self.assertLess(p["fa"] * p["fb"], 0)

    def test_comprobacion(self):
        c = self.r["comprobacion"]
        self.assertTrue(c["correcto"])
        self.assertTrue(c["cambio_signo"])
        self.assertLess(abs(c["fraiz"]), 1e-3)

    def test_grafica_con_secantes(self):
        g = self.r["grafica"]
        self.assertEqual(len(g["iteraciones"]), 6)
        self.assertEqual(g["iteraciones"][0]["secante"], [[1, -1], [2, 2]])
        self.assertIsNotNone(g["raiz"])

    def test_converge_en_menos_iteraciones_que_la_biseccion(self):
        for f, a, b in (("x^2 - 2", 1, 2), (POLINOMIO, "0.55", "1.1"),
                        ("cos(x) - x", 0, 1)):
            fp = falsa_posicion(f, a, b, "0.0001")["resultado"]["iteraciones"]
            bis = biseccion(f, a, b, "0.0001")["resultado"]["iteraciones"]
            self.assertLess(fp, bis, f)


class CasosBordeTests(unittest.TestCase):

    def test_polinomio_del_profesor(self):
        r = falsa_posicion(POLINOMIO, "0.55", "1.1", "0.0001")
        self.assertEqual(r["resultado"]["iteraciones"], 5)
        self.assertAlmostEqual(r["resultado"]["raiz"], 0.76392, places=4)

    def test_convergencia_lenta_deja_un_extremo_fijo(self):
        r = falsa_posicion("x^10 - 1", 0, "1.3", "0.0001", 200)
        self.assertEqual(r["resultado"]["iteraciones"], 39)
        self.assertEqual({p["b"] for p in r["pasos"]}, {1.3})

    def test_agotar_iteraciones_avisa(self):
        r = falsa_posicion("x^10 - 1", 0, "1.3", "0.0001", 10)
        self.assertFalse(r["resultado"]["convergio"])
        self.assertEqual(r["resultado"]["motivo"], "max_iter")
        self.assertTrue(any("Regula Falsi" in a for a in r["advertencias"]))
        self.assertFalse(r["comprobacion"]["correcto"])

    def test_sin_cambio_de_signo(self):
        with self.assertRaises(ValueError) as cm:
            falsa_posicion("x^2 + 1", 0, 2, "0.0001")
        self.assertIn("No hay cambio de signo", str(cm.exception))

    def test_extremo_que_ya_es_raiz(self):
        with self.assertRaises(ValueError) as cm:
            falsa_posicion("x^2 - 4", 2, 5, "0.0001")
        self.assertIn("ya es una raíz", str(cm.exception))

    def test_entradas_invalidas(self):
        for args in (("", 0, 1, "0.1"), ("5", 0, 1, "0.1"),
                     ("x", 2, 1, "0.1"), ("x", 0, 1, "0"),
                     ("x", -1, 1, "0.1", 0), ("x", -1, 1, "0.1", 201)):
            with self.subTest(args):
                with self.assertRaises(ValueError):
                    falsa_posicion(*args)

    def test_discontinuidad_bloquea_el_metodo(self):
        for f, a, b in (("1/x", -1, 2), ("tan(x)", 1, 2), ("abs(x)/x", -1, 2)):
            with self.subTest(f):
                r = falsa_posicion(f, a, b, "0.0001")
                self.assertTrue(r["bloqueada"])
                self.assertEqual(r["operacion"], "falsa_posicion")
                self.assertEqual(r["pasos"], [])
                self.assertIsNone(r["resultado"])
                self.assertIn("falsa posición", r["motivo_bloqueo"])
                self.assertNotIn("cota_iteraciones", r)
                self.assertTrue(r["grafica"]["discontinuidades"])

    def test_la_biseccion_sigue_igual(self):
        r = biseccion("1/x", -1, 2, "0.0001")
        self.assertEqual(r["operacion"], "biseccion")
        self.assertIn("bisección", r["motivo_bloqueo"])
        self.assertIn("cota_iteraciones", r)


class TextoTests(unittest.TestCase):

    def test_procedimiento_con_y_sin_pasos(self):
        r = falsa_posicion("x^2 - 2", 1, 2, "0.0001")
        con = procedimiento_texto(r)
        self.assertIn("MÉTODO DE REGULA FALSI", con)
        self.assertIn("Tabla de iteraciones", con)
        self.assertIn("c = 2 - 2·(2 - 1) / (2 - (-1))", con)
        self.assertIn("Raíz aproximada: x = 1.414201183", con)
        sin = procedimiento_texto(r, incluir_pasos=False)
        self.assertNotIn("Tabla de iteraciones", sin)
        self.assertIn("Comprobación", sin)

    def test_procedimiento_bloqueado(self):
        texto = procedimiento_texto(falsa_posicion("1/x", -1, 2, "0.0001"))
        self.assertIn("MÉTODO NO APLICADO", texto)


if __name__ == "__main__":
    unittest.main()
