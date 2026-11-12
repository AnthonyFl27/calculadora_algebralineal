"""
Método de la secante para resolver f(x) = 0 (método abierto, sin derivada).

Alternativa a Newton-Raphson cuando no se quiere calcular f′(x): usa dos
aproximaciones, x₀ y x₁, y reemplaza la tangente por la recta secante que pasa
por (x₀, f(x₀)) y (x₁, f(x₁)). La nueva aproximación es donde esa recta corta
el eje x,

    x_{n+1} = x_n − f(x_n)·(x_n − x_{n−1}) / [f(x_n) − f(x_{n−1})]

y en cada iteración se desplazan las dos aproximaciones (x₀ ← x₁, x₁ ← x₂).
No necesita intervalo con cambio de signo ni conserva uno que encierre la
raíz, y tampoco garantiza convergencia: depende de f, x₀ y x₁. Se detiene con
el mismo criterio que los demás métodos (ε_a/100 < E, con
ε_a = |(x_{n+1} − x_n)/x_{n+1}|·100), si f(x_n) = 0 o al llegar al máximo de
iteraciones. Cada paso informa el residuo |f(x_{n+1})| y el cambio
|x_{n+1} − x_n|. Puede fallar (denominador cero, salir del dominio, divergir):
se conservan las iteraciones hechas y se explica el motivo.

Aritmética de punto flotante, solo librería estándar.
"""

from .biseccion import (
    ITERACIONES_POR_DEFECTO,
    MAX_ITERACIONES,
    continuidad_texto,
    formatear_real,
)
from .continuidad import revisar_continuidad
from .evaluador import compilar, evaluar_numero
from .grafica import datos_grafica
from .newton_raphson import LIMITE_DIVERGENCIA, _ventana

__all__ = [
    "MAX_ITERACIONES", "ITERACIONES_POR_DEFECTO", "secante",
    "procedimiento_texto",
]

DENOMINADOR_MINIMO = 1e-12   # |f(xn) − f(xn−1)| menor que esto se trata como cero
DENOMINADOR_PEQUENO = 1e-6   # por debajo de esto el paso es inestable (aviso)


def _validar_entradas(funcion, x0, x1, tolerancia, max_iter):
    f = compilar(funcion)
    if not f.usa_x:
        raise ValueError("La función debe depender de x (por ejemplo x^3 - x - 2).")

    x0 = evaluar_numero(x0, "El valor inicial x₀")
    x1 = evaluar_numero(x1, "El valor inicial x₁")
    if x0 == x1:
        raise ValueError(
            "x₀ y x₁ deben ser distintos: con el mismo valor la recta secante "
            "no está definida (el denominador sería cero).")
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

    return f, x0, x1, tolerancia, max_iter


