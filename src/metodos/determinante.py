"""
Determinante de una matriz cuadrada por cofactores o por factorización LU.

Implementado a mano con Fraction (aritmética exacta), sin librerías externas.
Incluye una recomendación de eficiencia según el tamaño n para que el usuario
sepa cuál método conviene antes de elegir.

En los conteos, "multiplicaciones" incluye también las divisiones (los
multiplicadores de LU), que cuestan lo mismo que una multiplicación.
"""

from fractions import Fraction
from math import factorial

from .general_metodos import formatear
from .vectores_matrices import _dimensiones, _matriz, matriz_general_texto

METODOS_DETERMINANTE = ("cofactores", "lu")
NOMBRES_METODO = {"cofactores": "Cofactores", "lu": "LU"}

N_MAX_LU = 8
N_MAX_COFACTORES = 6


def _copiar(matriz):
    return [list(fila) for fila in matriz]


def _estimar_lu(n):
    return round(n ** 3 / 3)


def recomendar_metodo(n):
    """
    Indica cuál método es más eficiente para una matriz de n × n.

    Depende solo de n: cofactores crece como n! y LU como n³/3.
    """

    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("El tamaño n debe ser un entero positivo.")

    ops_cofactores = factorial(n)
    ops_lu = _estimar_lu(n)

    if n <= 3:
        recomendado = "cofactores"
        motivo = (
            f"Con n = {n} la matriz es pequeña: cofactores se resuelve "
            "directo y no hace falta factorizar nada."
        )
    else:
        recomendado = "lu"
        motivo = (
            f"Con n = {n}, cofactores necesita del orden de {ops_cofactores} "
            f"multiplicaciones (n!), mientras que LU necesita unas {ops_lu} "
            "(n³/3). LU es mucho más eficiente."
        )

    return {
        "n": n,
        "cofactores": {
            "operaciones": ops_cofactores,
            "texto": f"≈ n! = {ops_cofactores} multiplicaciones",
        },
        "lu": {
            "operaciones": ops_lu,
            "texto": f"≈ n³/3 = {ops_lu} multiplicaciones",
        },
        "recomendado": recomendado,
        "motivo": motivo,
        "cofactores_disponible": n <= N_MAX_COFACTORES,
        "lu_disponible": n <= N_MAX_LU,
        "maximo_cofactores": N_MAX_COFACTORES,
        "maximo_lu": N_MAX_LU,
    }


# ---------------------------------------------------------------------------
# Cofactores
# ---------------------------------------------------------------------------

def _menor(matriz, fila, columna):
    return [
        [valor for j, valor in enumerate(f) if j != columna]
        for i, f in enumerate(matriz) if i != fila
    ]


def _elegir_expansion(matriz):
    """Fila o columna con más ceros (empate: la primera, filas primero)."""

    n = len(matriz)
    mejor = ("fila", 0, -1)

    for i in range(n):
        ceros = sum(1 for v in matriz[i] if v == 0)
        if ceros > mejor[2]:
            mejor = ("fila", i, ceros)
    for j in range(n):
        ceros = sum(1 for i in range(n) if matriz[i][j] == 0)
        if ceros > mejor[2]:
            mejor = ("columna", j, ceros)

    return mejor


