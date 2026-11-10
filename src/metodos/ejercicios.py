"""
ejercicios.py
Catálogo de ejercicios de práctica para la calculadora.

Solo contiene datos (sin lógica matemática ni librerías externas): cada
ejercicio trae los valores listos para cargarse en el formulario de su
método, y `resultado_esperado` para que las pruebas comprueben que el
catálogo coincide con lo que calcula metodos/. server.py (GET /api/ejercicios)
lee de aquí, así no se escriben ejercicios a mano en la interfaz.

Los `datos` usan la misma forma que los cuerpos JSON de server.py, con los
números como texto tal cual se escribirían en los campos.

Estructura de cada ejercicio:
    id, titulo, dificultad ("básico" | "intermedio" | "avanzado"),
    descripcion, datos, resultado_esperado
Los de "determinante" llevan en `datos` la `matriz` y el `metodo` ("lu" |
"cofactores") con el que conviene probarlos.
Los de "biseccion" llevan en `datos` la `funcion`, `a`, `b`, `tolerancia` y
`max_iter` (todo como texto, tal cual se escribiría en los campos) y en
`resultado_esperado` la `raiz` y las `iteraciones`, o un `error` (fragmento
del mensaje) cuando el método debe rechazar el intervalo.
Los de "falsa-posicion" tienen la misma forma que los de "biseccion".
Los de "newton-raphson" llevan en `datos` la `funcion`, la `derivada` (vacía =
automática), `x0`, `tolerancia` y `max_iter`, y en `resultado_esperado` la
`raiz` y las `iteraciones` (más `motivo`/`convergio` si no converge), o un
`error` (fragmento del mensaje) cuando el método falla en la 1.ª iteración.
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
    ("determinante", "Determinante"),
    ("biseccion", "Bisección"),
    ("falsa-posicion", "Regula Falsi"),
    ("newton-raphson", "Newton-Raphson"),
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


def _determinante(id, titulo, dificultad, descripcion, matriz, metodo,
                  resultado, singular=False):
    return {
        "id": id,
        "titulo": titulo,
        "dificultad": dificultad,
        "descripcion": descripcion,
        "datos": {"matriz": matriz, "metodo": metodo},
        "resultado_esperado": {"resultado": resultado, "singular": singular},
    }


def _biseccion(id, titulo, dificultad, descripcion, funcion, a, b,
               tolerancia, max_iter, esperado):
    return {
        "id": id,
        "titulo": titulo,
        "dificultad": dificultad,
        "descripcion": descripcion,
        "datos": {"funcion": funcion, "a": a, "b": b,
                  "tolerancia": tolerancia, "max_iter": max_iter},
        "resultado_esperado": esperado,
    }


def _newton(id, titulo, dificultad, descripcion, funcion, derivada, x0,
            tolerancia, max_iter, esperado):
    return {
        "id": id,
        "titulo": titulo,
        "dificultad": dificultad,
        "descripcion": descripcion,
        "datos": {"funcion": funcion, "derivada": derivada, "x0": x0,
                  "tolerancia": tolerancia, "max_iter": max_iter},
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
        _operacion(
            "vm-13", "Producto de dos 2×2 (con animación)", INTERMEDIO,
            "Abre la gráfica y mueve el deslizador t: primero se aplica B "
            "(un corte) y luego A (un estiramiento).",
            "matrices", "Multiplicación A × B",
            {"matriz_a": [["2", "0"], ["0", "1"]],
             "matriz_b": [["1", "1"], ["0", "1"]]},
            {"resultado": [["2", "2"], ["0", "1"]]},
        ),
        _operacion(
            "vm-14", "Inversa de una reflexión (det < 0)", INTERMEDIO,
            "Intercambia los ejes: det A = −1. En la animación el cuadrado "
            "se aplasta en t = 0.5 y sale volteado.",
            "inversa", None,
            {"matriz": [["0", "1"], ["1", "0"]]},
            {"existe": True, "resultado": [["0", "1"], ["1", "0"]]},
        ),
    ],
    "determinante": [
        _determinante(
            "det-01", "Determinante 2×2", BASICO,
            "ad − bc: con cofactores no hay nada más que desarrollar.",
            [["3", "8"], ["4", "6"]], "cofactores", "-14",
        ),
        _determinante(
            "det-02", "Determinante 3×3", BASICO,
            "Expande por una fila y compara con LU: ambos dan lo mismo.",
            [["2", "-1", "3"], ["0", "4", "1"], ["5", "2", "-2"]],
            "cofactores", "-85",
        ),
        _determinante(
            "det-03", "Matriz singular 3×3", INTERMEDIO,
            "Las filas están en progresión: el determinante es 0 y no hay "
            "inversa.",
            [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]],
            "lu", "0", True,
        ),
        _determinante(
            "det-04", "4×4 con muchos ceros", INTERMEDIO,
            "Con tantos ceros, cofactores descarta casi todos los términos: "
            "pruébalo contra LU.",
            [["1", "0", "2", "0"], ["0", "3", "0", "4"],
             ["5", "0", "6", "0"], ["0", "7", "0", "8"]],
            "cofactores", "16",
        ),
        _determinante(
            "det-05", "4×4 que exige intercambio de filas", INTERMEDIO,
            "El primer pivote es 0: LU debe intercambiar filas y cambiar el "
            "signo.",
            [["0", "2", "1", "3"], ["1", "1", "0", "2"],
             ["3", "0", "1", "1"], ["2", "5", "4", "0"]],
            "lu", "40",
        ),
        _determinante(
            "det-06", "4×4 con fracciones", AVANZADO,
            "Los multiplicadores generan fracciones: prueba también el modo "
            "decimal.",
            [["1/2", "2", "-1", "3"], ["4", "3/4", "0", "1"],
             ["2", "2", "2", "1/3"], ["0", "1", "5", "2"]],
            "lu", "-2903/24",
        ),
        _determinante(
            "det-07", "Determinante 5×5", AVANZADO,
            "Con n = 5 cofactores necesita unas 120 multiplicaciones y LU "
            "unas 42: compara el contador real de cada método.",
            [["2", "0", "1", "3", "1"], ["1", "1", "0", "2", "4"],
             ["3", "0", "1", "1", "0"], ["2", "5", "4", "0", "1"],
             ["0", "1", "1", "1", "2"]],
            "lu", "76",
        ),
    ],
    "biseccion": [
        _biseccion(
            "bis-01", "Raíz cuadrada de 2", BASICO,
            "x² − 2 = 0 en [1, 2]: la raíz es √2 ≈ 1.41421. Observa cómo el "
            "intervalo se reduce a la mitad en cada fila.",
            "x^2 - 2", "1", "2", "0.0001", "50",
            {"raiz": 1.4142, "iteraciones": 13},
        ),
        _biseccion(
            "bis-02", "Cúbica x³ − x − 2", BASICO,
            "Una sola raíz real, cerca de 1.52. Verifica a mano que "
            "f(1) < 0 y f(2) > 0 antes de calcular.",
            "x^3 - x - 2", "1", "2", "0.0001", "50",
            {"raiz": 1.5214, "iteraciones": 13},
        ),
        _biseccion(
            "bis-03", "Polinomio del profesor", INTERMEDIO,
            "x⁴ − 5x³ + 0.5x² − 11x + 10 en [0.55, 1.1] con E = 0.0001: "
            "13 iteraciones y raíz ≈ 0.7639709473.",
            "x^4 - 5x^3 + 0.5x^2 - 11x + 10", "0.55", "1.1", "0.0001", "50",
            {"raiz": 0.7639709473, "iteraciones": 13},
        ),
        _biseccion(
            "bis-04", "cos(x) = x", INTERMEDIO,
            "Reescríbela como cos(x) − x = 0. La raíz (≈ 0.739085) es la "
            "constante de Dottie; el argumento va en radianes.",
            "cos(x) - x", "0", "1", "0.00001", "50",
            {"raiz": 0.739085, "iteraciones": 18},
        ),
        _biseccion(
            "bis-05", "e⁻ˣ = x", INTERMEDIO,
            "e^(-x) − x = 0 en [0, 1]: raíz ≈ 0.5671433. Prueba también "
            "con una E más pequeña y compara las iteraciones.",
            "exp(-x) - x", "0", "1", "0.00001", "50",
            {"raiz": 0.5671433, "iteraciones": 18},
        ),
        _biseccion(
            "bis-06", "Intervalo sin cambio de signo", AVANZADO,
            "x² + 1 no se anula nunca: f(a)·f(b) > 0 y el método debe "
            "rechazar el intervalo con un mensaje claro.",
            "x^2 + 1", "0", "2", "0.0001", "50",
            {"error": "No hay cambio de signo"},
        ),
        _biseccion(
            "bis-07", "Discontinuidad: 1/x", AVANZADO,
            "Hay cambio de signo en [−1, 2], pero 1/x no es continua en 0: "
            "la gráfica lo muestra y el método NO se aplica (no se itera).",
            "1/x", "-1", "2", "0.0001", "50",
            {"bloqueada": True, "continuidad": "polo"},
        ),
        _biseccion(
            "bis-08", "Se agotan las iteraciones", AVANZADO,
            "Con E = 1e-10 y solo 8 iteraciones no se llega a la "
            "tolerancia: revisa el aviso y sube el máximo de iteraciones.",
            "x^2 - 2", "1", "2", "1e-10", "8",
            {"raiz": 1.418, "iteraciones": 8, "convergio": False},
        ),
        _biseccion(
            "bis-09", "Polo de tan(x)", AVANZADO,
            "tan(x) cambia de signo en [1, 2] porque salta de +∞ a −∞ en "
            "π/2 ≈ 1.5708, no porque valga 0. La revisión de continuidad "
            "lo detecta y el método queda bloqueado.",
            "tan(x)", "1", "2", "0.0001", "50",
            {"bloqueada": True, "continuidad": "polo"},
        ),
        _biseccion(
            "bis-10", "Salto: |x|/x", AVANZADO,
            "|x|/x vale −1 a la izquierda de 0 y +1 a la derecha: hay cambio "
            "de signo pero ningún punto donde f sea 0. Es un salto, no un "
            "polo; fíjate en cómo lo describe la revisión.",
            "abs(x)/x", "-1", "2", "0.0001", "50",
            {"bloqueada": True, "continuidad": "salto"},
        ),
    ],
    "falsa-posicion": [
        _biseccion(
            "fp-01", "Raíz cuadrada de 2", BASICO,
            "x² − 2 = 0 en [1, 2]: la misma del ejercicio de bisección, pero "
            "aquí bastan 6 iteraciones (la bisección necesita 13). Observa "
            "cómo c es el corte de la secante con el eje x.",
            "x^2 - 2", "1", "2", "0.0001", "50",
            {"raiz": 1.41420, "iteraciones": 6},
        ),
        _biseccion(
            "fp-02", "Cúbica x³ − x − 2", BASICO,
            "Una sola raíz real, cerca de 1.52. Comprueba que f(1) < 0 y "
            "f(2) > 0 antes de calcular.",
            "x^3 - x - 2", "1", "2", "0.0001", "50",
            {"raiz": 1.52134, "iteraciones": 8},
        ),
        _biseccion(
            "fp-03", "Polinomio del profesor", INTERMEDIO,
            "x⁴ − 5x³ + 0.5x² − 11x + 10 en [0.55, 1.1] con E = 0.0001: "
            "Regula Falsi llega a ≈ 0.76392 en 5 iteraciones; compárala con "
            "las 13 de la bisección.",
            "x^4 - 5x^3 + 0.5x^2 - 11x + 10", "0.55", "1.1", "0.0001", "50",
            {"raiz": 0.76392, "iteraciones": 5},
        ),
        _biseccion(
            "fp-04", "cos(x) = x", INTERMEDIO,
            "cos(x) − x = 0 en [0, 1]: la raíz ≈ 0.739085 (constante de "
            "Dottie). El argumento va en radianes.",
            "cos(x) - x", "0", "1", "0.00001", "50",
            {"raiz": 0.739085, "iteraciones": 5},
        ),
        _biseccion(
            "fp-05", "e⁻ˣ = x", INTERMEDIO,
            "e^(-x) − x = 0 en [0, 1]: raíz ≈ 0.5671433.",
            "exp(-x) - x", "0", "1", "0.00001", "50",
            {"raiz": 0.567143, "iteraciones": 7},
        ),
        _biseccion(
            "fp-06", "Convergencia lenta: x¹⁰ − 1", AVANZADO,
            "Con una función muy curva un extremo se queda fijo y Regula "
            "Falsi avanza despacio (39 iteraciones). Fíjate en que a o b no "
            "cambia en la tabla; la bisección sería más estable aquí.",
            "x^10 - 1", "0", "1.3", "0.0001", "200",
            {"raiz": 0.99969, "iteraciones": 39},
        ),
        _biseccion(
            "fp-07", "Intervalo sin cambio de signo", AVANZADO,
            "x² + 1 no se anula nunca: f(a)·f(b) > 0 y el método debe "
            "rechazar el intervalo con un mensaje claro.",
            "x^2 + 1", "0", "2", "0.0001", "50",
            {"error": "No hay cambio de signo"},
        ),
        _biseccion(
            "fp-08", "Discontinuidad: 1/x", AVANZADO,
            "Hay cambio de signo en [−1, 2], pero 1/x no es continua en 0: "
            "la gráfica lo muestra y el método NO se aplica.",
            "1/x", "-1", "2", "0.0001", "50",
            {"bloqueada": True, "continuidad": "polo"},
        ),
        _biseccion(
            "fp-09", "Se agotan las iteraciones", AVANZADO,
            "x¹⁰ − 1 con solo 10 iteraciones no alcanza la tolerancia: "
            "revisa el aviso y sube el máximo de iteraciones.",
            "x^10 - 1", "0", "1.3", "0.0001", "10",
            {"raiz": 0.68694, "iteraciones": 10, "convergio": False},
        ),
    ],
    "newton-raphson": [
        _newton(
            "nr-01", "Ejemplo guiado: x³ − x − 2", BASICO,
            "El problema conductor de la clase con x₀ = 1.5: la primera "
            "iteración da x₁ ≈ 1.521739130 y en 3 iteraciones llega a "
            "1.521379707.",
            "x^3 - x - 2", "", "1.5", "0.000001", "50",
            {"raiz": 1.521380, "iteraciones": 3},
        ),
        _newton(
            "nr-02", "Actividad 1: x³ − 2x − 5", BASICO,
            "La actividad colaborativa de la clase con x₀ = 2: determina "
            "f′(x) = 3x² − 2, haz las iteraciones y calcula el residuo de "
            "cada una.",
            "x^3 - 2x - 5", "", "2", "0.000001", "50",
            {"raiz": 2.094551, "iteraciones": 4},
        ),
        _newton(
            "nr-03", "Raíz cuadrada de 2", BASICO,
            "x² − 2 = 0 desde x₀ = 1: Newton calcula √2 en 4 iteraciones "
            "(la bisección necesita 13).",
            "x^2 - 2", "", "1", "0.0001", "50",
            {"raiz": 1.414214, "iteraciones": 4},
        ),
        _newton(
            "nr-04", "cos(x) = x", INTERMEDIO,
            "cos(x) − x = 0 desde x₀ = 1: la raíz ≈ 0.739085. La derivada "
            "(−sin(x) − 1) la calcula el programa. El argumento va en "
            "radianes.",
            "cos(x) - x", "", "1", "0.00001", "50",
            {"raiz": 0.739085, "iteraciones": 4},
        ),
        _newton(
            "nr-05", "e⁻ˣ = x", INTERMEDIO,
            "e^(−x) − x = 0 desde x₀ = 0: raíz ≈ 0.5671433.",
            "exp(-x) - x", "", "0", "0.00001", "50",
            {"raiz": 0.567143, "iteraciones": 4},
        ),
        _newton(
            "nr-06", "Derivada escrita a mano", INTERMEDIO,
            "Mismo problema que nr-01, pero escribiendo tú f′(x) = 3x² − 1 "
            "en el campo de la derivada. Si la escribes mal, el programa lo "
            "avisa al compararla con la pendiente numérica.",
            "x^3 - x - 2", "3x^2 - 1", "1.5", "0.000001", "50",
            {"raiz": 1.521380, "iteraciones": 3},
        ),
        _newton(
            "nr-07", "Raíz doble: (x − 1)²", AVANZADO,
            "En una raíz múltiple Newton pierde su rapidez: cada paso solo "
            "reduce el error a la mitad (15 iteraciones en lugar de 4).",
            "(x - 1)^2", "", "3", "0.0001", "50",
            {"raiz": 1.000061, "iteraciones": 15},
        ),
        _newton(
            "nr-08", "Ciclo sin convergencia", AVANZADO,
            "x³ − 2x + 2 desde x₀ = 0 salta entre 0 y 1 sin acercarse a la "
            "raíz (≈ −1.769). Con un x₀ inadecuado Newton no converge: mira "
            "el aviso y prueba x₀ = −2.",
            "x^3 - 2x + 2", "", "0", "0.0001", "20",
            {"raiz": 0.0, "iteraciones": 20, "convergio": False,
             "motivo": "max_iter"},
        ),
        _newton(
            "nr-09", "Derivada cero en x₀", AVANZADO,
            "x² − 1 desde x₀ = 0: f′(0) = 0, la tangente es horizontal y la "
            "fórmula no está definida. Prueba con x₀ = 0.5.",
            "x^2 - 1", "", "0", "0.0001", "50",
            {"error": "es cero"},
        ),
        _newton(
            "nr-10", "Se sale del dominio: ln(x)", AVANZADO,
            "ln(x) desde x₀ = 3: la primera tangente cae en x ≈ −0.30, donde "
            "ln no existe. Con x₀ = 1.5 sí converge a 1.",
            "ln(x)", "", "3", "0.0001", "50",
            {"error": "fuera del dominio"},
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

    if clave == "determinante":
        matriz = datos["matriz"]
        ancho = max(len(celda) for fila in matriz for celda in fila)
        return "\n".join(
            "[ " + "  ".join(celda.rjust(ancho) for celda in fila) + " ]"
            for fila in matriz
        )

    if clave == "newton-raphson":
        derivada = datos["derivada"] or "automática"
        return (
            f"f(x) = {datos['funcion']}\n"
            f"f'(x) = {derivada} · x₀ = {datos['x0']}\n"
            f"E = {datos['tolerancia']} · máx. {datos['max_iter']} iteraciones"
        )

    if clave in ("biseccion", "falsa-posicion"):
        return (
            f"f(x) = {datos['funcion']}\n"
            f"[a, b] = [{datos['a']}, {datos['b']}]\n"
            f"E = {datos['tolerancia']} · máx. {datos['max_iter']} iteraciones"
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
    elif categoria == "inversa":
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