def secante(funcion, x0, x1, tolerancia, max_iter=ITERACIONES_POR_DEFECTO):
    """
    Aplica el método de la secante a `funcion` (texto) desde `x0` y `x1`.

    Devuelve `entradas`, `inicial`, `pasos` (una iteración cada uno: `x_ant`,
    `f_ant`, `x`, `fx`, `den`, `x_nuevo`, `f_nuevo`, `delta`, `error`,
    `decision`, `secante`), `resultado`, `continuidad` (aviso; no bloquea),
    `grafica`, `advertencias` y `comprobacion`. Lanza ValueError (en español)
    con datos inválidos o si ya la primera iteración falla.
    """

    f, x0, x1, tolerancia, max_iter = _validar_entradas(
        funcion, x0, x1, tolerancia, max_iter)

    f0, motivo_f = f.evaluar_seguro(x0)
    if f0 is None:
        raise ValueError(
            f"No se puede evaluar f en x₀ = {formatear_real(x0)}: {motivo_f}.")
    f1, motivo_f = f.evaluar_seguro(x1)
    if f1 is None:
        raise ValueError(
            f"No se puede evaluar f en x₁ = {formatear_real(x1)}: {motivo_f}.")

    pasos = []
    x_ant, f_ant, x, fx = x0, f0, x1, f1
    motivo = "max_iter"
    falla = None
    inestable = False

    for i in range(1, max_iter + 1):
        if fx == 0:
            pasos.append({
                "i": i, "x_ant": x_ant, "f_ant": f_ant, "x": x, "fx": 0.0,
                "den": fx - f_ant, "x_nuevo": x, "f_nuevo": 0.0, "delta": 0.0,
                "error": None, "decision": "raiz_exacta",
                "secante": [[x, 0.0], [x, 0.0]],
            })
            motivo = "raiz_exacta"
            break

        den = fx - f_ant
        if abs(den) < DENOMINADOR_MINIMO:
            falla = (f"f(x{i}) − f(x{i - 1}) = {formatear_real(den)} es cero "
                     "(o casi): la recta secante es horizontal y no corta el "
                     "eje x. Prueba con otros valores iniciales x₀ y x₁.")
            motivo = "denominador_cero"
            break
        if abs(den) < DENOMINADOR_PEQUENO:
            inestable = True

        x_nuevo = x - fx * (x - x_ant) / den
        if abs(x_nuevo) > LIMITE_DIVERGENCIA:
            falla = (f"x₍{i + 1}₎ = {formatear_real(x_nuevo)} se escapó al "
                     "infinito: el método diverge desde estos valores "
                     "(denominador muy pequeño). Prueba con otros x₀ y x₁.")
            motivo = "divergencia"
            break
        f_nuevo, motivo_f = f.evaluar_seguro(x_nuevo)
        if f_nuevo is None:
            falla = (f"La nueva aproximación x = {formatear_real(x_nuevo)} "
                     f"queda fuera del dominio de f: {motivo_f}. Prueba con "
                     "otros valores iniciales.")
            motivo = "no_evaluable"
            break

        error = abs((x_nuevo - x) / x_nuevo) * 100 if x_nuevo != 0 else None
        pasos.append({
            "i": i, "x_ant": x_ant, "f_ant": f_ant, "x": x, "fx": fx,
            "den": den, "x_nuevo": x_nuevo, "f_nuevo": f_nuevo,
            "delta": abs(x_nuevo - x), "error": error, "decision": "continuar",
            "secante": [[x_ant, f_ant], [x_nuevo, 0.0]],
        })
        # Se desplazan las dos aproximaciones: x₀ ← x₁ y x₁ ← x₂.
        x_ant, f_ant, x, fx = x, fx, x_nuevo, f_nuevo

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
            "E. Puede que x₀ y x₁ estén lejos de la raíz o que el método no "
            "converja: prueba otros valores iniciales o sube el máximo.")
    if inestable:
        advertencias.append(
            "En alguna iteración el denominador f(xₙ) − f(xₙ₋₁) fue muy "
            "pequeño: el paso puede ser inestable. Revisa el residuo y los "
            "cambios entre iteraciones.")

    # Gráfica alrededor de x₀, x₁ y las aproximaciones; la continuidad solo avisa.
    xs = [x0, x1] + [p["x_nuevo"] for p in pasos]
    x_min, x_max = _ventana(x0, xs)
    continuidad = revisar_continuidad(f, x_min, x_max)
    grafica = datos_grafica(f, x_min, x_max, continuidad)
    grafica["intervalo"] = None            # método abierto: no hay [a, b]
    if not continuidad["sin_senales"]:
        advertencias.append(
            "Se detectaron señales de discontinuidad cerca de las "
            "aproximaciones (marcadas en la gráfica): la secante supone f "
            "continua y puede fallar cerca de ellas.")

    y_min, y_max = grafica["y_min"], grafica["y_max"]

    def punto(xp, yp, **extra):
        return {"x": xp, "y": max(y_min, min(y_max, yp)), "valor": yp,
                "fuera": not y_min <= yp <= y_max, **extra}

    grafica["inicio"] = punto(x0, f0)
    grafica["inicio2"] = punto(x1, f1)
    grafica["iteraciones"] = [
        punto(p["x_nuevo"], p["f_nuevo"], i=p["i"], secante=p["secante"],
              etiqueta=f"x{p['i'] + 1}")
        for p in pasos
    ]
    grafica["raiz"] = punto(resultado["raiz"], resultado["fraiz"])

    return {
        "operacion": "secante",
        "bloqueada": False,
        "entradas": {
            "funcion": f.texto, "x0": x0, "x1": x1, "tolerancia": tolerancia,
            "max_iter": max_iter,
        },
        "inicial": {"fx0": f0, "fx1": f1},
        "pasos": pasos,
        "resultado": resultado,
        "continuidad": continuidad,
        "grafica": grafica,
        "advertencias": advertencias,
        "comprobacion": {
            "raiz": resultado["raiz"], "fraiz": f(resultado["raiz"]),
            "residuo": abs(f(resultado["raiz"])),
            "tolerancia_alcanzada": convergio,
            "denominador_estable": not inestable,
            "discontinuidad": not continuidad["sin_senales"],
            "correcto": convergio and not inestable,
        },
    }


