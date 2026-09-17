"""
Operaciones con vectores y matrices implementadas de forma manual.

Incluye operaciones aritméticas, comprobación de combinaciones lineales y
resolución de ecuaciones matriciales A·X = B. No usa librerías matemáticas
externas; para resolver sistemas reutiliza el motor Gauss-Jordan del proyecto.
"""

from fractions import Fraction

from .gauss_jordan import resolver as resolver_gauss_jordan
from .general_metodos import formatear, matriz_texto


def parsear_numero(valor):
    """Convierte enteros, decimales o fracciones escritas como texto."""

    if isinstance(valor, bool):
        raise ValueError("Los valores deben ser números.")

    if isinstance(valor, float):
        valor = str(valor)

    try:
        return Fraction(valor)
    except (ValueError, ZeroDivisionError, TypeError):
        raise ValueError(f"Valor numérico inválido: {valor!r}.")


def _vector(vector, nombre="vector"):
    if not isinstance(vector, (list, tuple)) or not vector:
        raise ValueError(f"El {nombre} debe contener al menos una componente.")
    return [parsear_numero(numero) for numero in vector]


def _matriz(matriz, nombre="matriz"):
    if not isinstance(matriz, (list, tuple)) or not matriz:
        raise ValueError(f"La {nombre} debe contener al menos una fila.")

    filas = []
    columnas = None

    for fila in matriz:
        if not isinstance(fila, (list, tuple)) or not fila:
            raise ValueError(f"Cada fila de la {nombre} debe tener valores.")
        if columnas is None:
            columnas = len(fila)
        elif len(fila) != columnas:
            raise ValueError(f"La {nombre} debe ser rectangular.")
        filas.append([parsear_numero(numero) for numero in fila])

    return filas


def _validar_misma_dimension(vectores):
    dimension = len(vectores[0])
    if any(len(vector) != dimension for vector in vectores[1:]):
        raise ValueError("Todos los vectores deben tener la misma dimensión.")


def _dimensiones(matriz):
    return len(matriz), len(matriz[0])


def suma_vectores(vectores):
    """Suma dos o más vectores, componente por componente."""

    if not isinstance(vectores, (list, tuple)) or len(vectores) < 2:
        raise ValueError("Se necesitan al menos dos vectores para sumar.")

    vectores = [_vector(vector, f"vector {i + 1}")
                for i, vector in enumerate(vectores)]
    _validar_misma_dimension(vectores)

    resultado = []
    pasos = []

    for componente in range(len(vectores[0])):
        sumandos = [vector[componente] for vector in vectores]
        total = sum(sumandos, Fraction(0))
        resultado.append(total)
        pasos.append({
            "componente": componente,
            "valores": sumandos,
            "resultado": total,
        })

    return {
        "operacion": "suma_vectores",
        "entradas": {"vectores": vectores},
        "pasos": pasos,
        "resultado": resultado,
    }


def resta_vectores(vector_a, vector_b):
    """Resta vector_b de vector_a, componente por componente."""

    vector_a = _vector(vector_a, "vector A")
    vector_b = _vector(vector_b, "vector B")
    _validar_misma_dimension([vector_a, vector_b])

    resultado = []
    pasos = []

    for componente, (valor_a, valor_b) in enumerate(zip(vector_a, vector_b)):
        diferencia = valor_a - valor_b
        resultado.append(diferencia)
        pasos.append({
            "componente": componente,
            "valor_a": valor_a,
            "valor_b": valor_b,
            "resultado": diferencia,
        })

    return {
        "operacion": "resta_vectores",
        "entradas": {"vector_a": vector_a, "vector_b": vector_b},
        "pasos": pasos,
        "resultado": resultado,
    }


def multiplicar_vector_escalar(vector, escalar):
    """Multiplica cada componente de un vector por un escalar."""

    vector = _vector(vector)
    escalar = parsear_numero(escalar)
    resultado = []
    pasos = []

    for componente, valor in enumerate(vector):
        producto = escalar * valor
        resultado.append(producto)
        pasos.append({
            "componente": componente,
            "escalar": escalar,
            "valor": valor,
            "resultado": producto,
        })

    return {
        "operacion": "escalar_vector",
        "entradas": {"vector": vector, "escalar": escalar},
        "pasos": pasos,
        "resultado": resultado,
    }


