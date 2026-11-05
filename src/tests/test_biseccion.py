"""Pruebas del método de bisección."""

import math
import unittest

from metodos.biseccion import (
    biseccion,
    cota_iteraciones,
    formatear_real,
    procedimiento_texto,
)

POLINOMIO = "x^4 - 5x^3 + 0.5x^2 - 11x + 10"


class CasoDelProfesorTests(unittest.TestCase):

    def setUp(self):
        self.r = biseccion(POLINOMIO, "0.55", "1.1", "0.0001")

    def test_13_iteraciones_y_raiz(self):
        res = self.r["resultado"]
        self.assertEqual(res["iteraciones"], 13)
        self.assertAlmostEqual(res["raiz"], 0.7639709473, places=9)
        self.assertEqual(res["motivo"], "tolerancia")
        self.assertTrue(res["convergio"])
        self.assertLess(abs(res["fraiz"]), 1e-3)

    def test_valores_corregidos_de_la_guia(self):
        self.assertAlmostEqual(self.r["inicial"]["fa"], 3.36088125)
        self.assertAlmostEqual(self.r["inicial"]["fb"], -6.6859)

    def test_tabla_de_iteraciones(self):
        pasos = self.r["pasos"]
        self.assertEqual(len(pasos), 13)
        self.assertEqual([p["i"] for p in pasos], list(range(1, 14)))
        self.assertIsNone(pasos[0]["error"])
        self.assertAlmostEqual(pasos[0]["c"], 0.825)
        self.assertAlmostEqual(pasos[1]["c"], 0.6875)
        self.assertAlmostEqual(pasos[1]["error"], 20.0)
        self.assertLess(pasos[-1]["error"] / 100, 0.0001)
        self.assertTrue(all(p["error"] / 100 >= 0.0001 for p in pasos[1:-1]))

    def test_el_intervalo_se_reduce_a_la_mitad(self):
        for p in self.r["pasos"]:
            self.assertAlmostEqual(p["b_nuevo"] - p["a_nuevo"],
                                   (p["b"] - p["a"]) / 2)
            self.assertLessEqual(p["a_nuevo"], p["c"])
            self.assertGreaterEqual(p["b_nuevo"], p["c"])
            self.assertLess(p["fa"] * p["fb"], 0)

    def test_decisiones(self):
        pasos = self.r["pasos"]
        self.assertEqual(pasos[0]["decision"], "izquierda")   # f(c) < 0
        self.assertEqual(pasos[1]["decision"], "derecha")     # f(c) > 0
        self.assertEqual(pasos[0]["signo"], -1)
        self.assertEqual(pasos[1]["signo"], 1)

    def test_comprobacion_y_cota(self):
        c = self.r["comprobacion"]
        self.assertTrue(c["correcto"])
        self.assertTrue(c["cambio_signo"])
        self.assertEqual(self.r["cota_iteraciones"], 13)
        self.assertEqual(self.r["advertencias"], [])


