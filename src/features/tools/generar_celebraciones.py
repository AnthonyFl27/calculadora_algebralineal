"""
Herramienta de desarrollo (NO se usa al ejecutar la calculadora).

Convierte los videos de la mascota (src/features/tools/videos/*.mp4, con fondo
gris claro) en hojas de sprites PNG con transparencia limpia + un JSON con la
duración de cada cuadro, que la web dibuja en un <canvas> al resolver:

    python src/features/tools/generar_celebraciones.py

Requiere ffmpeg instalado, solo aquí y solo para leer los videos. El fondo
no se recorta "por color" (eso deja un borde claro alrededor de cada figura):
cada píxel se separa como mezcla de fondo + un color de la paleta del dibujo,
así el borde suavizado queda con su color real y la opacidad correcta.
"""

import json
import struct
import subprocess
import zlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
VIDEOS = RAIZ / "src" / "features" / "tools" / "videos"
SALIDA = RAIZ / "src" / "web" / "media"

# Zona del video (x, y, ancho, alto, en píxeles del original 1920 px) que
# contiene a la mascota en todos los cuadros; el recorte final es automático.
CLIPS = {
    "festejo": (620, 160, 600, 540),
    "flag_clawd": (740, 160, 400, 470),
}
ESCALA = 0.42      # el doble del tamaño en pantalla (nítido en pantallas HiDPI)
FPS = 30
MAX_ANCHO_HOJA = 4096


def leer_cuadros(video, recorte):
    x, y, w, h = recorte
    ancho = int(w * ESCALA) // 2 * 2
    alto = int(h * ESCALA) // 2 * 2
    crudo = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vf",
         f"crop={w}:{h}:{x}:{y},scale={ancho}:{alto}:flags=area",
         "-r", str(FPS), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        check=True, capture_output=True,
    ).stdout
    tamano = ancho * alto * 3
    return ancho, alto, [crudo[i:i + tamano] for i in range(0, len(crudo), tamano)]


def color_fondo(cuadro, ancho, alto):
    esquinas = [0, ancho - 1, (alto - 1) * ancho, alto * ancho - 1]
    return tuple(
        sorted(cuadro[p * 3 + c] for p in esquinas)[1] for c in range(3)
    )


def distancia(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def paleta(cuadros, ancho, alto, fondo):
    """Colores planos del dibujo: píxeles lejos del fondo e iguales a sus vecinos."""
    conteo = {}
    for cuadro in cuadros[::3]:
        for y in range(alto - 1):
            for x in range(ancho - 1):
                i = (y * ancho + x) * 3
                c = cuadro[i:i + 3]
                if distancia(c, fondo) < 60:
                    continue
                if (distancia(c, cuadro[i + 3:i + 6]) > 6
                        or distancia(c, cuadro[i + ancho * 3:i + ancho * 3 + 3]) > 6):
                    continue
                clave = tuple(v // 12 for v in c)
                suma = conteo.setdefault(clave, [0, 0, 0, 0])
                suma[0] += 1
                for k in range(3):
                    suma[k + 1] += c[k]
    centros = []
    for n, r, g, b in sorted(conteo.values(), reverse=True):
        if n < 25:          # el confeti es chico: basta con unos pocos píxeles
            break
        color = (r / n, g / n, b / n)
        if all(distancia(color, otro) > 40 for otro in centros):
            centros.append(color)
    return centros


def separar(c, fondo, colores):
    """(r, g, b, a) del píxel c como mezcla del fondo con un color de la paleta
    (borde con el fondo) o de dos colores de la paleta (borde interno, opaco)."""
    mejor = None
    for f in colores:
        d = (f[0] - fondo[0], f[1] - fondo[1], f[2] - fondo[2])
        v = (c[0] - fondo[0], c[1] - fondo[1], c[2] - fondo[2])
        a = max(0.0, min(1.0, (v[0] * d[0] + v[1] * d[1] + v[2] * d[2])
                         / (d[0] ** 2 + d[1] ** 2 + d[2] ** 2)))
        error = sum((v[k] - a * d[k]) ** 2 for k in range(3))
        if mejor is None or error < mejor[0]:
            mejor = (error, f, a)
    error, f, a = mejor
    if error > 300:
        for i, f1 in enumerate(colores):
            for f2 in colores[i + 1:]:
                d = (f2[0] - f1[0], f2[1] - f1[1], f2[2] - f1[2])
                v = (c[0] - f1[0], c[1] - f1[1], c[2] - f1[2])
                t = max(0.0, min(1.0, (v[0] * d[0] + v[1] * d[1] + v[2] * d[2])
                                 / (d[0] ** 2 + d[1] ** 2 + d[2] ** 2)))
                e = sum((v[k] - t * d[k]) ** 2 for k in range(3))
                if e < error:
                    error, a = e, 1.0
                    f = tuple(f1[k] + t * d[k] for k in range(3))
    if a > 0.93:
        a = 1.0
    elif a < 0.1:
        return (0, 0, 0, 0)
    return (round(f[0]), round(f[1]), round(f[2]), round(a * 255))


def a_rgba(cuadro, ancho, alto, fondo, colores):
    salida = bytearray(ancho * alto * 4)
    for p in range(ancho * alto):
        c = cuadro[p * 3:p * 3 + 3]
        if distancia(c, fondo) < 8:
            continue
        salida[p * 4:p * 4 + 4] = bytes(separar(c, fondo, colores))
    return salida


def caja(cuadros, ancho, alto):
    x0, y0, x1, y1 = ancho, alto, -1, -1
    for cuadro in cuadros:
        for y in range(alto):
            fila = cuadro[y * ancho * 4:(y + 1) * ancho * 4]
            xs = [x for x in range(ancho) if fila[x * 4 + 3] > 24]
            if xs:
                x0, x1 = min(x0, xs[0]), max(x1, xs[-1])
                y0, y1 = min(y0, y), max(y1, y)
    return x0, y0, x1 + 1, y1 + 1


def recortar(cuadro, ancho, x0, y0, x1, y1):
    return b"".join(
        bytes(cuadro[(y * ancho + x0) * 4:(y * ancho + x1) * 4]) for y in range(y0, y1)
    )


def casi_iguales(a, b):
    distintos = 0
    for i in range(0, len(a), 4):
        if a[i + 3] == 0 and b[i + 3] == 0:
            continue
        if max(abs(a[i + k] - b[i + k]) for k in range(4)) > 40:
            distintos += 1
            if distintos > 3:
                return False
    return True


def png(ruta, ancho, alto, rgba):
    filas = b"".join(
        b"\x00" + rgba[y * ancho * 4:(y + 1) * ancho * 4] for y in range(alto)
    )

    def bloque(tipo, datos):
        return (struct.pack(">I", len(datos)) + tipo + datos
                + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF))

    ruta.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + bloque(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 6, 0, 0, 0))
        + bloque(b"IDAT", zlib.compress(filas, 9))
        + bloque(b"IEND", b"")
    )


