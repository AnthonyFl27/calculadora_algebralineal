"""Pruebas del método de la secante."""

import unittest

from metodos.secante import procedimiento_texto, secante


class CasoClaseTests(unittest.TestCase):
    """x³ − x − 2 con x₀ = 1 y x₁ = 2 (el problema conductor de la clase)."""

    def setUp(self):
        self.r = secante("x^3 - x - 2", 1, 2, "0.000001")

    def test_primera_iteracion_y_resultado(self):
        p = self.r["pasos"][0]
        self.assertAlmostEqual(p["x_nuevo"], 4 / 3, places=9)
        self.assertEqual((p["x_ant"], p["x"]), (1, 2))
        self.assertAlmostEqual(p["error"], 50.0, places=6)
        res = self.r["resultado"]
        self.assertAlmostEqual(res["raiz"], 1.5213797068, places=8)
        self.assertEqual(res["iteraciones"], 7)
        self.assertEqual(res["motivo"], "tolerancia")
        self.assertTrue(res["convergio"])
        self.assertTrue(self.r["comprobacion"]["correcto"])

    def test_se_desplazan_las_aproximaciones(self):
        pasos = self.r["pasos"]
        for ant, sig in zip(pasos, pasos[1:]):
            self.assertEqual(sig["x_ant"], ant["x"])
            self.assertEqual(sig["x"], ant["x_nuevo"])
            self.assertEqual(sig["f_ant"], ant["fx"])

    def test_formula(self):
        for p in self.r["pasos"]:
            esperado = p["x"] - p["fx"] * (p["x"] - p["x_ant"]) / (
                p["fx"] - p["f_ant"])
            self.assertAlmostEqual(p["x_nuevo"], esperado, places=12)

    def test_grafica(self):
        g = self.r["grafica"]
        self.assertIsNone(g["intervalo"])
        self.assertEqual(len(g["iteraciones"]), 7)
        self.assertEqual(g["iteraciones"][0]["etiqueta"], "x2")
        (xa, ya), (xb, yb) = g["iteraciones"][0]["secante"]
        self.assertEqual((xa, ya, yb), (1, -2.0, 0.0))
        self.assertAlmostEqual(xb, 4 / 3, places=12)
        self.assertEqual(g["inicio"]["x"], 1)
        self.assertEqual(g["inicio2"]["x"], 2)

    def test_texto(self):
        texto = procedimiento_texto(self.r)
        self.assertIn("MÉTODO DE LA SECANTE", texto)
        self.assertIn("Iteración 7", texto)
        self.assertIn("Tabla de iteraciones", texto)
        self.assertNotIn("Tabla de iteraciones", procedimiento_texto(
            self.r, incluir_pasos=False))


class OtrosCasosTests(unittest.TestCase):

    def test_sin_cambio_de_signo(self):
        r = secante("x^3 - x - 2", 3, 4, "0.000001")
        self.assertAlmostEqual(r["resultado"]["raiz"], 1.5213797, places=6)

    def test_x1_es_raiz(self):
        r = secante("x^2 - 4", 1, 2, "0.0001")
        self.assertEqual(r["resultado"]["motivo"], "raiz_exacta")
        self.assertEqual(r["resultado"]["raiz"], 2)

    def test_denominador_cero_en_la_primera_iteracion_es_error(self):
        with self.assertRaises(ValueError) as cm:
            secante("x^2 - 4", -3, 3, "0.0001")
        self.assertIn("es cero", str(cm.exception))

    def test_denominador_cero_despues_conserva_los_pasos(self):
        # x² + 1 desde 0 y 1: x₂ = −1... luego f(1) = f(−1).
        r = secante("x^2 + 1", 0, 1, "0.0001")
        self.assertEqual(r["resultado"]["motivo"], "denominador_cero")
        self.assertFalse(r["resultado"]["convergio"])
        self.assertTrue(r["pasos"])
        self.assertTrue(r["advertencias"])
        self.assertFalse(r["comprobacion"]["correcto"])

    def test_x0_igual_x1_es_error(self):
        with self.assertRaises(ValueError) as cm:
            secante("x^2 - 2", 1, 1, "0.1")
        self.assertIn("distintos", str(cm.exception))

    def test_fuera_del_dominio(self):
        with self.assertRaises(ValueError) as cm:
            secante("ln(x)", 3, 4, "0.0001")
        self.assertIn("fuera del dominio", str(cm.exception))

    def test_agota_iteraciones(self):
        r = secante("x^3 - 2x + 2", 0, 1, "0.0001", 20)
        self.assertEqual(r["resultado"]["motivo"], "max_iter")
        self.assertEqual(r["resultado"]["iteraciones"], 20)
        self.assertTrue(any("agotaron" in a for a in r["advertencias"]))

    def test_validaciones(self):
        for args in [("", 1, 2, "0.1"), ("5", 1, 2, "0.1"),
                     ("x^2 - 2", "", 2, "0.1"), ("x^2 - 2", 1, "", "0.1"),
                     ("x^2 - 2", 1, 2, "0"), ("x^2 - 2", 1, 2, "0.1", 0),
                     ("x^2 - 2", 1, 2, "0.1", 201)]:
            with self.subTest(args):
                with self.assertRaises(ValueError):
                    secante(*args)


if __name__ == "__main__":
    unittest.main()
