"""Pruebas del módulo de operaciones vectoriales y matriciales."""

import unittest
from fractions import Fraction

from metodos.vectores_matrices import (
    combinacion_lineal,
    ecuacion_matricial,
    multiplicar_matrices,
    multiplicar_matriz_escalar,
    multiplicar_vector_escalar,
    procedimiento_texto,
    resta_matrices,
    resta_vectores,
    suma_matrices,
    suma_vectores,
)


class OperacionesVectorialesTests(unittest.TestCase):

    def test_suma_resta_y_escalar_con_fracciones(self):
        suma = suma_vectores([
            ["1/2", 2, -1], ["1/2", 3, 4], [1, -1, 2]
        ])
        self.assertEqual(suma["resultado"], [2, 4, 5])

        resta = resta_vectores([3, "5/2"], [1, "1/2"])
        self.assertEqual(resta["resultado"], [2, 2])

        producto = multiplicar_vector_escalar([1, "3/2"], "2/3")
        self.assertEqual(
            producto["resultado"], [Fraction(2, 3), Fraction(1)]
        )

        for resultado in (suma, resta, producto):
            self.assertIn("pasos", resultado)
            self.assertTrue(procedimiento_texto(resultado))

    def test_dimension_vectorial_incompatible(self):
        with self.assertRaisesRegex(ValueError, "misma dimensión"):
            suma_vectores([[1, 2], [1]])

    def test_combinacion_lineal_positiva(self):
        resultado = combinacion_lineal([[1, 0], [0, 1]], [2, 3])
        self.assertTrue(resultado["es_combinacion"])
        self.assertEqual(resultado["tipo_solucion"], "unica")
        self.assertEqual(resultado["escalares"], [2, 3])
        self.assertIn("Sí es combinación lineal", procedimiento_texto(resultado))

    def test_combinacion_lineal_negativa(self):
        resultado = combinacion_lineal([[1, 0]], [0, 1])
        self.assertFalse(resultado["es_combinacion"])
        self.assertEqual(resultado["tipo_solucion"], "incompatible")
        self.assertIsNone(resultado["resultado"])

    def test_combinacion_lineal_con_infinitas_opciones(self):
        resultado = combinacion_lineal([[1, 0], [2, 0]], [3, 0])
        self.assertTrue(resultado["es_combinacion"])
        self.assertEqual(resultado["tipo_solucion"], "infinitas")


class OperacionesMatricialesTests(unittest.TestCase):

    def test_suma_resta_y_escalar(self):
        matriz_a = [[1, 2], [3, 4]]
        matriz_b = [[5, 6], [7, 8]]
        self.assertEqual(
            suma_matrices(matriz_a, matriz_b)["resultado"],
            [[6, 8], [10, 12]],
        )
        self.assertEqual(
            resta_matrices(matriz_b, matriz_a)["resultado"],
            [[4, 4], [4, 4]],
        )
        self.assertEqual(
            multiplicar_matriz_escalar(matriz_a, "1/2")["resultado"],
            [[Fraction(1, 2), 1], [Fraction(3, 2), 2]],
        )

    def test_multiplicacion_matricial_rectangular(self):
        resultado = multiplicar_matrices(
            [[1, 2, 3], [4, 5, 6]],
            [[7, 8], [9, 10], [11, 12]],
        )
        self.assertEqual(resultado["resultado"], [[58, 64], [139, 154]])
        self.assertIn("(1×7)", procedimiento_texto(resultado))

    def test_dimensiones_matriciales_incompatibles(self):
        with self.assertRaisesRegex(ValueError, "mismas dimensiones"):
            suma_matrices([[1, 2]], [[1], [2]])
        with self.assertRaisesRegex(ValueError, "columnas de A"):
            multiplicar_matrices([[1, 2]], [[1, 2]])


class EcuacionMatricialTests(unittest.TestCase):

    def test_solucion_unica_con_b_de_varias_columnas(self):
        resultado = ecuacion_matricial(
            [[2, 0], [0, 4]],
            [[4, 2], [8, 4]],
        )
        self.assertEqual(resultado["tipo_solucion"], "unica")
        self.assertEqual(resultado["resultado"], [[2, 1], [2, 1]])
        self.assertEqual(
            resultado["matriz_aumentada"],
            [[2, 0, 4, 2], [0, 4, 8, 4]],
        )
        self.assertIn("Solución única X", procedimiento_texto(resultado))

    def test_ecuacion_incompatible(self):
        resultado = ecuacion_matricial([[1], [1]], [[1], [2]])
        self.assertEqual(resultado["tipo_solucion"], "incompatible")
        self.assertIsNone(resultado["resultado"])

    def test_ecuacion_con_infinitas_soluciones(self):
        resultado = ecuacion_matricial([[1, 1]], [[2]])
        self.assertEqual(resultado["tipo_solucion"], "infinitas")
        self.assertEqual(resultado["resultado"], [[2], [0]])

    def test_filas_de_a_y_b_deben_coincidir(self):
        with self.assertRaisesRegex(ValueError, "misma cantidad de filas"):
            ecuacion_matricial([[1], [2]], [[1]])


if __name__ == "__main__":
    unittest.main()
