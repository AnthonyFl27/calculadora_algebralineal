"""
exportar.py
Exporta la respuesta de la calculadora como documento PDF o imagen PNG.

Primero convierte el resultado estándar de `metodos/` en un documento (lista
de líneas con estilo) reutilizando los formateadores existentes; después un
escritor lo vuelve PDF o PNG. Ambos formatos se escriben a mano con la
librería estándar (`zlib`, `struct`, `base64`): sin Pillow ni librerías
externas. El texto del PNG usa la fuente bitmap de `_fuente_exportar.py`.

Uso típico:

    contenido, mime, extension = exportar(
        "sistema", resultado, "pdf", modo="fraccion",
        incluir_pasos=True, titulo="Gauss-Jordan",
    )
"""

import base64
import struct
import unicodedata
import zlib
from datetime import datetime
from fractions import Fraction

from features import _fuente_exportar as _fuente
from metodos.general_metodos import (
    formatear,
    matriz_texto,
    texto_comprobacion,
)
from metodos.conversion import NOMBRES_BASE, procedimiento_texto as _conv_texto
from metodos.vectores_matrices import (
    matriz_general_texto,
    procedimiento_texto as _vm_texto,
    vector_texto,
)

FORMATOS = {
    "png": ("image/png", "png"),
    "pdf": ("application/pdf", "pdf"),
}
MODULOS = ("sistema", "conversion", "vectores_matrices")

# Paleta de impresión: único lugar con colores de los archivos exportados
# (no depende del tema de la interfaz; siempre fondo blanco).
PALETA_IMPRESION = {
    "fondo": (255, 255, 255),
    "texto": (30, 35, 45),
    "titulo": (15, 118, 110),
    "gris": (105, 112, 122),
    "seccion_fondo": (226, 240, 238),
    "seccion_texto": (15, 90, 84),
}

# Estilos de línea del documento.
TITULO, SUBTITULO, SECCION, TEXTO = "titulo", "subtitulo", "seccion", "texto"

PNG_ANCHO_MINIMO = 800
PNG_MARGEN = 32
PNG_ALTO_MAXIMO = 60000
PNG_ESPACIO = 4  # píxeles extra entre líneas

PDF_ANCHO, PDF_ALTO, PDF_MARGEN = 595, 842, 40

_TRANSLITERACION = {
    "⁻¹": "^-1", "−": "-", "–": "-", "∞": "inf", "≠": "!=", "≈": "~",
    "←": "<-", "→": "->", "↑": "^", "↓": "v", "↳": "->", "✓": "OK",
    "✗": "X", "✕": "X", "⁻": "^-", "⁰": "^0", "⁴": "^4", "⁵": "^5",
    "⁶": "^6", "⁷": "^7", "⁸": "^8", "⁹": "^9", "─": "-", "│": "|",
    "┌": "+", "┐": "+", "└": "+", "┘": "+", "═": "=",
}


# ======================================================
# DOCUMENTO (modelo de líneas)
# ======================================================

def _lineas(texto):
    return str(texto).rstrip("\n").split("\n")


def _agregar(documento, estilo, texto):
    for linea in _lineas(texto):
        documento.append((estilo, linea))


def _seccion(documento, titulo):
    if documento and documento[-1][1] != "":
        documento.append((TEXTO, ""))
    documento.append((SECCION, titulo))
    documento.append((TEXTO, ""))


def _encabezado(titulo, ahora=None):
    ahora = ahora or datetime.now()
    return [
        (TITULO, titulo),
        (SUBTITULO, "Calculadora de álgebra lineal · "
                    + ahora.strftime("%d/%m/%Y %H:%M")),
    ]


def _texto_tipo_sistema(tipo):
    if tipo == "unica":
        return ("Sistema compatible determinado.\n"
                "Tiene una única solución.")
    if tipo == "infinitas":
        return ("Sistema compatible indeterminado.\n"
                "Tiene infinitas soluciones.")
    return ("Sistema incompatible o inconsistente.\n"
            "No tiene solución.")


