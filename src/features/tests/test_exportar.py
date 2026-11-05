import struct
import sys
import unittest
import zlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from features import exportar as ex
from metodos.biseccion import biseccion
from metodos.conversion import resolver as convertir
from metodos.determinante import determinante
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
    # Las gráficas no llevan texto (su "texto" es un dict de datos).
    return "\n".join(texto for estilo, texto in documento
                     if estilo != ex.GRAFICA)


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
        # Fecha fija: la fecha real (p. ej. 04/11/2026) puede contener "1/2".
        texto = texto_documento(ex.construir_documento(
            "sistema", r, "decimal", True, ahora=datetime(2026, 9, 30, 15, 30)))
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

    def test_determinante_con_y_sin_pasos(self):
        matriz = [[0, 1, 2], [1, 0, 3], [4, -3, 8]]
        for metodo, marca in (("lu", "Intercambio F1 ↔ F2"),
                              ("cofactores", "menor M")):
            r = determinante(matriz, metodo)
            con = texto_documento(ex.construir_documento(
                "determinante", r, "fraccion", True))
            sin = texto_documento(ex.construir_documento(
                "determinante", r, "fraccion", False))
            with self.subTest(metodo):
                self.assertIn(f"Determinante ({'LU' if metodo == 'lu' else 'Cofactores'})", con)
                self.assertIn(marca, con)
                self.assertIn("det(A) = -2", con)
                self.assertIn("Comprobación", con)
                if metodo == "lu":
                    self.assertIn("P·A = L·U ✓", con)
                    self.assertIn("L·U =", con)
                self.assertNotIn(marca, sin)
                self.assertIn("det(A) = -2", sin)

    def test_determinante_singular_y_archivos(self):
        r = determinante([[1, 2], [2, 4]], "lu")
        texto = texto_documento(ex.construir_documento("determinante", r))
        self.assertIn("singular", texto)
        for formato in ("png", "pdf"):
            datos, _, _ = ex.exportar("determinante", r, formato)
            self.assertGreater(len(datos), 100)

    def test_biseccion_con_y_sin_pasos(self):
        r = biseccion("x^4 - 5x^3 + 0.5x^2 - 11x + 10", 0.55, 1.1, 0.0001)
        con = texto_documento(ex.construir_documento(
            "biseccion", r, "fraccion", True))
        sin = texto_documento(ex.construir_documento(
            "biseccion", r, "fraccion", False))
        self.assertIn("Método de bisección", con)
        self.assertIn("Tabla de iteraciones", con)
        self.assertIn("Iteración 13", con)
        self.assertIn("0.7639709473", con)
        self.assertIn("Comprobación", con)
        self.assertNotIn("Tabla de iteraciones", sin)
        self.assertIn("Raíz aproximada: x = 0.7639709473", sin)
        self.assertIn("Iteraciones: 13", sin)
        self.assertEqual(
            ex.titulo_documento("biseccion", r), "Método de bisección")
        for formato in ("png", "pdf"):
            for pasos in (True, False):
                datos, _, _ = ex.exportar(
                    "biseccion", r, formato, incluir_pasos=pasos)
                self.assertGreater(len(datos), 100)

    def test_biseccion_con_aviso(self):
        r = biseccion("1/x", -1, 2, "1e-4")
        texto = texto_documento(ex.construir_documento(
            "biseccion", r, incluir_pasos=False))
        self.assertIn("Aviso:", texto)
        self.assertIn("Continuidad", texto)
        self.assertIn("Posible polo", texto)
        leer_png(ex.exportar("biseccion", r, "png", incluir_pasos=False)[0])
        for formato in ("png", "pdf"):
            for pasos in (True, False):
                datos, _, _ = ex.exportar(
                    "biseccion", r, formato, incluir_pasos=pasos)
                self.assertGreater(len(datos), 100)

    def test_biseccion_incluye_la_grafica(self):
        r = biseccion("x^2 - 2", 1, 2, "1e-4")
        for pasos in (True, False):
            doc = ex.construir_documento("biseccion", r, incluir_pasos=pasos)
            graficas = [t for e, t in doc if e == ex.GRAFICA]
            self.assertEqual(len(graficas), 1)
            self.assertIs(graficas[0], r["grafica"])
            self.assertIn("Gráfica de f(x)", texto_documento(doc))
            self.assertIn("Círculo rojo: raíz aproximada x = 1.41",
                          texto_documento(doc))
        self.assertNotIn("discontinua", texto_documento(doc))
        malo = biseccion("tan(x)", 1, 2, "1e-4")
        self.assertIn("Línea naranja discontinua", texto_documento(
            ex.construir_documento("biseccion", malo, incluir_pasos=False)))

    def test_png_con_grafica_dibuja_pixeles_de_la_curva(self):
        r = biseccion("x^2 - 2", 1, 2, "1e-4")
        ancho, alto, crudo = leer_png(
            ex.exportar("biseccion", r, "png", incluir_pasos=False)[0])
        self.assertEqual(len(crudo), alto * (1 + ancho * 3))
        curva = bytes(ex.PALETA_IMPRESION["grafica_curva"])
        rojo = bytes(ex.PALETA_IMPRESION["grafica_raiz"])
        self.assertIn(curva, crudo)     # píxeles de la curva
        self.assertIn(rojo, crudo)      # marcador de la raíz
        sin_grafica = alto - ex.PNG_GRAFICA_ALTO
        self.assertGreater(sin_grafica, 100)

    def test_pdf_con_grafica_trae_trazos_vectoriales(self):
        r = biseccion("tan(x)", 1, 2, "1e-4")
        for pasos in (True, False):
            pdf = ex.exportar("biseccion", r, "pdf", incluir_pasos=pasos)[0]
            flujos = []
            resto = pdf
            while b"stream\n" in resto:
                _, resto = resto.split(b"stream\n", 1)
                datos, resto = resto.split(b"\nendstream", 1)
                flujos.append(zlib.decompress(datos))
            contenido = b"\n".join(flujos)
            self.assertIn(b" l S", contenido)     # polilínea de la curva
            self.assertIn(b" c f", contenido)     # círculos (puntos y raíz)
            self.assertIn(b"[", contenido)        # línea discontinua del polo

    def test_titulo_de_seccion_viaja_con_la_figura(self):
        r = biseccion("x^2 - 2", 1, 2, "1e-4")
        doc = ex.construir_documento("biseccion", r, incluir_pasos=True)
        paginas, _, alto_linea = ex._paginas_pdf(doc)
        for pagina in paginas:
            estilos = [e for e, _ in pagina]
            if ex.GRAFICA in estilos:
                i = estilos.index(ex.GRAFICA)
                self.assertEqual(pagina[i - 2][0], ex.SECCION)
            self.assertNotEqual(pagina[-1][0], ex.SECCION)
            self.assertNotEqual(pagina[-2][0], ex.SECCION)

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