def _expandir(matriz, contador, tipo=None, indice=None, modo="fraccion"):
    """
    Devuelve (determinante, paso). `contador` es una lista de un elemento
    con las multiplicaciones realizadas hasta ahora.
    """

    n = len(matriz)

    if n == 1:
        return matriz[0][0], {
            "tipo": "base_1x1", "matriz": _copiar(matriz),
            "valor": matriz[0][0],
        }

    if n == 2:
        (a, b), (c, d) = matriz
        contador[0] += 2
        valor = a * d - b * c
        return valor, {
            "tipo": "base_2x2", "matriz": _copiar(matriz), "valor": valor,
            "texto": (
                f"({formatear(a, modo)})·({formatear(d, modo)}) − "
                f"({formatear(b, modo)})·({formatear(c, modo)}) = "
                f"{formatear(valor, modo)}"
            ),
        }

    if tipo is None:
        tipo, indice, ceros = _elegir_expansion(matriz)
        motivo = (
            f"Se expande por la {tipo} {indice + 1} "
            f"({ceros} {'cero' if ceros == 1 else 'ceros'})."
        )
    else:
        motivo = f"Se expande por la {tipo} {indice + 1} (elegida por el usuario)."

    total = Fraction(0)
    terminos = []

    for k in range(n):
        i, j = (indice, k) if tipo == "fila" else (k, indice)
        valor = matriz[i][j]
        signo = 1 if (i + j) % 2 == 0 else -1
        termino = {
            "fila": i + 1, "columna": j + 1, "valor": valor, "signo": signo,
        }

        if valor == 0:
            termino.update(omitido=True, aporte=Fraction(0))
        else:
            menor = _menor(matriz, i, j)
            det_menor, sub = _expandir(menor, contador, modo=modo)
            contador[0] += 1
            aporte = signo * valor * det_menor
            termino.update(
                omitido=False, menor=menor, det_menor=det_menor,
                paso_menor=sub, aporte=aporte,
            )

        total += termino["aporte"]
        terminos.append(termino)

    return total, {
        "tipo": "expansion", "matriz": _copiar(matriz),
        "expansion": {"tipo": tipo, "indice": indice + 1, "motivo": motivo},
        "terminos": terminos, "valor": total,
    }


def _por_cofactores(matriz, modo, tipo_expansion, indice_expansion):
    n = len(matriz)

    if n > N_MAX_COFACTORES:
        raise ValueError(
            f"Cofactores solo se admite hasta n = {N_MAX_COFACTORES} "
            f"(la matriz es de {n}×{n}): el procedimiento sería enorme. "
            "Usa el método LU."
        )

    tipo = indice = None
    if tipo_expansion is not None or indice_expansion is not None:
        if tipo_expansion not in ("fila", "columna"):
            raise ValueError("La expansión debe ser por 'fila' o 'columna'.")
        if (isinstance(indice_expansion, bool)
                or not isinstance(indice_expansion, int)
                or not 1 <= indice_expansion <= n):
            raise ValueError(
                f"La {tipo_expansion} de expansión debe estar entre 1 y {n}."
            )
        tipo, indice = tipo_expansion, indice_expansion - 1

    contador = [0]
    valor, paso = _expandir(matriz, contador, tipo, indice, modo)

    return {
        "pasos": [paso],
        "resultado": valor,
        "multiplicaciones": contador[0],
        "expansion": (
            paso["expansion"] if paso["tipo"] == "expansion" else None
        ),
    }


# ---------------------------------------------------------------------------
# LU con pivoteo parcial
# ---------------------------------------------------------------------------

def _factorizar_lu(matriz):
    """
    Factoriza P·A = L·U (Doolittle con pivoteo parcial).

    Si una columna no tiene pivote se registra y se continúa: U queda con un 0
    en la diagonal (det = 0) y la igualdad P·A = L·U se sigue cumpliendo.
    """

    n = len(matriz)
    u = _copiar(matriz)
    l = [[Fraction(0)] * n for _ in range(n)]
    permutacion = list(range(n))
    intercambios = 0
    contador = 0
    pasos = []

    for k in range(n):
        paso = {
            "tipo": "eliminacion", "columna": k + 1, "intercambio": None,
            "pivote": None, "multiplicadores": [],
        }

        if u[k][k] == 0:
            candidata = next((i for i in range(k + 1, n) if u[i][k] != 0), None)
            if candidata is None:
                paso["tipo"] = "sin_pivote"
                paso["U"], paso["L"] = _copiar(u), _copiar(l)
                pasos.append(paso)
                continue
            u[k], u[candidata] = u[candidata], u[k]
            l[k], l[candidata] = l[candidata], l[k]
            permutacion[k], permutacion[candidata] = (
                permutacion[candidata], permutacion[k])
            intercambios += 1
            paso["intercambio"] = (k + 1, candidata + 1)

        pivote = u[k][k]
        paso["pivote"] = pivote

        for i in range(k + 1, n):
            if u[i][k] == 0:
                continue
            m = u[i][k] / pivote
            contador += 1
            for j in range(k, n):
                u[i][j] -= m * u[k][j]
                if j > k:
                    contador += 1
            l[i][k] = m
            paso["multiplicadores"].append({"fila": i + 1, "valor": m})

        paso["U"], paso["L"] = _copiar(u), _copiar(l)
        pasos.append(paso)

    for i in range(n):
        l[i][i] = Fraction(1)

    permutacion_matriz = [
        [Fraction(int(j == permutacion[i])) for j in range(n)]
        for i in range(n)
    ]

    return {
        "pasos": pasos, "L": l, "U": u, "P": permutacion_matriz,
        "intercambios": intercambios, "multiplicaciones": contador,
    }


