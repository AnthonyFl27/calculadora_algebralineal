import struct
import sys
import unittest
import zlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from features import exportar as ex
from metodos.conversion import resolver as convertir
from metodos.gauss_jordan import resolver as gauss_jordan
from metodos.pivote import resolver as pivote
from metodos.vectores_matrices import (
    combinacion_lineal,
    ecuacion_matricial,
    matriz_inversa,
    multiplicar_matrices,
    suma_vectores,
)

SISTEMA = [[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]]


def leer_png(datos):
    """Valida la estructura del PNG y devuelve (ancho, alto, crudo)."""
    assert datos[:8] == b"\x89PNG\r\n\x1a\n"
    posicion, trozos = 8, {}
    while posicion < len(datos):
        largo, = struct.unpack(">I", datos[posicion:posicion + 4])
        nombre = datos[posicion + 4:posicion + 8]
        cuerpo = datos[posicion + 8:posicion + 8 + largo]
        crc, = struct.unpack(
            ">I", datos[posicion + 8 + largo:posicion + 12 + largo]
        )
        assert crc == zlib.crc32(nombre + cuerpo) & 0xFFFFFFFF
        trozos[nombre] = cuerpo
        posicion += 12 + largo
    ancho, alto = struct.unpack(">II", trozos[b"IHDR"][:8])
    return ancho, alto, zlib.decompress(trozos[b"IDAT"])


def texto_documento(documento):
    return "\n".join(texto for _, texto in documento)


class DocumentoTest(unittest.TestCase):
    def test_sistema_con_y_sin_pasos(self):
        for resolver, nombre in ((gauss_jordan, "Gauss-Jordan"),
                                 (pivote, "Pivoteo")):
            r = resolver(SISTEMA)
            con = texto_documento(
                ex.construir_documento("sistema", r, "fraccion", True, nombre))
            sin = texto_documento(
                ex.construir_documento("sistema", r, "fraccion", False, nombre))
            self.assertIn(nombre, con)
            self.assertIn("Procedimiento", con)
            self.assertNotIn("Procedimiento", sin)
            for texto in (con, sin):
                self.assertIn("x1 = 2", texto)
                self.assertIn("COMPROBACIÓN CORRECTA", texto)

    def test_sistema_incompatible_no_tiene_comprobacion(self):
        r = gauss_jordan([[1, 1, 1], [1, 1, 2]])
        texto = texto_documento(ex.construir_documento("sistema", r))
        self.assertIn("No tiene solución", texto)
        self.assertIn("No es posible comprobar", texto)

    def test_modo_decimal(self):
        r = gauss_jordan([[2, 1, 1], [1, 3, 2]], "decimal")
        texto = texto_documento(
            ex.construir_documento("sistema", r, "decimal", True))
        self.assertIn("0.5", texto)
        self.assertNotIn("1/2", texto)

    def test_conversion(self):
        r = convertir("10", 10, 2)
        con = texto_documento(ex.construir_documento("conversion", r))
        sin = texto_documento(
            ex.construir_documento("conversion", r, incluir_pasos=False))
        self.assertIn("1010", con)
        self.assertIn("Divisiones sucesivas", con)
        self.assertIn("1010", sin)
        self.assertNotIn("Divisiones sucesivas", sin)

    def test_vectores_y_matrices_todas_las_operaciones(self):
        casos = [
            suma_vectores([[1, 2], [3, 4]]),
            multiplicar_matrices([[1, 2], [3, 4]], [[1, 0], [0, 1]]),
            combinacion_lineal([[1, 0], [0, 1]], [3, 4]),
            combinacion_lineal([[1, 0], [2, 0]], [0, 1]),
            ecuacion_matricial([[1, 0], [0, 1]], [[1], [2]]),
            matriz_inversa([[2, 1], [1, 1]]),
            matriz_inversa([[1, 1], [1, 1]], "pivoteo"),
        ]
        for datos in casos:
            for pasos in (True, False):
                with self.subTest(datos["operacion"], pasos=pasos):
                    doc = ex.construir_documento(
                        "vectores_matrices", datos, "fraccion", pasos)
                    texto = texto_documento(doc)
                    self.assertIn("Datos de entrada", texto)
                    # El título subrayado del procedimiento no se repite.
                    self.assertNotIn("=====", texto)

    def test_inversa_resultado(self):
        datos = matriz_inversa([[2, 1], [1, 1]])
        texto = texto_documento(ex.construir_documento(
            "vectores_matrices", datos, incluir_pasos=False))
        self.assertIn("A⁻¹", texto)

    def test_errores(self):
        with self.assertRaises(ValueError):
            ex.construir_documento("otro", {"a": 1})
        with self.assertRaises(ValueError):
            ex.construir_documento("sistema", None)
        with self.assertRaises(ValueError):
            ex.exportar("sistema", gauss_jordan(SISTEMA), "gif")
        with self.assertRaises(ValueError):
            ex.exportar("sistema", gauss_jordan(SISTEMA), None)


