"""
Método de Newton-Raphson para resolver f(x) = 0 (método abierto).

Parte de una sola aproximación inicial x₀ y reemplaza la curva por su recta
tangente: la nueva aproximación es donde esa tangente corta el eje x,

    x_{n+1} = x_n − f(x_n) / f′(x_n)

No necesita un intervalo con cambio de signo, pero tampoco garantiza
convergencia: depende de f y de x₀. Se detiene cuando ε_a/100 < E, con
ε_a = |(x_{n+1} − x_n)/x_{n+1}|·100 (el mismo criterio que bisección y Regula
Falsi), o si f(x_n) = 0, o al llegar al máximo de iteraciones. Además se
informan el residuo |f(x_n)| y el cambio |x_{n+1} − x_n| de cada iteración.
Puede fallar (f′ = 0 o muy pequeña, salir del dominio, divergir): en ese caso
se conservan las iteraciones hechas y se explica el motivo.

La derivada f′(x) se calcula sola con `derivada.py` (derivación simbólica) o
el usuario la escribe. Aritmética de punto flotante, sin librerías externas.
"""

from .biseccion import (
    ITERACIONES_POR_DEFECTO,
    MAX_ITERACIONES,
    continuidad_texto,
    formatear_real,
)
from .continuidad import revisar_continuidad
from .derivada import derivada_de
from .evaluador import compilar, evaluar_numero
from .grafica import datos_grafica

__all__ = [
    "MAX_ITERACIONES", "ITERACIONES_POR_DEFECTO", "newton_raphson",
    "procedimiento_texto",
]

DERIVADA_MINIMA = 1e-12      # |f′(x)| menor que esto se trata como cero
LIMITE_DIVERGENCIA = 1e12    # |x| mayor que esto: las aproximaciones se escapan
_MARGEN_VENTANA = 0.25       # holgura de la gráfica alrededor de las x_n


def _validar_entradas(funcion, derivada, x0, tolerancia, max_iter):
    f = compilar(funcion)
    if not f.usa_x:
        raise ValueError("La función debe depender de x (por ejemplo x^3 - x - 2).")

    texto_derivada = str(derivada if derivada is not None else "").strip()
    if texto_derivada:
        df = compilar(texto_derivada)
        origen = "manual"
    else:
        df = derivada_de(f)
        origen = "automatica"

    x0 = evaluar_numero(x0, "El valor inicial x₀")
    tolerancia = evaluar_numero(tolerancia, "La tolerancia E")
    if tolerancia <= 0:
        raise ValueError("La tolerancia E debe ser mayor que cero.")

    try:
        if isinstance(max_iter, bool) or (
                isinstance(max_iter, float) and max_iter != int(max_iter)):
            raise ValueError
        max_iter = int(str(max_iter).strip()) if isinstance(max_iter, str) \
            else int(max_iter)
    except (ValueError, TypeError):
        raise ValueError("El máximo de iteraciones debe ser un número entero.")
    if not 1 <= max_iter <= MAX_ITERACIONES:
        raise ValueError(
            f"El máximo de iteraciones debe estar entre 1 y {MAX_ITERACIONES}.")

    return f, df, origen, x0, tolerancia, max_iter


def _derivada_numerica(f, x):
    """Diferencia central, solo para comprobar la derivada (None si no se puede)."""

    h = 1e-6 * max(1.0, abs(x))
    a, _ = f.evaluar_seguro(x + h)
    b, _ = f.evaluar_seguro(x - h)
    return None if a is None or b is None else (a - b) / (2 * h)


def _ventana(x0, xs):
    """[x_min, x_max] de la gráfica: contiene x₀ y las x_n cercanas."""

    cercanas = [x for x in xs if abs(x - x0) <= 50 * max(1.0, abs(x0))]
    lo, hi = min(cercanas), max(cercanas)
    minimo = max(1.0, 0.5 * abs(x0))        # que se vea la curvatura de f
    if hi - lo < minimo:
        centro = (lo + hi) / 2
        lo, hi = centro - minimo / 2, centro + minimo / 2
    margen = _MARGEN_VENTANA * (hi - lo)
    return lo - margen, hi + margen


