"""
Escenas geométricas (2D y 3D): ayudas comunes (spec 014).

Aquí se decide *qué* se dibuja; la web (SVG interactivo), el PNG y el PDF solo
lo pintan, así los tres muestran exactamente lo mismo. Una *escena* es un
diccionario JSON:

    {
      "disponible": True,
      "dim": 2 | 3,
      "ejes": ["x1", "x2"],                  # nombres de los ejes
      "ventana": {"x": [a, b], "y": [a, b]}, # 2D: lo que se ve al inicio
      "caja": {"x": [..], "y": [..], "z": [..]},   # 3D
      "camara": {"azimut": -50, "elevacion": 25},  # 3D: vista inicial (grados)
      "elementos": [...],
      "leyenda": [{"serie": 0, "tipo": "recta", "texto": "x1 + x2 = 3"}, ...],
      "avisos": ["..."],
      "resumen": "texto corto para lectores de pantalla",
    }

Elementos (todos con `serie`: índice de color 0..SERIES-1, o `"solucion"`):

    {"tipo": "recta", "p": [x, y], "d": [dx, dy]}       2D, infinita
    {"tipo": "segmento", "a": [...], "b": [...]}
    {"tipo": "flecha", "a": [...], "b": [...]}
    {"tipo": "punto", "p": [...]}
    {"tipo": "poligono", "puntos": [[...], ...]}        relleno translúcido

y opcionalmente `etiqueta` (texto junto al elemento), `guion` (línea
discontinua) y `grosor` ("normal" | "fuerte").

Si no se puede graficar (más de 3 dimensiones, etc.) la escena es
`{"disponible": False, "motivo": "..."}` y la vista muestra el aviso.

Solo usa la librería estándar. Los números se convierten a `float` solo para
dibujar; el cálculo con fracciones no se toca.
"""

import math
from fractions import Fraction

SERIES = 6                  # colores de serie distintos (la web y el PNG/PDF)
MARGEN_VENTANA = 0.35       # holgura alrededor de lo que se dibuja (fracción)
MARGEN_CAJA = 0.2           # holgura de la caja 3D (menor: ocupa más espacio)
MITAD_MINIMA = 1.0          # la ventana nunca es más chica que ±1
LIMITE_NUMERO = 1e9         # números mayores se ignoran al dimensionar
CAMARA_INICIAL = {"azimut": -50.0, "elevacion": 25.0}

# Nombre de cada color de serie, para la leyenda en texto de los archivos
# exportados (así no depende solo del color).
NOMBRES_SERIES = ("verde azulado", "naranja", "azul", "morado", "ámbar", "gris")
NOMBRE_SOLUCION = "rojo"

MOTIVO_DIMENSION = "La gráfica solo está disponible para 2 o 3 dimensiones."


# ----------------------------------------------------------------------
# Escena y elementos
# ----------------------------------------------------------------------

def no_disponible(motivo=MOTIVO_DIMENSION):
    return {"disponible": False, "motivo": motivo}


def a_float(valor):
    """float(valor); ValueError con mensaje en español si no cabe en un float."""

    try:
        resultado = float(valor)
    except (OverflowError, TypeError):
        raise ValueError("Un número es demasiado grande para dibujarlo.")
    if not math.isfinite(resultado):
        raise ValueError("Un número no es finito: no se puede dibujar.")
    return resultado


def punto_float(coordenadas):
    return [a_float(c) for c in coordenadas]


def serie_de(indice):
    return indice % SERIES


def nueva_escena(dim, ejes):
    return {
        "disponible": True,
        "dim": dim,
        "ejes": list(ejes),
        "elementos": [],
        "leyenda": [],
        "avisos": [],
        "resumen": "",
    }


def recta(p, d, serie, etiqueta=None, guion=False, grosor="normal"):
    """Recta infinita 2D por el punto `p` con dirección `d` (se normaliza)."""

    norma = math.hypot(d[0], d[1])
    return {"tipo": "recta", "p": punto_float(p),
            "d": [d[0] / norma, d[1] / norma], "serie": serie,
            "etiqueta": etiqueta, "guion": guion, "grosor": grosor}


def segmento(a, b, serie, etiqueta=None, guion=False, grosor="normal"):
    return {"tipo": "segmento", "a": punto_float(a), "b": punto_float(b),
            "serie": serie, "etiqueta": etiqueta, "guion": guion,
            "grosor": grosor}


