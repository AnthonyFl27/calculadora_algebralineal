"""
escena_exportar.py
Dibuja las escenas geométricas (spec 014) en los archivos exportados.

La escena (rectas, flechas, puntos, polígonos) ya viene decidida por
`metodos/escena.py` y `escenas.py`. Aquí solo se arma el *plan* de primitivas
en coordenadas de lienzo, el mismo formato que `grafica_exportar.py` (que
tiene los intérpretes de PNG y PDF):

    ("rect", x0, y0, x1, y1, color)
    ("linea", x0, y0, x1, y1, color, grosor, guion)
    ("poli", [(x, y), ...], color, grosor)
    ("poligono", [(x, y), ...], relleno | None, borde, grosor)
    ("circulo", x, y, radio, relleno, borde)
    ("texto", x, y, texto, ancla, color, negrita)

2D usa la ventana inicial con escala igual en x e y. Los colores salen de la
paleta de impresión de `exportar.py`.

Solo librería estándar.
"""

import math

from metodos import escena as E
from metodos.grafica import marcas

MEZCLA_RELLENO = 0.22     # cuánto del color de la serie lleva el relleno


def mezclar(color, fondo, a):
    """Color `color` con opacidad `a` sobre `fondo` (RGB de 0 a 255)."""

    return tuple(round(f + (c - f) * a) for c, f in zip(color, fondo))


def color_serie(paleta, serie):
    if serie == "solucion":
        return paleta["escena_solucion"]
    return paleta["escena_serie"][serie % E.SERIES]


def recortar_poligono(puntos, x0, y0, x1, y1):
    """Recorta un polígono al rectángulo (Sutherland-Hodgman)."""

    def contra(puntos, dentro, cruce):
        salida = []
        for i, actual in enumerate(puntos):
            anterior = puntos[i - 1]
            if dentro(actual):
                if not dentro(anterior):
                    salida.append(cruce(anterior, actual))
                salida.append(actual)
            elif dentro(anterior):
                salida.append(cruce(anterior, actual))
        return salida

    def en_x(valor):
        return lambda a, b: (valor, a[1] + (b[1] - a[1]) * (valor - a[0]) / (b[0] - a[0]))

    def en_y(valor):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (valor - a[1]) / (b[1] - a[1]), valor)

    for dentro, cruce in (
            (lambda p: p[0] >= x0, en_x(x0)), (lambda p: p[0] <= x1, en_x(x1)),
            (lambda p: p[1] >= y0, en_y(y0)), (lambda p: p[1] <= y1, en_y(y1))):
        if not puntos:
            break
        puntos = contra(puntos, dentro, cruce)
    return puntos


def plan_escena(esc, ancho, alto, cw, ch, paleta):
    """Primitivas de la escena `esc` en un lienzo ancho × alto (`cw` y `ch`:
    ancho y alto de un carácter)."""

    if esc["dim"] == 3:
        return _plan_3d(esc, ancho, alto, cw, ch, paleta)
    return _plan_2d(esc, ancho, alto, cw, ch, paleta)


