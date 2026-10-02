"""
ejercicios.py
Catálogo de ejercicios de práctica para la calculadora.

Solo contiene datos (sin lógica matemática ni librerías externas): cada
ejercicio trae los valores listos para cargarse en el formulario de su
método, y `resultado_esperado` para que las pruebas comprueben que el
catálogo coincide con lo que calcula metodos/. Tanto main.py (importándolo)
como server.py (GET /api/ejercicios) leen de aquí, así no se escriben
ejercicios a mano en ninguna interfaz.

Los `datos` usan la misma forma que los cuerpos JSON de server.py, con los
números como texto tal cual se escribirían en los campos.

Estructura de cada ejercicio:
    id, titulo, dificultad ("básico" | "intermedio" | "avanzado"),
    descripcion, datos, resultado_esperado
Los ejercicios de "vectores-matrices" añaden `categoria`
("vectores" | "matrices" | "ecuacion-matricial" | "inversa") y `operacion`
(el nombre que usa el selector de la vista, cuando aplica).
"""

BASICO = "básico"
INTERMEDIO = "intermedio"
AVANZADO = "avanzado"

# Orden y nombre visible de los métodos con ejercicios.
METODOS_EJERCICIOS = [
    ("gauss-jordan", "Gauss-Jordan"),
    ("pivoteo", "Pivoteo"),
    ("conversion", "Conversión de bases"),
    ("vectores-matrices", "Vectores y matrices"),
]


def _sistema(id, titulo, dificultad, descripcion, matriz, tipo):
    return {
        "id": id,
        "titulo": titulo,
        "dificultad": dificultad,
        "descripcion": descripcion,
        "datos": {"matriz": matriz},
        "resultado_esperado": {"tipo": tipo},
    }


def _conversion(id, titulo, dificultad, descripcion, numero, base_entrada,
                base_salida, resultado):
    return {
        "id": id,
        "titulo": titulo,
        "dificultad": dificultad,
        "descripcion": descripcion,
        "datos": {
            "numero": numero,
            "base_entrada": base_entrada,
            "base_salida": base_salida,
        },
        "resultado_esperado": {"resultado": resultado},
    }


def _operacion(id, titulo, dificultad, descripcion, categoria, operacion,
               datos, esperado):
    return {
        "id": id,
        "titulo": titulo,
        "dificultad": dificultad,
        "descripcion": descripcion,
        "categoria": categoria,
        "operacion": operacion,
        "datos": datos,
        "resultado_esperado": esperado,
    }