def generar(nombre, recorte):
    ancho, alto, crudos = leer_cuadros(VIDEOS / f"{nombre}.mp4", recorte)
    fondo = color_fondo(crudos[0], ancho, alto)
    colores = paleta(crudos, ancho, alto, fondo)
    cuadros = [a_rgba(c, ancho, alto, fondo, colores) for c in crudos]

    x0, y0, x1, y1 = caja(cuadros, ancho, alto)
    if x0 <= 1 or y0 <= 1 or x1 >= ancho - 1 or y1 >= alto - 1:
        print(f"  ¡Aviso! {nombre}: el dibujo toca el borde de la zona; amplíala en CLIPS.")
    w, h = x1 - x0, y1 - y0
    cuadros = [recortar(c, ancho, x0, y0, x1, y1) for c in cuadros]

    # Cuadros repetidos seguidos se guardan una vez con más duración.
    unicos, duraciones = [], []
    for cuadro in cuadros:
        if unicos and casi_iguales(unicos[-1], cuadro):
            duraciones[-1] += 1
        else:
            unicos.append(cuadro)
            duraciones.append(1)

    columnas = max(1, min(len(unicos), MAX_ANCHO_HOJA // w))
    filas = -(-len(unicos) // columnas)
    hoja = bytearray(columnas * w * filas * h * 4)
    for n, cuadro in enumerate(unicos):
        cx, cy = (n % columnas) * w, (n // columnas) * h
        for y in range(h):
            inicio = ((cy + y) * columnas * w + cx) * 4
            hoja[inicio:inicio + w * 4] = cuadro[y * w * 4:(y + 1) * w * 4]

    SALIDA.mkdir(parents=True, exist_ok=True)
    png(SALIDA / f"{nombre}.png", columnas * w, filas * h, bytes(hoja))
    (SALIDA / f"{nombre}.json").write_text(json.dumps({
        "ancho": w, "alto": h, "columnas": columnas, "densidad": 2,
        "duraciones": [round(d * 1000 / FPS) for d in duraciones],
    }) + "\n", encoding="utf-8")
    print(f"  {nombre}: {len(cuadros)} cuadros -> {len(unicos)} únicos de {w}×{h} px, "
          f"paleta: {[tuple(round(v) for v in c) for c in colores]}")


if __name__ == "__main__":
    for nombre, recorte in CLIPS.items():
        generar(nombre, recorte)