def _plan_2d(esc, ancho, alto, cw, ch, paleta):
    v = esc["ventana"]
    arr, aba, der = 0.7 * ch, 1.9 * ch, 0.8 * cw
    # El ancho de las etiquetas del eje y depende de la escala: se estima
    # con la ventana inicial.
    izq = 6 * cw
    util_w, util_h = ancho - izq - der, alto - arr - aba

    esc_px = min(util_w / (v["x"][1] - v["x"][0]), util_h / (v["y"][1] - v["y"][0]))
    cx, cy = sum(v["x"]) / 2, sum(v["y"]) / 2
    medio_x, medio_y = izq + util_w / 2, arr + util_h / 2
    x_min, x_max = cx - util_w / 2 / esc_px, cx + util_w / 2 / esc_px
    y_min, y_max = cy - util_h / 2 / esc_px, cy + util_h / 2 / esc_px
    visible = {"x": [x_min, x_max], "y": [y_min, y_max]}

    def sx(x):
        return medio_x + (x - cx) * esc_px

    def sy(y):
        return medio_y - (y - cy) * esc_px

    plan = [("rect", izq, arr, izq + util_w, arr + util_h, paleta["grafica_fondo"])]
    for valor, texto in marcas(x_min, x_max, max(3, round(util_w / (8 * cw)))):
        x = sx(valor)
        plan.append(("linea", x, arr, x, arr + util_h, paleta["grafica_rejilla"], 1, None))
        plan.append(("texto", x, arr + util_h + 0.9 * ch, texto, "middle", paleta["gris"], False))
    for valor, texto in marcas(y_min, y_max, max(3, round(util_h / (3.5 * ch)))):
        y = sy(valor)
        plan.append(("linea", izq, y, izq + util_w, y, paleta["grafica_rejilla"], 1, None))
        plan.append(("texto", izq - 0.4 * cw, y, texto, "end", paleta["gris"], False))
    if y_min < 0 < y_max:
        plan.append(("linea", izq, sy(0), izq + util_w, sy(0), paleta["grafica_eje"], 1.5, None))
    if x_min < 0 < x_max:
        plan.append(("linea", sx(0), arr, sx(0), arr + util_h, paleta["grafica_eje"], 1.5, None))

    grosor = max(2.5, ch / 8)
    guion = (max(4.0, 0.6 * cw), max(3.0, 0.5 * cw))
    radio = max(3.0, ch / 7)
    orden = {"poligono": 0, "recta": 1, "segmento": 1, "flecha": 2, "punto": 3}
    rotulos = []

    def trazo(a, b, color, e, g):
        if a is None:
            return
        plan.append(("linea", sx(a[0]), sy(a[1]), sx(b[0]), sy(b[1]), color,
                     g * (1.9 if e.get("grosor") == "fuerte" else 1),
                     guion if e.get("guion") else None))

    for e in sorted(esc["elementos"], key=lambda e: orden[e["tipo"]]):
        color = color_serie(paleta, e["serie"])
        if e["tipo"] == "poligono":
            pts = recortar_poligono([(sx(p[0]), sy(p[1])) for p in e["puntos"]],
                                    izq, arr, izq + util_w, arr + util_h)
            if len(pts) >= 3:
                plan.append(("poligono", pts, mezclar(color, paleta["fondo"], MEZCLA_RELLENO),
                             color, grosor * 0.7))
        elif e["tipo"] == "recta":
            tramo = E.recortar_recta_2d(e["p"], e["d"], visible)
            trazo(tramo[0] if tramo else None, tramo[1] if tramo else None, color, e, grosor)
        elif e["tipo"] == "segmento":
            tramo = E.recortar_segmento_2d(e["a"], e["b"], visible)
            trazo(tramo[0] if tramo else None, tramo[1] if tramo else None, color, e, grosor)
        elif e["tipo"] == "flecha":
            tramo = E.recortar_segmento_2d(e["a"], e["b"], visible)
            trazo(tramo[0] if tramo else None, tramo[1] if tramo else None, color, e, grosor)
            ax, ay, bx, by = sx(e["a"][0]), sy(e["a"][1]), sx(e["b"][0]), sy(e["b"][1])
            largo = math.hypot(bx - ax, by - ay)
            dentro = izq <= bx <= izq + util_w and arr <= by <= arr + util_h
            if largo > 1 and dentro:
                ux, uy, h = (bx - ax) / largo, (by - ay) / largo, min(0.9 * ch, largo * 0.6)
                plan.append(("poligono", [
                    (bx, by),
                    (bx - ux * h - uy * h * 0.45, by - uy * h + ux * h * 0.45),
                    (bx - ux * h + uy * h * 0.45, by - uy * h - ux * h * 0.45)],
                    color, color, 1))
                if e.get("etiqueta"):
                    rotulos.append((bx + 0.5 * cw, by - 0.7 * ch, e["etiqueta"], "start"))
        elif e["tipo"] == "punto":
            px, py = sx(e["p"][0]), sy(e["p"][1])
            if izq <= px <= izq + util_w and arr <= py <= arr + util_h:
                plan.append(("circulo", px, py,
                             radio * (1.5 if e.get("grosor") == "fuerte" else 1.0),
                             color, paleta["fondo"]))
                if e.get("etiqueta"):
                    rotulos.append((px + 0.8 * cw, py - 0.9 * ch, e["etiqueta"], "start"))

    for x, y, texto, ancla in rotulos:
        y = min(max(y, arr + 0.6 * ch), arr + util_h - 0.6 * ch)
        plan.append(("texto", x, y, texto, ancla, paleta["texto"], True))

    for x0, y0, x1, y1 in ((izq, arr, izq + util_w, arr), (izq, arr + util_h, izq + util_w, arr + util_h),
                           (izq, arr, izq, arr + util_h), (izq + util_w, arr, izq + util_w, arr + util_h)):
        plan.append(("linea", x0, y0, x1, y1, paleta["grafica_marco"], 1, None))
    return plan


