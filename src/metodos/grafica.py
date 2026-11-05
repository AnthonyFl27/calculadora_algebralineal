"""
Datos para graficar f(x) en [a, b] (método de bisección).

Aquí se decide *qué* se dibuja; la web (SVG), el PNG y el PDF solo lo pintan,
así los tres muestran exactamente lo mismo:

- la curva, como varias polilíneas (se corta en los puntos donde f no está
  definida y en los polos, para no unir los dos lados de una asíntota);
- la ventana vertical, que ignora los valores extremos cuando hay polos
  (si no, `tan(x)` aplastaría la curva) y siempre incluye y = 0;
- las marcas de los ejes ("números bonitos" 1-2-5) con su etiqueta;
- los puntos c de cada iteración, la raíz y las señales de discontinuidad.

Solo usa la librería estándar.
"""

import math

PUNTOS = 400                 # subintervalos con que se muestrea la curva
_MARGEN_X = 0.03             # holgura horizontal (fracción del ancho)
_MARGEN_Y = 0.12             # holgura vertical (fracción del alto)
_CUANTIL_BAJO, _CUANTIL_ALTO = 0.10, 0.90   # ventana si hay discontinuidades


def _etiqueta(valor, escala):
    """Etiqueta corta de una marca; el ruido numérico se muestra como 0."""

    if abs(valor) <= 1e-9 * escala:
        return "0"
    return f"{valor:.4g}"


def marcas(minimo, maximo, aprox=6):
    """Marcas de eje en pasos 1-2-5 dentro de [minimo, maximo].

    Devuelve una lista de `[valor, etiqueta]`."""

    ancho = maximo - minimo
    if not ancho > 0:
        return []
    bruto = ancho / aprox
    potencia = 10 ** math.floor(math.log10(bruto))
    paso = potencia
    for factor in (1, 2, 5, 10):
        paso = factor * potencia
        if paso >= bruto:
            break

    escala = max(abs(minimo), abs(maximo))
    k = math.ceil(minimo / paso - 1e-9)
    resultado = []
    while k * paso <= maximo + 1e-9 * paso:
        valor = round(k * paso, 12)
        resultado.append([valor, _etiqueta(valor, escala)])
        k += 1
    return resultado


def _cuantil(ordenados, q):
    return ordenados[min(len(ordenados) - 1, int(q * len(ordenados)))]


def _ventana_y(valores, con_discontinuidad, extra):
    """(mínimo, máximo) vertical que contiene 0 y los valores relevantes."""

    valores = valores or [0.0]      # f no se pudo evaluar en ningún punto
    if con_discontinuidad:
        ordenados = sorted(valores)
        bajo = _cuantil(ordenados, _CUANTIL_BAJO)
        alto = _cuantil(ordenados, _CUANTIL_ALTO)
    else:
        bajo, alto = min(valores), max(valores)
    bajo = min([bajo, 0.0] + extra)
    alto = max([alto, 0.0] + extra)
    if alto - bajo <= 0:
        bajo, alto = bajo - 1, alto + 1
    holgura = _MARGEN_Y * (alto - bajo)
    return bajo - holgura, alto + holgura


def _recortar(tramo, y_min, y_max):
    """Recorta un tramo continuo a la ventana vertical (corta en el borde)."""

    def dentro(y):
        return y_min <= y <= y_max

    salida, actual = [], []
    anterior = None
    for x, y in tramo:
        if anterior is not None:
            px, py = anterior
            if dentro(py) != dentro(y) or (py < y_min and y > y_max) \
                    or (py > y_max and y < y_min):
                cruces = []
                for borde in (y_min, y_max):
                    if (py - borde) * (y - borde) < 0:
                        t = (borde - py) / (y - py)
                        cruces.append((t, [px + t * (x - px), borde]))
                for _, punto in sorted(cruces, key=lambda c: c[0]):
                    if actual:
                        actual.append(punto)
                        salida.append(actual)
                        actual = []
                    else:
                        actual = [punto]
        if dentro(y):
            actual.append([x, y])
        anterior = (x, y)
    if actual:
        salida.append(actual)
    return [t for t in salida if len(t) > 1]


def _polilineas(xs, ys, y_min, y_max):
    """Parte la curva en tramos continuos (se corta donde f no está definida
    y en los polos) y los recorta a la ventana vertical."""

    span = y_max - y_min
    crudos, actual = [], []
    anterior = None
    for x, y in zip(xs, ys):
        if y is None:
            crudos.append(actual)
            actual, anterior = [], None
            continue
        if anterior is not None and (anterior < 0) != (y < 0) \
                and abs(y - anterior) > span:
            crudos.append(actual)
            actual = []
        actual.append((x, y))
        anterior = y
    crudos.append(actual)

    tramos = []
    for crudo in crudos:
        tramos += _recortar(crudo, y_min, y_max)
    return tramos


