"""
metodos/pivote.py
Motor para resolver sistemas de ecuaciones lineales con Gauss-Jordan
aplicando pivoteo parcial (se elige el mayor valor absoluto de la
columna como pivote).

El formateo y la comprobación compartidos viven en general_metodos.py.
No usa NumPy ni librerías externas: solo la librería estándar.
Devuelve exactamente el mismo diccionario que
metodos.gauss_jordan.resolver, para que la GUI/CLI puedan reutilizarse
sin cambios.
"""

from fractions import Fraction

from .general_metodos import (
    formatear_operacion,
    soluciones_texto,
    comprobar_solucion,
)


def gauss_jordan_pivoteo(matriz):
    """
    Resuelve una matriz aumentada por Gauss-Jordan con pivoteo parcial.

    Devuelve:
        matriz_final
        pasos
        tipo
        pivotes
        variables_libres
    """

    # Convertimos todos los valores a fracciones exactas.
    A = [[Fraction(x) for x in fila] for fila in matriz]

    filas = len(A)
    columnas = len(A[0])
    variables = columnas - 1

    pasos = []
    fila_pivote = 0
    pivotes = []

    for columna in range(variables):

        if fila_pivote >= filas:
            break

        # Pivoteo parcial: mayor valor absoluto de la columna.
        fila_intercambio = fila_pivote

        for i in range(fila_pivote + 1, filas):
            if abs(A[i][columna]) > abs(A[fila_intercambio][columna]):
                fila_intercambio = i

        if A[fila_intercambio][columna] == 0:
            continue

        # Intercambiar filas.
        if fila_intercambio != fila_pivote:
            A[fila_pivote], A[fila_intercambio] = (
                A[fila_intercambio],
                A[fila_pivote],
            )

            pasos.append((
                "intercambio",
                fila_pivote + 1,
                fila_intercambio + 1,
                [fila[:] for fila in A],
            ))

        # Convertir el pivote en 1.
        pivote = A[fila_pivote][columna]

        if pivote != 1:
            for j in range(columnas):
                A[fila_pivote][j] /= pivote

            pasos.append((
                "normalizar",
                fila_pivote + 1,
                pivote,
                [fila[:] for fila in A],
            ))

        pivotes.append(columna)

        # Hacer ceros arriba y abajo del pivote.
        for i in range(filas):

            if i == fila_pivote:
                continue

            factor = A[i][columna]

            if factor != 0:
                for j in range(columnas):
                    A[i][j] -= factor * A[fila_pivote][j]

                pasos.append((
                    "eliminar",
                    i + 1,
                    fila_pivote + 1,
                    factor,
                    [fila[:] for fila in A],
                ))

        fila_pivote += 1

    # Identificar contradicción: 0 0 ... 0 | número distinto de 0.
    for i in range(filas):
        coeficientes_cero = all(A[i][j] == 0 for j in range(variables))

        if coeficientes_cero and A[i][variables] != 0:
            tipo = "incompatible"
            variables_libres = []
            return A, pasos, tipo, pivotes, variables_libres

    # Identificar variables libres.
    variables_libres = [
        j for j in range(variables)
        if j not in pivotes
    ]

    if len(pivotes) == variables:
        tipo = "unica"
    else:
        tipo = "infinitas"

    return A, pasos, tipo, pivotes, variables_libres


def resolver(matriz, modo="fraccion"):
    """
    Función pública del método de pivoteo.

    Devuelve el mismo diccionario estándar que
    metodos.gauss_jordan.resolver.
    """

    matriz_final, pasos, tipo, pivotes, variables_libres = (
        gauss_jordan_pivoteo(matriz)
    )

    resultado = {
        "matriz_inicial": matriz,
        "matriz_final": matriz_final,
        "tipo": tipo,
        "pivotes": pivotes,
        "variables_libres": variables_libres,
        "pasos": [],
        "soluciones": soluciones_texto(
            matriz_final,
            tipo,
            pivotes,
            variables_libres,
            modo,
        ),
        "comprobacion": comprobar_solucion(
            matriz,
            matriz_final,
            tipo,
            pivotes,
        ),
    }

    for paso in pasos:
        operacion = paso[:-1]
        matriz_paso = paso[-1]

        resultado["pasos"].append({
            "operacion": formatear_operacion(operacion, modo),
            "matriz": matriz_paso,
        })

    return resultado
