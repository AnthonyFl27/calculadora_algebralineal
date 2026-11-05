"""
Revisión heurística de la continuidad de f(x) en un intervalo [a, b].

Con números no se puede *demostrar* que una función sea continua; lo que sí se
puede es muestrear el intervalo y detectar señales de discontinuidad. Se
evalúa f en `subintervalos + 1` puntos equidistantes y se buscan tres cosas:

1. **Puntos donde f no está definida** (división entre cero, raíz o logaritmo
   fuera de su dominio, desbordamiento). Se acota el tramo con una bisección.
2. **Cambios de signo que no son una raíz**: entre dos muestras consecutivas
   con signo distinto se parte el subintervalo a la mitad varias veces. Si
   f(x) se acerca a 0 es una raíz de verdad; si |f| no baja (o crece) hay un
   salto o un polo, como 1/x en 0 o tan(x) en π/2.
3. **Polos del mismo signo** (1/x² en 0): un máximo local de |f| entre las
   muestras se refina con una búsqueda ternaria; si |f| crece mucho más que en
   las muestras vecinas hay una asíntota vertical.

El resultado es un *aviso*, no una prueba: una discontinuidad más angosta que
el paso de muestreo puede pasar sin detectarse, y una función muy picuda puede
dar un falso aviso. La vista lo dice así ("no se detectaron señales", nunca
"f es continua"). Solo usa la librería estándar.
"""

from .evaluador import MOTIVO_DIVISION, MOTIVO_GRANDE

SUBINTERVALOS = 400          # muestras = SUBINTERVALOS + 1
MAX_SOSPECHAS = 5            # cuántas se detallan (el total se informa aparte)
_PASOS_BISECCION = 100
_PASOS_TERNARIA = 80
_FACTOR_RAIZ = 1e-2          # |f| final <= 1 % de |f| inicial -> es una raíz
_FACTOR_POLO = 10            # |f| final > 10 veces la inicial -> polo
_FACTOR_PICO = 50            # pico refinado > 50 veces la muestra -> polo

# Prioridad al fusionar dos sospechas cercanas (la mayor se conserva).
_PRIORIDAD = {"no_definida": 3, "polo": 2, "salto": 1}


def _fmt(valor, escala):
    """Número con 6 cifras; lo que es ruido numérico frente a la escala del
    intervalo (p. ej. -2.3e-19 cuando el intervalo mide 3) se muestra como 0."""

    return "0" if abs(valor) <= 1e-9 * escala else f"{valor:.6g}"


def _signo(valor):
    return (valor > 0) - (valor < 0)


def _frontera(f, definido, indefinido):
    """Acota, entre un punto donde f se evalúa y otro donde no, el borde del
    dominio. Devuelve el extremo del lado donde f no se puede evaluar."""

    for _ in range(_PASOS_BISECCION):
        c = (definido + indefinido) / 2
        if c == definido or c == indefinido:
            break
        if f.evaluar_seguro(c)[0] is None:
            indefinido = c
        else:
            definido = c
    return indefinido


def _sospecha(tipo, desde, hasta, motivo=None):
    """Una sospecha; su mensaje se redacta al final (ver `_redactar`)."""

    return {"tipo": tipo, "x": (desde + hasta) / 2, "desde": desde,
            "hasta": hasta, "motivo": motivo}


def _redactar(s, escala):
    """Mensaje en español de una sospecha."""

    x = _fmt(s["x"], escala)
    if s["tipo"] == "polo":
        if s["motivo"]:
            return (f"Posible polo (asíntota vertical) en x ≈ {x}: "
                    f"{s['motivo']}.")
        return (f"Posible polo (asíntota vertical) cerca de x ≈ {x}: "
                "|f(x)| crece sin límite al acercarse.")
    if s["tipo"] == "salto":
        return (f"Posible salto cerca de x ≈ {x}: f cambia de signo pero no "
                "se acerca a 0, así que ahí no hay una raíz.")
    if s["hasta"] - s["desde"] <= 1e-9 * escala:
        return f"f(x) no está definida en x ≈ {x} ({s['motivo']})."
    return (f"f(x) no está definida en el tramo [{_fmt(s['desde'], escala)}, "
            f"{_fmt(s['hasta'], escala)}] ({s['motivo']}).")


def _no_definidas(f, xs, valores, motivos):
    """Tramos de muestras consecutivas donde f no se puede evaluar."""

    n = len(xs) - 1
    sospechas = []
    k = 0
    while k <= n:
        if valores[k] is not None:
            k += 1
            continue
        j = k
        while j < n and valores[j + 1] is None:
            j += 1
        desde = _frontera(f, xs[k - 1], xs[k]) if k > 0 else xs[k]
        hasta = _frontera(f, xs[j + 1], xs[j]) if j < n else xs[j]
        if desde > hasta:
            desde, hasta = hasta, desde
        punto = hasta - desde <= 1e-9 * max(1.0, abs(desde))
        polo = punto and motivos[k] in (MOTIVO_DIVISION, MOTIVO_GRANDE)
        sospechas.append(_sospecha(
            "polo" if polo else "no_definida", desde, hasta, motivos[k]))
        k = j + 1
    return sospechas