EJERCICIOS = {
    "gauss-jordan": [
        _sistema(
            "gj-01", "Sistema 2×2 con solución única", BASICO,
            "Dos ecuaciones y dos incógnitas: practica la reducción básica.",
            [["2", "1", "5"], ["1", "-1", "1"]], "unica",
        ),
        _sistema(
            "gj-02", "Sistema 3×3 escalonado", BASICO,
            "Ya viene casi triangular: ideal para seguir cada paso.",
            [["1", "1", "1", "6"], ["0", "2", "5", "-4"], ["2", "5", "-1", "27"]],
            "unica",
        ),
        _sistema(
            "gj-03", "Sistema 3×3 con fracciones", INTERMEDIO,
            "Los pasos intermedios generan fracciones: prueba también el "
            "modo decimal.",
            [["2", "4", "-2", "2"], ["4", "9", "-3", "8"], ["-2", "-3", "7", "10"]],
            "unica",
        ),
        _sistema(
            "gj-04", "Infinitas soluciones", INTERMEDIO,
            "Una ecuación es múltiplo de otra: queda una variable libre.",
            [["1", "2", "-1", "3"], ["2", "4", "-2", "6"], ["1", "1", "1", "4"]],
            "infinitas",
        ),
        _sistema(
            "gj-05", "Sistema incompatible", INTERMEDIO,
            "Dos ecuaciones se contradicen: no existe solución.",
            [["1", "1", "1", "3"], ["1", "1", "1", "5"], ["0", "1", "2", "1"]],
            "incompatible",
        ),
        _sistema(
            "gj-06", "Sistema 4×4 tridiagonal", AVANZADO,
            "Cuatro ecuaciones y cuatro incógnitas con muchos ceros.",
            [
                ["2", "1", "0", "0", "4"],
                ["1", "2", "1", "0", "8"],
                ["0", "1", "2", "1", "12"],
                ["0", "0", "1", "2", "11"],
            ],
            "unica",
        ),
        _sistema(
            "gj-07", "Menos ecuaciones que variables", INTERMEDIO,
            "Dos ecuaciones y tres incógnitas: siempre quedan variables "
            "libres.",
            [["1", "1", "1", "6"], ["0", "1", "-1", "0"]], "infinitas",
        ),
        _sistema(
            "gj-08", "Más ecuaciones que variables", INTERMEDIO,
            "Tres ecuaciones y dos incógnitas: la tercera no concuerda.",
            [["1", "1", "2"], ["1", "-1", "0"], ["2", "1", "5"]],
            "incompatible",
        ),
    ],
    "pivoteo": [
        _sistema(
            "pv-01", "Pivote inicial igual a cero", BASICO,
            "El primer pivote es 0: hay que intercambiar filas.",
            [["0", "2", "1", "5"], ["1", "1", "1", "4"], ["2", "1", "-1", "3"]],
            "unica",
        ),
        _sistema(
            "pv-02", "Pivote muy pequeño", INTERMEDIO,
            "Dividir entre 0.0001 amplifica errores: el pivoteo elige un "
            "pivote mayor.",
            [["0.0001", "1", "1"], ["1", "1", "2"]], "unica",
        ),
        _sistema(
            "pv-03", "Sistema 2×2 sencillo", BASICO,
            "Compara el resultado con el método de Gauss-Jordan.",
            [["3", "2", "7"], ["1", "-1", "-1"]], "unica",
        ),
        _sistema(
            "pv-04", "Sistema 3×3 con intercambios", INTERMEDIO,
            "Los coeficientes crecen por fila: el mayor pivote queda abajo.",
            [["1", "2", "3", "14"], ["4", "5", "6", "32"], ["7", "8", "10", "53"]],
            "unica",
        ),
        _sistema(
            "pv-05", "Infinitas soluciones con columna nula", INTERMEDIO,
            "La primera columna tiene un solo valor distinto de cero.",
            [["0", "1", "1", "2"], ["0", "2", "2", "4"], ["1", "0", "1", "1"]],
            "infinitas",
        ),
        _sistema(
            "pv-06", "Incompatible con columna de ceros", BASICO,
            "La primera variable no aparece y las ecuaciones se contradicen.",
            [["0", "1", "2"], ["0", "1", "3"]], "incompatible",
        ),
        _sistema(
            "pv-07", "Sistema 4×4 con filas desordenadas", AVANZADO,
            "El mismo sistema tridiagonal de Gauss-Jordan, con las filas "
            "mezcladas.",
            [
                ["0", "1", "2", "1", "12"],
                ["2", "1", "0", "0", "4"],
                ["0", "0", "1", "2", "11"],
                ["1", "2", "1", "0", "8"],
            ],
            "unica",
        ),
    ],
    "conversion": [
        _conversion(
            "cv-01", "Decimal a binario", BASICO,
            "Divisiones sucesivas entre 2.", "25", 10, 2, "11001",
        ),
        _conversion(
            "cv-02", "Decimal a octal", BASICO,
            "Divisiones sucesivas entre 8.", "156", 10, 8, "234",
        ),
        _conversion(
            "cv-03", "Decimal a hexadecimal", INTERMEDIO,
            "Los residuos 10 a 15 se escriben con letras A-F.",
            "255", 10, 16, "FF",
        ),
        _conversion(
            "cv-04", "Decimal negativo a binario", INTERMEDIO,
            "Se convierte la magnitud y se conserva el signo.",
            "-13", 10, 2, "-1101",
        ),
        _conversion(
            "cv-05", "Binario a decimal", BASICO,
            "Suma de dígito × potencia de 2.", "101101", 2, 10, "45",
        ),
        _conversion(
            "cv-06", "Octal a decimal", INTERMEDIO,
            "Suma de dígito × potencia de 8.", "745", 8, 10, "485",
        ),
        _conversion(
            "cv-07", "Hexadecimal a decimal", INTERMEDIO,
            "Suma de dígito × potencia de 16, con la letra F como 15.",
            "2F", 16, 10, "47",
        ),
    ],
    "vectores-matrices": [
        _operacion(
            "vm-01", "Suma de vectores", BASICO,
            "Suma componente por componente de dos vectores de R³.",
            "vectores", "Suma",
            {"vectores": [["1", "2", "3"], ["4", "5", "6"]]},
            {"resultado": ["5", "7", "9"]},
        ),
        _operacion(
            "vm-02", "Resta de vectores", BASICO,
            "El segundo vector se resta del primero.",
            "vectores", "Resta",
            {"vectores": [["5", "7"], ["2", "3"]]},
            {"resultado": ["3", "4"]},
        ),
        _operacion(
            "vm-03", "Vector por escalar", BASICO,
            "Cada componente se multiplica por 3.",
            "vectores", "Vector por escalar",
            {"vectores": [["1", "-2", "3"]], "escalar": "3"},
            {"resultado": ["3", "-6", "9"]},
        ),
        _operacion(
            "vm-04", "Combinación lineal que sí existe", INTERMEDIO,
            "¿Es (5, 6) combinación lineal de (1, 2) y (3, 4)?",
            "vectores", "Combinación lineal",
            {"vectores": [["1", "2"], ["3", "4"]], "objetivo": ["5", "6"]},
            {"es_combinacion": True, "tipo_solucion": "unica"},
        ),
        _operacion(
            "vm-05", "Combinación lineal que no existe", INTERMEDIO,
            "Los dos vectores son paralelos y el objetivo no está en su recta.",
            "vectores", "Combinación lineal",
            {"vectores": [["1", "2"], ["2", "4"]], "objetivo": ["1", "0"]},
            {"es_combinacion": False, "tipo_solucion": "incompatible"},
        ),
        _operacion(
            "vm-06", "Suma de matrices", BASICO,
            "Suma elemento por elemento de dos matrices 2×2.",
            "matrices", "Suma",
            {"matriz_a": [["1", "2"], ["3", "4"]],
             "matriz_b": [["5", "6"], ["7", "8"]]},
            {"resultado": [["6", "8"], ["10", "12"]]},
        ),
        _operacion(
            "vm-07", "Resta de matrices", BASICO,
            "Resta elemento por elemento.",
            "matrices", "Resta",
            {"matriz_a": [["5", "6"], ["7", "8"]],
             "matriz_b": [["1", "2"], ["3", "4"]]},
            {"resultado": [["4", "4"], ["4", "4"]]},
        ),
        _operacion(
            "vm-08", "Matriz por escalar", BASICO,
            "Cada elemento se multiplica por 2.",
            "matrices", "Matriz por escalar",
            {"matriz_a": [["1", "2"], ["3", "4"]], "escalar": "2"},
            {"resultado": [["2", "4"], ["6", "8"]]},
        ),
        _operacion(
            "vm-09", "Multiplicación A × B", INTERMEDIO,
            "A es 2×3 y B es 3×2: el resultado es 2×2.",
            "matrices", "Multiplicación A × B",
            {"matriz_a": [["1", "2", "3"], ["4", "5", "6"]],
             "matriz_b": [["7", "8"], ["9", "10"], ["11", "12"]]},
            {"resultado": [["58", "64"], ["139", "154"]]},
        ),
        _operacion(
            "vm-10", "Ecuación matricial A·X = B", INTERMEDIO,
            "Encuentra X resolviendo [A | B] con Gauss-Jordan.",
            "ecuacion-matricial", None,
            {"matriz_a": [["2", "1"], ["1", "3"]], "matriz_b": [["5"], ["10"]]},
            {"tipo_solucion": "unica"},
        ),
        _operacion(
            "vm-11", "Matriz inversa 2×2", INTERMEDIO,
            "Reduce [A | I] hasta obtener [I | A⁻¹].",
            "inversa", None,
            {"matriz": [["2", "1"], ["5", "3"]]},
            {"existe": True, "resultado": [["3", "-1"], ["-5", "2"]]},
        ),
        _operacion(
            "vm-12", "Matriz que no es invertible", AVANZADO,
            "La segunda fila es el doble de la primera: no hay inversa.",
            "inversa", None,
            {"matriz": [["1", "2"], ["2", "4"]]},
            {"existe": False},
        ),
    ],
}


