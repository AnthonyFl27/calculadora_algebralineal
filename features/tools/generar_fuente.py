"""
Herramienta de desarrollo (NO se usa al ejecutar la calculadora).

Rasteriza una fuente monoespaciada a una tabla de glifos en escala de grises
y la guarda, comprimida, en features/_fuente_exportar.py. Así el PNG exportado
se dibuja solo con la librería estándar. Requiere Pillow únicamente aquí:

    python features/tools/generar_fuente.py

Fuente base: Hack (licencia MIT / Bitstream Vera); ✓ ✗ ✕ salen de Symbola.
"""

import base64
import zlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REGULAR = "/usr/share/fonts/source-foundry-hack-fonts/Hack-Regular.ttf"
NEGRITA = "/usr/share/fonts/source-foundry-hack-fonts/Hack-Bold.ttf"
SIMBOLOS = "/usr/share/fonts/gdouros-symbola/Symbola.ttf"
TAMANO = 18
ANCHO, ALTO, BASE = 11, 22, 17
ESPECIALES = "✓✗✕"

CARACTERES = (
    "".join(chr(c) for c in range(32, 127))
    + "áéíóúüñÁÉÍÓÚÜÑ¿¡°²³¹×÷·—–−∞≠≈←↑→↓↳✓✗✕⁻⁰⁴⁵⁶⁷⁸⁹─│┌┐└┘═‹›"
)


def dibujar(caracter, ruta_fuente):
    fuente = ImageFont.truetype(ruta_fuente, TAMANO)
    if caracter in ESPECIALES:
        fuente = ImageFont.truetype(SIMBOLOS, TAMANO - 2)
    imagen = Image.new("L", (ANCHO, ALTO), 0)
    ImageDraw.Draw(imagen).text(
        (ANCHO // 2, BASE), caracter, fill=255, font=fuente, anchor="ms"
    )
    return imagen.tobytes()


def tabla(ruta_fuente):
    datos = b"".join(dibujar(c, ruta_fuente) for c in CARACTERES)
    return base64.b64encode(zlib.compress(datos, 9)).decode("ascii")


def partir(texto, largo=76):
    return "\n".join(
        f'    "{texto[i:i + largo]}"' for i in range(0, len(texto), largo)
    )


salida = Path(__file__).resolve().parent.parent / "_fuente_exportar.py"
salida.write_text(
    '"""\n'
    "Fuente bitmap monoespaciada para el PNG exportado (generada con\n"
    "features/tools/generar_fuente.py; no editar a mano).\n\n"
    "Basada en Hack (licencia MIT / Bitstream Vera). Cada glifo es una\n"
    "rejilla ANCHO×ALTO en escala de grises (0-255), comprimida con zlib y\n"
    "codificada en base64.\n"
    '"""\n\n'
    f"ANCHO = {ANCHO}\nALTO = {ALTO}\nBASE = {BASE}\n"
    f"CARACTERES = {CARACTERES!r}\n\n"
    f"REGULAR = (\n{partir(tabla(REGULAR))}\n)\n\n"
    f"NEGRITA = (\n{partir(tabla(NEGRITA))}\n)\n",
    encoding="utf-8",
)
print(salida, salida.stat().st_size, "bytes")
