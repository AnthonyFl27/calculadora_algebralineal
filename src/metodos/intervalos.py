"""
Buscador de intervalos [a, b] para los métodos de raíces (bisección y Regula
Falsi).

Los dos métodos piden un intervalo donde f sea continua y f(a)·f(b) < 0. Aquí
se encuentra con el mismo procedimiento que se hace a mano:

1. Tabla de valores: se evalúa f en los enteros de `desde` a `hasta`.
2. Se buscan dos valores consecutivos con signo contrario (cambio de signo).
3. Cada candidato se pasa por `revisar_continuidad`: si hay un polo o un salto
   (por ejemplo tan(x) cerca de π/2), el cambio de signo es falso y se
   descarta; ese tramo se vuelve a recorrer con paso 0.1.
4. Si en toda la tabla no hay ningún cambio de signo, se repite el recorrido
   completo con paso 0.1.

Es una ayuda numérica, no una demostración: dos raíces dentro del mismo tramo
(f cambia de signo dos veces) pasan inadvertidas. Sin librerías externas.
"""

from .continuidad import revisar_continuidad
from .evaluador import compilar

DESDE_POR_DEFECTO = -10
HASTA_POR_DEFECTO = 10
MAX_INTERVALOS = 8
PASO_FINO = 0.1
MAX_RANGO = 1000


def _puntos(desde, hasta, paso):
    """Valores desde, desde + paso, …, hasta (redondeados para no arrastrar
    errores como 1.2000000000000002)."""

    n = int(round((hasta - desde) / paso))
    return [round(desde + k * paso, 10) for k in range(n + 1)]


def _tabla(f, xs):
    filas = []
    for x in xs:
        valor, motivo = f.evaluar_seguro(x)
        filas.append((x, valor, motivo))
    return filas


def _candidatos(filas):
    """Pares consecutivos con cambio de signo y raíces exactas en la tabla."""

    pares, exactas = [], []
    for k, (x, valor, _) in enumerate(filas):
        if valor == 0:
            exactas.append(x)
        if k == 0:
            continue
        xa, va, _ = filas[k - 1]
        if va is None or valor is None or va == 0 or valor == 0:
            continue
        if (va > 0) != (valor > 0):
            pares.append((xa, x, va, valor))
    return pares, exactas


def _recorrer(f, desde, hasta, paso, origen, intervalos, descartados, exactas):
    """Busca cambios de signo con `paso`; los continuos van a `intervalos`,
    los que cruzan una discontinuidad a `descartados` (devuelve estos)."""

    pares, ceros = _candidatos(_tabla(f, _puntos(desde, hasta, paso)))
    for x in ceros:
        if x not in exactas:
            exactas.append(x)

    pendientes = []
    for a, b, fa, fb in pares:
        revision = revisar_continuidad(f, a, b)
        if revision["sin_senales"]:
            intervalos.append(
                {"a": a, "b": b, "fa": fa, "fb": fb, "origen": origen})
        else:
            motivo = revision["sospechas"][0]["mensaje"]
            pendientes.append({"a": a, "b": b, "fa": fa, "fb": fb,
                               "motivo": motivo})
    return pendientes


def buscar_intervalos(funcion, desde=DESDE_POR_DEFECTO, hasta=HASTA_POR_DEFECTO):
    """
    Sugiere intervalos [a, b] para `funcion` (texto) entre `desde` y `hasta`.

    Devuelve:
    - `tabla`: lista de `(x, f(x))` de la tabla de valores con paso 1
      (`f(x)` es None donde f no está definida);
    - `intervalos`: hasta `MAX_INTERVALOS` dicts `a`, `b`, `fa`, `fb`, `origen`
      (`"enteros"` o `"refinado"`) con f continua y f(a)·f(b) < 0;
    - `descartados`: cambios de signo que cruzan una discontinuidad
      (`a`, `b`, `motivo`);
    - `raices_exactas`: puntos de la tabla donde f(x) = 0;
    - `desde`, `hasta`, `paso`.

    Lanza ValueError (en español) con una función inválida o un rango malo.
    """

    f = compilar(funcion)
    if not f.usa_x:
        raise ValueError("La función debe depender de x (por ejemplo x^2 - 2).")

    desde, hasta = _entero(desde, "desde"), _entero(hasta, "hasta")
    if desde >= hasta:
        raise ValueError("El rango debe cumplir desde < hasta.")
    if hasta - desde > MAX_RANGO:
        raise ValueError(f"El rango puede tener como máximo {MAX_RANGO} unidades.")

    intervalos, descartados, exactas = [], [], []

    # Recorrido con enteros; los tramos con discontinuidad se afinan a 0.1.
    for pendiente in _recorrer(f, desde, hasta, 1, "enteros",
                               intervalos, descartados, exactas):
        descartados.append(pendiente)
        _recorrer(f, pendiente["a"], pendiente["b"], PASO_FINO, "refinado",
                  intervalos, [], exactas)

    # Sin ningún cambio de signo: se repite todo el rango con paso 0.1.
    if not intervalos and not descartados:
        descartados += _recorrer(f, desde, hasta, PASO_FINO, "refinado",
                                 intervalos, [], exactas)

    intervalos.sort(key=lambda i: i["a"])
    tabla = [(x, valor) for x, valor, _ in _tabla(f, _puntos(desde, hasta, 1))]

    return {
        "desde": desde, "hasta": hasta, "paso": 1,
        "tabla": tabla,
        "intervalos": intervalos[:MAX_INTERVALOS],
        "total_intervalos": len(intervalos),
        "descartados": descartados,
        "raices_exactas": sorted(exactas),
    }


def _entero(valor, nombre):
    try:
        if isinstance(valor, bool):
            raise ValueError
        numero = float(str(valor).strip().replace(",", "."))
        if numero != int(numero):
            raise ValueError
        return int(numero)
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f"El límite «{nombre}» debe ser un número entero.")