def _documento_sistema(resultado, modo, incluir_pasos, titulo):
    documento = []

    _seccion(documento, "Matriz aumentada inicial")
    _agregar(documento, TEXTO, matriz_texto(resultado["matriz_inicial"], modo))

    if incluir_pasos:
        _seccion(documento, f"Procedimiento ({titulo})")
        for paso in resultado["pasos"]:
            _agregar(
                documento, TEXTO,
                f"{paso['operacion']}   (pivote en columna "
                f"{paso['columna'] + 1})",
            )
            _agregar(documento, TEXTO, matriz_texto(paso["matriz"], modo))
            documento.append((TEXTO, ""))
        _seccion(documento, "Matriz final")
        _agregar(documento, TEXTO, matriz_texto(resultado["matriz_final"], modo))

    _seccion(documento, "Resultado")
    _agregar(documento, TEXTO, _texto_tipo_sistema(resultado["tipo"]))
    documento.append((TEXTO, ""))
    _agregar(documento, TEXTO, resultado["soluciones"])

    _seccion(documento, "Comprobación")
    _agregar(
        documento, TEXTO,
        texto_comprobacion(resultado["comprobacion"], modo),
    )
    return documento


def _documento_conversion(resultado, incluir_pasos):
    documento = []
    entrada, salida = resultado["base_entrada"], resultado["base_salida"]

    _seccion(documento, "Datos de entrada")
    _agregar(
        documento, TEXTO,
        f"Número: {resultado['numero_entrada']}\n"
        f"Base de entrada: {entrada} ({NOMBRES_BASE[entrada]})\n"
        f"Base de salida: {salida} ({NOMBRES_BASE[salida]})",
    )

    if incluir_pasos:
        _seccion(documento, "Procedimiento")
        _agregar(documento, TEXTO, _conv_texto(resultado))
    else:
        _seccion(documento, "Resultado")
        _agregar(documento, TEXTO, f"Resultado: {resultado['resultado']}")
    return documento


_NOMBRES_ENTRADA = {
    "vectores": "Vectores", "objetivo": "Vector objetivo",
    "vector": "Vector", "vector_a": "Vector a", "vector_b": "Vector b",
    "escalar": "Escalar", "matriz": "Matriz A",
    "matriz_a": "Matriz A", "matriz_b": "Matriz B",
}


def _es_vector(valor):
    return (isinstance(valor, (list, tuple)) and valor
            and not isinstance(valor[0], (list, tuple)))


def _entradas_texto(entradas, modo):
    lineas = []
    for clave, valor in entradas.items():
        nombre = _NOMBRES_ENTRADA.get(clave, clave)
        if isinstance(valor, (int, Fraction)):
            lineas.append(f"{nombre} = {formatear(valor, modo)}")
        elif _es_vector(valor):
            lineas.append(f"{nombre} = {vector_texto(valor, modo)}")
        elif clave == "vectores":
            for i, vector in enumerate(valor, 1):
                lineas.append(f"v{i} = {vector_texto(vector, modo)}")
        else:
            lineas.append(f"{nombre}:")
            lineas.append(matriz_general_texto(valor, modo))
    return "\n".join(lineas)


def _resultado_vm(datos, modo):
    """Resultado final (sin pasos) de cualquier operación del módulo."""
    operacion = datos["operacion"]
    resultado = datos["resultado"]

    if operacion in ("suma_vectores", "resta_vectores", "escalar_vector"):
        return "Resultado: " + vector_texto(resultado, modo)
    if operacion == "combinacion_lineal":
        if not datos["es_combinacion"]:
            return "No es combinación lineal: el sistema es incompatible."
        cabecera = ("Sí es combinación lineal (infinitas elecciones de "
                    "escalares); una elección particular es:"
                    if datos["tipo_solucion"] == "infinitas"
                    else "Sí es combinación lineal. Los escalares son:")
        return "\n".join(
            [cabecera]
            + [f"c{i + 1} = {formatear(e, modo)}"
               for i, e in enumerate(resultado)]
        )
    if operacion == "ecuacion_matricial":
        if datos["tipo_solucion"] == "incompatible":
            return "La ecuación matricial no tiene solución."
        return "Solución X:\n" + matriz_general_texto(resultado, modo)
    if operacion == "matriz_inversa":
        if not datos["existe"]:
            return "La inversa NO existe. " + datos["motivo"]
        return "A⁻¹ =\n" + matriz_general_texto(resultado, modo)
    return "Resultado:\n" + matriz_general_texto(resultado, modo)