def combinacion_lineal(vectores, objetivo, modo="fraccion"):
    """Determina si ``objetivo`` es combinación lineal de ``vectores``."""

    if not isinstance(vectores, (list, tuple)) or not vectores:
        raise ValueError("Ingrese al menos un vector generador.")

    vectores = [_vector(vector, f"vector {i + 1}")
                for i, vector in enumerate(vectores)]
    objetivo = _vector(objetivo, "vector objetivo")
    _validar_misma_dimension(vectores + [objetivo])

    sistema = []
    for componente in range(len(objetivo)):
        sistema.append(
            [vector[componente] for vector in vectores]
            + [objetivo[componente]]
        )

    resolucion = resolver_gauss_jordan(sistema, modo)
    es_combinacion = resolucion["tipo"] != "incompatible"
    escalares = None

    if es_combinacion:
        escalares = list(resolucion["comprobacion"]["X"])

    return {
        "operacion": "combinacion_lineal",
        "entradas": {"vectores": vectores, "objetivo": objetivo},
        "pasos": resolucion["pasos"],
        "sistema": sistema,
        "resolucion": resolucion,
        "es_combinacion": es_combinacion,
        "tipo_solucion": resolucion["tipo"],
        "escalares": escalares,
        "resultado": escalares,
    }


def suma_matrices(matriz_a, matriz_b):
    """Suma dos matrices con las mismas dimensiones."""

    matriz_a = _matriz(matriz_a, "matriz A")
    matriz_b = _matriz(matriz_b, "matriz B")

    if _dimensiones(matriz_a) != _dimensiones(matriz_b):
        raise ValueError("Las matrices deben tener las mismas dimensiones.")

    resultado = []
    pasos = []

    for i in range(len(matriz_a)):
        fila = []
        for j in range(len(matriz_a[0])):
            valor = matriz_a[i][j] + matriz_b[i][j]
            fila.append(valor)
            pasos.append({
                "fila": i,
                "columna": j,
                "valor_a": matriz_a[i][j],
                "valor_b": matriz_b[i][j],
                "resultado": valor,
            })
        resultado.append(fila)

    return {
        "operacion": "suma_matrices",
        "entradas": {"matriz_a": matriz_a, "matriz_b": matriz_b},
        "pasos": pasos,
        "resultado": resultado,
    }


def resta_matrices(matriz_a, matriz_b):
    """Resta matriz_b de matriz_a si sus dimensiones coinciden."""

    matriz_a = _matriz(matriz_a, "matriz A")
    matriz_b = _matriz(matriz_b, "matriz B")

    if _dimensiones(matriz_a) != _dimensiones(matriz_b):
        raise ValueError("Las matrices deben tener las mismas dimensiones.")

    resultado = []
    pasos = []

    for i in range(len(matriz_a)):
        fila = []
        for j in range(len(matriz_a[0])):
            valor = matriz_a[i][j] - matriz_b[i][j]
            fila.append(valor)
            pasos.append({
                "fila": i,
                "columna": j,
                "valor_a": matriz_a[i][j],
                "valor_b": matriz_b[i][j],
                "resultado": valor,
            })
        resultado.append(fila)

    return {
        "operacion": "resta_matrices",
        "entradas": {"matriz_a": matriz_a, "matriz_b": matriz_b},
        "pasos": pasos,
        "resultado": resultado,
    }


def multiplicar_matriz_escalar(matriz, escalar):
    """Multiplica todos los elementos de una matriz por un escalar."""

    matriz = _matriz(matriz)
    escalar = parsear_numero(escalar)
    resultado = []
    pasos = []

    for i, fila_original in enumerate(matriz):
        fila = []
        for j, valor_original in enumerate(fila_original):
            valor = escalar * valor_original
            fila.append(valor)
            pasos.append({
                "fila": i,
                "columna": j,
                "escalar": escalar,
                "valor": valor_original,
                "resultado": valor,
            })
        resultado.append(fila)

    return {
        "operacion": "escalar_matriz",
        "entradas": {"matriz": matriz, "escalar": escalar},
        "pasos": pasos,
        "resultado": resultado,
    }


