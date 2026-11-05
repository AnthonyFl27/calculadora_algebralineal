"""Pruebas de los datos de la gráfica de la bisección."""

import json
import unittest

from metodos.biseccion import biseccion
from metodos.grafica import PUNTOS, agregar_iteraciones, marcas


def grafica(funcion, a, b, tol="1e-4"):
    return biseccion(funcion, a, b, tol)["grafica"]


class MarcasTests(unittest.TestCase):

    def test_pasos_1_2_5(self):
        self.assertEqual([m[1] for m in marcas(0, 10)], ["0", "2", "4", "6", "8", "10"])
        self.assertEqual([m[1] for m in marcas(0.55, 1.1)],
                         ["0.6", "0.7", "0.8", "0.9", "1", "1.1"])

    def test_dentro_del_rango_y_con_cero_limpio(self):
        for lo, hi in ((-1.03, 2.03), (-7.9, 4.6), (1, 2), (-1e-9, 1)):
            m = marcas(lo, hi)
            self.assertTrue(all(lo <= v <= hi for v, _ in m), (lo, hi))
        etiquetas = dict((round(v, 9), t) for v, t in marcas(-1.03, 2.03))
        self.assertEqual(etiquetas[0], "0")     # nunca "-2.3e-17"

    def test_rango_vacio(self):
        self.assertEqual(marcas(1, 1), [])


class GraficaTests(unittest.TestCase):

    def test_funcion_continua(self):
        g = grafica("x^4 - 5x^3 + 0.5x^2 - 11x + 10", 0.55, 1.1, "0.0001")
        self.assertEqual(len(g["curva"]), 1)
        self.assertEqual(len(g["curva"][0]), PUNTOS + 1)
        self.assertEqual(len(g["iteraciones"]), 13)
        self.assertEqual(g["intervalo"], [0.55, 1.1])
        self.assertLess(g["x_min"], 0.55)
        self.assertGreater(g["x_max"], 1.1)
        # La ventana siempre contiene y = 0 y toda la curva.
        self.assertLess(g["y_min"], 0)
        self.assertGreater(g["y_max"], 0)
        self.assertTrue(all(g["y_min"] <= y <= g["y_max"]
                            for t in g["curva"] for _, y in t))
        self.assertFalse(g["raiz"]["fuera"])
        self.assertAlmostEqual(g["raiz"]["x"], 0.7639709473, places=6)
        self.assertEqual(g["discontinuidades"], [])

    def test_iteraciones_siguen_la_biseccion(self):
        r = biseccion("x^2 - 2", 1, 2, "1e-4")
        g = r["grafica"]
        for p, punto in zip(r["pasos"], g["iteraciones"]):
            self.assertEqual(punto["i"], p["i"])
            self.assertEqual(punto["x"], p["c"])
            self.assertEqual((punto["a"], punto["b"]), (p["a_nuevo"], p["b_nuevo"]))

    def test_polo_corta_la_curva_en_dos_tramos(self):
        g = grafica("tan(x)", 1, 2)
        self.assertEqual(len(g["curva"]), 2)
        izquierda, derecha = g["curva"]
        self.assertLess(izquierda[-1][0], 1.5708)
        self.assertGreater(derecha[0][0], 1.5708)
        self.assertEqual(len(g["discontinuidades"]), 1)
        self.assertAlmostEqual(g["discontinuidades"][0]["desde"], 1.5708, places=2)
        # La ventana no se estira hasta el infinito.
        self.assertLess(g["y_max"], 50)
        self.assertGreater(g["y_min"], -50)
        # Un punto con f(x) enorme (cerca del polo) queda fuera de la ventana.
        agregar_iteraciones(g, [], {"raiz": 1.5707, "fraiz": 10000.0})
        self.assertTrue(g["raiz"]["fuera"])

    def test_la_curva_se_recorta_sin_tramos_planos(self):
        g = grafica("tan(x)", 1, 2)
        for tramo in g["curva"]:
            tocan_borde = [p for p in tramo
                           if p[1] in (g["y_min"], g["y_max"])]
            # Solo el último/primer punto de cada tramo toca el borde.
            self.assertLessEqual(len(tocan_borde), 1)

    def test_funcion_indefinida_en_el_interior_corta_la_curva(self):
        # x*sqrt(x^2 - 1) no está definida en (-1, 1): la curva se parte en dos
        # tramos y se marca el tramo. Se usa `datos_grafica` directamente porque
        # f(-2) y f(2) tienen distinto signo pero el interior no se puede evaluar.
        from metodos.continuidad import revisar_continuidad
        from metodos.evaluador import compilar
        from metodos.grafica import datos_grafica

        f = compilar("x*sqrt(x^2 - 1)")
        cont = revisar_continuidad(f, -2, 2)
        g = datos_grafica(f, -2, 2, cont)
        self.assertEqual(len(g["curva"]), 2)
        self.assertLess(g["curva"][0][-1][0], -0.99)
        self.assertGreater(g["curva"][1][0][0], 0.99)
        self.assertEqual(g["discontinuidades"][0]["tipo"], "no_definida")

    def test_serializable_sin_nan_ni_infinito(self):
        for funcion, a, b in (("tan(x)", 1, 2), ("1/x", -1, 2),
                              ("exp(x) - 1000", 0, 50), ("x^2 - 2", 1, 2)):
            with self.subTest(funcion):
                json.dumps(grafica(funcion, a, b), allow_nan=False)

    def test_funcion_con_crecimiento_fuerte_sin_polos(self):
        g = grafica("exp(x) - 1000", 0, 50)
        self.assertEqual(len(g["curva"]), 1)
        self.assertEqual(len(g["curva"][0]), PUNTOS + 1)   # nada recortado