def _cambios_de_signo(f, xs, valores):
    """Cambios de signo entre muestras que no terminan en una raíz."""

    sospechas = []
    for k in range(len(xs) - 1):
        va, vb = valores[k], valores[k + 1]
        if va is None or vb is None or va == 0 or vb == 0:
            continue
        if _signo(va) == _signo(vb):
            continue

        lo, hi, flo, fhi = xs[k], xs[k + 1], va, vb
        puntual = None
        for _ in range(_PASOS_BISECCION):
            c = (lo + hi) / 2
            if c == lo or c == hi:
                break
            fc, motivo = f.evaluar_seguro(c)
            if fc is None:
                puntual = (c, motivo)
                break
            if fc == 0:
                lo = hi = c
                flo = fhi = 0.0
                break
            if _signo(fc) == _signo(flo):
                lo, flo = c, fc
            else:
                hi, fhi = c, fc

        if puntual is not None:
            c, motivo = puntual
            polo = motivo in (MOTIVO_DIVISION, MOTIVO_GRANDE)
            sospechas.append(_sospecha(
                "polo" if polo else "no_definida", c, c, motivo))
            continue

        escala = max(abs(va), abs(vb))
        final = max(abs(flo), abs(fhi))
        if final <= _FACTOR_RAIZ * escala:
            continue                       # f se acerca a 0: es una raíz
        tipo = "polo" if final > _FACTOR_POLO * escala else "salto"
        sospechas.append(_sospecha(tipo, lo, hi))
    return sospechas


def _magnitud(f, x):
    """|f(x)|, o infinito si f no se puede evaluar ahí (un polo exacto)."""

    valor = f.evaluar_seguro(x)[0]
    return float("inf") if valor is None else abs(valor)


def _picos(f, xs, valores):
    """Polos que no cambian de signo: máximos locales de |f| que, al
    refinarlos, crecen mucho más que en las muestras vecinas."""

    n = len(xs) - 1
    sospechas = []
    for k in range(n + 1):
        v = valores[k]
        if v is None or v == 0:
            continue
        vecinos = [valores[i] for i in (k - 1, k + 1) if 0 <= i <= n]
        if any(w is None for w in vecinos):
            continue
        magnitud = abs(v)
        if any(abs(w) > magnitud for w in vecinos):
            continue
        if all(abs(w) == magnitud for w in vecinos):
            continue                       # zona plana, no es un pico

        lo, hi = xs[max(k - 1, 0)], xs[min(k + 1, n)]
        mejor, donde = magnitud, xs[k]
        for _ in range(_PASOS_TERNARIA):
            tercio = (hi - lo) / 3
            m1, m2 = lo + tercio, hi - tercio
            g1, g2 = _magnitud(f, m1), _magnitud(f, m2)
            for g, m in ((g1, m1), (g2, m2)):
                if g > mejor:
                    mejor, donde = g, m
            if g1 == g2 == float("inf"):
                break
            if g1 < g2:
                lo = m1
            else:
                hi = m2

        if mejor > _FACTOR_PICO * magnitud:
            sospechas.append(_sospecha("polo", donde, donde))
    return sospechas


def _fusionar(sospechas, cercania):
    """Une sospechas muy cercanas (un mismo polo lo detectan varias reglas)."""

    resultado = []
    for s in sorted(sospechas, key=lambda s: s["x"]):
        if resultado and s["desde"] - resultado[-1]["hasta"] <= cercania:
            anterior = resultado[-1]
            if _PRIORIDAD[s["tipo"]] > _PRIORIDAD[anterior["tipo"]]:
                s["desde"] = min(s["desde"], anterior["desde"])
                s["hasta"] = max(s["hasta"], anterior["hasta"])
                resultado[-1] = s
            else:
                anterior["hasta"] = max(anterior["hasta"], s["hasta"])
        else:
            resultado.append(s)
    return resultado


def revisar_continuidad(f, a, b, subintervalos=SUBINTERVALOS):
    """
    Busca señales de discontinuidad de `f` (una `Funcion` del evaluador) en
    [a, b]. Devuelve un diccionario:

    - `muestras`: puntos evaluados;
    - `sospechas`: lista (hasta `MAX_SOSPECHAS`) de dicts con `tipo`
      (`no_definida`, `polo` o `salto`), `x`, `desde`, `hasta` y `mensaje`;
    - `total`: cuántas sospechas se encontraron en total;
    - `sin_senales`: True si no se detectó nada.
    """

    n = max(int(subintervalos), 1)
    paso = (b - a) / n
    xs = [a + k * paso for k in range(n)] + [b]
    valores, motivos = [], []
    for x in xs:
        valor, motivo = f.evaluar_seguro(x)
        valores.append(valor)
        motivos.append(motivo)

    hallazgos = (_no_definidas(f, xs, valores, motivos)
                 + _cambios_de_signo(f, xs, valores)
                 + _picos(f, xs, valores))
    todas = _fusionar(hallazgos, 2 * paso)
    escala = max(1.0, abs(a), abs(b))
    for sospecha in todas:
        sospecha["mensaje"] = _redactar(sospecha, escala)

    return {
        "muestras": n + 1,
        "sospechas": todas[:MAX_SOSPECHAS],
        "total": len(todas),
        "sin_senales": not todas,
    }
