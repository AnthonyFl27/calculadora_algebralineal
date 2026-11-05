import struct
import sys
import unittest
import zlib
from datetime import datetime
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from features import exportar as ex
from metodos.biseccion import biseccion
from metodos.conversion import resolver as convertir
from metodos.determinante import determinante
from metodos.escenas import (
    escena_determinante,
    escena_inversa,
    escena_producto,
    escena_sistema,
    escena_vectores,
)
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


def sistema_con_escena(filas):
    r = gauss_jordan([[Fraction(x) for x in f] for f in filas])
    r["escena"] = escena_sistema(r)
    return r


def hay_color_cercano(crudo, ancho, color, tolerancia=40):
    """¿Hay un píxel casi de `color`? (las rectas inclinadas llevan suavizado)."""
    paso = 1 + ancho * 3
    for fila in range(len(crudo) // paso):
        pixeles = crudo[fila * paso + 1:(fila + 1) * paso]
        for i in range(0, len(pixeles), 3):
            if all(abs(pixeles[i + k] - color[k]) <= tolerancia for k in range(3)):
                return True
    return False


def flujos_pdf(pdf):
    flujos, resto = [], pdf
    while b"stream\n" in resto:
        _, resto = resto.split(b"stream\n", 1)
        datos, resto = resto.split(b"\nendstream", 1)
        flujos.append(zlib.decompress(datos))
    return b"\n".join(flujos)


class EscenaExportarTest(unittest.TestCase):
    """Gráficas geométricas (spec 014) en los archivos exportados."""

    def test_sistema_incluye_la_grafica_y_su_leyenda(self):
        r = sistema_con_escena([[1, 1, 3], [1, -1, 1]])
        for pasos in (True, False):
            doc = ex.construir_documento("sistema", r, incluir_pasos=pasos)
            graficas = [t for e, t in doc if e == ex.GRAFICA]
            self.assertEqual(len(graficas), 1)
            self.assertIs(graficas[0], r["escena"])
            texto = texto_documento(doc)
            self.assertIn("Gráfica del sistema", texto)
            self.assertIn("Verde azulado: (1) x1 + x2 = 3", texto)
            self.assertIn("Rojo: Solución (2, 1)", texto)

    def test_el_aviso_va_en_la_leyenda(self):
        r = sistema_con_escena([[1, 1, 3], [2, 2, 5]])
        texto = texto_documento(ex.construir_documento("sistema", r))
        self.assertIn("paralelas", texto)

    def test_sin_escena_o_no_disponible_no_hay_seccion(self):
        for escena in (None, {"disponible": False, "motivo": "x"}):
            r = gauss_jordan([[Fraction(x) for x in f] for f in SISTEMA])
            r["escena"] = escena
            doc = ex.construir_documento("sistema", r)
            self.assertFalse([1 for e, _ in doc if e == ex.GRAFICA])
            self.assertNotIn("Gráfica del sistema", texto_documento(doc))

    def test_png_dibuja_las_rectas_y_la_solucion(self):
        r = sistema_con_escena([[1, 1, 3], [1, -1, 1]])
        ancho, alto, crudo = leer_png(ex.exportar("sistema", r, "png", incluir_pasos=False)[0])
        self.assertEqual(len(crudo), alto * (1 + ancho * 3))
        serie = ex.PALETA_IMPRESION["escena_serie"]
        for color in (serie[0], serie[1], ex.PALETA_IMPRESION["escena_solucion"]):
            self.assertTrue(hay_color_cercano(crudo, ancho, color), color)

    def test_pdf_trae_las_rectas(self):
        r = sistema_con_escena([[1, 1, 3], [1, -1, 1]])
        for pasos in (True, False):
            contenido = flujos_pdf(ex.exportar("sistema", r, "pdf", incluir_pasos=pasos)[0])
            self.assertIn(b" l S", contenido)      # rectas
            self.assertIn(b" c f", contenido)      # punto solución

    def test_poligono_se_rellena_en_png_y_pdf(self):
        from features import grafica_exportar as g
        plan = [("poligono", [(10, 10), (60, 10), (60, 40), (10, 40)], (200, 220, 240), (0, 0, 200), 1)]
        filas = g.rasterizar(plan, 80, 60, (255, 255, 255), {}, 8, 16)
        self.assertEqual(filas[25][35 * 3:35 * 3 + 3], bytes((200, 220, 240)))   # relleno
        self.assertEqual(filas[55][5 * 3:5 * 3 + 3], bytes((255, 255, 255)))     # afuera
        pdf = g.comandos_pdf(plan, 0, 100, 8, lambda t: t.encode())
        self.assertIn(" f", pdf)
        self.assertIn(" h", pdf)

    def test_recorte_de_poligono(self):
        from features.escena_exportar import recortar_poligono
        pts = recortar_poligono([(-10, -10), (20, -10), (20, 20), (-10, 20)], 0, 0, 10, 10)
        self.assertEqual(sorted(pts), [(0, 0), (0, 10), (10, 0), (10, 10)])
        self.assertEqual(recortar_poligono([(20, 20), (30, 20), (30, 30)], 0, 0, 10, 10), [])


class Escena3DExportarTest(unittest.TestCase):

    def resultado(self, filas):
        return sistema_con_escena(filas)

    def test_proyeccion_ortogonal(self):
        from features.escena_exportar import proyectar_3d
        cam = {"azimut": 0, "elevacion": 0}
        self.assertEqual(proyectar_3d([1, 2, 3], [0, 0, 0], cam), (1, 3, 2))   # y es la profundidad
        a, arriba, prof = proyectar_3d([0, 1, 0], [0, 0, 0], {"azimut": 90, "elevacion": 0})
        self.assertAlmostEqual(a, -1)
        self.assertAlmostEqual(prof, 0)
        # Con la cámara elevada, lo más lejano se ve más arriba.
        _, arriba, _ = proyectar_3d([0, 1, 0], [0, 0, 0], {"azimut": 0, "elevacion": 90})
        self.assertAlmostEqual(arriba, 1)

    def test_sistema_3x3_se_exporta_con_planos_rellenos(self):
        r = self.resultado([[1, 1, 1, 6], [0, 1, 1, 5], [1, 0, 1, 4]])
        for pasos in (True, False):
            doc = ex.construir_documento("sistema", r, incluir_pasos=pasos)
            self.assertEqual(len([1 for e, _ in doc if e == ex.GRAFICA]), 1)
            texto = texto_documento(doc)
            self.assertIn("Azul: (3) x1 + x3 = 4", texto)
            self.assertIn("Rojo: Solución (1, 2, 3)", texto)
        pdf = flujos_pdf(ex.exportar("sistema", r, "pdf", incluir_pasos=False)[0])
        self.assertGreaterEqual(pdf.count(b" h f"), 3)           # tres planos rellenos
        ancho, alto, crudo = leer_png(ex.exportar("sistema", r, "png", incluir_pasos=False)[0])
        self.assertEqual(len(crudo), alto * (1 + ancho * 3))
        for color in ex.PALETA_IMPRESION["escena_serie"][:3]:
            self.assertTrue(hay_color_cercano(crudo, ancho, color), color)

    def test_los_ejes_quedan_encima_de_los_planos(self):
        from features.escena_exportar import plan_escena
        r = self.resultado([[1, 1, 1, 6], [0, 1, 1, 5], [1, 0, 1, 4]])
        plan = plan_escena(r["escena"], 720, 400, 8, 16, ex.PALETA_IMPRESION)
        ultimo_poligono = max(i for i, p in enumerate(plan) if p[0] == "poligono")
        eje = ex.PALETA_IMPRESION["grafica_eje"]
        indices = [i for i, p in enumerate(plan) if p[0] == "linea" and p[5] == eje and p[6] == 1.5]
        self.assertTrue(indices and min(indices) > ultimo_poligono)

    def test_sistemas_sin_solucion_se_exportan(self):
        for filas in ([[1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 5]],
                      [[1, 1, 1, 6], [1, 1, 1, 7]],
                      [[1, 1, 1, 6], [2, 2, 2, 12], [3, 3, 3, 18]]):
            r = self.resultado(filas)
            for formato in ("png", "pdf"):
                self.assertGreater(len(ex.exportar("sistema", r, formato, incluir_pasos=False)[0]), 500)


class VectoresExportarTest(unittest.TestCase):

    def test_las_operaciones_de_vectores_traen_su_grafica(self):
        V = lambda *a: [Fraction(x) for x in a]
        casos = ((suma_vectores([V(1, 2), V(3, 4)]), "Gráfica de la suma", "Rojo: Suma = (4, 6)"),
                 (suma_vectores([V(1, 2, 3), V(3, 4, 5)]), "Gráfica de la suma", "Verde azulado: v1 = (1, 2, 3)"),
                 (combinacion_lineal([V(1, 0), V(0, 1)], V(3, 2)), "Gráfica de la combinación lineal",
                  "Rojo: b = (3, 2)"))
        for r, titulo, leyenda in casos:
            r["escena"] = escena_vectores(r)
            for formato in ("png", "pdf"):
                for pasos in (True, False):
                    self.assertGreater(len(ex.exportar("vectores_matrices", r, formato,
                                                       incluir_pasos=pasos)[0]), 500)
            texto = texto_documento(ex.construir_documento("vectores_matrices", r, incluir_pasos=False))
            self.assertIn(titulo, texto)
            self.assertIn(leyenda, texto)

    def test_flechas_dibujan_puntas_rellenas(self):
        V = lambda *a: [Fraction(x) for x in a]
        r = suma_vectores([V(1, 2), V(3, 4)])
        r["escena"] = escena_vectores(r)
        contenido = flujos_pdf(ex.exportar("vectores_matrices", r, "pdf", incluir_pasos=False)[0])
        self.assertGreaterEqual(contenido.count(b" h f"), 4)     # paralelogramo y puntas

    def test_sin_escena_no_hay_seccion(self):
        V = lambda *a: [Fraction(x) for x in a]
        r = suma_vectores([V(1, 2), V(3, 4)])
        doc = ex.construir_documento("vectores_matrices", r)
        self.assertFalse([1 for e, _ in doc if e == ex.GRAFICA])

    def test_mas_de_3_componentes_no_agrega_grafica(self):
        V = lambda *a: [Fraction(x) for x in a]
        r = suma_vectores([V(1, 2, 3, 4), V(1, 1, 1, 1)])
        r["escena"] = escena_vectores(r)
        doc = ex.construir_documento("vectores_matrices", r)
        self.assertFalse([1 for e, _ in doc if e == ex.GRAFICA])


class DeterminanteExportarTest(unittest.TestCase):

    def resultado(self, filas):
        r = determinante([[Fraction(x) for x in f] for f in filas], "lu")
        r["escena"] = escena_determinante(r)
        return r

    def test_incluye_la_grafica_con_y_sin_pasos(self):
        for filas, leyenda in (([[1, 3], [2, 4]], "Área = |det A| = 2"),
                               ([[1, 0, 0], [0, 2, 0], [0, 0, 3]], "Volumen = |det A| = 6")):
            r = self.resultado(filas)
            for pasos in (True, False):
                doc = ex.construir_documento("determinante", r, incluir_pasos=pasos)
                self.assertEqual(len([1 for e, _ in doc if e == ex.GRAFICA]), 1)
                texto = texto_documento(doc)
                self.assertIn("Gráfica del determinante", texto)
                self.assertIn(leyenda, texto)
            for formato in ("png", "pdf"):
                self.assertGreater(len(ex.exportar("determinante", r, formato, incluir_pasos=False)[0]), 500)

    def test_paralelepipedo_con_seis_caras_en_el_pdf(self):
        r = self.resultado([[1, 0, 0], [0, 2, 0], [0, 0, 3]])
        contenido = flujos_pdf(ex.exportar("determinante", r, "pdf", incluir_pasos=False)[0])
        self.assertGreaterEqual(contenido.count(b" h f"), 6 + 3)     # caras y puntas

    def test_4x4_no_agrega_grafica(self):
        r = self.resultado([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        doc = ex.construir_documento("determinante", r)
        self.assertFalse([1 for e, _ in doc if e == ex.GRAFICA])


class InversaExportarTest(unittest.TestCase):

    def resultado(self, filas):
        r = matriz_inversa([[Fraction(x) for x in f] for f in filas])
        r["escena"] = escena_inversa(r)
        return r

    def test_incluye_la_grafica(self):
        for filas, leyenda in (([[1, 2], [3, 4]], "Imagen por A^-1: área 1/|det A| = 1/2"),
                               ([[2, 0, 0], [0, 1, 0], [0, 0, 4]], "Imagen por A^-1: volumen")):
            r = self.resultado(filas)
            for pasos in (True, False):
                doc = ex.construir_documento("vectores_matrices", r, incluir_pasos=pasos)
                self.assertEqual(len([1 for e, _ in doc if e == ex.GRAFICA]), 1)
                texto = texto_documento(doc)
                self.assertIn("Gráfica de la matriz inversa", texto)
                self.assertIn("Cuadrado unitario" if len(filas) == 2 else "Cubo unitario", texto)
            for formato in ("png", "pdf"):
                self.assertGreater(len(ex.exportar("vectores_matrices", r, formato, incluir_pasos=False)[0]), 500)

    def test_singular_tambien_se_exporta(self):
        r = self.resultado([[1, 2], [2, 4]])
        texto = texto_documento(ex.construir_documento("vectores_matrices", r, incluir_pasos=False))
        self.assertIn("no es invertible", texto)

    def test_4x4_no_agrega_grafica(self):
        r = self.resultado([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        self.assertFalse([1 for e, _ in ex.construir_documento("vectores_matrices", r) if e == ex.GRAFICA])


class EcuacionMatricialExportarTest(unittest.TestCase):

    def resultado(self, a, b):
        r = ecuacion_matricial([[Fraction(x) for x in f] for f in a],
                               [[Fraction(x) for x in f] for f in b])
        r["escenas"] = [escena_sistema(x) for x in r["resoluciones"]]
        return r

    def test_una_gráfica_por_columna_de_b(self):
        r = self.resultado([[1, 1], [1, -1]], [[3, 5], [1, 1]])
        for pasos in (True, False):
            doc = ex.construir_documento("vectores_matrices", r, incluir_pasos=pasos)
            self.assertEqual(len([1 for e, _ in doc if e == ex.GRAFICA]), 2)
            texto = texto_documento(doc)
            self.assertIn("Gráfica de la columna 1 de B", texto)
            self.assertIn("Gráfica de la columna 2 de B", texto)
            self.assertIn("Rojo: Solución (3, 2)", texto)
        for formato in ("png", "pdf"):
            self.assertGreater(len(ex.exportar("vectores_matrices", r, formato, incluir_pasos=False)[0]), 500)

    def test_una_sola_columna_no_numera(self):
        r = self.resultado([[1, 1], [1, -1]], [[3], [1]])
        texto = texto_documento(ex.construir_documento("vectores_matrices", r, incluir_pasos=False))
        self.assertIn("Gráfica del sistema", texto)
        self.assertNotIn("columna 1 de B", texto)

    def test_limite_de_columnas_graficadas(self):
        columnas = ex.MAX_ESCENAS_EXPORTADAS + 2
        r = self.resultado([[1, 0], [0, 1]], [[k + 1 for k in range(columnas)], [1] * columnas])
        doc = ex.construir_documento("vectores_matrices", r, incluir_pasos=False)
        self.assertEqual(len([1 for e, _ in doc if e == ex.GRAFICA]), ex.MAX_ESCENAS_EXPORTADAS)
        self.assertIn("Se grafican las primeras", texto_documento(doc))


class ProductoExportarTest(unittest.TestCase):

    def resultado(self, a, b):
        r = multiplicar_matrices([[Fraction(x) for x in f] for f in a],
                                 [[Fraction(x) for x in f] for f in b])
        r["escena"] = escena_producto(r)
        return r

    def test_incluye_la_grafica(self):
        for a, b in (([[1, 2], [3, 4]], [[0, 1], [1, 0]]),
                     ([[2, 0, 0], [0, 1, 0], [0, 0, 1]], [[1, 0, 0], [0, 3, 0], [0, 0, 1]])):
            r = self.resultado(a, b)
            for pasos in (True, False):
                doc = ex.construir_documento("vectores_matrices", r, incluir_pasos=pasos)
                self.assertEqual(len([1 for e, _ in doc if e == ex.GRAFICA]), 1)
                texto = texto_documento(doc)
                self.assertIn("Gráfica del producto A × B", texto)
                self.assertIn("Imagen por A·B", texto)
            for formato in ("png", "pdf"):
                self.assertGreater(len(ex.exportar("vectores_matrices", r, formato, incluir_pasos=False)[0]), 500)

    def test_no_cuadradas_no_agregan_grafica(self):
        r = self.resultado([[1, 2, 3], [3, 4, 5]], [[0, 1], [1, 0], [1, 1]])
        self.assertFalse([1 for e, _ in ex.construir_documento("vectores_matrices", r) if e == ex.GRAFICA])


if __name__ == "__main__":
    unittest.main()
