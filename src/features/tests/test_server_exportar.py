"""Pruebas de POST /api/exportar con un servidor real en un puerto libre."""

import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

# server.py vive en la raíz del proyecto (dos niveles arriba de src/).
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import server

SISTEMA = {
    "metodo": "gauss-jordan", "modo": "fraccion",
    "matriz": [["2", "1", "-1", "8"], ["-3", "-1", "2", "-11"],
               ["-2", "1", "2", "-3"]],
}


def _sin_registro(*args, **kwargs):
    pass


class ExportarEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._registrar = server._registrar
        server._registrar = _sin_registro
        cls.servidor = ThreadingHTTPServer(("127.0.0.1", 0), server.Manejador)
        cls.puerto = cls.servidor.server_address[1]
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        server._registrar = cls._registrar

    def enviar(self, cuerpo):
        peticion = urllib.request.Request(
            f"http://127.0.0.1:{self.puerto}/api/exportar",
            data=json.dumps(cuerpo).encode(), method="POST",
        )
        try:
            return urllib.request.urlopen(peticion)
        except urllib.error.HTTPError as error:
            return error

    def test_determinante_exporta_y_responde(self):
        datos = {"matriz": [["2", "1"], ["1", "3"]], "metodo": "cofactores"}
        r = self.enviar({"modulo": "determinante", "formato": "pdf",
                         "datos": datos})
        self.assertEqual(r.status, 200)
        self.assertRegex(r.headers["Content-Disposition"],
                         r'filename="determinante-cofactores-\d{8}-\d{4}\.pdf"')

        bloque = server._resolver_determinante(datos)
        self.assertEqual(bloque["resultado"], "5")
        self.assertEqual(bloque["comprobacion"]["correcto"], True)
        self.assertEqual(
            server._resolver_recomendacion_determinante({"n": "5"})["recomendado"],
            "lu")
        with self.assertRaises(ValueError):
            server._resolver_recomendacion_determinante({"n": 0})

    def test_biseccion_resuelve_y_exporta(self):
        datos = {"funcion": "x^4 - 5x^3 + 0.5x^2 - 11x + 10", "a": "0.55",
                 "b": "1.1", "tolerancia": "0.0001", "max_iter": 50}
        bloque = server._resolver_biseccion(datos)
        self.assertEqual(bloque["resultado"]["iteraciones"], 13)
        self.assertEqual(bloque["resultado"]["raiz"], "0.7639709473")
        self.assertEqual(len(bloque["pasos"]), 13)
        self.assertTrue(bloque["comprobacion"]["correcto"])
        self.assertTrue(bloque["continuidad"]["sin_senales"])
        self.assertEqual(bloque["continuidad"]["muestras"], 401)
        g = bloque["grafica"]
        self.assertEqual(len(g["iteraciones"]), 13)
        self.assertEqual(len(g["curva"]), 1)
        self.assertTrue(g["marcas_x"] and g["marcas_y"])
        json.dumps(bloque)  # serializable
        for formato, mime in (("png", "image/png"), ("pdf", "application/pdf")):
            r = self.enviar({"modulo": "biseccion", "formato": formato,
                             "datos": datos})
            self.assertEqual(r.status, 200)
            self.assertEqual(r.headers["Content-Type"], mime)
            self.assertRegex(
                r.headers["Content-Disposition"],
                rf'filename="metodo-de-biseccion-\d{{8}}-\d{{4}}\.{formato}"')

    def test_biseccion_bloque_con_continuidad(self):
        bloque = server._resolver_biseccion(
            {"funcion": "tan(x)", "a": "1", "b": "2", "tolerancia": "0.0001"})
        cont = bloque["continuidad"]
        self.assertFalse(cont["sin_senales"])
        self.assertEqual(cont["sospechas"][0]["tipo"], "polo")
        self.assertIn("Posible polo", cont["sospechas"][0]["mensaje"])
        self.assertTrue(bloque["bloqueada"])
        self.assertIn("no es continua", bloque["motivo_bloqueo"])
        self.assertNotIn("pasos", bloque)
        self.assertTrue(bloque["grafica"]["curva"])
        json.dumps(bloque)
        # Exportar también funciona con el método bloqueado.
        for formato in ("png", "pdf"):
            r = self.enviar({"modulo": "biseccion", "formato": formato,
                             "datos": {"funcion": "tan(x)", "a": "1", "b": "2",
                                       "tolerancia": "0.0001"}})
            self.assertEqual(r.status, 200)

    def test_falsa_posicion_resuelve_y_exporta(self):
        datos = {"funcion": "x^2 - 2", "a": "1", "b": "2",
                 "tolerancia": "0.0001", "max_iter": 50}
        bloque = server._resolver_falsa_posicion(datos)
        self.assertEqual(bloque["tipo"], "falsa_posicion")
        self.assertEqual(bloque["resultado"]["iteraciones"], 6)
        self.assertEqual(bloque["resultado"]["raiz"], "1.414201183")
        self.assertNotIn("cota_iteraciones", bloque)
        self.assertTrue(bloque["comprobacion"]["correcto"])
        self.assertEqual(len(bloque["grafica"]["iteraciones"]), 6)
        self.assertIn("secante", bloque["grafica"]["iteraciones"][0])
        json.dumps(bloque)
        bloqueado = server._resolver_falsa_posicion(
            {"funcion": "tan(x)", "a": "1", "b": "2", "tolerancia": "0.0001"})
        self.assertTrue(bloqueado["bloqueada"])
        self.assertEqual(bloqueado["tipo"], "falsa_posicion")
        for formato, mime in (("png", "image/png"), ("pdf", "application/pdf")):
            r = self.enviar({"modulo": "falsa-posicion", "formato": formato,
                             "datos": datos})
            self.assertEqual(r.status, 200)
            self.assertEqual(r.headers["Content-Type"], mime)
            self.assertRegex(
                r.headers["Content-Disposition"],
                rf'filename="metodo-de-regula-falsi-\d{{8}}-\d{{4}}\.{formato}"')

    def test_newton_raphson_resuelve_y_exporta(self):
        datos = {"funcion": "x^3 - x - 2", "derivada": "", "x0": "1.5",
                 "tolerancia": "0.000001", "max_iter": 50}
        bloque = server._resolver_newton_raphson(datos)
        self.assertEqual(bloque["tipo"], "newton_raphson")
        self.assertEqual(bloque["resultado"]["iteraciones"], 3)
        self.assertEqual(bloque["resultado"]["raiz"], "1.521379707")
        self.assertEqual(bloque["entradas"]["derivada"], "3 * x^2 - 1")
        self.assertTrue(bloque["comprobacion"]["correcto"])
        self.assertEqual(len(bloque["grafica"]["iteraciones"]), 3)
        json.dumps(bloque)
        for formato, mime in (("png", "image/png"), ("pdf", "application/pdf")):
            r = self.enviar({"modulo": "newton-raphson", "formato": formato,
                             "datos": datos})
            self.assertEqual(r.status, 200)
            self.assertEqual(r.headers["Content-Type"], mime)
            self.assertRegex(
                r.headers["Content-Disposition"],
                rf'filename="metodo-de-newton-raphson-\d{{8}}-\d{{4}}\.{formato}"')

    def test_falsa_posicion_errores_son_json_400(self):
        for datos in ({"funcion": "x^2 + 1", "a": "0", "b": "2",
                       "tolerancia": "0.001"},
                      {"funcion": "", "a": "0", "b": "2", "tolerancia": "1"}):
            peticion = urllib.request.Request(
                f"http://127.0.0.1:{self.puerto}/api/falsa-posicion",
                data=json.dumps(datos).encode(), method="POST")
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(peticion)
            self.assertEqual(cm.exception.code, 400)
            self.assertIn("error", json.loads(cm.exception.read()))

    def test_biseccion_errores_son_json_400(self):
        for datos in ({"funcion": "x^2 + 1", "a": "0", "b": "2",
                       "tolerancia": "0.001"},
                      {"funcion": "", "a": "0", "b": "2", "tolerancia": "1"},
                      {"funcion": "x", "a": "2", "b": "1", "tolerancia": "1"}):
            peticion = urllib.request.Request(
                f"http://127.0.0.1:{self.puerto}/api/biseccion",
                data=json.dumps(datos).encode(), method="POST")
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(peticion)
            self.assertEqual(cm.exception.code, 400)
            self.assertIn("error", json.loads(cm.exception.read()))

    def test_pdf_adjunto(self):
        r = self.enviar({"modulo": "sistema", "formato": "pdf",
                         "incluir_pasos": True, "datos": SISTEMA})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.headers["Content-Type"], "application/pdf")
        self.assertRegex(r.headers["Content-Disposition"],
                         r'attachment; filename="gauss-jordan-\d{8}-\d{4}\.pdf"')
        self.assertTrue(r.read().startswith(b"%PDF-"))

    def test_png_de_cada_modulo(self):
        casos = [
            ("sistema", SISTEMA),
            ("conversion", {"numero": "255", "base_entrada": 10,
                            "base_salida": 16}),
            ("vectores", {"operacion": "Suma",
                          "vectores": [["1", "2"], ["3", "4"]]}),
            ("matrices", {"operacion": "Multiplicación A × B",
                          "matriz_a": [["1", "2"], ["3", "4"]],
                          "matriz_b": [["1", "0"], ["0", "1"]]}),
            ("ecuacion-matricial", {"matriz_a": [["1", "0"], ["0", "1"]],
                                    "matriz_b": [["1"], ["2"]]}),
            ("inversa", {"matriz": [["2", "1"], ["1", "1"]],
                         "metodo": "pivoteo"}),
        ]
        for modulo, datos in casos:
            with self.subTest(modulo):
                r = self.enviar({"modulo": modulo, "formato": "png",
                                 "incluir_pasos": False, "datos": datos})
                self.assertEqual(r.status, 200)
                self.assertEqual(r.headers["Content-Type"], "image/png")
                self.assertTrue(r.read().startswith(b"\x89PNG"))

    def test_errores_son_json_400(self):
        casos = [
            {"modulo": "sistema", "formato": "gif", "datos": SISTEMA},
            {"modulo": "nada", "formato": "pdf", "datos": {}},
            {"modulo": "sistema", "formato": "pdf",
             "datos": {**SISTEMA, "matriz": [["1", ""]]}},
            {"modulo": "sistema", "formato": "pdf"},
        ]
        for cuerpo in casos:
            with self.subTest(cuerpo.get("formato"), modulo=cuerpo["modulo"]):
                r = self.enviar(cuerpo)
                self.assertEqual(r.status, 400)
                self.assertIn("error", json.loads(r.read()))
                r.close()


if __name__ == "__main__":
    unittest.main()