def newton_raphson(funcion, derivada, x0, tolerancia,
                   max_iter=ITERACIONES_POR_DEFECTO):
    """
    Aplica Newton-Raphson a `funcion` (texto) desde `x0`. `derivada` es el texto
    de f′(x) o vacío para calcularla automáticamente.

    Devuelve `entradas`, `pasos` (una iteración cada uno: `x`, `fx`, `dfx`,
    `x_nuevo`, `f_nuevo`, `delta`, `error`, `decision`), `resultado`,
    `continuidad` (aviso; no bloquea), `grafica`, `advertencias` y
    `comprobacion`. Lanza ValueError (en español) con datos inválidos o si ya
    la primera iteración falla.
    """

    f, df, origen, x0, tolerancia, max_iter = _validar_entradas(
        funcion, derivada, x0, tolerancia, max_iter)

    pasos = []
    x = x0
    motivo = "max_iter"
    falla = None

    for i in range(1, max_iter + 1):
        fx, motivo_f = f.evaluar_seguro(x)
        if fx is None:
            falla = (f"No se puede evaluar f en x = {formatear_real(x)}: "
                     f"{motivo_f}.")
            motivo = "no_evaluable"
            break

        if fx == 0:
            pasos.append({
                "i": i, "x": x, "fx": 0.0, "dfx": df.evaluar_seguro(x)[0],
                "x_nuevo": x, "f_nuevo": 0.0, "delta": 0.0, "error": None,
                "decision": "raiz_exacta", "tangente": [[x, 0.0], [x, 0.0]],
            })
            motivo = "raiz_exacta"
            break

        dfx, motivo_d = df.evaluar_seguro(x)
        if dfx is None:
            falla = (f"No se puede evaluar f′ en x = {formatear_real(x)}: "
                     f"{motivo_d}.")
            motivo = "no_evaluable"
            break
        if abs(dfx) < DERIVADA_MINIMA:
            falla = (f"f′({formatear_real(x)}) = {formatear_real(dfx)} es "
                     "cero (o casi): la tangente es horizontal y no corta el "
                     "eje x. Prueba con otro valor inicial x₀.")
            motivo = "derivada_cero"
            break

        x_nuevo = x - fx / dfx
        if abs(x_nuevo) > LIMITE_DIVERGENCIA:
            falla = (f"x₍{i}₎ = {formatear_real(x_nuevo)} se escapó "
                     "al infinito: el método diverge desde este x₀ (f′ muy "
                     "pequeña). Prueba con otro valor inicial.")
            motivo = "divergencia"
            break
        f_nuevo, motivo_f = f.evaluar_seguro(x_nuevo)
        if f_nuevo is None:
            falla = (f"La nueva aproximación x = {formatear_real(x_nuevo)} "
                     f"queda fuera del dominio de f: {motivo_f}. Prueba con "
                     "otro valor inicial x₀.")
            motivo = "no_evaluable"
            break

        error = abs((x_nuevo - x) / x_nuevo) * 100 if x_nuevo != 0 else None
        pasos.append({
            "i": i, "x": x, "fx": fx, "dfx": dfx, "x_nuevo": x_nuevo,
            "f_nuevo": f_nuevo, "delta": abs(x_nuevo - x), "error": error,
            "decision": "continuar", "tangente": [[x, fx], [x_nuevo, 0.0]],
        })
        x = x_nuevo

        if error is not None and error / 100 < tolerancia:
            motivo = "tolerancia"
            break
        if f_nuevo == 0:
            motivo = "raiz_exacta"
            break

    if not pasos:
        raise ValueError(falla or "No se pudo hacer ninguna iteración.")

    ultimo = pasos[-1]
    convergio = motivo in ("tolerancia", "raiz_exacta")
    resultado = {
        "raiz": ultimo["x_nuevo"], "iteraciones": len(pasos),
        "fraiz": ultimo["f_nuevo"], "error": ultimo["error"],
        "residuo": abs(ultimo["f_nuevo"]), "convergio": convergio,
        "motivo": motivo,
    }

    advertencias = []
    if falla:
        advertencias.append(falla + " Se muestran las iteraciones hechas hasta ahí.")
    if motivo == "max_iter":
        advertencias.append(
            f"Se agotaron las {max_iter} iteraciones sin llegar a la tolerancia "
            "E. Puede que x₀ esté lejos de la raíz, que haya una raíz múltiple "
            "(convergencia lenta) o que el método no converja: prueba otro x₀ "
            "o sube el máximo.")

    # Gráfica alrededor de x₀ y de las aproximaciones; la continuidad solo avisa.
    xs = [x0] + [p["x_nuevo"] for p in pasos]
    x_min, x_max = _ventana(x0, xs)
    continuidad = revisar_continuidad(f, x_min, x_max)
    grafica = datos_grafica(f, x_min, x_max, continuidad)
    grafica["intervalo"] = None            # método abierto: no hay [a, b]
    if not continuidad["sin_senales"]:
        advertencias.append(
            "Se detectaron señales de discontinuidad cerca de las "
            "aproximaciones (marcadas en la gráfica): Newton-Raphson supone f "
            "derivable y puede fallar cerca de ellas.")

    y_min, y_max = grafica["y_min"], grafica["y_max"]

    def punto(xp, yp, **extra):
        return {"x": xp, "y": max(y_min, min(y_max, yp)), "valor": yp,
                "fuera": not y_min <= yp <= y_max, **extra}

    grafica["inicio"] = punto(x0, pasos[0]["fx"])
    grafica["iteraciones"] = [
        punto(p["x_nuevo"], p["f_nuevo"], i=p["i"], tangente=p["tangente"],
              etiqueta=f"x{p['i']}")
        for p in pasos
    ]
    grafica["raiz"] = punto(resultado["raiz"], resultado["fraiz"])

    # Comprobación de la derivada contra una diferencia numérica en x₀.
    d_formula = df.evaluar_seguro(x0)[0]
    d_numerica = _derivada_numerica(f, x0)
    derivada_ok = True
    if d_formula is not None and d_numerica is not None:
        derivada_ok = abs(d_formula - d_numerica) <= 1e-4 * max(
            1.0, abs(d_numerica))
    if not derivada_ok:
        advertencias.append(
            f"La derivada f′(x) = {df.texto} no coincide con la pendiente "
            f"numérica de f en x₀ ({formatear_real(d_formula)} contra "
            f"{formatear_real(d_numerica)}): revisa que f′ esté bien escrita.")

    return {
        "operacion": "newton_raphson",
        "bloqueada": False,
        "entradas": {
            "funcion": f.texto, "derivada": df.texto,
            "derivada_origen": origen, "x0": x0, "tolerancia": tolerancia,
            "max_iter": max_iter,
        },
        "inicial": {"fx0": pasos[0]["fx"], "dfx0": pasos[0]["dfx"]},
        "pasos": pasos,
        "resultado": resultado,
        "continuidad": continuidad,
        "grafica": grafica,
        "advertencias": advertencias,
        "comprobacion": {
            "raiz": resultado["raiz"], "fraiz": f(resultado["raiz"]),
            "residuo": abs(f(resultado["raiz"])),
            "tolerancia_alcanzada": convergio,
            "derivada_correcta": derivada_ok,
            "discontinuidad": not continuidad["sin_senales"],
            "correcto": convergio and derivada_ok,
        },
    }


