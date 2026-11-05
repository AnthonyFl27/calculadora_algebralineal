"""Pruebas de las escenas geométricas (spec 014)."""

import json
import unittest
from fractions import Fraction as F

from metodos import escena as E
from metodos import vectores_matrices as vm
from metodos.determinante import determinante
from metodos.escenas import (
    escena_determinante,
    escena_inversa,
    escena_producto,
    escena_sistema,
    escena_vectores,
)
from metodos.gauss_jordan import resolver as gauss
from metodos.pivote import resolver as pivote


def matriz(filas):
    return [[F(x) for x in fila] for fila in filas]


def escena(filas, resolver=gauss, modo="fraccion"):
    return escena_sistema(resolver(matriz(filas), modo), modo)


def elementos(esc, tipo):
    return [e for e in esc["elementos"] if e["tipo"] == tipo]


class AyudasTests(unittest.TestCase):

    def test_ecuacion_texto(self):
        n = ("x1", "x2", "x3")
        self.assertEqual(E.ecuacion_texto([1, 1], 3, n), "x1 + x2 = 3")
        self.assertEqual(E.ecuacion_texto([2, -1], 0, n), "2x1 - x2 = 0")
        self.assertEqual(E.ecuacion_texto([-1, F(1, 2)], F(-3, 4), n),
                         "-x1 + 1/2x2 = -3/4")
        self.assertEqual(E.ecuacion_texto([0, -1], 5, n), "-x1 = 5".replace("x1", "x2"))
        self.assertEqual(E.ecuacion_texto([F(1, 2), 1], 1, n, "decimal"),
                         "0.5x1 + x2 = 1")

    def test_ventana_contiene_puntos_y_origen(self):
        v = E.ventana_2d([[3, 4], [-1, 2]])
        self.assertLess(v["x"][0], -1)
        self.assertGreater(v["x"][1], 3)
        self.assertLess(v["y"][0], 0)
        self.assertGreater(v["y"][1], 4)

    def test_ventana_minima_si_todo_es_el_origen(self):
        v = E.ventana_2d([[0, 0]])
        self.assertEqual(v, {"x": [-1.0, 1.0], "y": [-1.0, 1.0]})

    def test_caja_3d_es_un_cubo(self):
        c = E.caja_3d([[1, 2, 3], [-2, 0, 9]])
        lados = {round(r[1] - r[0], 9) for r in c.values()}
        self.assertEqual(len(lados), 1)
        for eje, valor in zip("xyz", ([1, -2], [2, 0], [3, 9])):
            for v in valor:
                self.assertTrue(c[eje][0] <= v <= c[eje][1])

    def test_recortar_recta(self):
        v = {"x": [-2, 2], "y": [-2, 2]}
        a, b = E.recortar_recta_2d([0, 0], [1, 0], v)
        self.assertEqual((a, b), ([-2, 0], [2, 0]))
        self.assertIsNone(E.recortar_recta_2d([0, 5], [1, 0], v))
        a, b = E.recortar_recta_2d([0, 0], [1, 1], v)
        self.assertAlmostEqual(a[0], -2)
        self.assertAlmostEqual(b[1], 2)

    def test_numero_enorme_da_error_claro(self):
        with self.assertRaises(ValueError):
            E.a_float(F(10) ** 400)


