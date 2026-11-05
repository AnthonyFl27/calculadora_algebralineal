"""
grafica_exportar.py
Dibuja la gráfica de la bisección en los archivos exportados (PNG y PDF).

Los datos (curva, ventana, marcas, puntos) ya vienen calculados por
`metodos/grafica.py`. Aquí solo se decide el diseño una vez, como un *plan* de
primitivas en coordenadas de lienzo (origen arriba a la izquierda, y hacia
abajo), y dos intérpretes lo pintan:

- `rasterizar()` lo dibuja píxel a píxel (líneas con suavizado, círculos y la
  fuente bitmap del exportador) y devuelve las filas RGB para el PNG;
- `comandos_pdf()` lo convierte en operadores vectoriales de PDF.

Solo librería estándar. Los colores los pone `exportar.py` (paleta de
impresión): este módulo no define ninguno.

Primitivas del plan (tuplas):
    ("rect", x0, y0, x1, y1, color)
    ("linea", x0, y0, x1, y1, color, grosor, guion)      guion = None | (on, off)
    ("poli", [(x, y), ...], color, grosor)
    ("circulo", x, y, radio, relleno, borde)
    ("texto", x, y, texto, ancla, color, negrita)        y = centro vertical
"""

import math

PUNTOS_NUMERADOS = 5     # cuántas iteraciones se rotulan (c1, c2, ...)


def plan_grafica(g, ancho, alto, cw, ch, paleta):
    """Primitivas de la gráfica `g` en un lienzo ancho × alto.

    `cw` y `ch` son el ancho y alto de un carácter de texto en esas unidades
    (píxeles en el PNG, puntos en el PDF)."""

    etiquetas_y = [texto for _, texto in g["marcas_y"]] or ["0"]
    izq = max(len(t) for t in etiquetas_y) * cw + 0.9 * cw
    der, arr = 0.8 * cw, 0.7 * ch
    aba = 1.9 * ch
    util_w, util_h = ancho - izq - der, alto - arr - aba

    def sx(x):
        return izq + (x - g["x_min"]) / (g["x_max"] - g["x_min"]) * util_w

    def sy(y):
        return arr + (g["y_max"] - y) / (g["y_max"] - g["y_min"]) * util_h

    plan = [("rect", izq, arr, izq + util_w, arr + util_h, paleta["grafica_fondo"])]

    # Bandas de tramos fuera del dominio (antes de la rejilla).
    for d in g["discontinuidades"]:
        x1, x2 = sx(d["desde"]), sx(d["hasta"])
        if x2 - x1 > 3:
            plan.append(("rect", x1, arr, x2, arr + util_h, paleta["grafica_banda"]))

    for valor, texto in g["marcas_x"]:
        x = sx(valor)
        plan.append(("linea", x, arr, x, arr + util_h, paleta["grafica_rejilla"], 1, None))
        plan.append(("texto", x, arr + util_h + 0.9 * ch, texto, "middle",
                     paleta["gris"], False))
    for valor, texto in g["marcas_y"]:
        y = sy(valor)
        plan.append(("linea", izq, y, izq + util_w, y, paleta["grafica_rejilla"], 1, None))
        plan.append(("texto", izq - 0.4 * cw, y, texto, "end", paleta["gris"], False))

    # Ejes y = 0 y, si cae dentro, x = 0.
    plan.append(("linea", izq, sy(0), izq + util_w, sy(0), paleta["grafica_eje"], 1.5, None))
    if g["x_min"] < 0 < g["x_max"]:
        plan.append(("linea", sx(0), arr, sx(0), arr + util_h, paleta["grafica_eje"], 1.5, None))

    # Discontinuidades puntuales: línea discontinua.
    guion = (max(4.0, 0.5 * cw * 1.2), max(3.0, 0.4 * cw * 1.2))
    for d in g["discontinuidades"]:
        x1, x2 = sx(d["desde"]), sx(d["hasta"])
        if x2 - x1 <= 3:
            x = (x1 + x2) / 2
            plan.append(("linea", x, arr, x, arr + util_h,
                         paleta["grafica_discontinuidad"], 1.6, guion))

    for tramo in g["curva"]:
        plan.append(("poli", [(sx(x), sy(y)) for x, y in tramo],
                     paleta["grafica_curva"], max(2.0, ch / 10)))

    # Marco.
    for x0, y0, x1, y1 in ((izq, arr, izq + util_w, arr), (izq, arr + util_h, izq + util_w, arr + util_h),
                           (izq, arr, izq, arr + util_h), (izq + util_w, arr, izq + util_w, arr + util_h)):
        plan.append(("linea", x0, y0, x1, y1, paleta["grafica_marco"], 1, None))

    # Puntos c de las iteraciones; las primeras se numeran.
    radio = max(3.0, ch / 7)
    for p in g["iteraciones"]:
        plan.append(("circulo", sx(p["x"]), sy(p["y"]), radio,
                     paleta["grafica_punto"], paleta["fondo"]))
    ocupadas = []                      # cajas (x0, y0, x1, y1) ya rotuladas
    for p in g["iteraciones"][:PUNTOS_NUMERADOS]:
        x, y = sx(p["x"]), sy(p["y"])
        y_texto = min(max(y - 0.9 * ch, arr + 0.6 * ch), arr + util_h - 0.6 * ch)
        texto = f"c{p['i']}"
        x0 = x + radio + 2
        caja = (x0, y_texto - ch / 2, x0 + len(texto) * cw, y_texto + ch / 2)
        if any(caja[0] < o[2] and caja[2] > o[0] and caja[1] < o[3] and caja[3] > o[1]
               for o in ocupadas):
            continue                   # se omite si pisaría otra etiqueta
        ocupadas.append(caja)
        plan.append(("texto", x0, y_texto, texto, "start", paleta["texto"], True))

    # Raíz aproximada.
    plan.append(("circulo", sx(g["raiz"]["x"]), sy(g["raiz"]["y"]), radio * 1.7,
                 paleta["grafica_raiz"], paleta["fondo"]))
    return plan