# ---------------------------------------------------------------------------
# Texto del procedimiento (para exportar a PNG/PDF)
# ---------------------------------------------------------------------------

_MOTIVO_TEXTO = {
    "tolerancia": "Se alcanzó la tolerancia: Ea/100 < E.",
    "raiz_exacta": "Se encontró una raíz exacta: f(x) = 0.",
    "max_iter": "Se agotó el máximo de iteraciones sin llegar a E.",
    "derivada_cero": "El método se detuvo: la derivada es cero (o casi).",
    "no_evaluable": "El método se detuvo: f o f′ no se pueden evaluar.",
    "divergencia": "El método se detuvo: las aproximaciones divergen.",
}


def tabla_texto(pasos):
    """Tabla de iteraciones alineada (columnas de ancho fijo)."""

    f = formatear_real
    filas = [["n", "xn", "f(xn)", "f'(xn)", "xn+1", "|dx|", "Ea (%)"]]
    for p in pasos:
        filas.append([str(p["i"]), f(p["x"]), f(p["fx"]), f(p["dfx"]),
                      f(p["x_nuevo"]), f(p["delta"]), f(p["error"], 6)])
    anchos = [max(len(fila[k]) for fila in filas) for k in range(len(filas[0]))]
    return "\n".join(
        "  ".join(c.rjust(anchos[k]) for k, c in enumerate(fila))
        for fila in filas)


