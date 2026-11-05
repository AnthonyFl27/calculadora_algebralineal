"""
Evaluador de funciones f(x) escritas como texto.

Analiza la expresión con un analizador descendente recursivo escrito a mano y
la evalúa con la librería estándar (`math`). Nunca usa `eval()` ni `exec()`,
así que un texto escrito en la web no puede ejecutar código.

Gramática (de menor a mayor precedencia):

    expresion := termino (('+' | '-') termino)*
    termino   := unario (('*' | '/') unario | factor_implicito)*
    unario    := ('+' | '-') unario | potencia
    potencia  := primario ('^' unario)?          # asociativa a la derecha
    primario  := numero | constante | 'x' | funcion '(' expresion ')'
               | '(' expresion ')'

La multiplicación implícita (`2x`, `3(x+1)`, `(x+1)(x-1)`, `2pi`) tiene la
misma precedencia que `*`. `-x^2` se lee como `-(x^2)`.

Lo usan los métodos de búsqueda de raíces (`biseccion.py` y los siguientes).
"""

import math
import re

MAX_LONGITUD = 200
MAX_PROFUNDIDAD = 40


def _cbrt(valor):
    return math.copysign(abs(valor) ** (1 / 3), valor)


FUNCIONES = {
    "sin": math.sin, "sen": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "arcsin": math.asin, "arcsen": math.asin,
    "acos": math.acos, "arccos": math.acos,
    "atan": math.atan, "arctan": math.atan,
    "sinh": math.sinh, "senh": math.sinh, "cosh": math.cosh,
    "tanh": math.tanh,
    "exp": math.exp, "ln": math.log, "log": math.log10, "log10": math.log10,
    "log2": math.log2,
    "sqrt": math.sqrt, "raiz": math.sqrt, "cbrt": _cbrt, "abs": abs,
}
CONSTANTES = {"pi": math.pi, "e": math.e}

# Teclados móviles y texto copiado traen estos símbolos.
_SIMBOLOS = str.maketrans({
    "−": "-", "–": "-", "×": "*", "·": "*", "÷": "/", "π": "pi",
    "²": "^2", "³": "^3", "[": "(", "]": ")", "{": "(", "}": ")",
})

_NUMERO = re.compile(r"(\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?")


def _separar_letras(letras):
    """Parte una racha de letras en x, e, pi (p. ej. 'xe' -> x, e)."""

    partes = []
    i = 0
    while i < len(letras):
        for nombre in ("pi", "x", "e"):
            if letras.startswith(nombre, i):
                partes.append(nombre)
                i += len(nombre)
                break
        else:
            return None
    return partes


def _tokenizar(texto):
    texto = texto.translate(_SIMBOLOS).replace("**", "^")
    tokens = []
    i = 0

    while i < len(texto):
        caracter = texto[i]

        if caracter.isspace():
            i += 1
        elif caracter.isdigit() or caracter in ".,":
            m = _NUMERO.match(texto, i)
            if not m:
                raise ValueError(f"No entiendo el símbolo '{caracter}'.")
            try:
                valor = float(m.group(0).replace(",", "."))
            except ValueError:
                raise ValueError(f"El número '{m.group(0)}' no es válido.")
            tokens.append(("num", valor))
            i = m.end()
        elif caracter.isalpha():
            j = i
            while j < len(texto) and texto[j].isalpha():
                j += 1
            nombre = texto[i:j].lower()
            if nombre in FUNCIONES:
                tokens.append(("fn", nombre))
            elif nombre in CONSTANTES or nombre == "x":
                tokens.append(("id", nombre))
            else:
                partes = _separar_letras(nombre)
                if partes is None:
                    raise ValueError(
                        f"No reconozco '{texto[i:j]}'. Usa x, pi, e o una "
                        "función como sin(x), exp(x), ln(x), sqrt(x)."
                    )
                tokens.extend(("id", p) for p in partes)
            i = j
        elif caracter in "+-*/^()":
            tokens.append(("op", caracter))
            i += 1
        else:
            raise ValueError(f"No entiendo el símbolo '{caracter}'.")

    return tokens