# ======================================================
# PNG (rasterizador)
# ======================================================

def _mezclar(lienzo, ancho, alto, x, y, color, a):
    if 0 <= x < ancho and 0 <= y < alto and a > 0:
        if a > 1:
            a = 1
        i = (y * ancho + x) * 3
        for k in range(3):
            lienzo[i + k] = int(color[k] * a + lienzo[i + k] * (1 - a) + 0.5)


def _linea_wu(lienzo, ancho, alto, x0, y0, x1, y1, color):
    """Línea de 1 píxel con suavizado (algoritmo de Xiaolin Wu)."""

    pendiente = abs(y1 - y0) > abs(x1 - x0)
    if pendiente:
        x0, y0, x1, y1 = y0, x0, y1, x1
    if x0 > x1:
        x0, x1, y0, y1 = x1, x0, y1, y0
    dx, dy = x1 - x0, y1 - y0
    gradiente = dy / dx if dx else 1.0

    def punto(x, y, a):
        if pendiente:
            _mezclar(lienzo, ancho, alto, y, x, color, a)
        else:
            _mezclar(lienzo, ancho, alto, x, y, color, a)

    x_ini, x_fin = int(round(x0)), int(round(x1))
    y_cur = y0 + gradiente * (x_ini - x0)
    for x in range(x_ini, x_fin + 1):
        entero = math.floor(y_cur)
        frac = y_cur - entero
        punto(x, entero, 1 - frac)
        punto(x, entero + 1, frac)
        y_cur += gradiente


def _trazo(lienzo, ancho, alto, x0, y0, x1, y1, color, grosor):
    """Segmento con grosor: varias líneas de Wu paralelas."""

    largo = math.hypot(x1 - x0, y1 - y0)
    if largo == 0:
        return
    nx, ny = -(y1 - y0) / largo, (x1 - x0) / largo
    n = max(1, round(grosor))
    for k in range(n):
        d = k - (n - 1) / 2
        _linea_wu(lienzo, ancho, alto, x0 + nx * d, y0 + ny * d,
                  x1 + nx * d, y1 + ny * d, color)


def _trazo_guion(lienzo, ancho, alto, x0, y0, x1, y1, color, grosor, guion):
    largo = math.hypot(x1 - x0, y1 - y0)
    if largo == 0:
        return
    ux, uy = (x1 - x0) / largo, (y1 - y0) / largo
    on, off = guion
    t = 0.0
    while t < largo:
        fin = min(t + on, largo)
        _trazo(lienzo, ancho, alto, x0 + ux * t, y0 + uy * t,
               x0 + ux * fin, y0 + uy * fin, color, grosor)
        t += on + off


def _circulo(lienzo, ancho, alto, cx, cy, radio, color):
    for y in range(int(cy - radio) - 1, int(cy + radio) + 2):
        for x in range(int(cx - radio) - 1, int(cx + radio) + 2):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            _mezclar(lienzo, ancho, alto, x, y, color, radio + 0.5 - d)


def _texto(lienzo, ancho, alto, x, y, texto, ancla, color, negrita,
           glifos, cw, ch):
    tabla = glifos("NEGRITA" if negrita else "REGULAR")
    largo = len(texto) * cw
    x0 = x - largo / 2 if ancla == "middle" else (x - largo if ancla == "end" else x)
    y0 = int(round(y - ch / 2))
    x0 = int(round(x0))
    for k, caracter in enumerate(texto):
        alfas = tabla.get(caracter) or tabla["?"]
        for fila in range(ch):
            for col in range(cw):
                a = alfas[fila * cw + col]
                if a:
                    _mezclar(lienzo, ancho, alto, x0 + k * cw + col, y0 + fila,
                             color, a / 255)