def flecha(a, b, serie, etiqueta=None, guion=False, grosor="normal"):
    return {"tipo": "flecha", "a": punto_float(a), "b": punto_float(b),
            "serie": serie, "etiqueta": etiqueta, "guion": guion,
            "grosor": grosor}


def punto(p, serie, etiqueta=None, grosor="normal"):
    return {"tipo": "punto", "p": punto_float(p), "serie": serie,
            "etiqueta": etiqueta, "grosor": grosor}


def poligono(puntos, serie, etiqueta=None, guion=False):
    return {"tipo": "poligono", "puntos": [punto_float(p) for p in puntos],
            "serie": serie, "etiqueta": etiqueta, "guion": guion}


def leyenda(escena, serie, tipo, texto):
    escena["leyenda"].append({"serie": serie, "tipo": tipo, "texto": texto})


# ----------------------------------------------------------------------
# Texto de números y ecuaciones
# ----------------------------------------------------------------------

def numero_texto(valor, modo="fraccion"):
    """Fracción como `1/2` o decimal corto, según el modo de la web."""

    valor = Fraction(valor)
    if modo == "decimal":
        return f"{float(valor):.4f}".rstrip("0").rstrip(".") or "0"
    if valor.denominator == 1:
        return str(valor.numerator)
    return f"{valor.numerator}/{valor.denominator}"


def ecuacion_texto(coeficientes, termino, nombres, modo="fraccion"):
    """`2x1 - x2 = 3` a partir de los coeficientes y el término independiente."""

    partes = []
    for c, nombre in zip(coeficientes, nombres):
        c = Fraction(c)
        if c == 0:
            continue
        magnitud = abs(c)
        coef = "" if magnitud == 1 else numero_texto(magnitud, modo)
        signo = "-" if c < 0 else "+"
        if not partes:
            partes.append(("-" if c < 0 else "") + coef + nombre)
        else:
            partes.append(f" {signo} {coef}{nombre}")
    cuerpo = "".join(partes) or "0"
    return f"{cuerpo} = {numero_texto(termino, modo)}"


def coordenadas_texto(valores, modo="fraccion"):
    return "(" + ", ".join(numero_texto(v, modo) for v in valores) + ")"


# ----------------------------------------------------------------------
# Ventana 2D y caja 3D
# ----------------------------------------------------------------------

def _rango(valores, margen=MARGEN_VENTANA, mitad_minima=MITAD_MINIMA):
    valores = [v for v in valores if abs(v) <= LIMITE_NUMERO]
    minimo = min(valores + [0.0])
    maximo = max(valores + [0.0])
    ancho = maximo - minimo
    holgura = margen * ancho if ancho > 0 else 0
    minimo, maximo = minimo - holgura, maximo + holgura
    centro = (minimo + maximo) / 2
    mitad = max((maximo - minimo) / 2, mitad_minima)
    return [centro - mitad, centro + mitad]


def ventana_2d(puntos):
    """Ventana que contiene `puntos` (lista de [x, y]) y el origen."""

    return {"x": _rango([p[0] for p in puntos]),
            "y": _rango([p[1] for p in puntos])}


def caja_3d(puntos):
    """Caja que contiene `puntos` (lista de [x, y, z]) y el origen. Es un
    cubo: las tres dimensiones tienen la misma longitud, así no se deforma."""

    rangos = [_rango([p[i] for p in puntos], MARGEN_CAJA) for i in range(3)]
    mitad = max((r[1] - r[0]) / 2 for r in rangos)
    cajas = []
    for r in rangos:
        centro = (r[0] + r[1]) / 2
        cajas.append([centro - mitad, centro + mitad])
    return {"x": cajas[0], "y": cajas[1], "z": cajas[2]}


# ----------------------------------------------------------------------
# Geometría auxiliar (la usan las escenas y el exportador)
# ----------------------------------------------------------------------

def recortar_recta_2d(p, d, ventana):
    """Segmento de la recta (p, d) dentro del rectángulo `ventana`
    ({"x": [a, b], "y": [a, b]}) o `None` si no lo cruza."""

    t0, t1 = -math.inf, math.inf
    for eje, (lo, hi) in enumerate((ventana["x"], ventana["y"])):
        if abs(d[eje]) < 1e-15:
            if not lo <= p[eje] <= hi:
                return None
            continue
        ta, tb = (lo - p[eje]) / d[eje], (hi - p[eje]) / d[eje]
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
    if t0 > t1:
        return None
    return ([p[0] + t0 * d[0], p[1] + t0 * d[1]],
            [p[0] + t1 * d[0], p[1] + t1 * d[1]])