def _multiplicar(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b)))
         for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def _por_lu(matriz, modo):
    n = len(matriz)

    if n > N_MAX_LU:
        raise ValueError(
            f"El tamaño máximo admitido es n = {N_MAX_LU} "
            f"(la matriz es de {n}×{n})."
        )

    lu = _factorizar_lu(matriz)
    diagonal = [lu["U"][i][i] for i in range(n)]
    producto = Fraction(1)
    for valor in diagonal:
        producto *= valor
    signo = -1 if lu["intercambios"] % 2 else 1
    resultado = signo * producto
    multiplicaciones = lu["multiplicaciones"] + max(n - 1, 0)

    paso_final = {
        "tipo": "producto_diagonal", "diagonal": diagonal,
        "intercambios": lu["intercambios"], "signo": signo,
        "producto": producto, "valor": resultado,
        "texto": (
            f"(−1)^{lu['intercambios']} · "
            + " · ".join(f"({formatear(v, modo)})" for v in diagonal)
            + f" = {formatear(resultado, modo)}"
        ),
    }

    return {
        "pasos": lu["pasos"] + [paso_final],
        "resultado": resultado,
        "multiplicaciones": multiplicaciones,
        "P": lu["P"], "L": lu["L"], "U": lu["U"],
        "intercambios": lu["intercambios"],
        "singular_columnas": [
            p["columna"] for p in lu["pasos"] if p["tipo"] == "sin_pivote"
        ],
    }


# ---------------------------------------------------------------------------
# Función pública
# ---------------------------------------------------------------------------

def determinante(matriz, metodo="lu", modo="fraccion",
                 tipo_expansion=None, indice_expansion=None):
    """
    Calcula det(A) con cofactores o LU y devuelve resultado, pasos y
    comprobación. `indice_expansion` es 1-based (como lo ve el usuario) y solo
    aplica a cofactores.
    """

    if metodo not in METODOS_DETERMINANTE:
        raise ValueError(f"Método desconocido: {metodo}.")

    matriz = _matriz(matriz, "matriz A")
    filas, columnas = _dimensiones(matriz)

    if filas != columnas:
        raise ValueError(
            "Solo las matrices cuadradas tienen determinante "
            f"(la matriz es de {filas}×{columnas})."
        )

    n = filas
    if (tipo_expansion is not None or indice_expansion is not None) \
            and metodo != "cofactores":
        raise ValueError("La fila o columna de expansión solo aplica a cofactores.")

    if metodo == "cofactores":
        datos = _por_cofactores(matriz, modo, tipo_expansion, indice_expansion)
    else:
        datos = _por_lu(matriz, modo)

    resultado = datos["resultado"]
    comprobacion = _comprobar(matriz, metodo, resultado, datos, modo)

    salida = {
        "operacion": "determinante",
        "metodo": metodo,
        "entradas": {"matriz": matriz},
        "pasos": datos["pasos"],
        "resultado": resultado,
        "singular": resultado == 0,
        "multiplicaciones": datos["multiplicaciones"],
        "recomendacion": recomendar_metodo(n),
        "comprobacion": comprobacion,
    }

    if metodo == "cofactores":
        salida["expansion"] = datos["expansion"]
    else:
        for clave in ("P", "L", "U", "intercambios"):
            salida[clave] = datos[clave]

    return salida


def _comprobar(matriz, metodo, resultado, datos, modo):
    """Recalcula con el otro método; si no aplica, verifica P·A = L·U."""

    n = len(matriz)

    if metodo == "cofactores":
        otro = _por_lu(matriz, modo)["resultado"]
        return {"metodo": "lu", "valor": otro, "correcto": otro == resultado}

    if n <= N_MAX_COFACTORES:
        otro = _por_cofactores(matriz, modo, None, None)["resultado"]
        return {
            "metodo": "cofactores", "valor": otro, "correcto": otro == resultado,
        }

    pa = _multiplicar(datos["P"], matriz)
    lu = _multiplicar(datos["L"], datos["U"])
    return {"metodo": "P·A = L·U", "valor": None, "correcto": pa == lu}