class OtrosCasosTests(unittest.TestCase):

    def test_raiz_cuadrada_de_2(self):
        r = biseccion("x^2 - 2", 1, 2, 1e-6)
        self.assertAlmostEqual(r["resultado"]["raiz"], math.sqrt(2), places=4)

    def test_funciones_trascendentes(self):
        r = biseccion("cos(x) - x", 0, 1, "1e-8", 100)
        self.assertAlmostEqual(r["resultado"]["raiz"], 0.7390851332, places=6)
        r = biseccion("exp(-x) - x", 0, 1, "1e-8", 100)
        self.assertAlmostEqual(r["resultado"]["raiz"], 0.5671432904, places=6)

    def test_extremos_como_expresiones(self):
        r = biseccion("sin(x)", "pi/2", "3*pi/2", "1e-8", 100)
        self.assertAlmostEqual(r["resultado"]["raiz"], math.pi, places=5)

    def test_raiz_exacta_termina(self):
        r = biseccion("x - 1.5", 1, 2, "1e-9")
        self.assertEqual(r["resultado"]["motivo"], "raiz_exacta")
        self.assertEqual(r["resultado"]["iteraciones"], 1)
        self.assertEqual(r["resultado"]["raiz"], 1.5)
        self.assertEqual(r["pasos"][0]["decision"], "raiz_exacta")
        self.assertTrue(r["comprobacion"]["correcto"])

    def test_raiz_negativa_y_cero_en_el_medio(self):
        r = biseccion("x^3 - x - 2", 1, 2, "1e-6")
        self.assertAlmostEqual(r["resultado"]["raiz"], 1.5213797, places=4)
        r = biseccion("x", -1, 3, "1e-3")  # c = 1, luego 0 exacto
        self.assertEqual(r["resultado"]["raiz"], 0)

    def test_c_cero_no_divide_entre_cero(self):
        r = biseccion("x^3 + 0.001", -1, 1, "1e-3", 60)  # raíz cerca de 0
        self.assertTrue(all(p["error"] is None or math.isfinite(p["error"])
                            for p in r["pasos"]))

    def test_se_agotan_las_iteraciones(self):
        r = biseccion("x^2 - 2", 1, 2, "1e-12", 5)
        self.assertEqual(r["resultado"]["iteraciones"], 5)
        self.assertEqual(r["resultado"]["motivo"], "max_iter")
        self.assertFalse(r["resultado"]["convergio"])
        self.assertFalse(r["comprobacion"]["correcto"])
        self.assertTrue(any("Se agotaron" in a for a in r["advertencias"]))

    def test_discontinuidad_se_advierte(self):
        for funcion, a, b in (("1/x", -1, 2), ("tan(x)", 1, 2)):
            with self.subTest(funcion):
                r = biseccion(funcion, a, b, "1e-4")
                self.assertTrue(any("discontinuidad" in x for x in r["advertencias"]))
                self.assertTrue(r["comprobacion"]["discontinuidad"])
                self.assertFalse(r["comprobacion"]["correcto"])

    def test_cota_teorica(self):
        self.assertEqual(cota_iteraciones(0, 1, 1 / 1024), 10)
        self.assertEqual(cota_iteraciones(0, 1, 5), 1)

    def test_formatear_real(self):
        self.assertEqual(formatear_real(None), "—")
        self.assertEqual(formatear_real(0.0), "0")
        self.assertEqual(formatear_real(-0.0), "0")
        self.assertEqual(formatear_real(0.76397094726), "0.7639709473")
        self.assertEqual(formatear_real(2.0), "2")


class ErroresTests(unittest.TestCase):

    def assertError(self, parte, *args):
        with self.assertRaises(ValueError) as cm:
            biseccion(*args)
        self.assertIn(parte, str(cm.exception))

    def test_sin_cambio_de_signo(self):
        self.assertError("No hay cambio de signo", "x^2 + 1", 0, 2, "1e-3")
        self.assertError("f(a)·f(b) > 0", "x^2 - 1", -2, 2, "1e-3")

    def test_extremo_que_ya_es_raiz(self):
        self.assertError("ya es una raíz", "x^2 - 4", 0, 2, "1e-3")
        self.assertError("f(a) = 0", "x", 0, 1, "1e-3")

    def test_intervalo_invalido(self):
        self.assertError("a debe ser menor que b", "x", 2, 1, "1e-3")
        self.assertError("a debe ser menor que b", "x", 1, 1, "1e-3")

    def test_tolerancia_y_iteraciones(self):
        self.assertError("mayor que cero", "x - 1.5", 1, 2, 0)
        self.assertError("mayor que cero", "x - 1.5", 1, 2, "-1")
        self.assertError("entre 1 y 200", "x - 1.5", 1, 2, "1e-3", 0)
        self.assertError("entre 1 y 200", "x - 1.5", 1, 2, "1e-3", 201)
        self.assertError("entero", "x - 1.5", 1, 2, "1e-3", "dos")
        self.assertError("entero", "x - 1.5", 1, 2, "1e-3", 2.5)

    def test_funcion_invalida(self):
        self.assertError("Escribe una función", "", 1, 2, "1e-3")
        self.assertError("Falta cerrar", "sin(x", 1, 2, "1e-3")
        self.assertError("depender de x", "5", 1, 2, "1e-3")
        self.assertError("No se puede evaluar", "sqrt(x)", -1, 2, "1e-3")

    def test_valores_vacios_o_con_x(self):
        self.assertError("extremo a", "x", "", 2, "1e-3")
        self.assertError("extremo b", "x", 1, "abc", "1e-3")
        self.assertError("tolerancia", "x", 1, 2, "x")


class TextoTests(unittest.TestCase):

    def test_procedimiento_texto(self):
        r = biseccion(POLINOMIO, "0.55", "1.1", "0.0001")
        con = procedimiento_texto(r, incluir_pasos=True)
        sin = procedimiento_texto(r, incluir_pasos=False)
        self.assertIn("MÉTODO DE BISECCIÓN", con)
        self.assertIn("0.7639709473", con)
        self.assertIn("Tabla de iteraciones", con)
        self.assertIn("Iteración 13", con)
        self.assertNotIn("Tabla de iteraciones", sin)
        self.assertIn("Raíz aproximada: x = 0.7639709473", sin)
        self.assertLess(len(sin), len(con))


if __name__ == "__main__":
    unittest.main()