def proyectar_3d(p, centro, camara):
    """Proyección ortogonal de un punto 3D: (a, arriba, profundidad). Es la
    misma fórmula que `crearEscena3D` en la web: azimut alrededor del eje z y
    elevación de la cámara; profundidad mayor = más lejos."""

    az, el = math.radians(camara["azimut"]), math.radians(camara["elevacion"])
    x, y, z = (p[i] - centro[i] for i in range(3))
    a = x * math.cos(az) - y * math.sin(az)
    b = x * math.sin(az) + y * math.cos(az)
    return (a, z * math.cos(el) + b * math.sin(el),
            b * math.cos(el) - z * math.sin(el))


def _plan_3d(esc, ancho, alto, cw, ch, paleta):
    caja = esc["caja"]
    rangos = [caja["x"], caja["y"], caja["z"]]
    centro = [(r[0] + r[1]) / 2 for r in rangos]
    radio = (rangos[0][1] - rangos[0][0]) / 2 * math.sqrt(3)
    camara = esc["camara"]
    izq, der, arr, aba = 0.8 * cw, 0.8 * cw, 0.7 * ch, 0.7 * ch
    util_w, util_h = ancho - izq - der, alto - arr - aba
    escala = min(util_w, util_h) / (2 * radio) * 0.95
    medio_x, medio_y = izq + util_w / 2, arr + util_h / 2

    def proy(p):
        a, arriba, prof = proyectar_3d(p, centro, camara)
        return medio_x + a * escala, medio_y - arriba * escala, prof

    plan = [("rect", izq, arr, izq + util_w, arr + util_h, paleta["grafica_fondo"])]
    rx, ry, rz = rangos

    def linea(a, b, color, grosor=1, guion=None):
        pa, pb = proy(a), proy(b)
        plan.append(("linea", pa[0], pa[1], pb[0], pb[1], color, grosor, guion))

    # Suelo con rejilla y aristas de la caja.
    for valor, _ in marcas(rx[0], rx[1], 5):
        linea([valor, ry[0], rz[0]], [valor, ry[1], rz[0]], paleta["grafica_rejilla"])
    for valor, _ in marcas(ry[0], ry[1], 5):
        linea([rx[0], valor, rz[0]], [rx[1], valor, rz[0]], paleta["grafica_rejilla"])
    for i in (0, 1):
        for j in (0, 1):
            linea([rx[i], ry[j], rz[0]], [rx[i], ry[j], rz[1]], paleta["grafica_rejilla"])
            linea([rx[0], ry[i], rz[j]], [rx[1], ry[i], rz[j]], paleta["grafica_rejilla"])
            linea([rx[i], ry[0], rz[j]], [rx[i], ry[1], rz[j]], paleta["grafica_rejilla"])

    # Ejes por el origen con su nombre y marcas. Se dibujan después de los
    # polígonos (en PNG/PDF el relleno es opaco y los taparía).
    rotulos = []
    base = len(plan)
    for k, rango in enumerate(rangos):
        ini, fin = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
        ini[k], fin[k] = rango[0], rango[1]
        linea(ini, fin, paleta["grafica_eje"], 1.5)
        punta = proy(fin)
        rotulos.append((punta[0] + 0.4 * cw, punta[1] - 0.7 * ch, esc["ejes"][k],
                        paleta["texto"], True))
        for valor, texto in marcas(rango[0], rango[1], 4):
            if valor == 0:
                continue
            q = [0.0, 0.0, 0.0]
            q[k] = valor
            s = proy(q)
            rotulos.append((s[0] + 0.3 * cw, s[1] + 0.9 * ch, texto, paleta["gris"], False))

    plan_ejes = plan[base:]
    del plan[base:]

    grosor = max(2.5, ch / 8)
    guion = (max(4.0, 0.6 * cw), max(3.0, 0.5 * cw))
    radio_punto = max(3.0, ch / 7)
    caja_px = (izq, arr, izq + util_w, arr + util_h)

    poligonos = []
    for e in esc["elementos"]:
        if e["tipo"] == "poligono":
            pts = [proy(p) for p in e["puntos"]]
            poligonos.append((sum(p[2] for p in pts) / len(pts), e, pts))
    for _, e, pts in sorted(poligonos, key=lambda t: -t[0]):
        color = color_serie(paleta, e["serie"])
        recortado = recortar_poligono([(p[0], p[1]) for p in pts], *caja_px)
        if len(recortado) >= 3:
            plan.append(("poligono", recortado,
                         mezclar(color, paleta["fondo"], MEZCLA_RELLENO),
                         color, grosor * 0.7))

    plan.extend(plan_ejes)

    trazos = []
    for e in esc["elementos"]:
        if e["tipo"] in ("segmento", "flecha"):
            pa, pb = proy(e["a"]), proy(e["b"])
            trazos.append(((pa[2] + pb[2]) / 2, e, pa, pb))
    for _, e, pa, pb in sorted(trazos, key=lambda t: -t[0]):
        color = color_serie(paleta, e["serie"])
        plan.append(("linea", pa[0], pa[1], pb[0], pb[1], color,
                     grosor * (1.9 if e.get("grosor") == "fuerte" else 1),
                     guion if e.get("guion") else None))
        if e["tipo"] == "flecha":
            largo = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
            if largo > 1:
                ux, uy, h = (pb[0] - pa[0]) / largo, (pb[1] - pa[1]) / largo, min(0.9 * ch, largo * 0.6)
                plan.append(("poligono", [
                    (pb[0], pb[1]),
                    (pb[0] - ux * h - uy * h * 0.45, pb[1] - uy * h + ux * h * 0.45),
                    (pb[0] - ux * h + uy * h * 0.45, pb[1] - uy * h - ux * h * 0.45)],
                    color, color, 1))
                if e.get("etiqueta"):
                    rotulos.append((pb[0] + 0.5 * cw, pb[1] - 0.7 * ch, e["etiqueta"],
                                    paleta["texto"], True))

    puntos = sorted(((proy(e["p"]), e) for e in esc["elementos"] if e["tipo"] == "punto"),
                    key=lambda t: -t[0][2])
    for (px, py, _), e in puntos:
        plan.append(("circulo", px, py,
                     radio_punto * (1.5 if e.get("grosor") == "fuerte" else 1.0),
                     color_serie(paleta, e["serie"]), paleta["fondo"]))
        if e.get("etiqueta"):
            rotulos.append((px + 0.8 * cw, py - 0.9 * ch, e["etiqueta"], paleta["texto"], True))

    for x, y, texto, color, negrita in rotulos:
        y = min(max(y, arr + 0.6 * ch), arr + util_h - 0.6 * ch)
        plan.append(("texto", x, y, texto, "start", color, negrita))

    x0, y0, x1, y1 = caja_px
    for a, b, c, d in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
        plan.append(("linea", a, b, c, d, paleta["grafica_marco"], 1, None))
    return plan