# ---------------------------------------------------------------------------
# Texto del procedimiento (para exportar a PNG/PDF)
# ---------------------------------------------------------------------------

def _sangrar(texto, nivel):
    margen = "    " * nivel
    return "\n".join(margen + linea for linea in texto.split("\n"))


def _texto_expansion(paso, modo, nivel=0):
    f = lambda v: formatear(v, modo)

    if paso["tipo"] == "base_1x1":
        return _sangrar(f"det = {f(paso['valor'])}", nivel)
    if paso["tipo"] == "base_2x2":
        return _sangrar(paso["texto"], nivel)

    lineas = [paso["expansion"]["motivo"]]
    for t in paso["terminos"]:
        signo = "+" if t["signo"] > 0 else "−"
        nombre = f"a{t['fila']}{t['columna']} = {f(t['valor'])} (signo {signo})"
        if t["omitido"]:
            lineas.append(f"{nombre}: vale 0, se omite.")
            continue
        lineas.append(f"{nombre}, menor M{t['fila']}{t['columna']}:")
        lineas.append(_sangrar(matriz_general_texto(t["menor"], modo), 1))
        lineas.append(_texto_expansion(t["paso_menor"], modo, 1))
        lineas.append(
            f"    det(M) = {f(t['det_menor'])}  →  aporte = "
            f"{signo}{f(abs(t['valor']))}·({f(t['det_menor'])}) = {f(t['aporte'])}"
        )
    lineas.append(f"det(A) = {f(paso['valor'])}")
    return _sangrar("\n".join(lineas), nivel)


def procedimiento_texto(datos, modo="fraccion", incluir_pasos=True):
    """Procedimiento y resultado del determinante como texto legible."""

    f = lambda v: formatear(v, modo)
    lineas = []
    nombre = NOMBRES_METODO[datos["metodo"]]

    lineas += [f"DETERMINANTE ({nombre.upper()})", "", "Matriz A:",
               matriz_general_texto(datos["entradas"]["matriz"], modo), ""]

    if incluir_pasos and datos["metodo"] == "cofactores":
        lineas += [_texto_expansion(datos["pasos"][0], modo), ""]
    elif incluir_pasos:
        for paso in datos["pasos"]:
            if paso["tipo"] == "producto_diagonal":
                lineas += ["Producto de la diagonal de U:", paso["texto"], ""]
            elif paso["tipo"] == "sin_pivote":
                lineas += [f"Columna {paso['columna']}: sin pivote, se continúa.", ""]
            else:
                lineas.append(f"Columna {paso['columna']}: pivote {f(paso['pivote'])}")
                if paso["intercambio"]:
                    a, b = paso["intercambio"]
                    lineas.append(f"  Intercambio F{a} ↔ F{b}")
                for m in paso["multiplicadores"]:
                    lineas.append(
                        f"  l{m['fila']}{paso['columna']} = {f(m['valor'])}  "
                        f"(F{m['fila']} ← F{m['fila']} − l·F{paso['columna']})"
                    )
                lineas += ["U:", matriz_general_texto(paso["U"], modo), ""]
        lineas += ["P:", matriz_general_texto(datos["P"], modo), "",
                   "L:", matriz_general_texto(datos["L"], modo), "",
                   "U:", matriz_general_texto(datos["U"], modo), ""]

    lineas.append(f"det(A) = {f(datos['resultado'])}")
    if datos["singular"]:
        lineas.append("La matriz es singular (no tiene inversa).")
    lineas.append(f"Multiplicaciones realizadas: {datos['multiplicaciones']}")

    c = datos["comprobacion"]
    if c["valor"] is not None:
        lineas.append(
            f"Comprobación con {NOMBRES_METODO[c['metodo']]}: {f(c['valor'])} "
            + ("✓" if c["correcto"] else "✗")
        )
    else:
        lineas.append("Comprobación P·A = L·U: " + ("✓" if c["correcto"] else "✗"))

    return "\n".join(lineas)