NOMBRES_BASE = {2: "binario", 8: "octal", 10: "decimal", 16: "hexadecimal"}


def _vector_texto(vector):
    return "(" + ", ".join(vector) + ")"


def _matriz_texto(matriz):
    return "[" + ", ".join("[" + ", ".join(fila) + "]" for fila in matriz) + "]"


def vista_previa(clave, ejercicio):
    """Texto corto (varias líneas) con los datos del ejercicio, para mostrarlo
    en la lista antes de probarlo. Es solo formato: ambas interfaces lo
    muestran tal cual."""

    datos = ejercicio["datos"]

    if clave in ("gauss-jordan", "pivoteo"):
        matriz = datos["matriz"]
        ancho = max(len(celda) for fila in matriz for celda in fila)
        return "\n".join(
            "  ".join(celda.rjust(ancho) for celda in fila[:-1])
            + " │ " + fila[-1].rjust(ancho)
            for fila in matriz
        )

    if clave == "conversion":
        return (
            f"{datos['numero']}  "
            f"({NOMBRES_BASE[datos['base_entrada']]} → "
            f"{NOMBRES_BASE[datos['base_salida']]})"
        )

    categoria = ejercicio["categoria"]
    lineas = []

    if categoria == "vectores":
        lineas.append(ejercicio["operacion"])
        for n, vector in enumerate(datos["vectores"], start=1):
            lineas.append(f"v{n} = {_vector_texto(vector)}")
        if "objetivo" in datos:
            lineas.append(f"objetivo = {_vector_texto(datos['objetivo'])}")
        if "escalar" in datos:
            lineas.append(f"escalar = {datos['escalar']}")
    elif categoria == "matrices":
        lineas.append(ejercicio["operacion"])
        lineas.append(f"A = {_matriz_texto(datos['matriz_a'])}")
        if "matriz_b" in datos:
            lineas.append(f"B = {_matriz_texto(datos['matriz_b'])}")
        if "escalar" in datos:
            lineas.append(f"escalar = {datos['escalar']}")
    elif categoria == "ecuacion-matricial":
        lineas.append("A·X = B")
        lineas.append(f"A = {_matriz_texto(datos['matriz_a'])}")
        lineas.append(f"B = {_matriz_texto(datos['matriz_b'])}")
    else:
        lineas.append("Matriz inversa")
        lineas.append(f"A = {_matriz_texto(datos['matriz'])}")

    return "\n".join(lineas)


def catalogo():
    """Devuelve una copia del catálogo completo, por método, con la
    `vista_previa` de cada ejercicio ya calculada."""

    return {
        clave: [
            {**ejercicio, "vista_previa": vista_previa(clave, ejercicio)}
            for ejercicio in ejercicios
        ]
        for clave, ejercicios in EJERCICIOS.items()
    }
