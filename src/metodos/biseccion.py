"""
Método de Bisección para resolver f(x) = 0.

Dada f continua en [a, b] con f(a)·f(b) < 0, el Teorema del Valor Intermedio
garantiza una raíz en el intervalo. Cada iteración toma el punto medio
c = (a + b) / 2 y se queda con la mitad donde sigue habiendo cambio de signo.

Criterio de paro: ε_a/100 < E, donde ε_a = |(c_nuevo − c_anterior)/c_nuevo|·100
(porcentaje, desde la 2.ª iteración). E se compara contra ε_a como fracción;
así E = 0.0001 reproduce el caso de referencia del profesor (13 iteraciones).

La función se escribe como texto y se evalúa con `evaluador.py`. La aritmética
es de punto flotante (la función puede ser trascendente), sin librerías
externas.
"""

import math

from .continuidad import revisar_continuidad
from .evaluador import compilar, evaluar_numero
from .grafica import datos_grafica

MAX_ITERACIONES = 200
ITERACIONES_POR_DEFECTO = 50


def formatear_real(valor, cifras=10):
    """Número real con `cifras` cifras significativas (None -> '—')."""

    if valor is None:
        return "—"
    if valor == 0:
        return "0"
    texto = f"{valor:.{cifras}g}"
    return "0" if texto in ("-0", "0.0") else texto


def _signo(valor):
    return (valor > 0) - (valor < 0)


def _validar_entradas(funcion, a, b, tolerancia, max_iter):
    f = compilar(funcion)

    if not f.usa_x:
        raise ValueError(
            "La función debe depender de x (por ejemplo x^2 - 2)."
        )

    a = evaluar_numero(a, "El extremo a")
    b = evaluar_numero(b, "El extremo b")
    tolerancia = evaluar_numero(tolerancia, "La tolerancia E")

    if a >= b:
        raise ValueError(
            f"El extremo a debe ser menor que b (se recibió a = {formatear_real(a)} "
            f"y b = {formatear_real(b)})."
        )

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
            f"El máximo de iteraciones debe estar entre 1 y {MAX_ITERACIONES}."
        )

    return f, a, b, tolerancia, max_iter


def cota_iteraciones(a, b, tolerancia):
    """Iteraciones n ≥ log2((b − a)/tol) para un error absoluto igual a tol."""

    if tolerancia >= b - a:
        return 1
    return math.ceil(math.log2((b - a) / tolerancia))


def biseccion(funcion, a, b, tolerancia, max_iter=ITERACIONES_POR_DEFECTO):
    """
    Aplica la bisección a `funcion` (texto) en [a, b].

    Devuelve un diccionario con `entradas`, `inicial`, `pasos` (una iteración
    cada uno), `resultado`, `cota_iteraciones`, `continuidad` (revisión previa
    del intervalo, ver `continuidad.py`), `grafica` (datos para dibujar f y las
    iteraciones, ver `grafica.py`), `advertencias` y `comprobacion`. Lanza ValueError (en español) con datos inválidos o sin
    cambio de signo.
    """

    f, a, b, tolerancia, max_iter = _validar_entradas(
        funcion, a, b, tolerancia, max_iter)

    a0, b0 = a, b
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

    continuidad = revisar_continuidad(f, a0, b0)

    pasos = []
    anterior = None
    motivo = "max_iter"

    for i in range(1, max_iter + 1):
        c = (a + b) / 2
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
    if not continuidad["sin_senales"]:
        advertencias.append(
            "Se detectaron señales de discontinuidad en el intervalo (ver "
            "el apartado Continuidad): la bisección solo garantiza una raíz "
            "si f es continua en [a, b]."
        )
    f_extremos = (abs(f(a0)), abs(f(b0)))
    cerca_de_cero = not (abs(ultimo["fc"]) > max(f_extremos) or (
        convergio and abs(ultimo["fc"]) >= min(f_extremos)))
    if not cerca_de_cero:
        advertencias.append(
            "f(raíz) no es cercano a 0: la función podría tener una "
            "discontinuidad en el intervalo (por ejemplo un polo como 1/x) y "
            "la bisección solo habría encontrado un cambio de signo, no una raíz."
        )
    if not convergio:
        advertencias.append(
            f"Se agotaron las {max_iter} iteraciones sin llegar a la tolerancia "
            "E. Aumenta el máximo de iteraciones o usa una E mayor."
        )

    return {
        "operacion": "biseccion",
        "entradas": {
            "funcion": f.texto, "a": a0, "b": b0, "tolerancia": tolerancia,
            "max_iter": max_iter,
        },
        "inicial": {"fa": f(a0), "fb": f(b0)},
        "pasos": pasos,
        "resultado": resultado,
        "cota_iteraciones": cota_iteraciones(a0, b0, tolerancia),
        "continuidad": continuidad,
        "grafica": datos_grafica(f, a0, b0, pasos, resultado, continuidad),
        "advertencias": advertencias,
        "comprobacion": _comprobar(
            f, ultimo, resultado, continuidad, cerca_de_cero),
    }