def rasterizar(plan, ancho, alto, fondo, glifos, cw, ch):
    """Filas RGB (una `bytes` por fila de píxeles) de la gráfica dibujada."""

    ancho, alto = int(ancho), int(alto)
    lienzo = bytearray(bytes(fondo) * (ancho * alto))

    for primitiva in plan:
        tipo = primitiva[0]
        if tipo == "rect":
            _, x0, y0, x1, y1, color = primitiva
            x0, x1 = max(0, int(round(x0))), min(ancho, int(round(x1)))
            fila = bytes(color) * max(0, x1 - x0)
            for y in range(max(0, int(round(y0))), min(alto, int(round(y1)))):
                lienzo[(y * ancho + x0) * 3:(y * ancho + x1) * 3] = fila
        elif tipo == "linea":
            _, x0, y0, x1, y1, color, grosor, guion = primitiva
            if guion:
                _trazo_guion(lienzo, ancho, alto, x0, y0, x1, y1, color, grosor, guion)
            else:
                _trazo(lienzo, ancho, alto, x0, y0, x1, y1, color, grosor)
        elif tipo == "poli":
            _, puntos, color, grosor = primitiva
            for (x0, y0), (x1, y1) in zip(puntos, puntos[1:]):
                _trazo(lienzo, ancho, alto, x0, y0, x1, y1, color, grosor)
        elif tipo == "circulo":
            _, x, y, radio, relleno, borde = primitiva
            _circulo(lienzo, ancho, alto, x, y, radio + 1.5, borde)
            _circulo(lienzo, ancho, alto, x, y, radio, relleno)
        elif tipo == "texto":
            _, x, y, texto, ancla, color, negrita = primitiva
            _texto(lienzo, ancho, alto, x, y, texto, ancla, color, negrita,
                   glifos, cw, ch)

    paso = ancho * 3
    return [bytes(lienzo[i:i + paso]) for i in range(0, len(lienzo), paso)]


# ======================================================
# PDF (operadores vectoriales)
# ======================================================

def _rg(color):
    return " ".join(f"{canal / 255:.3f}" for canal in color)


def comandos_pdf(plan, x_pdf, y_arriba, tamano, texto_pdf):
    """Operadores PDF de la gráfica. (x_pdf, y_arriba) es la esquina superior
    izquierda en puntos PDF; `texto_pdf` escapa el texto (WinAnsi)."""

    def X(x):
        return f"{x_pdf + x:.2f}"

    def Y(y):
        return f"{y_arriba - y:.2f}"

    k = 0.5522847498   # círculo con 4 curvas de Bézier
    salida = []
    for primitiva in plan:
        tipo = primitiva[0]
        if tipo == "rect":
            _, x0, y0, x1, y1, color = primitiva
            salida.append(f"{_rg(color)} rg {X(x0)} {Y(y1)} {x1 - x0:.2f} {y1 - y0:.2f} re f")
        elif tipo == "linea":
            _, x0, y0, x1, y1, color, grosor, guion = primitiva
            patron = f"[{guion[0]:.1f} {guion[1]:.1f}] 0 d" if guion else "[] 0 d"
            salida.append(f"{_rg(color)} RG {grosor * 0.6:.2f} w {patron} "
                          f"{X(x0)} {Y(y0)} m {X(x1)} {Y(y1)} l S [] 0 d")
        elif tipo == "poli":
            _, puntos, color, grosor = primitiva
            trazo = " ".join(f"{X(x)} {Y(y)} {'m' if i == 0 else 'l'}"
                             for i, (x, y) in enumerate(puntos))
            salida.append(f"{_rg(color)} RG {grosor * 0.6:.2f} w 1 j 1 J {trazo} S")
        elif tipo == "circulo":
            _, x, y, radio, relleno, borde = primitiva
            for r, color in ((radio + 1.0, borde), (radio, relleno)):
                c = r * k
                salida.append(
                    f"{_rg(color)} rg {X(x + r)} {Y(y)} m "
                    f"{X(x + r)} {Y(y - c)} {X(x + c)} {Y(y - r)} {X(x)} {Y(y - r)} c "
                    f"{X(x - c)} {Y(y - r)} {X(x - r)} {Y(y - c)} {X(x - r)} {Y(y)} c "
                    f"{X(x - r)} {Y(y + c)} {X(x - c)} {Y(y + r)} {X(x)} {Y(y + r)} c "
                    f"{X(x + c)} {Y(y + r)} {X(x + r)} {Y(y + c)} {X(x + r)} {Y(y)} c f")
        elif tipo == "texto":
            _, x, y, texto, ancla, color, negrita = primitiva
            largo = len(texto) * 0.6 * tamano
            x0 = x - largo / 2 if ancla == "middle" else (x - largo if ancla == "end" else x)
            fuente = "F2" if negrita else "F1"
            salida.append(
                f"BT /{fuente} {tamano:.2f} Tf {_rg(color)} rg "
                f"{X(x0)} {Y(y + 0.33 * tamano)} Td "
                f"({texto_pdf(texto).decode('latin-1')}) Tj ET")
    return "\n".join(salida)
