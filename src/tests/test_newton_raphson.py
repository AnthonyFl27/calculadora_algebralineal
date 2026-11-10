"""Pruebas del método de Newton-Raphson y de la derivada simbólica."""

import unittest

from metodos.derivada import derivada_de
from metodos.evaluador import compilar
from metodos.newton_raphson import (
    newton_raphson,
    procedimiento_texto,
)


class DerivadaTests(unittest.TestCase):

    def test_contra_diferencia_numerica(self):
        casos = [
            "x^3 - x - 2", "3x^2 - 2x + 7", "sin(x)*cos(x)", "exp(-x) - x",
            "1/x", "x^x", "ln(x^2 + 1)", "sqrt(x)/(x + 1)", "2^x", "-x^2",
            "cos(x) - x", "tan(x)", "atan(x)", "x^4 - 5x^3 + 0.5x^2 - 11x + 10",
            "sinh(x) + cosh(x)", "log(x) + ln(2x)", "cbrt(x)", "abs(x)",
        ]
        x, h = 0.7, 1e-6
        for texto in casos:
            with self.subTest(texto):
                f = compilar(texto)
                d = derivada_de(f)
                numerica = (f(x + h) - f(x - h)) / (2 * h)
                self.assertAlmostEqual(d(x), numerica, places=4)
                # El texto de la derivada se puede volver a leer.
                self.assertAlmostEqual(compilar(d.texto)(x), d(x), places=10)

    def test_texto_legible(self):
        self.assertEqual(derivada_de(compilar("x^3 - x - 2")).texto, "3 * x^2 - 1")
        self.assertEqual(derivada_de(compilar("x^3 - 2x - 5")).texto, "3 * x^2 - 2")
        self.assertEqual(derivada_de(compilar("5")).texto, "0")


class EjemploDeClaseTests(unittest.TestCase):
    """x³ − x − 2 con x₀ = 1.5 (tabla de la presentación)."""

    def setUp(self):
        self.r = newton_raphson("x^3 - x - 2", "", 1.5, "0.000001")

    def test_primera_iteracion(self):
        p = self.r["pasos"][0]
        self.assertAlmostEqual(p["fx"], -0.125)
        self.assertAlmostEqual(p["dfx"], 5.75)
        self.assertAlmostEqual(p["x_nuevo"], 1.521739130, places=9)

    def test_resultado(self):
        res = self.r["resultado"]
        self.assertEqual(res["iteraciones"], 3)
        self.assertAlmostEqual(res["raiz"], 1.521379707, places=9)
        self.assertTrue(res["convergio"])
        self.assertLess(res["residuo"], 1e-9)
        self.assertEqual(self.r["entradas"]["derivada_origen"], "automatica")
        self.assertTrue(self.r["comprobacion"]["correcto"])

    def test_grafica(self):
        g = self.r["grafica"]
        self.assertIsNone(g["intervalo"])
        self.assertEqual(len(g["iteraciones"]), 3)
        self.assertEqual(g["iteraciones"][0]["etiqueta"], "x1")
        self.assertEqual(g["iteraciones"][0]["tangente"][1][1], 0.0)
        self.assertAlmostEqual(g["inicio"]["x"], 1.5)
        self.assertLess(g["x_min"], 1.5)
        self.assertGreater(g["x_max"], 1.5214)

    def test_texto(self):
        texto = procedimiento_texto(self.r)
        self.assertIn("MÉTODO DE NEWTON-RAPHSON", texto)
        self.assertIn("f'(x) = 3 * x^2 - 1", texto)
        self.assertIn("Iteración 3", texto)
        self.assertNotIn("Tabla de iteraciones", procedimiento_texto(
            self.r, incluir_pasos=False))


class OtrosCasosTests(unittest.TestCase):

    def test_actividad_1(self):
        r = newton_raphson("x^3 - 2x - 5", "", 2, "0.000001")
        self.assertAlmostEqual(r["resultado"]["raiz"], 2.0945514815, places=8)
        self.assertEqual(r["resultado"]["iteraciones"], 4)

    def test_derivada_manual_y_derivada_mal_escrita(self):
        r = newton_raphson("x^3 - x - 2", "3x^2 - 1", 1.5, "0.000001")
        self.assertEqual(r["entradas"]["derivada_origen"], "manual")
        self.assertTrue(r["comprobacion"]["derivada_correcta"])
        mala = newton_raphson("x^3 - x - 2", "3x^2 - 2", 1.5, "0.000001")
        self.assertFalse(mala["comprobacion"]["derivada_correcta"])
        self.assertTrue(any("no coincide" in a for a in mala["advertencias"]))

    def test_x0_es_raiz(self):
        r = newton_raphson("x^2 - 4", "", 2, "0.0001")
        self.assertEqual(r["resultado"]["motivo"], "raiz_exacta")
        self.assertEqual(r["resultado"]["iteraciones"], 1)
        self.assertEqual(r["resultado"]["raiz"], 2)

    def test_derivada_cero_en_x0_es_error(self):
        with self.assertRaises(ValueError) as cm:
            newton_raphson("x^2 - 1", "", 0, "0.0001")
        self.assertIn("es cero", str(cm.exception))

    def test_fuera_del_dominio_en_la_primera_iteracion(self):
        with self.assertRaises(ValueError) as cm:
            newton_raphson("ln(x)", "", 3, "0.0001")
        self.assertIn("fuera del dominio", str(cm.exception))

    def test_falla_tras_algunas_iteraciones_conserva_los_pasos(self):
        # x² + 1 desde 1: x₁ = 0 y ahí f′(0) = 0.
        r = newton_raphson("x^2 + 1", "", 1, "0.0001")
        self.assertEqual(r["resultado"]["motivo"], "derivada_cero")
        self.assertFalse(r["resultado"]["convergio"])
        self.assertEqual(len(r["pasos"]), 1)
        self.assertTrue(r["advertencias"])
        self.assertFalse(r["comprobacion"]["correcto"])

    def test_ciclo_agota_iteraciones(self):
        r = newton_raphson("x^3 - 2x + 2", "", 0, "0.0001", 20)
        self.assertEqual(r["resultado"]["motivo"], "max_iter")
        self.assertEqual(r["resultado"]["iteraciones"], 20)
        self.assertTrue(any("agotaron" in a for a in r["advertencias"]))

    def test_raiz_multiple_converge_lento(self):
        r = newton_raphson("(x - 1)^2", "", 3, "0.0001")
        self.assertEqual(r["resultado"]["iteraciones"], 15)

    def test_discontinuidad_solo_avisa(self):
        r = newton_raphson("1/x - 2", "", 0.4, "0.0001")
        self.assertAlmostEqual(r["resultado"]["raiz"], 0.5, places=6)
        self.assertFalse(r["bloqueada"])

    def test_validaciones(self):
        for args in [("", "", 1, "0.1"), ("5", "", 1, "0.1"),
                     ("x^2 - 2", "", "", "0.1"), ("x^2 - 2", "", 1, "0"),
                     ("x^2 - 2", "x +", 1, "0.1"),
                     ("x^2 - 2", "", 1, "0.1", 0),
                     ("x^2 - 2", "", 1, "0.1", 201)]:
            with self.subTest(args):
                with self.assertRaises(ValueError):
                    newton_raphson(*args)


if __name__ == "__main__":
    unittest.main()
