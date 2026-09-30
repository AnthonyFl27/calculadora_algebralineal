"""Pruebas del catálogo de ejercicios: cada uno debe coincidir con lo que
calcula metodos/ (así un ejercicio nunca promete un resultado falso)."""

import unittest
from fractions import Fraction

from metodos import ejercicios
from metodos.conversion import resolver as resolver_conversion
from metodos.gauss_jordan import resolver as resolver_gauss_jordan
from metodos.pivote import resolver as resolver_pivote
from metodos.vectores_matrices import (
    combinacion_lineal,
    ecuacion_matricial,
    matriz_inversa,
    multiplicar_matrices,
    multiplicar_matriz_escalar,
    multiplicar_vector_escalar,
    resta_matrices,
    resta_vectores,
    suma_matrices,
    suma_vectores,
)

CAMPOS = {"id", "titulo", "dificultad", "descripcion", "datos",
          "resultado_esperado"}
DIFICULTADES = {"básico", "intermedio", "avanzado"}


def a_texto(valor):
    """Normaliza resultados (Fraction, listas anidadas) a texto."""

    if isinstance(valor, (list, tuple)):
        return [a_texto(v) for v in valor]
    if isinstance(valor, Fraction) and valor.denominator == 1:
        return str(valor.numerator)
    return str(valor)


def calcular_operacion(ejercicio):
    datos = ejercicio["datos"]
    categoria = ejercicio["categoria"]
    operacion = ejercicio["operacion"]

    if categoria == "vectores":
        vectores = datos["vectores"]
        if operacion == "Suma":
            return suma_vectores(vectores)
        if operacion == "Resta":
            return resta_vectores(vectores[0], vectores[1])
        if operacion == "Vector por escalar":
            return multiplicar_vector_escalar(vectores[0], datos["escalar"])
        return combinacion_lineal(vectores, datos["objetivo"])

    if categoria == "matrices":
        a = datos["matriz_a"]
        if operacion == "Matriz por escalar":
            return multiplicar_matriz_escalar(a, datos["escalar"])
        funcion = {
            "Suma": suma_matrices,
            "Resta": resta_matrices,
            "Multiplicación A × B": multiplicar_matrices,
        }[operacion]
        return funcion(a, datos["matriz_b"])

    if categoria == "ecuacion-matricial":
        return ecuacion_matricial(datos["matriz_a"], datos["matriz_b"])

    return matriz_inversa(datos["matriz"])


class CatalogoTests(unittest.TestCase):

    def test_metodos_y_estructura(self):
        self.assertEqual(
            [clave for clave, _ in ejercicios.METODOS_EJERCICIOS],
            list(ejercicios.EJERCICIOS),
        )

        for clave, lista in ejercicios.EJERCICIOS.items():
            for ejercicio in lista:
                with self.subTest(ejercicio["id"]):
                    self.assertTrue(CAMPOS <= set(ejercicio))
                    self.assertIn(ejercicio["dificultad"], DIFICULTADES)

    def test_ids_unicos(self):
        ids = [e["id"] for lista in ejercicios.EJERCICIOS.values() for e in lista]
        self.assertEqual(len(ids), len(set(ids)))

    def test_contenido_minimo(self):
        catalogo = ejercicios.EJERCICIOS

        for clave in ("gauss-jordan", "pivoteo", "conversion"):
            self.assertGreaterEqual(len(catalogo[clave]), 5, clave)

        for clave in ("gauss-jordan", "pivoteo"):
            tipos = {e["resultado_esperado"]["tipo"] for e in catalogo[clave]}
            self.assertEqual(tipos, {"unica", "infinitas", "incompatible"})

        operaciones = {
            (e["categoria"], e["operacion"]) for e in catalogo["vectores-matrices"]
        }
        esperadas = {
            ("vectores", "Suma"), ("vectores", "Resta"),
            ("vectores", "Vector por escalar"),
            ("vectores", "Combinación lineal"),
            ("matrices", "Suma"), ("matrices", "Resta"),
            ("matrices", "Matriz por escalar"),
            ("matrices", "Multiplicación A × B"),
            ("ecuacion-matricial", None), ("inversa", None),
        }
        self.assertEqual(operaciones, esperadas)

    def test_sistemas_coinciden_con_el_motor(self):
        for clave, resolver in (("gauss-jordan", resolver_gauss_jordan),
                                ("pivoteo", resolver_pivote)):
            for ejercicio in ejercicios.EJERCICIOS[clave]:
                with self.subTest(ejercicio["id"]):
                    matriz = [[float(x) for x in fila]
                              for fila in ejercicio["datos"]["matriz"]]
                    resultado = resolver(matriz, "fraccion")
                    self.assertEqual(
                        resultado["tipo"],
                        ejercicio["resultado_esperado"]["tipo"],
                    )

    def test_conversiones_coinciden_con_el_motor(self):
        for ejercicio in ejercicios.EJERCICIOS["conversion"]:
            with self.subTest(ejercicio["id"]):
                datos = ejercicio["datos"]
                resultado = resolver_conversion(
                    datos["numero"], datos["base_entrada"], datos["base_salida"]
                )
                self.assertEqual(
                    resultado["resultado"],
                    ejercicio["resultado_esperado"]["resultado"],
                )

    def test_vectores_y_matrices_coinciden_con_el_motor(self):
        for ejercicio in ejercicios.EJERCICIOS["vectores-matrices"]:
            with self.subTest(ejercicio["id"]):
                resultado = calcular_operacion(ejercicio)
                for clave, esperado in ejercicio["resultado_esperado"].items():
                    self.assertEqual(a_texto(resultado[clave]), a_texto(esperado)
                                     if not isinstance(esperado, bool) else
                                     str(esperado), clave)

    def test_vista_previa_para_todos_los_ejercicios(self):
        for clave, lista in ejercicios.catalogo().items():
            for ejercicio in lista:
                with self.subTest(ejercicio["id"]):
                    self.assertTrue(ejercicio["vista_previa"].strip())

    def test_vista_previa_ejemplos(self):
        catalogo = ejercicios.catalogo()
        self.assertEqual(catalogo["gauss-jordan"][0]["vista_previa"],
                         " 2   1 │  5\n 1  -1 │  1")
        self.assertEqual(catalogo["conversion"][0]["vista_previa"],
                         "25  (decimal → binario)")
        self.assertEqual(
            catalogo["vectores-matrices"][0]["vista_previa"],
            "Suma\nv1 = (1, 2, 3)\nv2 = (4, 5, 6)",
        )

    def test_catalogo_devuelve_copia(self):
        copia = ejercicios.catalogo()
        copia["gauss-jordan"][0]["titulo"] = "otro"
        self.assertNotEqual(
            ejercicios.EJERCICIOS["gauss-jordan"][0]["titulo"], "otro"
        )


if __name__ == "__main__":
    unittest.main()