def _documento_vectores_matrices(datos, modo, incluir_pasos):
    documento = []

    _seccion(documento, "Datos de entrada")
    _agregar(documento, TEXTO, _entradas_texto(datos["entradas"], modo))

    if incluir_pasos:
        _seccion(documento, "Procedimiento y resultado")
        lineas = _lineas(_vm_texto(datos, modo))
        # Se quita el título subrayado con "=" que ya trae el procedimiento.
        if len(lineas) > 2 and set(lineas[1]) == {"="}:
            lineas = lineas[3:]
        _agregar(documento, TEXTO, "\n".join(lineas))
    else:
        _seccion(documento, "Resultado")
        _agregar(documento, TEXTO, _resultado_vm(datos, modo))
    return documento


_TITULOS_OPERACION = {
    "suma_vectores": "Suma de vectores",
    "resta_vectores": "Resta de vectores",
    "escalar_vector": "Vector por escalar",
    "combinacion_lineal": "Combinación lineal",
    "suma_matrices": "Suma de matrices",
    "resta_matrices": "Resta de matrices",
    "escalar_matriz": "Matriz por escalar",
    "multiplicacion_matrices": "Multiplicación de matrices",
    "ecuacion_matricial": "Ecuación matricial",
}


def titulo_documento(modulo, resultado, titulo=None):
    """Título del documento (y base del nombre del archivo)."""
    if titulo:
        return titulo
    if modulo == "conversion":
        return "Conversión de bases"
    if modulo == "vectores_matrices":
        operacion = resultado["operacion"]
        if operacion == "matriz_inversa":
            metodo = ("Pivoteo" if resultado["metodo"] == "pivoteo"
                      else "Gauss-Jordan")
            return f"Matriz inversa ({metodo})"
        return _TITULOS_OPERACION.get(operacion, "Vectores y matrices")
    return "Sistema de ecuaciones"


def construir_documento(modulo, resultado, modo="fraccion",
                        incluir_pasos=True, titulo=None, ahora=None):
    """
    Convierte el resultado de `metodos/` en una lista de (estilo, texto).

    modulo: "sistema" (Gauss-Jordan / Pivoteo), "conversion" o
    "vectores_matrices". `titulo` es el nombre que se muestra arriba.
    """
    if modulo not in MODULOS:
        raise ValueError(f"Módulo desconocido para exportar: {modulo}")
    if not resultado:
        raise ValueError("Primero resuelva algo para poder exportarlo.")

    titulo = titulo_documento(modulo, resultado, titulo)

    if modulo == "sistema":
        cuerpo = _documento_sistema(resultado, modo, incluir_pasos, titulo)
    elif modulo == "conversion":
        cuerpo = _documento_conversion(resultado, incluir_pasos)
    else:
        cuerpo = _documento_vectores_matrices(resultado, modo, incluir_pasos)

    return _encabezado(titulo, ahora) + [(TEXTO, "")] + cuerpo


def _ancho_maximo(documento):
    return max((len(texto) for _, texto in documento), default=1)


# ======================================================
# PDF
# ======================================================

def _texto_pdf(texto):
    """Texto compatible con WinAnsi (cp1252) y escapado para PDF."""
    for origen, destino in _TRANSLITERACION.items():
        texto = texto.replace(origen, destino)
    datos = texto.encode("cp1252", errors="replace")
    return (datos.replace(b"\\", b"\\\\").replace(b"(", b"\\(")
            .replace(b")", b"\\)"))


def _color_pdf(color):
    return " ".join(f"{canal / 255:.3f}" for canal in color)