# ---------------------------------------------------------------------------
# Texto del procedimiento (para exportar a PNG/PDF)
# ---------------------------------------------------------------------------

_MOTIVO_TEXTO = {
    "tolerancia": "Se alcanzó la tolerancia: Ea/100 < E.",
    "raiz_exacta": "Se encontró una raíz exacta: f(x) = 0.",
    "max_iter": "Se agotó el máximo de iteraciones sin llegar a E.",
    "denominador_cero": "El método se detuvo: f(xn) - f(xn-1) es cero (o casi).",
    "no_evaluable": "El método se detuvo: f no se puede evaluar.",
    "divergencia": "El método se detuvo: las aproximaciones divergen.",
}


def tabla_texto(pasos):
    """Tabla de iteraciones alineada (columnas de ancho fijo)."""

    f = formatear_real
    filas = [["n", "xn-1", "xn", "f(xn-1)", "f(xn)", "xn+1", "|dx|", "Ea (%)"]]
    for p in pasos:
        filas.append([str(p["i"]), f(p["x_ant"]), f(p["x"]), f(p["f_ant"]),
                      f(p["fx"]), f(p["x_nuevo"]), f(p["delta"]),
                      f(p["error"], 6)])
    anchos = [max(len(fila[k]) for fila in filas) for k in range(len(filas[0]))]
    return "\n".join(
        "  ".join(c.rjust(anchos[k]) for k, c in enumerate(fila))
        for fila in filas)


def procedimiento_texto(datos, modo="fraccion", incluir_pasos=True):
    """Procedimiento y resultado de la secante como texto legible."""

    f = formatear_real
    e = datos["entradas"]
    r = datos["resultado"]
    c = datos["comprobacion"]
    marca = lambda ok: "✓" if ok else "✗"
    par = lambda v: f"({f(v)})" if v < 0 else f(v)

    lineas = [
        "MÉTODO DE LA SECANTE", "",
        f"f(x) = {e['funcion']}",
        f"Valores iniciales x0 = {f(e['x0'])}, x1 = {f(e['x1'])}",
        f"Tolerancia E = {f(e['tolerancia'])} "
        f"({f(e['tolerancia'] * 100)} % de error relativo)",
        f"Máximo de iteraciones: {e['max_iter']}", "",
        "Fórmula: x(n+1) = xn - f(xn)·(xn - xn-1) / [f(xn) - f(xn-1)]  "
        "(corte de la secante con el eje x)", "",
    ]

    if incluir_pasos:
        lineas += ["Tabla de iteraciones:", tabla_texto(datos["pasos"]), ""]
        for p in datos["pasos"]:
            n = p["i"]
            if p["decision"] == "raiz_exacta" and p["x"] == p["x_nuevo"]:
                lineas.append(
                    f"Iteración {n}: f({f(p['x'])}) = 0, x es la raíz exacta")
                continue
            lineas.append(
                f"Iteración {n}: x{n + 1} = {f(p['x'])} - {par(p['fx'])}·"
                f"({f(p['x'])} - {par(p['x_ant'])}) / "
                f"({f(p['fx'])} - {par(p['f_ant'])}) = {f(p['x_nuevo'])}")
            lineas.append(
                f"    f(x{n + 1}) = {f(p['f_nuevo'])}   "
                f"|x{n + 1} - x{n}| = {f(p['delta'])}")
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
        f"Denominador estable en todas las iteraciones "
        f"{marca(c['denominador_estable'])}",
    ]
    return "\n".join(lineas)