class SistemaDosIncognitasTests(unittest.TestCase):

    def test_solucion_unica(self):
        esc = escena([[1, 1, 3], [1, -1, 1]])
        self.assertTrue(esc["disponible"])
        self.assertEqual(esc["dim"], 2)
        self.assertEqual(len(elementos(esc, "recta")), 2)
        p = elementos(esc, "punto")
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0]["p"], [2.0, 1.0])
        self.assertEqual(p[0]["serie"], "solucion")
        self.assertEqual(p[0]["etiqueta"], "(2, 1)")
        self.assertEqual(esc["avisos"], [])
        # La ventana deja ver la solución y el origen.
        v = esc["ventana"]
        self.assertTrue(v["x"][0] < 0 < v["x"][1] and v["x"][0] < 2 < v["x"][1])
        self.assertTrue(v["y"][0] < 0 < v["y"][1] and v["y"][0] < 1 < v["y"][1])

    def test_rectas_son_correctas(self):
        esc = escena([[1, 1, 3], [1, -1, 1]])
        for r, (a, b, c) in zip(elementos(esc, "recta"), ((1, 1, 3), (1, -1, 1))):
            x, y = r["p"]
            self.assertAlmostEqual(a * x + b * y, c)          # p está en la recta
            dx, dy = r["d"]
            self.assertAlmostEqual(a * dx + b * dy, 0)         # d es su dirección
            self.assertAlmostEqual(dx * dx + dy * dy, 1)

    def test_pivoteo_da_la_misma_escena(self):
        a = escena([[2, 1, 4], [1, 3, 5]], gauss)
        b = escena([[2, 1, 4], [1, 3, 5]], pivote)
        self.assertEqual(a["elementos"], b["elementos"])
        self.assertEqual(a["ventana"], b["ventana"])

    def test_paralelas_sin_solucion(self):
        esc = escena([[1, 1, 3], [2, 2, 5]])
        self.assertEqual(len(elementos(esc, "recta")), 2)
        self.assertEqual(elementos(esc, "punto"), [])
        self.assertIn("paralelas", esc["avisos"][0])

    def test_infinitas_resalta_la_recta_comun(self):
        esc = escena([[1, 1, 3], [2, 2, 6]])
        rectas = elementos(esc, "recta")
        self.assertEqual(len(rectas), 3)                 # 2 ecuaciones + la solución
        self.assertEqual(rectas[-1]["serie"], "solucion")
        self.assertEqual(rectas[-1]["grosor"], "fuerte")
        self.assertIn("misma recta", esc["avisos"][0])

    def test_tres_rectas_sin_punto_comun(self):
        esc = escena([[1, 0, 1], [0, 1, 1], [1, 1, 5]])
        self.assertEqual(len(elementos(esc, "recta")), 3)
        self.assertEqual(elementos(esc, "punto"), [])
        self.assertIn("no se cruzan todas", esc["avisos"][0])

    def test_sobredeterminado_con_solucion(self):
        esc = escena([[1, 0, 1], [0, 1, 2], [1, 1, 3]])
        self.assertEqual(elementos(esc, "punto")[0]["p"], [1.0, 2.0])

    def test_ecuacion_degenerada_se_explica(self):
        esc = escena([[1, 1, 3], [0, 0, 4]])
        self.assertEqual(len(elementos(esc, "recta")), 1)
        self.assertIn("0 = 4", esc["avisos"][0])

    def test_fracciones_y_decimales(self):
        esc = escena([[2, 1, 1], [1, 3, 1]], modo="fraccion")
        self.assertEqual(elementos(esc, "punto")[0]["etiqueta"], "(2/5, 1/5)")
        esc = escena([[2, 1, 1], [1, 3, 1]], modo="decimal")
        self.assertEqual(elementos(esc, "punto")[0]["etiqueta"], "(0.4, 0.2)")

    def test_serializable_sin_nan_ni_infinito(self):
        for filas in ([[1, 1, 3], [1, -1, 1]], [[1, 1, 3], [2, 2, 5]],
                      [[1, 1, 3], [2, 2, 6]], [[1, 0, 10**12], [0, 1, 1]]):
            with self.subTest(filas):
                json.dumps(escena(filas), allow_nan=False)

    def test_leyenda_tiene_una_entrada_por_recta_y_la_solucion(self):
        esc = escena([[1, 1, 3], [1, -1, 1]])
        textos = [l["texto"] for l in esc["leyenda"]]
        self.assertEqual(textos, ["(1) x1 + x2 = 3", "(2) x1 - x2 = 1",
                                  "Solución (2, 1)"])

    def test_mas_de_tres_incognitas_no_se_grafica(self):
        esc = escena([[1, 0, 0, 0, 1], [0, 1, 0, 0, 2],
                      [0, 0, 1, 0, 3], [0, 0, 0, 1, 4]])
        self.assertFalse(esc["disponible"])
        self.assertIn("2 o 3", esc["motivo"])

    def test_una_incognita_no_se_grafica(self):
        self.assertFalse(escena([[2, 4]])["disponible"])


CAJA = {"x": [-1, 1], "y": [-1, 1], "z": [-1, 1]}


