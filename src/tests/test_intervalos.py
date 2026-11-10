"""Pruebas del buscador de intervalos para bisección y Regula Falsi."""

import unittest

from metodos.biseccion import biseccion
from metodos.falsa_posicion import falsa_posicion
from metodos.intervalos import buscar_intervalos


def pares(r):
    return [(i["a"], i["b"]) for i in r["intervalos"]]


class BuscarIntervalosTests(unittest.TestCase):

    def test_polinomio(self):
        r = buscar_intervalos("x^3 - x - 2")
        self.assertEqual(pares(r), [(1, 2)])
        self.assertEqual(len(r["tabla"]), 21)

    def test_dos_raices(self):
        self.assertEqual(pares(buscar_intervalos("x^2 - 2")), [(-2, -1), (1, 2)])

    def test_tan_descarta_el_polo_y_afina(self):
        r = buscar_intervalos("tan(x) - x^10 + 1")
        self.assertEqual(pares(r), [(-1, 0), (1.1, 1.2)])
        self.assertEqual([(d["a"], d["b"]) for d in r["descartados"]], [(1, 2)])
        self.assertEqual(r["intervalos"][1]["origen"], "refinado")

    def test_raiz_exacta_en_la_tabla(self):
        r = buscar_intervalos("2x - 4")
        self.assertEqual(r["raices_exactas"], [2])
        self.assertEqual(r["intervalos"], [])

    def test_sin_raices(self):
        r = buscar_intervalos("x^2 + 1")
        self.assertEqual((r["intervalos"], r["descartados"]), ([], []))

    def test_polo_sin_raiz(self):
        self.assertEqual(buscar_intervalos("1/x")["intervalos"], [])

    def test_fuera_del_dominio_se_omite(self):
        r = buscar_intervalos("ln(x) - 1")
        self.assertEqual(pares(r), [(2, 3)])
        self.assertIsNone(r["tabla"][0][1])      # ln(-10) no está definida

    def test_cada_sugerencia_sirve_en_los_metodos(self):
        for texto in ("x^3 - x - 2", "tan(x) - x^10 + 1", "x^2 - 2"):
            for i in buscar_intervalos(texto)["intervalos"]:
                for metodo in (biseccion, falsa_posicion):
                    r = metodo(texto, i["a"], i["b"], "0.0001")
                    self.assertFalse(r["bloqueada"])
                    self.assertTrue(r["resultado"]["convergio"])

    def test_errores(self):
        with self.assertRaises(ValueError):
            buscar_intervalos("5")
        with self.assertRaises(ValueError):
            buscar_intervalos("x", 3, 3)
        with self.assertRaises(ValueError):
            buscar_intervalos("x", "a", 3)
        with self.assertRaises(ValueError):
            buscar_intervalos("x", -5000, 5000)


if __name__ == "__main__":
    unittest.main()