def multiplicar_matrices(matriz_a, matriz_b):
    """Calcula A × B mediante productos punto de filas por columnas."""

    matriz_a = _matriz(matriz_a, "matriz A")
    matriz_b = _matriz(matriz_b, "matriz B")
    filas_a, columnas_a = _dimensiones(matriz_a)
    filas_b, columnas_b = _dimensiones(matriz_b)

    if columnas_a != filas_b:
        raise ValueError(
            "No se pueden multiplicar: las columnas de A deben coincidir "
            "con las filas de B."
        )

    resultado = []
    pasos = []

    for i in range(filas_a):
        fila = []
        for j in range(columnas_b):
            productos = [matriz_a[i][k] * matriz_b[k][j]
                         for k in range(columnas_a)]
            valor = sum(productos, Fraction(0))
            fila.append(valor)
            pasos.append({
                "fila": i,
                "columna": j,
                "factores": [
                    (matriz_a[i][k], matriz_b[k][j])
                    for k in range(columnas_a)
                ],
                "productos": productos,
                "resultado": valor,
            })
        resultado.append(fila)

    return {
        "operacion": "multiplicacion_matrices",
        "entradas": {"matriz_a": matriz_a, "matriz_b": matriz_b},
        "pasos": pasos,
        "resultado": resultado,
    }


def ecuacion_matricial(matriz_a, matriz_b, modo="fraccion"):
    """Resuelve A·X = B reutilizando Gauss-Jordan para cada columna de B."""

    matriz_a = _matriz(matriz_a, "matriz A")
    matriz_b = _matriz(matriz_b, "matriz B")
    filas_a, columnas_a = _dimensiones(matriz_a)
    filas_b, columnas_b = _dimensiones(matriz_b)

    if filas_a != filas_b:
        raise ValueError("A y B deben tener la misma cantidad de filas.")

    aumentada = [matriz_a[i] + matriz_b[i] for i in range(filas_a)]
    resoluciones = []

    for columna_b in range(columnas_b):
        sistema = [
            matriz_a[i] + [matriz_b[i][columna_b]]
            for i in range(filas_a)
        ]
        resoluciones.append(resolver_gauss_jordan(sistema, modo))

    tipos = [resolucion["tipo"] for resolucion in resoluciones]
    if "incompatible" in tipos:
        tipo = "incompatible"
        solucion = None
    else:
        tipo = "infinitas" if "infinitas" in tipos else "unica"
        columnas_x = [
            list(resolucion["comprobacion"]["X"])
            for resolucion in resoluciones
        ]
        solucion = [
            [columnas_x[j][i] for j in range(columnas_b)]
            for i in range(columnas_a)
        ]

    return {
        "operacion": "ecuacion_matricial",
        "entradas": {"matriz_a": matriz_a, "matriz_b": matriz_b},
        "pasos": [
            {"columna_b": i, "resolucion": resolucion}
            for i, resolucion in enumerate(resoluciones)
        ],
        "matriz_aumentada": aumentada,
        "resoluciones": resoluciones,
        "tipo_solucion": tipo,
        "resultado": solucion,
    }


def vector_texto(vector, modo="fraccion"):
    """Devuelve un vector con formato legible."""

    return "(" + ", ".join(formatear(x, modo) for x in vector) + ")"


def matriz_general_texto(matriz, modo="fraccion"):
    """Devuelve una matriz ordinaria con columnas alineadas."""

    textos = [[formatear(numero, modo) for numero in fila] for fila in matriz]
    anchos = [max(len(fila[j]) for fila in textos)
              for j in range(len(textos[0]))]
    return "\n".join(
        "[ " + "  ".join(texto.rjust(anchos[j])
                            for j, texto in enumerate(fila)) + " ]"
        for fila in textos
    )