class Geometria3DTests(unittest.TestCase):

    def test_plano_horizontal_da_un_cuadrado(self):
        poli = E.recortar_plano_caja([0, 0, 1], 0, CAJA)
        self.assertEqual(len(poli), 4)
        self.assertTrue(all(abs(p[2]) < 1e-12 for p in poli))

    def test_plano_diagonal_da_un_hexagono(self):
        poli = E.recortar_plano_caja([1, 1, 1], 0, CAJA)
        self.assertEqual(len(poli), 6)
        for p in poli:
            self.assertAlmostEqual(sum(p), 0)
            self.assertTrue(all(-1 - 1e-9 <= c <= 1 + 1e-9 for c in p))

    def test_poligono_ordenado_alrededor(self):
        # Un cuadrado ordenado no se cruza: lados consecutivos miden 2.
        poli = E.recortar_plano_caja([0, 1, 0], 0.5, CAJA)
        lados = [((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5
                 for a, b in zip(poli, poli[1:] + poli[:1])]
        self.assertTrue(all(abs(l - 2) < 1e-9 for l in lados))

    def test_plano_fuera_de_la_caja(self):
        self.assertEqual(E.recortar_plano_caja([0, 0, 1], 5, CAJA), [])

    def test_plano_que_toca_una_cara_o_un_vertice(self):
        self.assertEqual(len(E.recortar_plano_caja([0, 0, 1], 1, CAJA)), 4)
        self.assertEqual(E.recortar_plano_caja([1, 1, 1], 3, CAJA), [])  # solo un vértice

    def test_recta_en_la_caja(self):
        a, b = E.recortar_recta_caja([0, 0, 0], [1, 0, 0], CAJA)
        self.assertEqual((a, b), ([-1, 0, 0], [1, 0, 0]))
        self.assertIsNone(E.recortar_recta_caja([0, 5, 0], [1, 0, 0], CAJA))
        a, b = E.recortar_recta_caja([0, 0, 0], [1, 1, 1], CAJA)
        self.assertEqual((a, b), ([-1, -1, -1], [1, 1, 1]))


class SistemaTresIncognitasTests(unittest.TestCase):

    def test_solucion_unica(self):
        esc = escena([[1, 1, 1, 6], [0, 1, 1, 5], [1, 0, 1, 4]])
        self.assertEqual(esc["dim"], 3)
        self.assertEqual(len(elementos(esc, "poligono")), 3)
        p = elementos(esc, "punto")[0]
        self.assertEqual(p["p"], [1.0, 2.0, 3.0])
        self.assertEqual(p["etiqueta"], "(1, 2, 3)")
        # La solución está dentro de la caja y sobre los tres planos.
        for eje, valor in zip("xyz", p["p"]):
            self.assertTrue(esc["caja"][eje][0] < valor < esc["caja"][eje][1])
        for poli, (a, b, c, d) in zip(elementos(esc, "poligono"),
                                      ([1, 1, 1, 6], [0, 1, 1, 5], [1, 0, 1, 4])):
            for x, y, z in poli["puntos"]:
                self.assertAlmostEqual(a * x + b * y + c * z, d)
        self.assertEqual(esc["camara"], E.camara_inicial())
        self.assertEqual(esc["avisos"], [])

    def test_la_caja_es_un_cubo_con_el_origen(self):
        esc = escena([[1, 0, 0, 10], [0, 1, 0, 1], [0, 0, 1, 1]])
        lados = {round(r[1] - r[0], 9) for r in esc["caja"].values()}
        self.assertEqual(len(lados), 1)
        for eje in "xyz":
            self.assertTrue(esc["caja"][eje][0] < 0 < esc["caja"][eje][1])

    def test_infinitas_con_recta_de_corte(self):
        esc = escena([[1, 1, 1, 6], [2, 2, 2, 12], [1, 0, 1, 4]])
        seg = [e for e in elementos(esc, "segmento") if e["serie"] == "solucion"]
        self.assertEqual(len(seg), 1)
        # Los extremos cumplen las ecuaciones independientes.
        for x, y, z in (seg[0]["a"], seg[0]["b"]):
            self.assertAlmostEqual(x + y + z, 6)
            self.assertAlmostEqual(x + z, 4)
        self.assertIn("recta", esc["avisos"][0])

    def test_infinitas_con_un_solo_plano(self):
        esc = escena([[1, 1, 1, 6], [2, 2, 2, 12], [3, 3, 3, 18]])
        solucion = [e for e in elementos(esc, "poligono") if e["serie"] == "solucion"]
        self.assertEqual(len(solucion), 1)
        self.assertIn("mismo plano", esc["avisos"][0])

    def test_planos_paralelos(self):
        esc = escena([[1, 1, 1, 6], [1, 1, 1, 7]])
        self.assertEqual(len(elementos(esc, "poligono")), 2)
        self.assertEqual(elementos(esc, "punto"), [])
        self.assertIn("paralelos", esc["avisos"][0])

    def test_prisma_sin_punto_comun_muestra_las_rectas_de_corte(self):
        esc = escena([[1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 5]])
        cortes = [e for e in elementos(esc, "segmento") if e["serie"] == 5]
        self.assertEqual(len(cortes), 3)
        self.assertTrue(all(c["guion"] for c in cortes))
        self.assertIn("ningún punto en común", esc["avisos"][0])

    def test_pivoteo_da_la_misma_escena(self):
        filas = [[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]]
        self.assertEqual(escena(filas, gauss)["elementos"],
                         escena(filas, pivote)["elementos"])

    def test_serializable_sin_nan_ni_infinito(self):
        for filas in ([[1, 1, 1, 6], [0, 1, 1, 5], [1, 0, 1, 4]],
                      [[1, 1, 1, 6], [2, 2, 2, 12], [1, 0, 1, 4]],
                      [[1, 1, 1, 6], [1, 1, 1, 7]],
                      [[1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 5]]):
            with self.subTest(filas):
                json.dumps(escena(filas), allow_nan=False)

    def test_leyenda(self):
        esc = escena([[1, 1, 1, 6], [0, 1, 1, 5], [1, 0, 1, 4]])
        self.assertEqual([l["texto"] for l in esc["leyenda"]],
                         ["(1) x1 + x2 + x3 = 6", "(2) x2 + x3 = 5",
                          "(3) x1 + x3 = 4", "Solución (1, 2, 3)"])


def V(*valores):
    return [F(x) for x in valores]


def flechas(esc, serie=None):
    return [e for e in esc["elementos"]
            if e["tipo"] == "flecha" and (serie is None or e["serie"] == serie)]


class VectoresTests(unittest.TestCase):

    def test_suma_2d_con_paralelogramo(self):
        esc = escena_vectores(vm.suma_vectores([V(1, 2), V(3, 4)]))
        self.assertEqual(esc["dim"], 2)
        poligono = elementos(esc, "poligono")
        self.assertEqual(len(poligono), 1)
        self.assertEqual(poligono[0]["puntos"], [[0, 0], [1, 2], [4, 6], [3, 4]])
        resultado = flechas(esc, "solucion")[0]
        self.assertEqual((resultado["a"], resultado["b"]), ([0, 0], [4, 6]))
        # copia punta con cola de v2 desde la punta de v1
        copia = [f for f in flechas(esc) if f["guion"]][0]
        self.assertEqual((copia["a"], copia["b"]), ([1, 2], [4, 6]))

    def test_suma_de_tres_vectores_encadena_las_flechas(self):
        esc = escena_vectores(vm.suma_vectores([V(1, 0), V(0, 1), V(2, 2)]))
        copias = [f for f in flechas(esc) if f["guion"]]
        self.assertEqual([(c["a"], c["b"]) for c in copias],
                         [([1, 0], [1, 1]), ([1, 1], [3, 3])])
        self.assertEqual(elementos(esc, "poligono"), [])      # solo con 2 vectores
        self.assertEqual(flechas(esc, "solucion")[0]["b"], [3, 3])

    def test_suma_3d(self):
        esc = escena_vectores(vm.suma_vectores([V(1, 2, 0), V(3, 4, 1)]))
        self.assertEqual(esc["dim"], 3)
        self.assertEqual(esc["ejes"], ["x", "y", "z"])
        self.assertEqual(flechas(esc, "solucion")[0]["b"], [4, 6, 1])
        self.assertEqual(len(elementos(esc, "poligono")[0]["puntos"]), 4)
        for eje, valor in zip("xyz", (4, 6, 1)):
            self.assertTrue(esc["caja"][eje][0] < valor < esc["caja"][eje][1])

    def test_resta(self):
        esc = escena_vectores(vm.resta_vectores(V(5, 1), V(2, 3)))
        resultado = flechas(esc, "solucion")
        self.assertEqual(resultado[0]["b"], [3, -2])                 # desde el origen
        self.assertEqual((resultado[1]["a"], resultado[1]["b"]),     # de la punta de b a la de a
                         ([2, 3], [5, 1]))
        self.assertTrue(resultado[1]["guion"])
        self.assertEqual([l["texto"] for l in esc["leyenda"]],
                         ["a = (5, 1)", "b = (2, 3)", "a - b = (3, -2)"])

    def test_vector_por_escalar(self):
        esc = escena_vectores(vm.multiplicar_vector_escalar(V(1, 2), "3/2"))
        self.assertEqual(flechas(esc, "solucion")[0]["b"], [1.5, 3.0])
        self.assertIn("alarga", esc["avisos"][0])
        self.assertEqual(esc["leyenda"][1]["texto"], "3/2·v = (3/2, 3)")
        for k, palabra in (("-2", "sentido"), ("1/2", "acorta"), ("0", "cero")):
            esc = escena_vectores(vm.multiplicar_vector_escalar(V(1, 2), k))
            self.assertIn(palabra, esc["avisos"][0])
        self.assertEqual(len(elementos(escena_vectores(
            vm.multiplicar_vector_escalar(V(1, 2), "0")), "punto")), 1)

    def test_combinacion_lineal(self):
        esc = escena_vectores(vm.combinacion_lineal([V(1, 0), V(0, 1)], V(3, 2)))
        cadena = [f for f in flechas(esc) if f["guion"]]
        self.assertEqual([(c["a"], c["b"]) for c in cadena],
                         [([0, 0], [3, 0]), ([3, 0], [3, 2])])
        self.assertEqual(flechas(esc, "solucion")[0]["b"], [3, 2])
        self.assertIn("b = 3·v1 + 2·v2", esc["avisos"][0])

    def test_combinacion_con_infinitas_formas(self):
        esc = escena_vectores(vm.combinacion_lineal([V(1, 2), V(2, 4)], V(3, 6)))
        self.assertIn("infinitas", esc["avisos"][1])

    def test_combinacion_imposible(self):
        esc = escena_vectores(vm.combinacion_lineal([V(1, 2), V(2, 4)], V(3, 7)))
        objetivo = flechas(esc, "solucion")[0]
        self.assertTrue(objetivo["guion"])
        self.assertIn("no es combinación lineal", esc["avisos"][0])
        self.assertEqual([f for f in flechas(esc) if f["guion"] and f is not objetivo], [])

    def test_combinacion_3d(self):
        esc = escena_vectores(vm.combinacion_lineal(
            [V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)], V(1, 2, 3)))
        self.assertEqual(esc["dim"], 3)
        self.assertEqual(flechas(esc, "solucion")[0]["b"], [1, 2, 3])

    def test_mas_de_tres_componentes_no_se_grafica(self):
        for r in (vm.suma_vectores([V(1, 2, 3, 4), V(1, 1, 1, 1)]),
                  vm.multiplicar_vector_escalar(V(1, 2, 3, 4), "2"),
                  vm.resta_vectores(V(1, 2, 3, 4), V(1, 1, 1, 1))):
            esc = escena_vectores(r)
            self.assertFalse(esc["disponible"])
            self.assertIn("2 o 3 componentes", esc["motivo"])

    def test_un_componente_no_se_grafica(self):
        self.assertFalse(escena_vectores(vm.suma_vectores([V(1), V(2)]))["disponible"])

    def test_serializable_sin_nan_ni_infinito(self):
        for r in (vm.suma_vectores([V(1, 2), V(3, 4)]),
                  vm.resta_vectores(V(1, 2, 3), V(4, 5, 6)),
                  vm.multiplicar_vector_escalar(V(1, 2), "0"),
                  vm.combinacion_lineal([V(1, 2), V(2, 4)], V(3, 7))):
            json.dumps(escena_vectores(r), allow_nan=False)

    def test_modo_decimal(self):
        esc = escena_vectores(vm.suma_vectores([V(F(1, 2), 1), V(1, 1)]), "decimal")
        self.assertEqual(esc["leyenda"][0]["texto"], "v1 = (0.5, 1)")


def escena_det(filas, metodo="lu", modo="fraccion"):
    return escena_determinante(determinante(matriz(filas), metodo, modo), modo)


class DeterminanteTests(unittest.TestCase):

    def test_2x2_paralelogramo_de_las_columnas(self):
        esc = escena_det([[1, 3], [2, 4]])
        self.assertEqual(esc["dim"], 2)
        poligono = elementos(esc, "poligono")[0]
        self.assertEqual(poligono["puntos"], [[0, 0], [1, 2], [4, 6], [3, 4]])   # columnas (1,2) y (3,4)
        self.assertEqual([f["b"] for f in flechas(esc) if f["serie"] != "solucion"],
                         [[1, 2], [3, 4]])
        # área = |det| = |1·4 − 3·2| = 2
        self.assertIn("Área = |det A| = 2  (det A = -2)", esc["leyenda"][-1]["texto"])
        self.assertIn("horario", esc["avisos"][0])

    def test_2x2_positivo_es_antihorario(self):
        esc = escena_det([[2, 0], [0, 3]])
        self.assertIn("antihorario", esc["avisos"][0])
        self.assertIn("= 6", esc["leyenda"][-1]["texto"])

    def test_2x2_singular_se_aplasta(self):
        esc = escena_det([[1, 2], [2, 4]])
        self.assertIn("no tiene inversa", esc["avisos"][0])
        self.assertIn("paralelas", esc["avisos"][0])
        self.assertIn("Área = |det A| = 0", esc["leyenda"][-1]["texto"])

    def test_3x3_tiene_seis_caras(self):
        esc = escena_det([[1, 0, 0], [0, 2, 0], [0, 0, 3]])
        self.assertEqual(esc["dim"], 3)
        caras = elementos(esc, "poligono")
        self.assertEqual(len(caras), 6)
        vertices = {tuple(p) for c in caras for p in c["puntos"]}
        self.assertEqual(len(vertices), 8)
        self.assertIn((1.0, 2.0, 3.0), vertices)
        self.assertIn("Volumen = |det A| = 6", esc["leyenda"][-1]["texto"])
        self.assertIn("mano derecha", esc["avisos"][0])

    def test_3x3_singular(self):
        esc = escena_det([[1, 2, 3], [2, 4, 6], [1, 0, 1]])
        self.assertIn("mismo plano", esc["avisos"][0])

    def test_3x3_con_det_negativo(self):
        esc = escena_det([[0, 1, 0], [1, 0, 0], [0, 0, 1]])
        self.assertIn("mano izquierda", esc["avisos"][0])

    def test_cofactores_y_lu_dan_la_misma_escena(self):
        filas = [[2, 1, 0], [1, 3, 1], [0, 1, 4]]
        self.assertEqual(escena_det(filas, "lu")["elementos"],
                         escena_det(filas, "cofactores")["elementos"])

    def test_otros_tamanos_no_se_grafican(self):
        for filas in ([[5]], [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]):
            esc = escena_det(filas)
            self.assertFalse(esc["disponible"])
            self.assertIn("2×2 o 3×3", esc["motivo"])

    def test_serializable_y_decimal(self):
        for filas in ([[1, 2], [3, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 10]]):
            json.dumps(escena_det(filas), allow_nan=False)
        esc = escena_det([[F(1, 2), 0], [0, 1]], modo="decimal")
        self.assertEqual(esc["leyenda"][0]["texto"], "c1 = (0.5, 0)")


def escena_inv(filas, modo="fraccion"):
    return escena_inversa(vm.matriz_inversa(filas, "gauss_jordan", modo), modo)


def poligonos_de(esc, serie):
    return [e["puntos"] for e in esc["elementos"] if e["tipo"] == "poligono" and e["serie"] == serie]


class InversaTests(unittest.TestCase):

    def test_2x2_tres_figuras(self):
        esc = escena_inv([[1, 2], [3, 4]])
        self.assertEqual(esc["dim"], 2)
        # cuadrado unitario (gris, discontinuo)
        self.assertEqual(poligonos_de(esc, 5), [[[0, 0], [1, 0], [1, 1], [0, 1]]])
        # imagen por A: columnas (1, 3) y (2, 4)
        self.assertEqual(poligonos_de(esc, 1), [[[0, 0], [1, 3], [3, 7], [2, 4]]])
        # imagen por A⁻¹: columnas (-2, 3/2) y (1, -1/2)
        self.assertEqual(poligonos_de(esc, 0), [[[0, 0], [-2, 1.5], [-1, 1.0], [1, -0.5]]])
        self.assertTrue([e for e in esc["elementos"] if e["tipo"] == "poligono" and e["serie"] == 5][0]["guion"])
        self.assertEqual([l["texto"] for l in esc["leyenda"]],
                         ["Cuadrado unitario", "Imagen por A: área |det A| = 2",
                          "Imagen por A⁻¹: área 1/|det A| = 1/2"])
        self.assertEqual(len(flechas(esc)), 2)
        self.assertIn("deshace", esc["avisos"][0])

    def test_2x2_singular_no_tiene_figura_de_la_inversa(self):
        esc = escena_inv([[1, 2], [2, 4]])
        self.assertEqual(poligonos_de(esc, 0), [])
        self.assertEqual(len(poligonos_de(esc, 1)), 1)
        self.assertIn("no es invertible", esc["avisos"][0])
        self.assertIn("|det A| = 0", esc["leyenda"][1]["texto"])

    def test_3x3_son_tres_cubos(self):
        esc = escena_inv([[2, 0, 0], [0, 1, 0], [0, 0, 4]])
        self.assertEqual(esc["dim"], 3)
        for serie in (5, 0, 1):
            self.assertEqual(len(poligonos_de(esc, serie)), 6)
        vertices = {tuple(p) for c in poligonos_de(esc, 1) for p in c}
        self.assertIn((2.0, 1.0, 4.0), vertices)
        self.assertEqual(esc["leyenda"][0]["texto"], "Cubo unitario")
        self.assertIn("volumen |det A| = 8", esc["leyenda"][1]["texto"])
        self.assertEqual(len(flechas(esc)), 3)

    def test_3x3_singular(self):
        esc = escena_inv([[1, 2, 3], [2, 4, 6], [1, 0, 1]])
        self.assertEqual(poligonos_de(esc, 0), [])
        self.assertIn("no es invertible", esc["avisos"][0])

    def test_otros_tamanos_no_se_grafican(self):
        for filas in ([[5]], [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]):
            esc = escena_inv(filas)
            self.assertFalse(esc["disponible"])
            self.assertIn("2×2 o 3×3", esc["motivo"])

    def test_pivoteo_da_la_misma_escena_y_se_serializa(self):
        a = escena_inversa(vm.matriz_inversa([[1, 2], [3, 4]], "gauss_jordan"))
        b = escena_inversa(vm.matriz_inversa([[1, 2], [3, 4]], "pivoteo"))
        self.assertEqual(a["elementos"], b["elementos"])
        for filas in ([[1, 2], [3, 4]], [[1, 2], [2, 4]], [[2, 0, 0], [0, 1, 0], [0, 0, 4]]):
            json.dumps(escena_inv(filas), allow_nan=False)


class EcuacionMatricialTests(unittest.TestCase):

    def escenas(self, a, b):
        r = vm.ecuacion_matricial(a, b)
        return [escena_sistema(x) for x in r["resoluciones"]]

    def test_una_escena_por_columna_de_b(self):
        escenas = self.escenas([[1, 1], [1, -1]], [[3, 5], [1, 1]])
        self.assertEqual(len(escenas), 2)
        self.assertEqual(elementos(escenas[0], "punto")[0]["p"], [2.0, 1.0])
        self.assertEqual(elementos(escenas[1], "punto")[0]["p"], [3.0, 2.0])

    def test_columna_incompatible_y_otra_con_solucion(self):
        escenas = self.escenas([[1, 1], [2, 2]], [[3, 3], [6, 7]])
        self.assertIn("misma recta", escenas[0]["avisos"][0])
        self.assertIn("paralelas", escenas[1]["avisos"][0])

    def test_3_incognitas_es_3d(self):
        escenas = self.escenas([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[1], [2], [3]])
        self.assertEqual(escenas[0]["dim"], 3)
        self.assertEqual(elementos(escenas[0], "punto")[0]["p"], [1.0, 2.0, 3.0])

    def test_4_incognitas_no_se_grafica(self):
        identidad = [[int(i == j) for j in range(4)] for i in range(4)]
        escenas = self.escenas(identidad, [[1], [2], [3], [4]])
        self.assertFalse(escenas[0]["disponible"])


def escena_prod(a, b, modo="fraccion"):
    return escena_producto(vm.multiplicar_matrices(a, b), modo)


class ProductoTests(unittest.TestCase):

    def test_2x2_composicion(self):
        esc = escena_prod([[1, 2], [3, 4]], [[0, 1], [1, 0]])    # A·B = [[2,1],[4,3]]
        self.assertEqual(esc["dim"], 2)
        self.assertEqual(poligonos_de(esc, 5), [[[0, 0], [1, 0], [1, 1], [0, 1]]])
        self.assertEqual(poligonos_de(esc, 0), [[[0, 0], [0, 1], [1, 1], [1, 0]]])     # columnas de B
        self.assertEqual(poligonos_de(esc, "solucion"), [[[0, 0], [2, 4], [3, 7], [1, 3]]])  # columnas de A·B
        self.assertEqual([l["texto"] for l in esc["leyenda"]],
                         ["Cuadrado unitario", "Imagen por B: área |det B| = 1",
                          "Imagen por A·B: área |det(A·B)| = 2"])
        self.assertIn("primero B y luego A", esc["avisos"][0])
        self.assertEqual(len(flechas(esc)), 4)

    def test_el_orden_importa(self):
        a, b = [[1, 1], [0, 1]], [[1, 0], [1, 1]]
        ab = poligonos_de(escena_prod(a, b), "solucion")
        ba = poligonos_de(escena_prod(b, a), "solucion")
        self.assertNotEqual(ab, ba)

    def test_identidad_no_cambia_nada(self):
        esc = escena_prod([[3, 1], [0, 2]], [[1, 0], [0, 1]])
        self.assertEqual(poligonos_de(esc, 0), poligonos_de(esc, 5))
        self.assertEqual(poligonos_de(esc, "solucion")[0],
                         [[0, 0], [3, 0], [4, 2], [1, 2]])

    def test_producto_singular(self):
        esc = escena_prod([[1, 2], [2, 4]], [[1, 0], [0, 1]])
        self.assertIn("|det(A·B)| = 0", esc["leyenda"][-1]["texto"])

    def test_3x3_cubos(self):
        esc = escena_prod([[2, 0, 0], [0, 1, 0], [0, 0, 1]], [[1, 0, 0], [0, 3, 0], [0, 0, 1]])
        self.assertEqual(esc["dim"], 3)
        for serie in (5, 0, "solucion"):
            self.assertEqual(len(poligonos_de(esc, serie)), 6)
        vertices = {tuple(p) for c in poligonos_de(esc, "solucion") for p in c}
        self.assertIn((2.0, 3.0, 1.0), vertices)
        self.assertEqual(len(flechas(esc)), 6)

    def test_no_cuadradas_o_grandes_no_se_grafican(self):
        for a, b in (([[1, 2, 3], [3, 4, 5]], [[0, 1], [1, 0], [1, 1]]),
                     ([[1, 0], [0, 1]], [[1, 2, 3], [4, 5, 6]]),
                     ([[int(i == j) for j in range(4)] for i in range(4)],
                      [[int(i == j) for j in range(4)] for i in range(4)])):
            esc = escena_prod(a, b)
            self.assertFalse(esc["disponible"])
            self.assertIn("2×2 o 3×3", esc["motivo"])

    def test_serializable(self):
        json.dumps(escena_prod([[1, 2], [3, 4]], [[0, 1], [1, 0]]), allow_nan=False)
        json.dumps(escena_prod([[1, 2, 3], [4, 5, 6], [7, 8, 10]], [[1, 0, 0], [0, 1, 0], [0, 0, 1]]), allow_nan=False)


class AnimacionTests(unittest.TestCase):
    """Spec 015: cuadros precalculados de la transformación (deslizador t)."""

    def test_inversa_t0_es_la_identidad_y_t1_es_a(self):
        esc = escena_inv([[1, 2], [3, 4]])
        anim = esc["animacion"]
        pasos = anim["pasos"]
        self.assertEqual(len(pasos), 21)
        self.assertEqual(pasos[0]["t"], 0.0)
        self.assertEqual(pasos[-1]["t"], 1.0)
        self.assertEqual(anim["paso_final"], 20)
        # t = 0: cuadrado unitario; t = 1: imagen por A (columnas (1,3) y (2,4))
        primero = [e for e in pasos[0]["elementos"] if e["tipo"] == "poligono"][0]
        ultimo = [e for e in pasos[-1]["elementos"] if e["tipo"] == "poligono"][0]
        self.assertEqual(primero["puntos"], [[0, 0], [1, 0], [1, 1], [0, 1]])
        self.assertEqual(ultimo["puntos"], [[0, 0], [1, 3], [3, 7], [2, 4]])
        # el último cuadro es lo que ya mostraba la escena base
        base = esc["elementos"][anim["reemplaza_desde"]:]
        self.assertEqual(pasos[-1]["elementos"], base)

    def test_punto_medio_es_la_mezcla_de_i_y_a(self):
        pasos = escena_inv([[3, 0], [0, 5]])["animacion"]["pasos"]
        medio = [e for e in pasos[10]["elementos"] if e["tipo"] == "poligono"][0]
        self.assertEqual(pasos[10]["t"], 0.5)
        self.assertEqual(medio["puntos"][2], [2.0, 3.0])   # (1+3)/2, (1+5)/2

    def test_determinante_anima_desde_el_primer_elemento(self):
        esc = escena_det([[2, 0], [0, 3]])
        anim = esc["animacion"]
        self.assertEqual(anim["reemplaza_desde"], 0)
        self.assertEqual(anim["pasos"][0]["det"], "1")
        self.assertEqual(anim["pasos"][-1]["det"], "6")
        self.assertEqual(anim["pasos"][-1]["elementos"], esc["elementos"])
        self.assertFalse(any(p["aplastado"] for p in anim["pasos"]))

    def test_3x3_trae_seis_caras_y_tres_flechas_por_cuadro(self):
        pasos = escena_det([[1, 0, 0], [0, 2, 0], [0, 0, 3]])["animacion"]["pasos"]
        for paso in pasos:
            tipos = [e["tipo"] for e in paso["elementos"]]
            self.assertEqual(tipos.count("poligono"), 6)
            self.assertEqual(tipos.count("flecha"), 3)

    def test_singular_queda_aplastada_al_final(self):
        pasos = escena_det([[1, 2], [2, 4]])["animacion"]["pasos"]
        self.assertTrue(pasos[-1]["aplastado"])
        self.assertEqual(pasos[-1]["det"], "0")
        self.assertFalse(pasos[0]["aplastado"])

    def test_det_negativo_pasa_por_cero_y_se_marca(self):
        # intercambiar ejes: det A = -1, así que det M(t) cruza por 0 en t = 1/2
        pasos = escena_det([[0, 1], [1, 0]])["animacion"]["pasos"]
        self.assertTrue(pasos[10]["aplastado"])     # t = 0.5: det = 0
        self.assertFalse(pasos[5]["aplastado"])
        self.assertFalse(pasos[0]["aplastado"])

    def test_producto_tiene_dos_tramos(self):
        a, b = [[2, 0], [0, 1]], [[1, 1], [0, 1]]
        esc = escena_prod(a, b)
        anim = esc["animacion"]
        self.assertEqual(len(anim["pasos"]), 41)
        self.assertEqual(anim["tramos"], ["Identidad → B", "B → A·B"])
        self.assertEqual([p["tramo"] for p in anim["pasos"]].count(0), 21)
        self.assertEqual(anim["pasos"][20]["t"], 0.5)
        # en t = 1/2 la figura es la imagen por B (con B como fantasma encima)
        figura = [e for e in anim["pasos"][20]["elementos"]
                  if e["tipo"] == "poligono" and not e["guion"]][0]
        self.assertEqual(figura["puntos"], [[0, 0], [1, 0], [2, 1], [1, 1]])
        # t = 1: imagen por A·B (columnas (2,0) y (2,1))
        final = [e for e in anim["pasos"][-1]["elementos"]
                 if e["tipo"] == "poligono" and not e["guion"]][0]
        self.assertEqual(final["puntos"], [[0, 0], [2, 0], [4, 1], [2, 1]])
        self.assertEqual(anim["pasos"][-1]["det"], "2")

    def test_la_ventana_contiene_todos_los_cuadros(self):
        for esc in (escena_det([[1, 2], [3, 4]]), escena_inv([[0, 1], [1, 0]]),
                    escena_prod([[2, 0], [0, 1]], [[1, 1], [0, 1]])):
            v = esc["ventana"]
            for paso in esc["animacion"]["pasos"]:
                for e in paso["elementos"]:
                    if e["tipo"] != "poligono":
                        continue
                    for x, y in e["puntos"]:
                        self.assertTrue(v["x"][0] <= x <= v["x"][1])
                        self.assertTrue(v["y"][0] <= y <= v["y"][1])

    def test_la_caja_3d_contiene_todos_los_cuadros(self):
        esc = escena_det([[1, 2, 0], [0, 1, 3], [4, 0, 1]])
        caja = esc["caja"]
        for paso in esc["animacion"]["pasos"]:
            for e in paso["elementos"]:
                if e["tipo"] == "poligono":
                    for punto in e["puntos"]:
                        for eje, valor in zip("xyz", punto):
                            self.assertTrue(caja[eje][0] <= valor <= caja[eje][1])

    def test_inversa_de_matriz_singular_tambien_anima(self):
        esc = escena_inv([[1, 2], [2, 4]])
        self.assertEqual(len(esc["animacion"]["pasos"]), 21)
        self.assertTrue(esc["animacion"]["pasos"][-1]["aplastado"])

    def test_sin_grafica_no_hay_animacion(self):
        self.assertNotIn("animacion", escena_det([[5]]))
        self.assertNotIn("animacion", escena_prod([[1, 2, 3]], [[1], [2], [3]]))

    def test_decimal_y_serializable(self):
        for esc in (escena_det([[F(1, 2), 0], [0, 1]], modo="decimal"),
                    escena_inv([[1, 2, 3], [0, 1, 4], [5, 6, 0]]),
                    escena_prod([[1, 2], [3, 4]], [[0, 1], [1, 0]])):
            json.dumps(esc, allow_nan=False)
        pasos = escena_det([[F(1, 2), 0], [0, 1]], modo="decimal")["animacion"]["pasos"]
        self.assertEqual(pasos[-1]["det"], "0.5")


if __name__ == "__main__":
    unittest.main()
