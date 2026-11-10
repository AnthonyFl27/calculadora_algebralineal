"""
Método de Regula Falsi (falsa posición) para resolver f(x) = 0.

Igual que la bisección, parte de f continua en [a, b] con f(a)·f(b) < 0. La
diferencia es cómo se elige c: en vez del punto medio, se toma el punto donde
la **recta secante** que une (a, f(a)) con (b, f(b)) corta el eje x:

    c = b − f(b)·(b − a) / (f(b) − f(a)) = (a·f(b) − b·f(a)) / (f(b) − f(a))

Luego se conserva el subintervalo con cambio de signo ([a, c] o [c, b]).
Criterio de paro: ε_a/100 < E, con ε_a = |(c_nuevo − c_anterior)/c_nuevo|·100
(desde la 2.ª iteración), el mismo que la bisección. Como el intervalo no se
parte a la mitad, el ancho [a, b] puede no tender a 0 (un extremo se queda
fijo); por eso se mira el error entre aproximaciones sucesivas.

Reutiliza la validación, la revisión de continuidad y la gráfica de la
bisección. Aritmética de punto flotante, sin librerías externas.
"""

from .biseccion import (
    MAX_ITERACIONES,
    ITERACIONES_POR_DEFECTO,
    _resultado_bloqueado,
    _signo,
    _validar_entradas,
    continuidad_texto,
    f_cerca_de_cero,
    formatear_real,
    tabla_texto,
)
from .continuidad import revisar_continuidad
from .grafica import agregar_iteraciones, datos_grafica

__all__ = [
    "MAX_ITERACIONES", "ITERACIONES_POR_DEFECTO", "falsa_posicion",
    "procedimiento_texto",
]


def punto_secante(a, b, fa, fb):
    """Corte con el eje x de la secante por (a, fa) y (b, fb). Se limita a
    [a, b] por si el redondeo lo sacara un instante del intervalo."""

    c = b - fb * (b - a) / (fb - fa)
    return min(max(c, a), b)


