"""Pruebas de la revisión heurística de continuidad."""

import unittest

from metodos.continuidad import MAX_SOSPECHAS, revisar_continuidad
from metodos.evaluador import compilar


def revisar(funcion, a, b, **kwargs):
    return revisar_continuidad(compilar(funcion), a, b, **kwargs)


class SinFalsosAvisosTests(unittest.TestCase):
    """Funciones continuas: no debe haber ninguna sospecha."""

    CASOS = (
        ("x^4 - 5x^3 + 0.5x^2 - 11x + 10", 0.55, 1.1),
        ("x^2 - 2", 1, 2),
        ("cos(x) - x", 0, 1),
        ("exp(-x) - x", 0, 1),
        ("x", -1, 3),
        ("x^3 + 0.001", -1, 1),
        ("cbrt(x - 1)", 0, 3),          # tangente vertical, pero continua
        ("(x - 1)^3", 0, 3),
        ("sin(x)", 1.5707963, 4.7123889),
        ("exp(x) - 1000", 0, 50),       # crecimiento fuerte, sin polo
        ("abs(x)", -1, 1),              # pico sin salto
        ("1/(1 + 25x^2)", -1, 1),       # función de Runge
        ("sin(100x)", 0, 10),           # muy oscilante
        ("x^2 - 1", -2, 2),
        ("ln(x - 1)*(x - 3)", 1.5, 4),  # raíz en el extremo de la zona
    )

    def test_funciones_continuas_no_dan_aviso(self):
        for funcion, a, b in self.CASOS:
            with self.subTest(funcion):
                r = revisar(funcion, a, b)
                self.assertTrue(r["sin_senales"], r["sospechas"])
                self.assertEqual(r["total"], 0)
                self.assertEqual(r["sospechas"], [])
                self.assertEqual(r["muestras"], 401)


class DeteccionTests(unittest.TestCase):

    def tipos(self, funcion, a, b):
        r = revisar(funcion, a, b)
        self.assertFalse(r["sin_senales"], funcion)
        return [s["tipo"] for s in r["sospechas"]], r

    def test_polo_con_cambio_de_signo(self):
        for funcion, a, b, x in (("1/x", -1, 2, 0), ("tan(x)", 1, 2, 1.5708),
                                 ("1/(x - 1)", 0, 3, 1), ("tan(x)", 0.5, 3, 1.5708)):
            with self.subTest(funcion):
                tipos, r = self.tipos(funcion, a, b)
                self.assertEqual(tipos, ["polo"])
                self.assertAlmostEqual(r["sospechas"][0]["x"], x, places=3)

    def test_polo_sin_cambio_de_signo(self):
        for funcion, a, b, x in (("1/x^2", -1, 2, 0), ("1/(x - 1)^2", 0, 3, 1)):
            with self.subTest(funcion):
                tipos, r = self.tipos(funcion, a, b)
                self.assertEqual(tipos, ["polo"])
                self.assertAlmostEqual(r["sospechas"][0]["x"], x, places=3)

    def test_polo_exacto_en_una_muestra(self):
        # 0 cae justo en una muestra: f no se puede evaluar ahí.
        tipos, r = self.tipos("1/x", -1, 1)
        self.assertEqual(tipos, ["polo"])
        self.assertIn("división entre cero", r["sospechas"][0]["mensaje"])

    def test_salto_no_es_raiz(self):
        tipos, r = self.tipos("abs(x)/x", -1, 2)
        self.assertEqual(tipos, ["salto"])
        self.assertIn("no se acerca a 0", r["sospechas"][0]["mensaje"])

    def test_fuera_del_dominio(self):
        tipos, r = self.tipos("sqrt(x^2 - 1)", -2, 2)
        self.assertEqual(tipos, ["no_definida"])
        s = r["sospechas"][0]
        self.assertAlmostEqual(s["desde"], -1, places=6)
        self.assertAlmostEqual(s["hasta"], 1, places=6)
        self.assertIn("[-1, 1]", s["mensaje"])

    def test_una_raiz_real_no_se_confunde_con_un_polo(self):
        r = revisar("x - 1.5", 1, 2)
        self.assertTrue(r["sin_senales"])

    def test_ruido_numerico_se_muestra_como_cero(self):
        _, r = self.tipos("1/x", -1, 2)
        self.assertIn("x ≈ 0:", r["sospechas"][0]["mensaje"])

    def test_un_polo_se_reporta_una_sola_vez(self):
        for funcion, a, b in (("1/x", -1, 2), ("tan(x)", 1, 2)):
            with self.subTest(funcion):
                self.assertEqual(revisar(funcion, a, b)["total"], 1)

    def test_varias_sospechas_y_tope(self):
        # tan(x) tiene un polo cada π: en [0, 40] hay 13.
        r = revisar("tan(x)", 0, 40)
        self.assertGreater(r["total"], MAX_SOSPECHAS)
        self.assertEqual(len(r["sospechas"]), MAX_SOSPECHAS)
        xs = [s["x"] for s in r["sospechas"]]
        self.assertEqual(xs, sorted(xs))


class ParametrosTests(unittest.TestCase):

    def test_numero_de_muestras(self):
        self.assertEqual(revisar("x", 0, 1, subintervalos=50)["muestras"], 51)

    def test_extremos_indefinidos_no_rompen(self):
        r = revisar("ln(x)", -1, 2)
        self.assertFalse(r["sin_senales"])
        self.assertEqual(r["sospechas"][0]["tipo"], "no_definida")


if __name__ == "__main__":
    unittest.main()