def _comprobar(f, ultimo, resultado, continuidad, cerca_de_cero):
    """Vuelve a evaluar f en la raíz y en los extremos del intervalo final.

    `discontinuidad` es True si la revisión previa encontró señales o si f(raíz)
    no quedó cerca de 0 (la bisección pudo converger a un polo)."""

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


def tabla_texto(pasos):
    """Tabla de iteraciones (i, a, b, c, f(c), Ea%) en texto de ancho fijo."""

    f = formatear_real
    filas = [("i", "a", "b", "c", "f(c)", "Ea (%)")]
    for p in pasos:
        filas.append((str(p["i"]), f(p["a"]), f(p["b"]), f(p["c"]),
                      f(p["fc"]), f(p["error"], 6)))
    anchos = [max(len(fila[k]) for fila in filas) for k in range(6)]
    return "\n".join(
        "  ".join(celda.rjust(anchos[k]) for k, celda in enumerate(fila))
        for fila in filas
    )


def continuidad_texto(continuidad):
    """Líneas de la revisión de continuidad (vista y archivos exportados)."""

    lineas = [f"Continuidad (revisión en {continuidad['muestras']} puntos "
              "del intervalo):"]
    if continuidad["sin_senales"]:
        lineas.append("No se detectaron señales de discontinuidad "
                      "(es una revisión numérica, no una demostración).")
        return lineas
    lineas += [f"- {s['mensaje']}" for s in continuidad["sospechas"]]
    resto = continuidad["total"] - len(continuidad["sospechas"])
    if resto > 0:
        lineas.append(f"- ... y {resto} más.")
    return lineas


def procedimiento_texto(datos, modo="fraccion", incluir_pasos=True):
    """Procedimiento y resultado de la bisección como texto legible."""

    f = formatear_real
    e = datos["entradas"]
    r = datos["resultado"]
    c = datos["comprobacion"]
    marca = lambda ok: "✓" if ok else "✗"

    lineas = [
        "MÉTODO DE BISECCIÓN", "",
        f"f(x) = {e['funcion']}",
        f"Intervalo [a, b] = [{f(e['a'])}, {f(e['b'])}]",
        f"Tolerancia E = {f(e['tolerancia'])} "
        f"({f(e['tolerancia'] * 100)} % de error relativo)",
        f"Máximo de iteraciones: {e['max_iter']}", "",
        f"f(a) = {f(datos['inicial']['fa'])}   f(b) = {f(datos['inicial']['fb'])}",
        "f(a)·f(b) < 0: hay cambio de signo, el intervalo contiene una raíz.", "",
    ]

    if incluir_pasos:
        lineas += ["Tabla de iteraciones:", tabla_texto(datos["pasos"]), ""]
        for p in datos["pasos"]:
            lineas.append(
                f"Iteración {p['i']}: c = ({f(p['a'])} + {f(p['b'])})/2 = "
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
        f"Iteraciones: {r['iteraciones']} "
        f"(cota teórica: n >= {datos['cota_iteraciones']})",
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
