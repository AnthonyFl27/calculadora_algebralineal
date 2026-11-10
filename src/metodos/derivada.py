"""
Derivada simbólica de f(x) para el método de Newton-Raphson.

Trabaja sobre el árbol que arma `evaluador.py` (nodos `num`, `var`, `neg`,
`fn` y `bin`) aplicando las reglas de derivación (suma, producto, cociente,
potencia, cadena) y simplifica lo evidente (0, 1, constantes). Devuelve la
derivada como `Funcion` (con su texto legible), así se evalúa con el mismo
analizador sin `eval()`. Solo usa la librería estándar.
"""

import math

from .evaluador import Funcion

CERO, UNO = ("num", 0.0), ("num", 1.0)


def _es_num(n, valor=None):
    return n[0] == "num" and (valor is None or n[1] == valor)


def _tiene_x(n):
    if n[0] == "var":
        return True
    if n[0] == "num":
        return False
    if n[0] == "neg":
        return _tiene_x(n[1])
    if n[0] == "fn":
        return _tiene_x(n[2])
    return _tiene_x(n[2]) or _tiene_x(n[3])


# --- constructores que simplifican -------------------------------------

def _neg(a):
    if _es_num(a):
        return ("num", -a[1])
    if a[0] == "neg":
        return a[1]
    return ("neg", a)


def _sum(a, b):
    if _es_num(a, 0):
        return b
    if _es_num(b, 0):
        return a
    if _es_num(a) and _es_num(b):
        return ("num", a[1] + b[1])
    return ("bin", "+", a, b)


def _res(a, b):
    if _es_num(b, 0):
        return a
    if _es_num(a, 0):
        return _neg(b)
    if _es_num(a) and _es_num(b):
        return ("num", a[1] - b[1])
    return ("bin", "-", a, b)


def _mul(a, b):
    if _es_num(a, 0) or _es_num(b, 0):
        return CERO
    if _es_num(a, 1):
        return b
    if _es_num(b, 1):
        return a
    if _es_num(a) and _es_num(b):
        return ("num", a[1] * b[1])
    if _es_num(a) and b[0] == "neg":
        return _mul(("num", -a[1]), b[1])
    if _es_num(b) and b[1] < 0 and not _es_num(a):
        return _neg(_mul(a, ("num", -b[1])))
    if _es_num(b) and not _es_num(a):          # constante primero: 3*x, no x*3
        return _mul(b, a)
    if _es_num(a) and b[0] == "bin" and b[1] == "*" and _es_num(b[2]):
        return _mul(("num", a[1] * b[2][1]), b[3])     # 5·(3·u) = 15·u
    if a[0] == "neg":
        return _neg(_mul(a[1], b))
    if b[0] == "neg":
        return _neg(_mul(a, b[1]))
    return ("bin", "*", a, b)


def _div(a, b):
    if _es_num(a, 0):
        return CERO
    if _es_num(b, 1):
        return a
    if _es_num(a) and _es_num(b) and b[1] != 0:
        return ("num", a[1] / b[1])
    if a[0] == "neg":
        return _neg(_div(a[1], b))
    return ("bin", "/", a, b)


def _pot(a, b):
    if _es_num(b, 1):
        return a
    if _es_num(b, 0):
        return UNO
    return ("bin", "^", a, b)


def _fn(nombre, a):
    return ("fn", nombre, a)


# --- derivada -----------------------------------------------------------

_LN10, _LN2 = math.log(10), math.log(2)


