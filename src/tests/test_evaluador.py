"""Pruebas del evaluador de funciones f(x) escrito a mano."""

import math
import unittest

from metodos.evaluador import compilar, evaluar_numero


def valor(texto, x=0.0):
    return compilar(texto)(x)


class EvaluadorTests(unittest.TestCase):

    def test_aritmetica_y_precedencia(self):
        self.assertEqual(valor("2 + 3 * 4"), 14)
        self.assertEqual(valor("(2 + 3) * 4"), 20)
        self.assertEqual(valor("10 - 4 - 3"), 3)
        self.assertEqual(valor("2 ^ 3 ^ 2"), 512)        # derecha a izquierda
        self.assertEqual(valor("-2 ^ 2"), -4)             # -(2^2)
        self.assertEqual(valor("2 ^ -1"), 0.5)
        self.assertEqual(valor("2 ** 3"), 8)
        self.assertEqual(valor("8 / 4 / 2"), 1)

    def test_variable_y_polinomio(self):
        f = compilar("x^4 - 5x^3 + 0.5x^2 - 11x + 10")
        self.assertAlmostEqual(f(0.55), 3.36088125)
        self.assertAlmostEqual(f(1.1), -6.6859)
        self.assertTrue(f.usa_x)

    def test_multiplicacion_implicita(self):
        self.assertEqual(valor("2x", 3), 6)
        self.assertEqual(valor("3(x+1)", 1), 6)
        self.assertEqual(valor("(x+1)(x-1)", 3), 8)
        self.assertEqual(valor("2x^2", 3), 18)
        self.assertAlmostEqual(valor("2pi"), 2 * math.pi)
        self.assertAlmostEqual(valor("xe", 2), 2 * math.e)
        self.assertAlmostEqual(valor("3sin(x)", math.pi / 2), 3)

    def test_funciones_y_constantes(self):
        self.assertAlmostEqual(valor("sin(pi/2)"), 1)
        self.assertAlmostEqual(valor("sen(pi/2)"), 1)
        self.assertAlmostEqual(valor("cos(0)"), 1)
        self.assertAlmostEqual(valor("exp(1)"), math.e)
        self.assertAlmostEqual(valor("e^x", 2), math.e ** 2)
        self.assertAlmostEqual(valor("ln(e)"), 1)
        self.assertAlmostEqual(valor("log(1000)"), 3)
        self.assertAlmostEqual(valor("sqrt(16)"), 4)
        self.assertAlmostEqual(valor("cbrt(-27)"), -3)
        self.assertEqual(valor("abs(x)", -5), 5)
        self.assertAlmostEqual(valor("exp(-x) - x", 0.5671432904),
                               0, places=6)

    def test_mayusculas_y_simbolos_de_teclado(self):
        self.assertEqual(valor("X^2 + 1", 2), 5)
        self.assertEqual(valor("SIN(0)"), 0)
        self.assertEqual(valor("x² − 1", 3), 8)
        self.assertEqual(valor("2×3÷6"), 1)
        self.assertEqual(valor("0,5 * 4"), 2)
        self.assertAlmostEqual(valor("π"), math.pi)

    def test_notacion_cientifica(self):
        self.assertEqual(valor("1e-4"), 0.0001)
        self.assertEqual(valor("2E3"), 2000)
        self.assertAlmostEqual(valor("2e - 3"), 2 * math.e - 3)

    def test_errores_de_sintaxis(self):
        casos = {
            "": "Escribe una función",
            "   ": "Escribe una función",
            "2 +": "incompleta",
            "(x + 1": "Falta cerrar",
            "x + 1)": "de más",
            "()": "vacío",
            "* 3": "Falta un valor",
            "2 3": "Falta un operador",
            "sin x": "necesita paréntesis",
            "foo(x)": "No reconozco",
            "x $ 2": "No entiendo",
            "x +* 2": "Falta un valor",
        }
        for texto, parte in casos.items():
            with self.subTest(texto):
                with self.assertRaises(ValueError) as cm:
                    compilar(texto)
                self.assertIn(parte, str(cm.exception))

    def test_limites_de_tamano(self):
        with self.assertRaises(ValueError):
            compilar("x+" * 150 + "x")
        with self.assertRaises(ValueError):
            compilar("(" * 100 + "x" + ")" * 100)

    def test_errores_de_evaluacion(self):
        for texto, x in (("1/x", 0), ("sqrt(x)", -1), ("ln(x)", 0),
                         ("exp(x)", 1000), ("x^0.5", -4), ("0^x", -1),
                         ("tan(x)^1000", 1.5)):
            with self.subTest(texto):
                with self.assertRaises(ValueError) as cm:
                    compilar(texto)(x)
                self.assertIn("No se puede evaluar f(x)", str(cm.exception))

    def test_no_ejecuta_codigo(self):
        for texto in ("__import__('os').system('echo hola')", "open('x')",
                      "x.__class__", "1; 2"):
            with self.subTest(texto):
                with self.assertRaises(ValueError):
                    compilar(texto)

    def test_evaluar_numero(self):
        self.assertEqual(evaluar_numero("0.55"), 0.55)
        self.assertEqual(evaluar_numero(3), 3.0)
        self.assertAlmostEqual(evaluar_numero("pi/2"), math.pi / 2)
        self.assertEqual(evaluar_numero("1e-4"), 0.0001)
        for malo in ("", "  ", "x + 1", "abc", None, True, float("inf")):
            with self.subTest(malo):
                with self.assertRaises(ValueError):
                    evaluar_numero(malo, "El valor")


if __name__ == "__main__":
    unittest.main()