def _paginas_pdf(documento):
    """Reparte las líneas en páginas; devuelve (paginas, tamano_fuente)."""
    util = PDF_ANCHO - 2 * PDF_MARGEN
    # Courier: cada carácter mide 0.6 veces el tamaño de la fuente.
    tamano = max(5.0, min(10.0, util / (0.6 * _ancho_maximo(documento))))
    alto_linea = tamano * 1.35
    por_pagina = int((PDF_ALTO - 2 * PDF_MARGEN) // alto_linea)

    paginas = []
    for inicio in range(0, len(documento), por_pagina):
        paginas.append(documento[inicio:inicio + por_pagina])
    return paginas or [[]], tamano, alto_linea


def _contenido_pagina(lineas, tamano, alto_linea):
    paleta = PALETA_IMPRESION
    partes = []
    y = PDF_ALTO - PDF_MARGEN - tamano

    for estilo, texto in lineas:
        if estilo == SECCION:
            partes.append(
                f"{_color_pdf(paleta['seccion_fondo'])} rg "
                f"{PDF_MARGEN - 4} {y - 3:.2f} "
                f"{PDF_ANCHO - 2 * PDF_MARGEN + 8} {alto_linea:.2f} re f"
            )
        fuente, color, escala = {
            TITULO: ("F2", paleta["titulo"], 1.5),
            SUBTITULO: ("F1", paleta["gris"], 1.0),
            SECCION: ("F2", paleta["seccion_texto"], 1.0),
        }.get(estilo, ("F1", paleta["texto"], 1.0))

        if texto:
            partes.append(
                f"BT /{fuente} {tamano * escala:.2f} Tf "
                f"{_color_pdf(color)} rg {PDF_MARGEN} {y:.2f} Td "
                f"({_texto_pdf(texto).decode('latin-1')}) Tj ET"
            )
        y -= alto_linea * (1.5 if estilo == TITULO else 1.0)

    return "\n".join(partes).encode("latin-1")


def exportar_pdf(documento):
    """Devuelve los bytes de un PDF (A4, Courier) con el documento."""
    paginas, tamano, alto_linea = _paginas_pdf(documento)

    objetos = [None]  # el índice 0 no se usa (los objetos empiezan en 1)

    def nuevo(contenido):
        objetos.append(contenido)
        return len(objetos) - 1

    catalogo = nuevo(None)
    arbol = nuevo(None)
    regular = nuevo(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier "
        b"/Encoding /WinAnsiEncoding >>"
    )
    negrita = nuevo(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold "
        b"/Encoding /WinAnsiEncoding >>"
    )

    referencias = []
    for lineas in paginas:
        flujo = zlib.compress(_contenido_pagina(lineas, tamano, alto_linea))
        contenido = nuevo(
            b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(flujo)
            + flujo + b"\nendstream"
        )
        pagina = nuevo(
            (f"<< /Type /Page /Parent {arbol} 0 R "
             f"/MediaBox [0 0 {PDF_ANCHO} {PDF_ALTO}] "
             f"/Resources << /Font << /F1 {regular} 0 R /F2 {negrita} 0 R >> >> "
             f"/Contents {contenido} 0 R >>").encode("ascii")
        )
        referencias.append(pagina)

    objetos[catalogo] = f"<< /Type /Catalog /Pages {arbol} 0 R >>".encode()
    kids = " ".join(f"{r} 0 R" for r in referencias)
    objetos[arbol] = (
        f"<< /Type /Pages /Kids [{kids}] /Count {len(referencias)} >>"
    ).encode()

    salida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posiciones = [0]
    for numero in range(1, len(objetos)):
        posiciones.append(len(salida))
        salida += f"{numero} 0 obj\n".encode() + objetos[numero] + b"\nendobj\n"

    inicio_xref = len(salida)
    salida += f"xref\n0 {len(objetos)}\n".encode()
    salida += b"0000000000 65535 f \n"
    for posicion in posiciones[1:]:
        salida += f"{posicion:010d} 00000 n \n".encode()
    salida += (
        f"trailer\n<< /Size {len(objetos)} /Root {catalogo} 0 R >>\n"
        f"startxref\n{inicio_xref}\n%%EOF\n"
    ).encode()
    return bytes(salida)


# ======================================================
# PNG
# ======================================================

_cache_fuente = {}


def _glifos(nombre):
    """Tabla {carácter: [alfa por fila]} de la fuente (se decodifica una vez)."""
    if nombre not in _cache_fuente:
        datos = zlib.decompress(base64.b64decode(getattr(_fuente, nombre)))
        tamano = _fuente.ANCHO * _fuente.ALTO
        _cache_fuente[nombre] = {
            caracter: datos[i * tamano:(i + 1) * tamano]
            for i, caracter in enumerate(_fuente.CARACTERES)
        }
    return _cache_fuente[nombre]


_cache_filas = {}


def _filas_glifo(caracter, negrita, color, fondo):
    """Filas RGB (bytes) de un glifo mezclado entre color y fondo."""
    clave = (caracter, negrita, color, fondo)
    if clave not in _cache_filas:
        tabla = _glifos("NEGRITA" if negrita else "REGULAR")
        alfas = tabla.get(caracter) or tabla["?"]
        ancho = _fuente.ANCHO
        filas = []
        for fila in range(_fuente.ALTO):
            pixeles = bytearray()
            for a in alfas[fila * ancho:(fila + 1) * ancho]:
                for canal in range(3):
                    pixeles.append(
                        (color[canal] * a + fondo[canal] * (255 - a)) // 255
                    )
            filas.append(bytes(pixeles))
        _cache_filas[clave] = filas
    return _cache_filas[clave]


def _fragmento(chunk, datos):
    cuerpo = chunk + datos
    return (struct.pack(">I", len(datos)) + cuerpo
            + struct.pack(">I", zlib.crc32(cuerpo) & 0xFFFFFFFF))


def exportar_png(documento):
    """Devuelve los bytes de un PNG RGB con el documento dibujado."""
    paleta = PALETA_IMPRESION
    ancho_celda, alto_celda = _fuente.ANCHO, _fuente.ALTO
    ancho = max(PNG_ANCHO_MINIMO,
                2 * PNG_MARGEN + _ancho_maximo(documento) * ancho_celda)
    alto_linea = alto_celda + PNG_ESPACIO
    alto = 2 * PNG_MARGEN + len(documento) * alto_linea

    if alto > PNG_ALTO_MAXIMO:
        raise ValueError(
            "La respuesta es demasiado larga para una imagen PNG. "
            "Exporte en PDF o desmarque «Incluir pasos»."
        )

    estilos = {
        TITULO: (paleta["titulo"], True, paleta["fondo"]),
        SUBTITULO: (paleta["gris"], False, paleta["fondo"]),
        SECCION: (paleta["seccion_texto"], True, paleta["seccion_fondo"]),
        TEXTO: (paleta["texto"], False, paleta["fondo"]),
    }

    papel = bytes(paleta["fondo"])
    margen = papel * PNG_MARGEN
    util = ancho - 2 * PNG_MARGEN
    margen_alto = (b"\x00" + papel * ancho) * PNG_MARGEN
    barras = []

    for estilo, texto in documento:
        color, negrita, fondo = estilos[estilo]
        texto = texto.expandtabs(4)
        glifos = [_filas_glifo(c, negrita, color, fondo) for c in texto]
        # Solo la barra de sección pinta su fondo en todo el ancho útil.
        sobrante = bytes(fondo) * (util - len(texto) * ancho_celda)
        relleno = (b"\x00" + margen + bytes(fondo) * util + margen)
        relleno *= PNG_ESPACIO // 2

        barras.append(relleno)
        for fila in range(alto_celda):
            barras.append(
                b"\x00" + margen + b"".join(g[fila] for g in glifos)
                + sobrante + margen
            )
        barras.append(relleno)

    crudo = margen_alto + b"".join(barras) + margen_alto
    cabecera = struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _fragmento(b"IHDR", cabecera)
        + _fragmento(b"IDAT", zlib.compress(crudo, 6))
        + _fragmento(b"IEND", b"")
    )