def _derivada_funcion(nombre, u):
    """Derivada de nombre(u) respecto de u (antes de la regla de la cadena)."""

    cuadrado = lambda t: _pot(t, ("num", 2.0))
    uno_menos_u2 = _res(UNO, cuadrado(u))
    if nombre in ("sin", "sen"):
        return _fn("cos", u)
    if nombre == "cos":
        return _neg(_fn("sin", u))
    if nombre == "tan":
        return _div(UNO, cuadrado(_fn("cos", u)))
    if nombre in ("asin", "arcsin", "arcsen"):
        return _div(UNO, _fn("sqrt", uno_menos_u2))
    if nombre in ("acos", "arccos"):
        return _neg(_div(UNO, _fn("sqrt", uno_menos_u2)))
    if nombre in ("atan", "arctan"):
        return _div(UNO, _sum(UNO, cuadrado(u)))
    if nombre in ("sinh", "senh"):
        return _fn("cosh", u)
    if nombre == "cosh":
        return _fn("sinh", u)
    if nombre == "tanh":
        return _res(UNO, cuadrado(_fn("tanh", u)))
    if nombre == "exp":
        return _fn("exp", u)
    if nombre == "ln":
        return _div(UNO, u)
    if nombre in ("log", "log10"):
        return _div(UNO, _mul(u, ("num", _LN10)))
    if nombre == "log2":
        return _div(UNO, _mul(u, ("num", _LN2)))
    if nombre in ("sqrt", "raiz"):
        return _div(UNO, _mul(("num", 2.0), _fn("sqrt", u)))
    if nombre == "cbrt":
        return _div(UNO, _mul(("num", 3.0), cuadrado(_fn("cbrt", u))))
    if nombre == "abs":
        return _div(u, _fn("abs", u))        # u/|u| (signo de u)
    raise ValueError(f"No sé derivar la función {nombre}.")


def derivar(n):
    """Árbol de la derivada de `n` respecto de x."""

    tipo = n[0]
    if tipo == "num":
        return CERO
    if tipo == "var":
        return UNO
    if tipo == "neg":
        return _neg(derivar(n[1]))
    if tipo == "fn":
        u = n[2]
        return _mul(_derivada_funcion(n[1], u), derivar(u))

    _, op, a, b = n
    da, db = derivar(a), derivar(b)
    if op == "+":
        return _sum(da, db)
    if op == "-":
        return _res(da, db)
    if op == "*":
        return _sum(_mul(da, b), _mul(a, db))
    if op == "/":
        return _div(_res(_mul(da, b), _mul(a, db)), _pot(b, ("num", 2.0)))

    # potencia a^b
    if not _tiene_x(b):                           # a^k  ->  k·a^(k-1)·a'
        k = _res(b, UNO)
        return _mul(_mul(b, _pot(a, k)), da)
    if not _tiene_x(a):                           # k^b  ->  k^b·ln(k)·b'
        return _mul(_mul(n, _fn("ln", a)), db)
    # a^b con x en los dos: a^b·(b'·ln a + b·a'/a)
    return _mul(n, _sum(_mul(db, _fn("ln", a)), _div(_mul(b, da), a)))


# --- texto legible --------------------------------------------------------

def _numero_texto(v):
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return f"{v:.10g}"


# Precedencias: 1 suma/resta, 2 producto/división, 3 negación, 4 potencia, 5 átomo
def _texto(n):
    """(texto, precedencia) de un nodo, con los paréntesis mínimos."""

    tipo = n[0]
    if tipo == "num":
        v = n[1]
        return (_numero_texto(v), 5 if v >= 0 else 3)
    if tipo == "var":
        return ("x", 5)
    if tipo == "fn":
        return (f"{n[1]}({_texto(n[2])[0]})", 5)
    if tipo == "neg":
        t, p = _texto(n[1])
        return ("-" + (f"({t})" if p < 3 else t), 3)

    _, op, a, b = n
    ta, pa = _texto(a)
    tb, pb = _texto(b)
    if op in "+-":
        if op == "-" and pb < 3:
            tb = f"({tb})"
        elif pb < 1:
            tb = f"({tb})"
        if pb == 3 and tb.startswith("-") and op == "+":
            return (f"{ta} - {tb[1:]}", 1)
        return (f"{ta} {op} {tb}", 1)
    if op in "*/":
        if pa < 2:
            ta = f"({ta})"
        if pb < 3 or (op == "/" and pb < 5) or pb == 3:
            tb = f"({tb})"
        return (f"{ta}{' * ' if op == '*' else ' / '}{tb}", 2)
    if pa < 5:
        ta = f"({ta})"
    if pb < 5:
        tb = f"({tb})"
    return (f"{ta}^{tb}", 4)


def derivada_de(funcion):
    """Derivada simbólica de una `Funcion` como otra `Funcion`."""

    arbol = derivar(funcion.arbol)
    return Funcion.desde_arbol(arbol, _texto(arbol)[0])