class CurvaVentanaTests(unittest.TestCase):
    """Curva que se pide al hacer zoom o mover la gráfica."""

    def ventana(self, funcion, x0, x1, y0, y1):
        from metodos.evaluador import compilar
        from metodos.grafica import curva_ventana
        return curva_ventana(compilar(funcion), x0, x1, y0, y1)

    def test_muestrea_mas_alla_de_la_ventana(self):
        from metodos.grafica import PUNTOS_VENTANA
        v = self.ventana("x^2", -1, 1, -1, 5)
        self.assertEqual(len(v["curva"]), 1)
        xs = [p[0] for p in v["curva"][0]]
        self.assertEqual(len(xs), PUNTOS_VENTANA + 1)
        self.assertLess(min(xs), -1.4)          # relleno a la izquierda
        self.assertGreater(max(xs), 1.4)        # y a la derecha
        self.assertEqual((v["x_min"], v["x_max"]), (-1, 1))
        self.assertTrue(all(-1 <= m[0] <= 1 for m in v["marcas_x"]))

    def test_polo_fuera_del_intervalo_original_corta_la_curva(self):
        v = self.ventana("tan(x)", -3, 3, -10, 10)     # polos en ±π/2
        self.assertGreaterEqual(len(v["curva"]), 3)
        borde = 10 + 0.5 * 20
        for tramo in v["curva"]:
            self.assertTrue(all(-borde <= y <= borde for _, y in tramo))

    def test_zoom_profundo_en_una_raiz(self):
        v = self.ventana("x^2 - 2", 1.41421356, 1.41421357, -1e-7, 1e-7)
        self.assertEqual(len(v["curva"]), 1)
        self.assertGreater(len(v["marcas_x"]), 2)

    def test_dominio_parcial_deja_huecos(self):
        v = self.ventana("sqrt(x)", -2, 2, -3, 3)
        self.assertEqual(len(v["curva"]), 1)
        self.assertGreaterEqual(min(p[0] for p in v["curva"][0]), 0)

    def test_serializable_sin_nan_ni_infinito(self):
        json.dumps(self.ventana("1/x", -5, 5, -5, 5), allow_nan=False)

    def test_rechaza_ventanas_invalidas(self):
        for args in ((1, 1, 0, 1), (2, 1, 0, 1), (0, 1, 1, 1),
                     (0, 1e13, 0, 1), (float("nan"), 1, 0, 1),
                     (None, 1, 0, 1), ("a", 1, 0, 1), (True, 2, 0, 1)):
            with self.subTest(args):
                with self.assertRaises(ValueError):
                    self.ventana("x", *args)

    def test_puntos_traen_el_valor_real_de_f(self):
        g = grafica("tan(x)", 1, 2)
        agregar_iteraciones(g, [], {"raiz": 1.5707, "fraiz": 10000.0})
        self.assertGreater(g["raiz"]["valor"], 8000)       # y está recortado
        self.assertLessEqual(g["raiz"]["y"], g["y_max"])


if __name__ == "__main__":
    unittest.main()