def datos_grafica(f, a, b, continuidad):
    """
    Datos de la gráfica de `f` (una `Funcion`) en [a, b], con las
    discontinuidades de `continuidad`. Es el **primer paso** del método: se
    dibuja antes de iterar, así que `iteraciones` va vacía y `raiz` es None
    hasta que `agregar_iteraciones` las completa.
    """

    n = PUNTOS
    xs = [a + k * (b - a) / n for k in range(n)] + [b]
    ys = [f.evaluar_seguro(x)[0] for x in xs]
    finitos = [y for y in ys if y is not None]

    y_min, y_max = _ventana_y(
        finitos, not continuidad["sin_senales"],
        [y for y in (ys[0], ys[-1]) if y is not None])
    holgura_x = _MARGEN_X * (b - a)
    x_min, x_max = a - holgura_x, b + holgura_x

    return {
        "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
        "marcas_x": marcas(x_min, x_max),
        "marcas_y": marcas(y_min, y_max, 7),
        "curva": _polilineas(xs, ys, y_min, y_max),
        "intervalo": [a, b],
        "iteraciones": [],
        "raiz": None,
        "discontinuidades": [
            {"tipo": s["tipo"], "desde": s["desde"], "hasta": s["hasta"]}
            for s in continuidad["sospechas"]
        ],
    }


def agregar_iteraciones(grafica, pasos, resultado):
    """Completa la gráfica del paso 1 con los puntos c de cada iteración y la
    raíz aproximada (`pasos` y `resultado` de `biseccion()`)."""

    y_min, y_max = grafica["y_min"], grafica["y_max"]

    def punto(x, y):
        # "y" es el valor recortado a la ventana inicial; "valor" es f real,
        # que la web usa al hacer zoom (el punto puede entrar en la vista).
        return {"x": x, "y": max(y_min, min(y_max, y)), "valor": y,
                "fuera": not y_min <= y <= y_max}

    grafica["iteraciones"] = [
        {"i": p["i"], "a": p["a_nuevo"], "b": p["b_nuevo"],
         **punto(p["c"], p["fc"])}
        for p in pasos
    ]
    grafica["raiz"] = punto(resultado["raiz"], resultado["fraiz"])


# ----------------------------------------------------------------------
# Gráfica interactiva: curva de la ventana que el usuario está viendo
# ----------------------------------------------------------------------

PUNTOS_VENTANA = 800         # subintervalos en la ventana pedida (con relleno)
RELLENO_VENTANA = 0.5        # se muestrea medio ancho/alto extra a cada lado
_LIMITE_VENTANA = 1e12       # la web no puede pedir ventanas mayores a esto
_ANCHO_MINIMO = 1e-12        # ni más angostas que esto (error de redondeo)


def _numero_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser un número.")
    valor = float(valor)
    if not math.isfinite(valor) or abs(valor) > _LIMITE_VENTANA:
        raise ValueError(f"{nombre} está fuera del rango permitido.")
    return valor


def curva_ventana(f, x_min, x_max, y_min, y_max):
    """
    Curva de `f` (una `Funcion`) para la ventana [x_min, x_max] × [y_min, y_max]
    que el usuario ve al hacer zoom o mover la gráfica.

    Se muestrea un poco más allá de la ventana (`RELLENO_VENTANA`) para que al
    arrastrar ya haya curva del otro lado mientras llega la siguiente petición.
    Devuelve la curva (polilíneas recortadas, cortadas en polos y en puntos
    sin dominio) y las marcas de los ejes de la ventana *visible*.
    """

    x_min = _numero_finito(x_min, "x_min")
    x_max = _numero_finito(x_max, "x_max")
    y_min = _numero_finito(y_min, "y_min")
    y_max = _numero_finito(y_max, "y_max")
    if not (x_max - x_min > _ANCHO_MINIMO * max(1.0, abs(x_min), abs(x_max))
            and y_max - y_min > _ANCHO_MINIMO * max(1.0, abs(y_min), abs(y_max))):
        raise ValueError("La ventana de la gráfica es demasiado pequeña.")

    ancho_x, alto_y = x_max - x_min, y_max - y_min
    mx, my = RELLENO_VENTANA * ancho_x, RELLENO_VENTANA * alto_y
    xa, xb = x_min - mx, x_max + mx
    ya, yb = y_min - my, y_max + my

    n = PUNTOS_VENTANA
    xs = [xa + k * (xb - xa) / n for k in range(n)] + [xb]
    ys = [f.evaluar_seguro(x)[0] for x in xs]

    return {
        "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
        "marcas_x": marcas(x_min, x_max),
        "marcas_y": marcas(y_min, y_max, 7),
        "curva": _polilineas(xs, ys, ya, yb),
    }