def falsa_posicion(funcion, a, b, tolerancia, max_iter=ITERACIONES_POR_DEFECTO):
    """
    Aplica Regula Falsi a `funcion` (texto) en [a, b].

    Devuelve el mismo formato que `biseccion()` (`entradas`, `inicial`, `pasos`,
    `resultado`, `continuidad`, `grafica`, `advertencias`, `comprobacion`), con
    `operacion: "falsa_posicion"`, sin `cota_iteraciones` (este método no tiene
    una cota simple) y con `secante` en cada punto de `grafica["iteraciones"]`.
    Orden: 1) gráfica, 2) continuidad (si hay señales de discontinuidad
    devuelve `bloqueada: True` sin iterar), 3) cambio de signo, 4) iteraciones.
    Lanza ValueError (en español) con datos inválidos o sin cambio de signo.
    """

    f, a, b, tolerancia, max_iter = _validar_entradas(
        funcion, a, b, tolerancia, max_iter)

    a0, b0 = a, b

    continuidad = revisar_continuidad(f, a0, b0)
    grafica = datos_grafica(f, a0, b0, continuidad)

    if not continuidad["sin_senales"]:
        bloqueado = _resultado_bloqueado(
            f, a0, b0, tolerancia, max_iter, continuidad, grafica,
            operacion="falsa_posicion", nombre="de falsa posición")
        del bloqueado["cota_iteraciones"]
        return bloqueado

    fa, fb = f(a), f(b)

    if fa == 0 or fb == 0:
        extremo, valor = ("a", a) if fa == 0 else ("b", b)
        raise ValueError(
            f"f({extremo}) = 0: el extremo {extremo} = {formatear_real(valor)} "
            "ya es una raíz. El método pide f(a)·f(b) < 0; elige un intervalo "
            "donde f cambie de signo."
        )

    if _signo(fa) == _signo(fb):
        raise ValueError(
            f"No hay cambio de signo en [{formatear_real(a)}, {formatear_real(b)}]: "
            f"f(a) = {formatear_real(fa)} y f(b) = {formatear_real(fb)} tienen el "
            "mismo signo, así que f(a)·f(b) > 0. Prueba con otro intervalo."
        )

    pasos = []
    anterior = None
    motivo = "max_iter"

    for i in range(1, max_iter + 1):
        c = punto_secante(a, b, fa, fb)
        fc = f(c)
        error = None
        if anterior is not None and c != 0:
            error = abs((c - anterior) / c) * 100

        signo = _signo(fa) * _signo(fc)
        paso = {
            "i": i, "a": a, "b": b, "c": c, "fa": fa, "fb": fb, "fc": fc,
            "error": error, "signo": signo,
        }

        if signo == 0:
            paso["decision"] = "raiz_exacta"
            paso["a_nuevo"], paso["b_nuevo"] = c, c
        elif signo < 0:
            paso["decision"] = "izquierda"       # raíz en [a, c]
            paso["a_nuevo"], paso["b_nuevo"] = a, c
            b, fb = c, fc
        else:
            paso["decision"] = "derecha"         # raíz en [c, b]
            paso["a_nuevo"], paso["b_nuevo"] = c, b
            a, fa = c, fc

        pasos.append(paso)
        anterior = c

        if signo == 0:
            motivo = "raiz_exacta"
            break
        if error is not None and error / 100 < tolerancia:
            motivo = "tolerancia"
            break

    ultimo = pasos[-1]
    convergio = motivo in ("tolerancia", "raiz_exacta")
    resultado = {
        "raiz": ultimo["c"],
        "iteraciones": len(pasos),
        "fraiz": ultimo["fc"],
        "error": ultimo["error"],
        "convergio": convergio,
        "motivo": motivo,
    }

    advertencias = []
    cerca_de_cero = f_cerca_de_cero(f, a0, b0, ultimo["fc"], convergio)
    if not cerca_de_cero:
        advertencias.append(
            "f(raíz) no es cercano a 0: la función podría tener una "
            "discontinuidad en el intervalo (por ejemplo un polo como 1/x) y "
            "el método solo habría encontrado un cambio de signo, no una raíz."
        )
    if not convergio:
        advertencias.append(
            f"Se agotaron las {max_iter} iteraciones sin llegar a la tolerancia "
            "E. Regula Falsi puede ser lenta cuando un extremo se queda fijo; "
            "aumenta el máximo de iteraciones, usa una E mayor o prueba la "
            "bisección."
        )

    agregar_iteraciones(grafica, pasos, resultado)
    for punto, p in zip(grafica["iteraciones"], pasos):
        # Recta secante usada en esa iteración, para dibujarla en la gráfica.
        punto["secante"] = [[p["a"], p["fa"]], [p["b"], p["fb"]]]

    return {
        "operacion": "falsa_posicion",
        "bloqueada": False,
        "entradas": {
            "funcion": f.texto, "a": a0, "b": b0, "tolerancia": tolerancia,
            "max_iter": max_iter,
        },
        "inicial": {"fa": f(a0), "fb": f(b0)},
        "pasos": pasos,
        "resultado": resultado,
        "continuidad": continuidad,
        "grafica": grafica,
        "advertencias": advertencias,
        "comprobacion": _comprobar(
            f, ultimo, resultado, continuidad, cerca_de_cero),
    }


def _comprobar(f, ultimo, resultado, continuidad, cerca_de_cero):
    """Vuelve a evaluar f en la raíz y en los extremos del intervalo final."""

    a, b = ultimo["a_nuevo"], ultimo["b_nuevo"]
    fraiz = f(resultado["raiz"])
    fa, fb = f(a), f(b)
    cambio_signo = a == b or _signo(fa) * _signo(fb) <= 0
    discontinuidad = not continuidad["sin_senales"] or not cerca_de_cero

    return {
        "raiz": resultado["raiz"], "fraiz": fraiz,
        "intervalo": (a, b), "fa": fa, "fb": fb,
        "cambio_signo": cambio_signo,
        "tolerancia_alcanzada": resultado["convergio"],
        "cerca_de_cero": cerca_de_cero,
        "discontinuidad": discontinuidad,
        "correcto": cambio_signo and resultado["convergio"] and not discontinuidad,
    }


# ---------------------------------------------------------------------------
# Texto del procedimiento (para exportar a PNG/PDF)
# ---------------------------------------------------------------------------

