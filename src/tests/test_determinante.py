"""Pruebas del módulo de determinante (cofactores y LU)."""

import unittest
from fractions import Fraction

from metodos.determinante import (
    _multiplicar,
    determinante,
    recomendar_metodo,
)

BATERIA = [
    [[5]],
    [[1, 2], [3, 4]],
    [[2, -1, 3], [0, 4, 1], [5, 2, -2]],
    [[0, 1, 2], [1, 0, 3], [4, -3, 8]],
    [[1, 0, 2, 0], [0, 3, 0, 4], [5, 0, 6, 0], [0, 7, 0, 8]],
    [[0, 2, 1, 3], [1, 1, 0, 2], [3, 0, 1, 1], [2, 5, 4, 0]],
    [["1/2", 2, -1, 3], [4, "3/4", 0, 1], [2, 2, 2, "1/3"], [0, 1, 5, 2]],
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    [[2, 0, 1, 3, 1], [1, 1, 0, 2, 4], [3, 0, 1, 1, 0],
     [2, 5, 4, 0, 1], [0, 1, 1, 1, 2]],
]


class RecomendacionTests(unittest.TestCase):

    def test_pequenas_recomiendan_cofactores(self):
        for n in (1, 2, 3):
            self.assertEqual(recomendar_metodo(n)["recomendado"], "cofactores")

    def test_desde_cuatro_recomienda_lu(self):
        for n in (4, 5, 8):
            self.assertEqual(recomendar_metodo(n)["recomendado"], "lu")

    def test_conteos_estimados(self):
        r = recomendar_metodo(4)
        self.assertEqual(r["cofactores"]["operaciones"], 24)
        self.assertEqual(r["lu"]["operaciones"], 21)

    def test_disponibilidad_por_tamano(self):
        r = recomendar_metodo(7)
        self.assertFalse(r["cofactores_disponible"])
        self.assertTrue(r["lu_disponible"])
        self.assertFalse(recomendar_metodo(9)["lu_disponible"])
        self.assertTrue(recomendar_metodo(6)["cofactores_disponible"])

    def test_n_invalido(self):
        for n in (0, -1, "3", 2.5, True):
            with self.assertRaises(ValueError):
                recomendar_metodo(n)


class DeterminanteTests(unittest.TestCase):

    def test_valores_conocidos(self):
        casos = [
            ([[5]], 5),
            ([[1, 2], [3, 4]], -2),
            ([[2, -1, 3], [0, 4, 1], [5, 2, -2]], -85),
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 0),
        ]
        for matriz, esperado in casos:
            for metodo in ("cofactores", "lu"):
                with self.subTest(matriz=matriz, metodo=metodo):
                    r = determinante(matriz, metodo)
                    self.assertEqual(r["resultado"], esperado)
                    self.assertEqual(r["singular"], esperado == 0)

    def test_ambos_metodos_coinciden(self):
        for matriz in BATERIA:
            with self.subTest(matriz=matriz):
                a = determinante(matriz, "cofactores")
                b = determinante(matriz, "lu")
                self.assertEqual(a["resultado"], b["resultado"])
                self.assertTrue(a["comprobacion"]["correcto"])
                self.assertTrue(b["comprobacion"]["correcto"])

    def test_fracciones_exactas(self):
        r = determinante([["1/2", 0], [0, "1/3"]], "lu")
        self.assertEqual(r["resultado"], Fraction(1, 6))

    def test_lu_con_intercambio_de_filas(self):
        r = determinante([[0, 1, 2], [1, 0, 3], [4, -3, 8]], "lu")
        self.assertGreaterEqual(r["intercambios"], 1)
        self.assertEqual(r["resultado"], -2)

    def test_lu_cumple_pa_igual_lu(self):
        for matriz in BATERIA:
            r = determinante(matriz, "lu")
            a = [[Fraction(v) for v in fila] for fila in matriz]
            self.assertEqual(_multiplicar(r["P"], a), _multiplicar(r["L"], r["U"]))

    def test_lu_singular_sigue_cumpliendo_pa_igual_lu(self):
        matriz = [[1, 2, 3], [2, 4, 6], [1, 1, 1]]
        r = determinante(matriz, "lu")
        self.assertEqual(r["resultado"], 0)
        self.assertTrue(r["singular"])
        a = [[Fraction(v) for v in fila] for fila in matriz]
        self.assertEqual(_multiplicar(r["P"], a), _multiplicar(r["L"], r["U"]))

    def test_matriz_identidad_y_cero(self):
        self.assertEqual(determinante([[1, 0], [0, 1]], "lu")["resultado"], 1)
        self.assertEqual(determinante([[0, 0], [0, 0]], "cofactores")["resultado"], 0)

    def test_n_8_con_lu_usa_pa_igual_lu(self):
        n = 8
        matriz = [[(i * j + i + 2 * j) % 7 + (3 if i == j else 0)
                   for j in range(n)] for i in range(n)]
        r = determinante(matriz, "lu")
        self.assertEqual(r["comprobacion"]["metodo"], "P·A = L·U")
        self.assertTrue(r["comprobacion"]["correcto"])