class PdfTest(unittest.TestCase):
    def test_estructura(self):
        datos, mime, extension = ex.exportar(
            "sistema", gauss_jordan(SISTEMA), "pdf", titulo="Gauss-Jordan")
        self.assertEqual((mime, extension), ("application/pdf", "pdf"))
        self.assertTrue(datos.startswith(b"%PDF-"))
        self.assertTrue(datos.rstrip().endswith(b"%%EOF"))
        inicio = int(datos.split(b"startxref\n")[1].split(b"\n")[0])
        self.assertTrue(datos[inicio:].startswith(b"xref"))

    def test_xref_apunta_a_cada_objeto(self):
        datos = ex.exportar("sistema", gauss_jordan(SISTEMA), "pdf")[0]
        inicio = int(datos.split(b"startxref\n")[1].split(b"\n")[0])
        lineas = datos[inicio:].split(b"\n")
        total = int(lineas[1].split()[1])
        for numero in range(1, total):
            posicion = int(lineas[2 + numero][:10])
            self.assertTrue(
                datos[posicion:].startswith(b"%d 0 obj" % numero))

    def test_varias_paginas(self):
        grande = [[i + j + 1 for j in range(6)] + [1] for i in range(6)]
        documento = ex.construir_documento("sistema", gauss_jordan(grande))
        paginas, _, _ = ex._paginas_pdf(documento)
        self.assertGreater(len(paginas), 1)
        datos = ex.exportar_pdf(documento)
        self.assertEqual(datos.count(b"/Type /Page "), len(paginas))

    def test_acentos_y_parentesis_escapados(self):
        self.assertEqual(ex._texto_pdf("á(ñ)"), b"\xe1\\(\xf1\\)")
        self.assertEqual(ex._texto_pdf("A⁻¹ ✓ −"), b"A^-1 OK -")


class PngTest(unittest.TestCase):
    def test_estructura(self):
        datos, mime, extension = ex.exportar(
            "sistema", gauss_jordan(SISTEMA), "png")
        self.assertEqual((mime, extension), ("image/png", "png"))
        ancho, alto, crudo = leer_png(datos)
        self.assertGreaterEqual(ancho, ex.PNG_ANCHO_MINIMO)
        self.assertEqual(len(crudo), alto * (1 + ancho * 3))

    def test_sin_pasos_es_mas_corto(self):
        r = gauss_jordan(SISTEMA)
        alto_con = leer_png(ex.exportar("sistema", r, "png")[0])[1]
        alto_sin = leer_png(
            ex.exportar("sistema", r, "png", incluir_pasos=False)[0])[1]
        self.assertLess(alto_sin, alto_con)

    def test_todos_los_caracteres_tienen_glifo(self):
        tabla = ex._glifos("REGULAR")
        for caracter in "áéíóúñÑ¿¡×÷−∞≠←→✓✗⁻¹─│┌┐└┘":
            self.assertIn(caracter, tabla)
            self.assertTrue(any(tabla[caracter]), caracter)

    def test_demasiado_largo(self):
        documento = [(ex.TEXTO, "x")] * 5000
        with self.assertRaises(ValueError):
            ex.exportar_png(documento)

    def test_modulos_restantes(self):
        for modulo, datos in (
            ("conversion", convertir("FF", 16, 10)),
            ("vectores_matrices", matriz_inversa([[2, 1], [1, 1]])),
        ):
            leer_png(ex.exportar(modulo, datos, "png")[0])


class NombreTest(unittest.TestCase):
    def test_nombre_archivo(self):
        ahora = datetime(2026, 9, 30, 15, 30)
        self.assertEqual(
            ex.nombre_archivo("Gauss-Jordan", "pdf", ahora),
            "gauss-jordan-20260930-1530.pdf")
        self.assertEqual(
            ex.nombre_archivo("Vectores: Combinación lineal", "png", ahora),
            "vectores-combinacion-lineal-20260930-1530.png")


if __name__ == "__main__":
    unittest.main()