class _Analizador:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.profundidad = 0
        self.usa_x = False

    def _ver(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _es_op(self, *operadores):
        t = self._ver()
        return t is not None and t[0] == "op" and t[1] in operadores

    def _entrar(self):
        self.profundidad += 1
        if self.profundidad > MAX_PROFUNDIDAD:
            raise ValueError("La expresión tiene demasiados paréntesis anidados.")

    def _salir(self):
        self.profundidad -= 1

    def analizar(self):
        if not self.tokens:
            raise ValueError("Escribe una función, por ejemplo x^2 - 2.")
        nodo = self._expresion()
        sobrante = self._ver()
        if sobrante is not None:
            if sobrante == ("op", ")"):
                raise ValueError("Hay un paréntesis ')' de más.")
            raise ValueError("Falta un operador en la expresión (por ejemplo *).")
        return nodo

    def _expresion(self):
        self._entrar()
        nodo = self._termino()
        while self._es_op("+", "-"):
            op = self.tokens[self.pos][1]
            self.pos += 1
            nodo = ("bin", op, nodo, self._termino())
        self._salir()
        return nodo

    def _inicia_primario(self):
        t = self._ver()
        return t is not None and (
            t[0] in ("id", "fn") or t == ("op", "("))

    def _termino(self):
        nodo = self._unario()
        while True:
            if self._es_op("*", "/"):
                op = self.tokens[self.pos][1]
                self.pos += 1
                nodo = ("bin", op, nodo, self._unario())
            elif self._inicia_primario():
                nodo = ("bin", "*", nodo, self._potencia())
            else:
                return nodo

    def _unario(self):
        if self._es_op("+", "-"):
            op = self.tokens[self.pos][1]
            self.pos += 1
            self._entrar()
            operando = self._unario()
            self._salir()
            return ("neg", operando) if op == "-" else operando
        return self._potencia()

    def _potencia(self):
        base = self._primario()
        if self._es_op("^"):
            self.pos += 1
            return ("bin", "^", base, self._unario())
        return base

    def _primario(self):
        t = self._ver()

        if t is None:
            raise ValueError("La expresión está incompleta: falta un valor al final.")

        self.pos += 1

        if t[0] == "num":
            return ("num", t[1])

        if t[0] == "id":
            if t[1] == "x":
                self.usa_x = True
                return ("var",)
            return ("num", CONSTANTES[t[1]])

        if t[0] == "fn":
            if not self._es_op("("):
                raise ValueError(
                    f"La función {t[1]} necesita paréntesis: {t[1]}(x)."
                )
            self.pos += 1
            argumento = self._expresion()
            self._cerrar()
            return ("fn", t[1], argumento)

        if t == ("op", "("):
            nodo = self._expresion()
            self._cerrar()
            return nodo

        if t == ("op", ")"):
            raise ValueError("Hay un paréntesis vacío o un ')' de más.")

        raise ValueError(f"Falta un valor antes de '{t[1]}'.")

    def _cerrar(self):
        if not self._es_op(")"):
            raise ValueError("Falta cerrar un paréntesis ')'.")
        self.pos += 1


def _evaluar(nodo, x):
    tipo = nodo[0]

    if tipo == "num":
        return nodo[1]
    if tipo == "var":
        return x
    if tipo == "neg":
        return -_evaluar(nodo[1], x)
    if tipo == "fn":
        return FUNCIONES[nodo[1]](_evaluar(nodo[2], x))

    _, op, izq, der = nodo
    a, b = _evaluar(izq, x), _evaluar(der, x)

    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a / b
    return math.pow(a, b)


class Funcion:
    """f(x) ya analizada. Se llama como una función: `f(1.5)`."""

    def __init__(self, texto):
        texto = str(texto if texto is not None else "").strip()

        if len(texto) > MAX_LONGITUD:
            raise ValueError(
                f"La expresión es demasiado larga (máximo {MAX_LONGITUD} caracteres)."
            )

        analizador = _Analizador(_tokenizar(texto))
        self._arbol = analizador.analizar()
        self.texto = texto
        self.usa_x = analizador.usa_x

    def __call__(self, x):
        try:
            valor = _evaluar(self._arbol, float(x))
        except ZeroDivisionError:
            motivo = "división entre cero"
        except OverflowError:
            motivo = "el resultado es demasiado grande"
        except (ValueError, RecursionError):
            motivo = "fuera del dominio de la función"
        else:
            if isinstance(valor, float) and math.isfinite(valor):
                return valor
            if isinstance(valor, int):
                return float(valor)
            motivo = "el resultado no es un número finito"

        raise ValueError(
            f"No se puede evaluar f(x) en x = {x:.10g}: {motivo}."
        )


def compilar(texto):
    """Analiza `texto` y devuelve una `Funcion` (ValueError si está mal escrita)."""

    return Funcion(texto)


def evaluar_numero(texto, nombre="el valor"):
    """Evalúa una expresión constante (sin x), como `0.55`, `pi/2` o `1e-4`."""

    if isinstance(texto, bool):
        raise ValueError(f"{nombre} debe ser un número.")
    if isinstance(texto, (int, float)):
        valor = float(texto)
    else:
        texto = str(texto if texto is not None else "").strip()
        if texto == "":
            raise ValueError(f"Escribe {nombre}.")
        try:
            funcion = Funcion(texto)
        except ValueError as error:
            raise ValueError(f"{nombre}: {error}")
        if funcion.usa_x:
            raise ValueError(f"{nombre} debe ser un número, sin la variable x.")
        valor = funcion(0.0)

    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser un número finito.")
    return valor