# ======================================================
# FUNCIÓN PRINCIPAL
# ======================================================

def nombre_archivo(base, formato, ahora=None):
    """Nombre sugerido, p. ej. gauss-jordan-20260930-1530.pdf."""
    ahora = ahora or datetime.now()
    sin_acentos = unicodedata.normalize("NFKD", base).encode(
        "ascii", "ignore").decode("ascii")
    limpio = "-".join(
        "".join(c if c.isalnum() else " " for c in sin_acentos.lower()).split()
    )
    return f"{limpio}-{ahora.strftime('%Y%m%d-%H%M')}.{FORMATOS[formato][1]}"


def exportar(modulo, resultado, formato, modo="fraccion",
             incluir_pasos=True, titulo=None):
    """
    Genera el archivo. Devuelve (bytes, tipo_mime, extension).
    Lanza ValueError (en español) si el formato o los datos no son válidos.
    """
    formato = (formato or "").lower()
    if formato not in FORMATOS:
        raise ValueError("Formato de exportación no válido. Use PNG o PDF.")

    documento = construir_documento(
        modulo, resultado, modo, incluir_pasos, titulo
    )
    escribir = exportar_png if formato == "png" else exportar_pdf
    mime, extension = FORMATOS[formato]
    return escribir(documento), mime, extension