class CofactoresOpcionesTests(unittest.TestCase):

    def test_expansion_por_defecto_es_la_de_mas_ceros(self):
        r = determinante([[1, 2, 3], [0, 0, 5], [4, 6, 7]], "cofactores")
        self.assertEqual(r["expansion"], {
            "tipo": "fila", "indice": 2,
            "motivo": "Se expande por la fila 2 (2 ceros).",
        })

    def test_expansion_elegida_por_el_usuario(self):
        matriz = [[2, -1, 3], [0, 4, 1], [5, 2, -2]]
        for tipo in ("fila", "columna"):
            for indice in (1, 2, 3):
                with self.subTest(tipo=tipo, indice=indice):
                    r = determinante(matriz, "cofactores",
                                     tipo_expansion=tipo, indice_expansion=indice)
                    self.assertEqual(r["resultado"], -85)
                    self.assertEqual(r["expansion"]["indice"], indice)

    def test_terminos_con_cero_se_omiten(self):
        r = determinante([[1, 0, 2], [0, 0, 5], [4, 6, 7]], "cofactores",
                         tipo_expansion="fila", indice_expansion=1)
        terminos = r["pasos"][0]["terminos"]
        self.assertTrue(terminos[1]["omitido"])
        self.assertFalse(terminos[0]["omitido"])

    def test_expansion_invalida(self):
        m = [[1, 2], [3, 4]]
        for tipo, idx in [("diagonal", 1), ("fila", 0), ("fila", 3), ("fila", None)]:
            with self.subTest(tipo=tipo, idx=idx):
                with self.assertRaises(ValueError):
                    determinante(m, "cofactores", tipo_expansion=tipo,
                                 indice_expansion=idx)

    def test_expansion_con_lu_es_error(self):
        with self.assertRaises(ValueError):
            determinante([[1, 2], [3, 4]], "lu", tipo_expansion="fila",
                         indice_expansion=1)


class EficienciaTests(unittest.TestCase):

    def test_lu_hace_menos_multiplicaciones_desde_n_5(self):
        matriz = [[(i + 1) * (j + 2) % 11 + (i == j) * 5 + 1
                   for j in range(6)] for i in range(6)]
        for n in (5, 6):
            sub = [fila[:n] for fila in matriz[:n]]
            c = determinante(sub, "cofactores")["multiplicaciones"]
            l = determinante(sub, "lu")["multiplicaciones"]
            self.assertLess(l, c)

    def test_conteo_cofactores_3x3_denso(self):
        r = determinante([[1, 2, 3], [4, 5, 6], [7, 8, 10]], "cofactores")
        self.assertEqual(r["multiplicaciones"], 9)

    def test_ceros_reducen_cofactores(self):
        denso = determinante([[1, 2, 3], [4, 5, 6], [7, 8, 10]], "cofactores")
        ralo = determinante([[1, 0, 0], [4, 5, 6], [7, 8, 10]], "cofactores")
        self.assertLess(ralo["multiplicaciones"], denso["multiplicaciones"])


class ErroresTests(unittest.TestCase):

    def test_no_cuadrada(self):
        with self.assertRaisesRegex(ValueError, "cuadradas"):
            determinante([[1, 2, 3], [4, 5, 6]])

    def test_vacia_o_irregular(self):
        for m in ([], [[]], [[1, 2], [3]]):
            with self.subTest(m=m):
                with self.assertRaises(ValueError):
                    determinante(m)

    def test_valor_invalido(self):
        with self.assertRaises(ValueError):
            determinante([["a", 1], [2, 3]])

    def test_metodo_desconocido(self):
        with self.assertRaisesRegex(ValueError, "Método desconocido"):
            determinante([[1]], "sarrus")

    def test_cofactores_excede_n_6(self):
        m = [[int(i == j) for j in range(7)] for i in range(7)]
        with self.assertRaisesRegex(ValueError, "LU"):
            determinante(m, "cofactores")
        self.assertEqual(determinante(m, "lu")["resultado"], 1)

    def test_lu_excede_n_8(self):
        m = [[int(i == j) for j in range(9)] for i in range(9)]
        with self.assertRaisesRegex(ValueError, "máximo"):
            determinante(m, "lu")


if __name__ == "__main__":
    unittest.main()