def procedimiento_texto(datos, modo="fraccion", incluir_pasos=True):
    """Procedimiento y resultado de Newton-Raphson como texto legible."""

    f = formatear_real
    e = datos["entradas"]
    r = datos["resultado"]
    c = datos["comprobacion"]
    marca = lambda ok: "✓" if ok else "✗"
    par = lambda v: f"({f(v)})" if v < 0 else f(v)

    lineas = [
        "MÉTODO DE NEWTON-RAPHSON", "",
        f"f(x) = {e['funcion']}",
        f"f'(x) = {e['derivada']}   "
        f"({'calculada automáticamente' if e['derivada_origen'] == 'automatica' else 'escrita por el usuario'})",
        f"Valor inicial x0 = {f(e['x0'])}",
        f"Tolerancia E = {f(e['tolerancia'])} "
        f"({f(e['tolerancia'] * 100)} % de error relativo)",
        f"Máximo de iteraciones: {e['max_iter']}", "",
        "Fórmula: x(n+1) = xn - f(xn) / f'(xn)  "
        "(corte de la tangente con el eje x)", "",
    ]

    if incluir_pasos:
        lineas += ["Tabla de iteraciones:", tabla_texto(datos["pasos"]), ""]
        for p in datos["pasos"]:
            lineas.append(
                f"Iteración {p['i']}: x{p['i']} = {f(p['x'])} - "
                f"{par(p['fx'])} / {par(p['dfx'])} = {f(p['x_nuevo'])}"
                if p["decision"] != "raiz_exacta" else
                f"Iteración {p['i']}: f({f(p['x'])}) = 0, x es la raíz exacta")
            if p["decision"] != "raiz_exacta":
                lineas.append(
                    f"    f(x{p['i']}) = {f(p['f_nuevo'])}   "
                    f"|x{p['i']} - x{p['i'] - 1}| = {f(p['delta'])}")
            if p["error"] is not None:
                lineas.append(f"    Ea = {f(p['error'], 6)} %")
        lineas.append("")

    lineas += [
        _MOTIVO_TEXTO[r["motivo"]],
        f"Raíz aproximada: x = {f(r['raiz'])}",
        f"Iteraciones: {r['iteraciones']}",
        f"Residuo |f(x)| = {f(r['residuo'])}",
        f"Error relativo final Ea = {f(r['error'], 6)} %",
    ]
    lineas += [f"Aviso: {texto}" for texto in datos["advertencias"]]
    lineas += ["", *continuidad_texto(datos["continuidad"])]
    lineas += [
        "", "Comprobación (se vuelve a evaluar f):",
        f"f({f(c['raiz'])}) = {f(c['fraiz'])}",
        f"Tolerancia alcanzada {marca(c['tolerancia_alcanzada'])}",
        f"f'(x) coincide con la pendiente numérica {marca(c['derivada_correcta'])}",
    ]
    return "\n".join(lineas)
