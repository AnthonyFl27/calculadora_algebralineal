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