def procedimiento_texto(datos, modo="fraccion"):
    """Convierte cualquier resultado del módulo en un procedimiento legible."""

    operacion = datos["operacion"]
    lineas = []

    if operacion in ("suma_vectores", "resta_vectores", "escalar_vector"):
        titulos = {
            "suma_vectores": "SUMA DE VECTORES",
            "resta_vectores": "RESTA DE VECTORES",
            "escalar_vector": "MULTIPLICACIÓN DE VECTOR POR ESCALAR",
        }
        lineas.extend((titulos[operacion], "=" * len(titulos[operacion]), ""))

        for paso in datos["pasos"]:
            indice = paso["componente"] + 1
            if operacion == "suma_vectores":
                expresion = " + ".join(formatear(x, modo)
                                       for x in paso["valores"])
            elif operacion == "resta_vectores":
                expresion = (f"{formatear(paso['valor_a'], modo)} - "
                             f"{formatear(paso['valor_b'], modo)}")
            else:
                expresion = (f"{formatear(paso['escalar'], modo)} × "
                             f"{formatear(paso['valor'], modo)}")
            lineas.append(
                f"Componente {indice}: {expresion} = "
                f"{formatear(paso['resultado'], modo)}"
            )

        lineas.extend(("", "Resultado: " + vector_texto(datos["resultado"], modo)))
        return "\n".join(lineas)

    if operacion == "combinacion_lineal":
        lineas.extend(("COMBINACIÓN LINEAL", "=" * 18, ""))
        generadores = datos["entradas"]["vectores"]
        objetivo = datos["entradas"]["objetivo"]
        expresion = " + ".join(
            f"c{i + 1}{vector_texto(vector, modo)}"
            for i, vector in enumerate(generadores)
        )
        lineas.append(f"Planteamiento: {expresion} = {vector_texto(objetivo, modo)}")
        lineas.extend(("", "Sistema aumentado:", matriz_texto(datos["sistema"], modo)))

        for paso in datos["resolucion"]["pasos"]:
            lineas.extend(("", paso["operacion"],
                           matriz_texto(paso["matriz"], modo)))

        lineas.extend(("", "Matriz reducida:",
                       matriz_texto(datos["resolucion"]["matriz_final"], modo), ""))
        if datos["es_combinacion"]:
            if datos["tipo_solucion"] == "infinitas":
                lineas.append("Sí es combinación lineal (hay infinitas elecciones de escalares).")
                lineas.append("Una elección particular es:")
            else:
                lineas.append("Sí es combinación lineal. Los escalares son:")
            for i, escalar in enumerate(datos["escalares"]):
                lineas.append(f"c{i + 1} = {formatear(escalar, modo)}")
        else:
            lineas.append("No es combinación lineal: el sistema es incompatible.")
        return "\n".join(lineas)

    if operacion in ("suma_matrices", "resta_matrices", "escalar_matriz"):
        titulos = {
            "suma_matrices": "SUMA DE MATRICES",
            "resta_matrices": "RESTA DE MATRICES",
            "escalar_matriz": "MULTIPLICACIÓN DE MATRIZ POR ESCALAR",
        }
        simbolo = "+" if operacion == "suma_matrices" else "-"
        lineas.extend((titulos[operacion], "=" * len(titulos[operacion]), ""))
        for paso in datos["pasos"]:
            posicion = f"Elemento ({paso['fila'] + 1}, {paso['columna'] + 1})"
            if operacion == "escalar_matriz":
                expresion = (f"{formatear(paso['escalar'], modo)} × "
                             f"{formatear(paso['valor'], modo)}")
            else:
                expresion = (f"{formatear(paso['valor_a'], modo)} {simbolo} "
                             f"{formatear(paso['valor_b'], modo)}")
            lineas.append(f"{posicion}: {expresion} = {formatear(paso['resultado'], modo)}")
        lineas.extend(("", "Resultado:", matriz_general_texto(datos["resultado"], modo)))
        return "\n".join(lineas)

    if operacion == "multiplicacion_matrices":
        lineas.extend(("MULTIPLICACIÓN DE MATRICES", "=" * 27, ""))
        for paso in datos["pasos"]:
            terminos = " + ".join(
                f"({formatear(a, modo)}×{formatear(b, modo)})"
                for a, b in paso["factores"]
            )
            lineas.append(
                f"Elemento ({paso['fila'] + 1}, {paso['columna'] + 1}): "
                f"{terminos} = {formatear(paso['resultado'], modo)}"
            )
        lineas.extend(("", "Resultado:", matriz_general_texto(datos["resultado"], modo)))
        return "\n".join(lineas)

    if operacion == "ecuacion_matricial":
        lineas.extend(("ECUACIÓN MATRICIAL A·X = B", "=" * 27, "",
                       "Matriz aumentada [A | B]:",
                       matriz_general_texto(datos["matriz_aumentada"], modo)))
        for indice, resolucion in enumerate(datos["resoluciones"], 1):
            lineas.extend(("", f"Columna {indice} de B:",
                           matriz_texto(resolucion["matriz_inicial"], modo)))
            for paso in resolucion["pasos"]:
                lineas.extend(("", paso["operacion"],
                               matriz_texto(paso["matriz"], modo)))
            lineas.extend(("", "Matriz reducida:",
                           matriz_texto(resolucion["matriz_final"], modo)))

        lineas.append("")
        if datos["tipo_solucion"] == "incompatible":
            lineas.append("La ecuación matricial no tiene solución.")
        else:
            if datos["tipo_solucion"] == "infinitas":
                lineas.append("La ecuación tiene infinitas soluciones; se muestra una solución particular X:")
            else:
                lineas.append("Solución única X:")
            lineas.append(matriz_general_texto(datos["resultado"], modo))
        return "\n".join(lineas)

    raise ValueError(f"Operación desconocida: {operacion}")