_DECISION_TEXTO = {
    "izquierda": "f(a)·f(c) < 0: la raíz está en [a, c]; b = c",
    "derecha": "f(a)·f(c) > 0: la raíz está en [c, b]; a = c",
    "raiz_exacta": "f(c) = 0: c es la raíz",
}

_MOTIVO_TEXTO = {
    "tolerancia": "Se alcanzó la tolerancia: Ea/100 < E.",
    "raiz_exacta": "Se encontró una raíz exacta: f(c) = 0.",
    "max_iter": "Se agotó el máximo de iteraciones sin llegar a E.",
}


def procedimiento_texto(datos, modo="fraccion", incluir_pasos=True):
    """Procedimiento y resultado de Regula Falsi como texto legible."""

    f = formatear_real
    e = datos["entradas"]
    r = datos["resultado"]
    c = datos["comprobacion"]
    marca = lambda ok: "✓" if ok else "✗"
    par = lambda v: f"({f(v)})" if v < 0 else f(v)   # negativos entre paréntesis

    if datos.get("bloqueada"):
        return "\n".join([
            "MÉTODO DE REGULA FALSI", "",
            f"f(x) = {e['funcion']}",
            f"Intervalo [a, b] = [{f(e['a'])}, {f(e['b'])}]", "",
            "Paso 1. Gráfica de f(x) en [a, b] (ver la figura).",
            "Paso 2. Revisión de continuidad:",
            *continuidad_texto(datos["continuidad"]), "",
            "MÉTODO NO APLICADO: " + datos["motivo_bloqueo"],
        ])

    lineas = [
        "MÉTODO DE REGULA FALSI", "",
        f"f(x) = {e['funcion']}",
        f"Intervalo [a, b] = [{f(e['a'])}, {f(e['b'])}]",
        f"Tolerancia E = {f(e['tolerancia'])} "
        f"({f(e['tolerancia'] * 100)} % de error relativo)",
        f"Máximo de iteraciones: {e['max_iter']}", "",
        f"f(a) = {f(datos['inicial']['fa'])}   f(b) = {f(datos['inicial']['fb'])}",
        "f(a)·f(b) < 0: hay cambio de signo, el intervalo contiene una raíz.",
        "Fórmula: c = b - f(b)·(b - a) / (f(b) - f(a))  "
        "(corte de la secante con el eje x)", "",
    ]

    if incluir_pasos:
        lineas += ["Tabla de iteraciones:", tabla_texto(datos["pasos"]), ""]
        for p in datos["pasos"]:
            lineas.append(
                f"Iteración {p['i']}: c = {f(p['b'])} - {par(p['fb'])}·"
                f"({f(p['b'])} - {par(p['a'])}) / ({f(p['fb'])} - {par(p['fa'])}) = "
                f"{f(p['c'])}, f(c) = {f(p['fc'])}"
            )
            lineas.append(f"    {_DECISION_TEXTO[p['decision']]}")
            if p["decision"] != "raiz_exacta":
                lineas.append(
                    f"    Nuevo intervalo: [{f(p['a_nuevo'])}, {f(p['b_nuevo'])}]"
                )
            if p["error"] is not None:
                lineas.append(f"    Ea = {f(p['error'], 6)} %")
        lineas.append("")

    lineas += [
        _MOTIVO_TEXTO[r["motivo"]],
        f"Raíz aproximada: x = {f(r['raiz'])}",
        f"Iteraciones: {r['iteraciones']}",
        f"f(raíz) = {f(r['fraiz'])}",
        f"Error relativo final Ea = {f(r['error'], 6)} %",
    ]
    lineas += [f"Aviso: {texto}" for texto in datos["advertencias"]]
    lineas += ["", *continuidad_texto(datos["continuidad"])]
    lineas += [
        "", "Comprobación (se vuelve a evaluar f):",
        f"f({f(c['raiz'])}) = {f(c['fraiz'])}",
        f"Intervalo final [{f(c['intervalo'][0])}, {f(c['intervalo'][1])}]: "
        f"f(a) = {f(c['fa'])}, f(b) = {f(c['fb'])}",
        f"Sigue habiendo cambio de signo {marca(c['cambio_signo'])}",
        f"Tolerancia alcanzada {marca(c['tolerancia_alcanzada'])}",
    ]

    return "\n".join(lineas)