def recortar_segmento_2d(a, b, ventana):
    """Parte del segmento a→b dentro del rectángulo `ventana`, o `None`."""

    d = [b[0] - a[0], b[1] - a[1]]
    t0, t1 = 0.0, 1.0
    for eje, (lo, hi) in enumerate((ventana["x"], ventana["y"])):
        if abs(d[eje]) < 1e-15:
            if not lo <= a[eje] <= hi:
                return None
            continue
        ta, tb = (lo - a[eje]) / d[eje], (hi - a[eje]) / d[eje]
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
    if t0 > t1:
        return None
    return ([a[0] + t0 * d[0], a[1] + t0 * d[1]],
            [a[0] + t1 * d[0], a[1] + t1 * d[1]])


def leyenda_texto(escena):
    """Líneas de texto con el significado de cada color (para PNG/PDF)."""

    lineas = []
    for item in escena["leyenda"]:
        if item["serie"] == "solucion":
            color = NOMBRE_SOLUCION
        else:
            color = NOMBRES_SERIES[item["serie"] % SERIES]
        lineas.append(f"{color.capitalize()}: {item['texto']}")
    return lineas + list(escena["avisos"])


# ----------------------------------------------------------------------
# Geometría 3D: recortes a la caja
# ----------------------------------------------------------------------

def _aristas_caja(caja):
    """Las 12 aristas de la caja como pares de vértices."""

    x, y, z = caja["x"], caja["y"], caja["z"]
    vertices = [[x[i], y[j], z[k]] for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    aristas = []
    for a in range(8):
        for b in range(a + 1, 8):
            if sum(1 for u, v in zip(vertices[a], vertices[b]) if u != v) == 1:
                aristas.append((vertices[a], vertices[b]))
    return aristas


def recortar_plano_caja(n, d, caja):
    """Polígono (lista de [x, y, z], ordenado) que es la parte del plano
    `n·x = d` dentro de la caja; lista vacía si no la toca."""

    n = [float(c) for c in n]
    d = float(d)
    norma = math.sqrt(sum(c * c for c in n))
    tolerancia = 1e-9 * max(1.0, abs(d), norma)
    puntos = []
    for p, q in _aristas_caja(caja):
        fp = sum(a * b for a, b in zip(n, p)) - d
        fq = sum(a * b for a, b in zip(n, q)) - d
        candidatos = []
        if abs(fp) <= tolerancia:
            candidatos.append(list(p))
        if abs(fq) <= tolerancia:
            candidatos.append(list(q))
        if not candidatos and fp * fq < 0:
            t = fp / (fp - fq)
            candidatos.append([a + t * (b - a) for a, b in zip(p, q)])
        for c in candidatos:
            if all(math.dist(c, otro) > 1e-9 * max(1.0, norma) for otro in puntos):
                puntos.append(c)
    if len(puntos) < 3:
        return []

    centro = [sum(p[i] for p in puntos) / len(puntos) for i in range(3)]
    # Base ortonormal del plano para ordenar los puntos alrededor del centro.
    eje = min(range(3), key=lambda i: abs(n[i]))
    auxiliar = [0.0, 0.0, 0.0]
    auxiliar[eje] = 1.0
    u = _cruz(n, auxiliar)
    lu = math.sqrt(sum(c * c for c in u))
    u = [c / lu for c in u]
    v = _cruz(n, u)
    lv = math.sqrt(sum(c * c for c in v))
    v = [c / lv for c in v]

    def angulo(p):
        r = [p[i] - centro[i] for i in range(3)]
        return math.atan2(sum(a * b for a, b in zip(r, v)),
                          sum(a * b for a, b in zip(r, u)))

    return sorted(puntos, key=angulo)


def recortar_recta_caja(p, d, caja):
    """Segmento de la recta (p, d) dentro de la caja, o `None`."""

    t0, t1 = -math.inf, math.inf
    for i, eje in enumerate("xyz"):
        lo, hi = caja[eje]
        if abs(d[i]) < 1e-15:
            if not lo <= p[i] <= hi:
                return None
            continue
        ta, tb = (lo - p[i]) / d[i], (hi - p[i]) / d[i]
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
    if t0 > t1:
        return None
    return ([p[i] + t0 * d[i] for i in range(3)],
            [p[i] + t1 * d[i] for i in range(3)])


def _cruz(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def camara_inicial():
    return dict(CAMARA_INICIAL)
