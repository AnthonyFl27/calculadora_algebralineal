"""
server.py
Servidor HTTP local que expone la lógica de metodos/ como endpoints JSON,
para que web/index.html pueda usarla desde el navegador mediante fetch().

No contiene lógica matemática propia: recibe los datos capturados en el
formulario web, llama directamente a las funciones ya existentes en
metodos/ y devuelve el resultado -incluyendo
los pasos del procedimiento- en JSON. Usa únicamente la librería estándar
de Python (http.server, json).

Uso: python server.py [puerto]
Al iniciar muestra un banner y, por cada petición, una línea de registro con
la ruta, el código de estado, el tiempo y qué función de metodos/ se usó.
Luego abrir http://127.0.0.1:8000 en el navegador. index.html no funciona
si se abre directamente con doble clic: necesita este servidor corriendo.
"""

import json
import os
import sys
import threading
import time
from fractions import Fraction
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Este archivo vive en la raíz del proyecto; el resto del código está en src/.
RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"
sys.path.insert(0, str(SRC))

from features.exportar import exportar, nombre_archivo, titulo_documento
from metodos.general_metodos import formatear
from metodos.gauss_jordan import resolver as resolver_gauss_jordan
from metodos.pivote import resolver as resolver_pivote
from metodos.conversion import NOMBRES_BASE, resolver as resolver_conversion
from metodos.biseccion import (
    ITERACIONES_POR_DEFECTO,
    biseccion,
    formatear_real,
)
from metodos.falsa_posicion import falsa_posicion
from metodos.newton_raphson import newton_raphson
from metodos.intervalos import buscar_intervalos
from metodos.determinante import determinante, recomendar_metodo
from metodos.escenas import (
    escena_determinante,
    escena_inversa,
    escena_producto,
    escena_sistema,
    escena_vectores,
)
from metodos.evaluador import compilar as compilar_funcion
from metodos.grafica import curva_ventana
from metodos.ejercicios import METODOS_EJERCICIOS, catalogo as catalogo_ejercicios
from metodos.vectores_matrices import (
    combinacion_lineal,
    ecuacion_matricial,
    matriz_inversa,
    multiplicar_matrices,
    multiplicar_matriz_escalar,
    multiplicar_vector_escalar,
    resta_matrices,
    resta_vectores,
    suma_matrices,
    suma_vectores,
)

PUERTO = 8000

RESOLVER_SISTEMA = {
    "gauss-jordan": resolver_gauss_jordan,
    "pivoteo": resolver_pivote,
}


def _serializar(valor):
    """Red de seguridad final: convierte cualquier Fraction que haya
    quedado sin formatear a texto plano, para que json.dumps no falle."""

    if isinstance(valor, Fraction):
        return str(valor)
    if isinstance(valor, (list, tuple)):
        return [_serializar(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _serializar(v) for k, v in valor.items()}
    return valor


def _formatear_matriz(matriz, modo):
    """Formatea una matriz numérica pura (celdas float, int o Fraction,
    sin metadatos mezclados) como una grilla de texto ya formateado.
    Se usa para matriz_inicial/matriz_final/paso['matriz'], donde
    metodos/gauss_jordan.py y metodos/pivote.py pueden devolver la matriz
    de entrada tal cual la capturó el usuario (floats) y no como
    Fraction."""

    return [[formatear(celda, modo) for celda in fila] for fila in matriz]


def _formatear_estructura(valor, modo):
    """Recorre listas/diccionarios anidados y formatea cada Fraction con
    `formatear()` (fracción o decimal, según `modo`), dejando enteros e
    índices (columna, fila, componente, etc.) intactos. Es la versión
    consciente del modo de visualización que usa `_armar_bloque_*` para
    poder mostrar los mismos datos que ya calcula metodos/ como celdas de
    tabla en vez de como un bloque de texto ya alineado."""

    if isinstance(valor, Fraction):
        return formatear(valor, modo)
    if isinstance(valor, (list, tuple)):
        return [_formatear_estructura(v, modo) for v in valor]
    if isinstance(valor, dict):
        return {k: _formatear_estructura(v, modo) for k, v in valor.items()}
    return valor


def _matriz_desde_texto(filas):
    """Convierte la matriz capturada en el navegador a floats."""

    matriz = []

    for fila in filas:
        fila_numeros = []

        for texto in fila:
            texto = str(texto).strip()

            if texto == "":
                raise ValueError(
                    "Complete todos los campos de la matriz con números."
                )

            try:
                fila_numeros.append(float(texto))
            except ValueError:
                raise ValueError(
                    "Complete todos los campos de la matriz con números."
                )

        matriz.append(fila_numeros)

    return matriz


def _armar_bloque_sistema(resultado, modo):
    """Convierte el diccionario de gauss_jordan/pivote.resolver(...) en una
    estructura de celdas ya formateadas (sin texto pre-alineado), lista
    para que index.html renderice una tabla real por paso y resalte el
    pivote de cada uno."""

    pasos = []

    for paso in resultado["pasos"]:
        pasos.append({
            "tipo": paso["tipo"],
            "columna": paso["columna"],
            "operacion": paso["operacion"],
            "fila_a": paso.get("fila_a"),
            "fila_b": paso.get("fila_b"),
            "fila": paso.get("fila"),
            "fila_pivote": paso.get("fila_pivote"),
            "matriz": _formatear_matriz(paso["matriz"], modo),
        })

    comprobacion_datos = resultado["comprobacion"]

    if comprobacion_datos is None:
        comprobacion = {"correcto": None}
    else:
        variables = len(comprobacion_datos["matriz_original"][0]) - 1
        comprobacion = {
            "correcto": comprobacion_datos["correcto"],
            "tipo_sistema": comprobacion_datos["tipo"],
            "matriz_a": _formatear_matriz(
                [fila[:variables] for fila in comprobacion_datos["matriz_original"]],
                modo,
            ),
            "vector_x": [formatear(x, modo) for x in comprobacion_datos["X"]],
            "vector_b": [
                formatear(fila[variables], modo)
                for fila in comprobacion_datos["matriz_original"]
            ],
            "filas": [
                {
                    "ax": formatear(ax_i, modo),
                    "b": formatear(b_i, modo),
                    "correcta": correcta,
                }
                for (ax_i, b_i), correcta in zip(
                    comprobacion_datos["comparaciones"],
                    comprobacion_datos["correctas"],
                )
            ],
        }

    return {
        "tipo": resultado["tipo"],
        "soluciones": resultado["soluciones"],
        "matriz_inicial": _formatear_matriz(resultado["matriz_inicial"], modo),
        "matriz_final": _formatear_matriz(resultado["matriz_final"], modo),
        "pivotes": resultado["pivotes"],
        "pasos": pasos,
        "comprobacion": comprobacion,
        "escena": resultado.get("escena"),
    }


def _calcular_sistema(datos):
    metodo = datos.get("metodo")
    funcion = RESOLVER_SISTEMA.get(metodo)

    if funcion is None:
        raise ValueError(f"Método no soportado: {metodo}")

    modo = datos.get("modo", "fraccion")
    matriz = _matriz_desde_texto(datos.get("matriz", []))
    titulo = "Gauss-Jordan" if metodo == "gauss-jordan" else "Pivoteo"

    resultado = funcion(matriz, modo)
    resultado["escena"] = escena_sistema(resultado, modo)   # gráfica (spec 014)

    return "sistema", resultado, modo, titulo


def _resolver_sistema(datos):
    _, resultado, modo, _ = _calcular_sistema(datos)

    return _armar_bloque_sistema(resultado, modo)


def _calcular_conversion(datos):
    numero = datos.get("numero", "")
    base_entrada = int(datos.get("base_entrada"))
    base_salida = int(datos.get("base_salida"))

    resultado = resolver_conversion(numero, base_entrada, base_salida)

    return "conversion", resultado, "fraccion", None


def _resolver_conversion(datos):
    _, resultado, _, _ = _calcular_conversion(datos)

    return {
        "tipo": resultado["tipo"],
        "numero_entrada": resultado["numero_entrada"],
        "resultado": resultado["resultado"],
        "base_entrada": resultado["base_entrada"],
        "base_salida": resultado["base_salida"],
        "nombre_base_entrada": NOMBRES_BASE[resultado["base_entrada"]],
        "nombre_base_salida": NOMBRES_BASE[resultado["base_salida"]],
        "pasos": resultado["pasos"],
    }


def _armar_bloque_operacion(resultado, modo):
    """Convierte cualquier resultado de metodos/vectores_matrices.py en una
    estructura de datos ya formateada (celdas/componentes), sin colapsarla
    a un único bloque de texto. `combinacion_lineal` y `ecuacion_matricial`
    reutilizan `_armar_bloque_sistema` para su(s) resolución(es) internas,
    de modo que el navegador pueda mostrar esos pasos con la misma vista
    de tabla/tarjeta que Gauss-Jordan y Pivoteo."""

    tipo = resultado["operacion"]

    bloque = {
        "tipo": tipo,
        "entradas": _formatear_estructura(resultado["entradas"], modo),
        "pasos": _formatear_estructura(resultado["pasos"], modo),
        "resultado": _formatear_estructura(resultado["resultado"], modo),
        "escena": resultado.get("escena"),
    }

    if tipo == "combinacion_lineal":
        bloque["sistema"] = _formatear_estructura(resultado["sistema"], modo)
        bloque["es_combinacion"] = resultado["es_combinacion"]
        bloque["tipo_solucion"] = resultado["tipo_solucion"]
        bloque["escalares"] = _formatear_estructura(resultado["escalares"], modo)
        bloque["sistema_resuelto"] = _armar_bloque_sistema(
            resultado["resolucion"], modo
        )

    if tipo == "ecuacion_matricial":
        bloque["matriz_aumentada"] = _formatear_estructura(
            resultado["matriz_aumentada"], modo
        )
        bloque["tipo_solucion"] = resultado["tipo_solucion"]
        bloque["columnas"] = [
            _armar_bloque_sistema(resolucion, modo)
            for resolucion in resultado["resoluciones"]
        ]
        bloque["escenas"] = resultado.get("escenas")

    if tipo == "matriz_inversa":
        bloque["metodo"] = resultado["metodo"]
        bloque["matriz_aumentada"] = _formatear_estructura(
            resultado["matriz_aumentada"], modo
        )
        bloque["matriz_final"] = _formatear_estructura(
            resultado["matriz_final"], modo
        )
        bloque["pivotes"] = resultado["pivotes"]
        bloque["existe"] = resultado["existe"]
        bloque["filas_cero"] = resultado["filas_cero"]
        bloque["motivo"] = resultado["motivo"]
        bloque["comprobacion"] = _formatear_estructura(
            resultado["comprobacion"], modo
        )

    return bloque


def _calcular_vectores(datos):
    operacion = datos.get("operacion")
    modo = datos.get("modo", "fraccion")
    vectores = datos.get("vectores", [])

    if operacion == "Suma":
        resultado = suma_vectores(vectores)
    elif operacion == "Resta":
        resultado = resta_vectores(vectores[0], vectores[1])
    elif operacion == "Vector por escalar":
        resultado = multiplicar_vector_escalar(
            vectores[0], datos.get("escalar", "")
        )
    elif operacion == "Combinación lineal":
        resultado = combinacion_lineal(
            vectores, datos.get("objetivo", []), modo
        )
    else:
        raise ValueError(f"Operación de vectores no soportada: {operacion}")

    resultado["escena"] = escena_vectores(resultado, modo)   # gráfica (spec 014)

    return "vectores_matrices", resultado, modo, None


def _resolver_vectores(datos):
    _, resultado, modo, _ = _calcular_vectores(datos)

    return _armar_bloque_operacion(resultado, modo)


def _calcular_matrices(datos):
    operacion = datos.get("operacion")
    modo = datos.get("modo", "fraccion")
    matriz_a = datos.get("matriz_a", [])

    if operacion == "Matriz por escalar":
        resultado = multiplicar_matriz_escalar(matriz_a, datos.get("escalar", ""))
    else:
        matriz_b = datos.get("matriz_b", [])

        if operacion == "Suma":
            resultado = suma_matrices(matriz_a, matriz_b)
        elif operacion == "Resta":
            resultado = resta_matrices(matriz_a, matriz_b)
        elif operacion == "Multiplicación A × B":
            resultado = multiplicar_matrices(matriz_a, matriz_b)
        else:
            raise ValueError(f"Operación de matrices no soportada: {operacion}")

    if operacion == "Multiplicación A × B":
        resultado["escena"] = escena_producto(resultado, modo)   # gráfica (spec 014)

    return "vectores_matrices", resultado, modo, None


def _resolver_matrices(datos):
    _, resultado, modo, _ = _calcular_matrices(datos)

    return _armar_bloque_operacion(resultado, modo)


def _calcular_ecuacion_matricial(datos):
    modo = datos.get("modo", "fraccion")
    resultado = ecuacion_matricial(
        datos.get("matriz_a", []), datos.get("matriz_b", []), modo
    )
    # Una gráfica por columna de B (cada columna es un sistema; spec 014).
    resultado["escenas"] = [
        escena_sistema(resolucion, modo)
        for resolucion in resultado["resoluciones"]
    ]

    return "vectores_matrices", resultado, modo, None


def _resolver_ecuacion_matricial(datos):
    _, resultado, modo, _ = _calcular_ecuacion_matricial(datos)

    return _armar_bloque_operacion(resultado, modo)


def _calcular_inversa(datos):
    modo = datos.get("modo", "fraccion")
    metodo = datos.get("metodo", "gauss_jordan")
    resultado = matriz_inversa(datos.get("matriz", []), metodo, modo)
    resultado["escena"] = escena_inversa(resultado, modo)   # gráfica (spec 014)

    return "vectores_matrices", resultado, modo, None


def _resolver_inversa(datos):
    _, resultado, modo, _ = _calcular_inversa(datos)

    return _armar_bloque_operacion(resultado, modo)


def _armar_bloque_determinante(resultado, modo):
    """Formatea el resultado de metodos/determinante.determinante()."""

    bloque = {
        "tipo": "determinante",
        "metodo": resultado["metodo"],
        "entradas": _formatear_estructura(resultado["entradas"], modo),
        "pasos": _formatear_estructura(resultado["pasos"], modo),
        "resultado": _formatear_estructura(resultado["resultado"], modo),
        "singular": resultado["singular"],
        "multiplicaciones": resultado["multiplicaciones"],
        "recomendacion": resultado["recomendacion"],
        "comprobacion": _formatear_estructura(resultado["comprobacion"], modo),
        "escena": resultado.get("escena"),
    }

    if resultado["metodo"] == "cofactores":
        bloque["expansion"] = resultado["expansion"]
    else:
        for clave in ("P", "L", "U", "intercambios"):
            bloque[clave] = _formatear_estructura(resultado[clave], modo)

    return bloque


def _calcular_determinante(datos):
    modo = datos.get("modo", "fraccion")
    metodo = datos.get("metodo", "lu")
    expansion = datos.get("expansion") or {}
    resultado = determinante(
        datos.get("matriz", []), metodo, modo,
        tipo_expansion=expansion.get("tipo"),
        indice_expansion=expansion.get("indice"),
    )
    resultado["escena"] = escena_determinante(resultado, modo)   # gráfica (spec 014)

    return "determinante", resultado, modo, None


def _resolver_determinante(datos):
    _, resultado, modo, _ = _calcular_determinante(datos)

    return _armar_bloque_determinante(resultado, modo)


def _resolver_recomendacion_determinante(datos):
    n = datos.get("n")

    if isinstance(n, str) and n.strip().isdigit():
        n = int(n)

    return recomendar_metodo(n)


def _armar_bloque_biseccion(resultado, tipo="biseccion"):
    """Formatea el resultado de metodos/biseccion.biseccion() (o de
    falsa_posicion(), que tiene el mismo formato): todos los números salen ya
    como texto (10 cifras significativas)."""

    f = formatear_real
    e = resultado["entradas"]
    r = resultado["resultado"]
    c = resultado["comprobacion"]
    cont = resultado["continuidad"]
    bloqueada = resultado["bloqueada"]
    continuidad = {
        "muestras": cont["muestras"], "total": cont["total"],
        "sin_senales": cont["sin_senales"],
        "sospechas": [
            {"tipo": q["tipo"], "mensaje": q["mensaje"]}
            for q in cont["sospechas"]
        ],
    }

    if bloqueada:
        # f no es continua: solo se informan la gráfica y la continuidad.
        return {
            "tipo": tipo,
            "bloqueada": True,
            "motivo_bloqueo": resultado["motivo_bloqueo"],
            "entradas": {
                "funcion": e["funcion"], "a": f(e["a"]), "b": f(e["b"]),
                "tolerancia": f(e["tolerancia"]),
                "tolerancia_porcentaje": f(e["tolerancia"] * 100),
                "max_iter": e["max_iter"],
            },
            "continuidad": continuidad,
            "grafica": resultado["grafica"],
        }

    bloque = {
        "tipo": tipo,
        "bloqueada": False,
        "entradas": {
            "funcion": e["funcion"], "a": f(e["a"]), "b": f(e["b"]),
            "tolerancia": f(e["tolerancia"]),
            "tolerancia_porcentaje": f(e["tolerancia"] * 100),
            "max_iter": e["max_iter"],
        },
        "inicial": {"fa": f(resultado["inicial"]["fa"]),
                    "fb": f(resultado["inicial"]["fb"])},
        "pasos": [
            {
                "i": p["i"], "a": f(p["a"]), "b": f(p["b"]), "c": f(p["c"]),
                "fa": f(p["fa"]), "fb": f(p["fb"]), "fc": f(p["fc"]),
                "error": f(p["error"], 6), "signo": p["signo"],
                "decision": p["decision"],
                "a_nuevo": f(p["a_nuevo"]), "b_nuevo": f(p["b_nuevo"]),
            }
            for p in resultado["pasos"]
        ],
        "resultado": {
            "raiz": f(r["raiz"]), "iteraciones": r["iteraciones"],
            "fraiz": f(r["fraiz"]), "error": f(r["error"], 6),
            "convergio": r["convergio"], "motivo": r["motivo"],
        },
        "continuidad": continuidad,
        "grafica": resultado["grafica"],
        "advertencias": resultado["advertencias"],
        "comprobacion": {
            "raiz": f(c["raiz"]), "fraiz": f(c["fraiz"]),
            "intervalo": [f(c["intervalo"][0]), f(c["intervalo"][1])],
            "fa": f(c["fa"]), "fb": f(c["fb"]),
            "cambio_signo": c["cambio_signo"],
            "tolerancia_alcanzada": c["tolerancia_alcanzada"],
            "cerca_de_cero": c["cerca_de_cero"],
            "discontinuidad": c["discontinuidad"],
            "correcto": c["correcto"],
        },
    }
    if "cota_iteraciones" in resultado:     # solo la bisección tiene cota
        bloque["cota_iteraciones"] = resultado["cota_iteraciones"]
    return bloque


def _calcular_biseccion(datos):
    resultado = biseccion(
        datos.get("funcion", ""), datos.get("a"), datos.get("b"),
        datos.get("tolerancia"),
        datos.get("max_iter", ITERACIONES_POR_DEFECTO),
    )

    return "biseccion", resultado, "fraccion", None


def _resolver_biseccion(datos):
    _, resultado, _, _ = _calcular_biseccion(datos)

    return _armar_bloque_biseccion(resultado)


def _calcular_falsa_posicion(datos):
    resultado = falsa_posicion(
        datos.get("funcion", ""), datos.get("a"), datos.get("b"),
        datos.get("tolerancia"),
        datos.get("max_iter", ITERACIONES_POR_DEFECTO),
    )

    return "falsa_posicion", resultado, "fraccion", None


def _resolver_falsa_posicion(datos):
    _, resultado, _, _ = _calcular_falsa_posicion(datos)

    return _armar_bloque_biseccion(resultado, "falsa_posicion")


def _armar_bloque_newton(resultado):
    """Formatea el resultado de metodos/newton_raphson.newton_raphson(): todos
    los números salen ya como texto (10 cifras significativas)."""

    f = formatear_real
    e = resultado["entradas"]
    r = resultado["resultado"]
    c = resultado["comprobacion"]
    cont = resultado["continuidad"]

    return {
        "tipo": "newton_raphson",
        "bloqueada": False,
        "entradas": {
            "funcion": e["funcion"], "derivada": e["derivada"],
            "derivada_origen": e["derivada_origen"], "x0": f(e["x0"]),
            "tolerancia": f(e["tolerancia"]),
            "tolerancia_porcentaje": f(e["tolerancia"] * 100),
            "max_iter": e["max_iter"],
        },
        "inicial": {"fx0": f(resultado["inicial"]["fx0"]),
                    "dfx0": f(resultado["inicial"]["dfx0"])},
        "pasos": [
            {
                "i": p["i"], "x": f(p["x"]), "fx": f(p["fx"]),
                "dfx": f(p["dfx"]), "x_nuevo": f(p["x_nuevo"]),
                "f_nuevo": f(p["f_nuevo"]), "delta": f(p["delta"]),
                "error": f(p["error"], 6), "decision": p["decision"],
            }
            for p in resultado["pasos"]
        ],
        "resultado": {
            "raiz": f(r["raiz"]), "iteraciones": r["iteraciones"],
            "fraiz": f(r["fraiz"]), "residuo": f(r["residuo"]),
            "error": f(r["error"], 6), "convergio": r["convergio"],
            "motivo": r["motivo"],
        },
        "continuidad": {
            "muestras": cont["muestras"], "total": cont["total"],
            "sin_senales": cont["sin_senales"],
            "sospechas": [{"tipo": q["tipo"], "mensaje": q["mensaje"]}
                          for q in cont["sospechas"]],
        },
        "grafica": resultado["grafica"],
        "advertencias": resultado["advertencias"],
        "comprobacion": {
            "raiz": f(c["raiz"]), "fraiz": f(c["fraiz"]),
            "residuo": f(c["residuo"]),
            "tolerancia_alcanzada": c["tolerancia_alcanzada"],
            "derivada_correcta": c["derivada_correcta"],
            "discontinuidad": c["discontinuidad"], "correcto": c["correcto"],
        },
    }


def _calcular_newton_raphson(datos):
    resultado = newton_raphson(
        datos.get("funcion", ""), datos.get("derivada", ""), datos.get("x0"),
        datos.get("tolerancia"),
        datos.get("max_iter", ITERACIONES_POR_DEFECTO),
    )

    return "newton_raphson", resultado, "fraccion", None


def _resolver_newton_raphson(datos):
    _, resultado, _, _ = _calcular_newton_raphson(datos)

    return _armar_bloque_newton(resultado)


def _resolver_intervalos(datos):
    """Sugiere intervalos [a, b] con cambio de signo y f continua (todo sale
    ya como texto; la web solo los muestra y los copia a los campos a y b)."""

    r = buscar_intervalos(
        datos.get("funcion", ""),
        datos.get("desde"), datos.get("hasta"), datos.get("paso", 0.1),
    )
    f = formatear_real

    return {
        "desde": f(r["desde"]), "hasta": f(r["hasta"]), "paso": f(r["paso"]),
        "tabla": [[f(x), f(v) if v is not None else "no definida"]
                  for x, v in r["tabla"]],
        "intervalos": [
            {"a": repr(i["a"]), "b": repr(i["b"]), "fa": f(i["fa"]),
             "fb": f(i["fb"]), "origen": i["origen"]}
            for i in r["intervalos"]],
        "total_intervalos": r["total_intervalos"],
        "descartados": [
            {"a": f(d["a"]), "b": f(d["b"]), "motivo": d["motivo"]}
            for d in r["descartados"]],
        "raices_exactas": [format(x, ".17g") for x in r["raices_exactas"]],
        "agotado": r["agotado"], "evaluaciones": r["evaluaciones"],
    }


def _resolver_grafica(datos):
    """Curva de f(x) para la ventana que la web está mostrando (zoom/arrastre)."""

    f = compilar_funcion(datos.get("funcion", ""))
    if not f.usa_x:
        raise ValueError("La función debe depender de x (por ejemplo x^2 - 2).")

    return curva_ventana(f, datos.get("x_min"), datos.get("x_max"),
                         datos.get("y_min"), datos.get("y_max"))


RUTAS = {
    "/api/sistema": _resolver_sistema,
    "/api/conversion": _resolver_conversion,
    "/api/vectores": _resolver_vectores,
    "/api/matrices": _resolver_matrices,
    "/api/ecuacion-matricial": _resolver_ecuacion_matricial,
    "/api/inversa": _resolver_inversa,
    "/api/determinante": _resolver_determinante,
    "/api/determinante/recomendar": _resolver_recomendacion_determinante,
    "/api/biseccion": _resolver_biseccion,
    "/api/falsa-posicion": _resolver_falsa_posicion,
    "/api/newton-raphson": _resolver_newton_raphson,
    "/api/grafica": _resolver_grafica,
    "/api/intervalos": _resolver_intervalos,
}

# Cálculo crudo de cada módulo (el mismo que usan las rutas de arriba);
# /api/exportar lo vuelve a ejecutar y entrega el resultado como archivo.
CALCULOS = {
    "sistema": _calcular_sistema,
    "conversion": _calcular_conversion,
    "vectores": _calcular_vectores,
    "matrices": _calcular_matrices,
    "ecuacion-matricial": _calcular_ecuacion_matricial,
    "inversa": _calcular_inversa,
    "determinante": _calcular_determinante,
    "biseccion": _calcular_biseccion,
    "falsa-posicion": _calcular_falsa_posicion,
    "newton-raphson": _calcular_newton_raphson,
}

RUTA_EXPORTAR = "/api/exportar"


def _exportar(datos):
    """Calcula con metodos/ y genera el archivo con features/exportar.py.

    Cuerpo: {"modulo": <clave de CALCULOS>, "datos": <mismo cuerpo que la
    ruta de resolución>, "formato": "png"|"pdf", "incluir_pasos": bool}.
    Devuelve (contenido, tipo_mime, nombre_de_archivo).
    """

    calcular = CALCULOS.get(datos.get("modulo"))

    if calcular is None:
        raise ValueError("Módulo no soportado para exportar.")

    formato = str(datos.get("formato", "")).lower()
    modulo, resultado, modo, titulo = calcular(datos.get("datos") or {})
    contenido, mime, _ = exportar(
        modulo, resultado, formato, modo,
        bool(datos.get("incluir_pasos", True)), titulo,
    )

    return contenido, mime, nombre_archivo(
        titulo_documento(modulo, resultado, titulo), formato
    )


# ======================================================================
# Registro en consola (solo presentación; no toca la lógica de metodos/)
# ======================================================================

ESTILOS = {
    "negrita": "1", "tenue": "2",
    "rojo": "31", "verde": "32", "amarillo": "33",
    "azul": "34", "magenta": "35", "cian": "36",
}

# Función de metodos/ que atiende cada ruta, solo para mostrarla en consola.
DESTINO = {
    "/api/sistema": "metodos.gauss_jordan / metodos.pivote .resolver",
    "/api/conversion": "metodos.conversion.resolver",
    "/api/vectores": "metodos.vectores_matrices (vectores)",
    "/api/matrices": "metodos.vectores_matrices (matrices)",
    "/api/ecuacion-matricial": "metodos.vectores_matrices.ecuacion_matricial",
    "/api/inversa": "metodos.vectores_matrices.matriz_inversa",
    "/api/determinante": "metodos.determinante.determinante",
    "/api/determinante/recomendar": "metodos.determinante.recomendar_metodo",
    "/api/biseccion": "metodos.biseccion.biseccion (+ continuidad)",
    "/api/falsa-posicion": "metodos.falsa_posicion.falsa_posicion (+ continuidad)",
    "/api/newton-raphson": "metodos.newton_raphson.newton_raphson (+ derivada simbólica)",
    "/api/grafica": "metodos.grafica.curva_ventana",
    "/api/intervalos": "metodos.intervalos.buscar_intervalos",
    RUTA_EXPORTAR: "features.exportar.exportar",
}

RUTAS_SILENCIOSAS = {"/api/estado"}  # El sidebar la consulta cada 5 s.

_candado = threading.Lock()


def _usa_color():
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return False
    if os.name == "nt":
        os.system("")  # Activa las secuencias ANSI en la consola de Windows.
    return True


COLOR = _usa_color()


def _c(texto, *estilos):
    if not COLOR or not estilos:
        return texto
    codigos = ";".join(ESTILOS[e] for e in estilos)
    return f"\033[{codigos}m{texto}\033[0m"


def _caja(lineas):
    """Dibuja un recuadro; cada línea es una lista de (texto, *estilos)."""

    ancho = max(sum(len(seg[0]) for seg in linea) for linea in lineas) + 4
    salida = [_c("  ┌" + "─" * ancho + "┐", "tenue")]

    for linea in lineas:
        largo = sum(len(seg[0]) for seg in linea)
        cuerpo = "".join(_c(seg[0], *seg[1:]) for seg in linea)
        salida.append(
            _c("  │", "tenue") + "  " + cuerpo + " " * (ancho - 2 - largo)
            + _c("│", "tenue")
        )

    salida.append(_c("  └" + "─" * ancho + "┘", "tenue"))
    return "\n".join(salida)


def _descripcion_peticion(ruta, datos, resultado):
    """Resume qué se calculó, leyendo la petición y la respuesta."""

    modo = datos.get("modo", "fraccion")
    pasos = len(resultado.get("pasos", []))

    if ruta == "/api/sistema":
        metodo = datos.get("metodo")
        matriz = datos.get("matriz", [])
        destino = {"gauss-jordan": "metodos.gauss_jordan.resolver",
                   "pivoteo": "metodos.pivote.resolver"}.get(metodo, metodo)
        forma = f"{len(matriz)}×{len(matriz[0])}" if matriz else "?"
        return (destino, f"matriz {forma} · modo={modo}",
                f"{resultado.get('tipo')} · {pasos} pasos")

    if ruta == "/api/conversion":
        return (DESTINO[ruta],
                f"{datos.get('numero')} (base {datos.get('base_entrada')} → "
                f"base {datos.get('base_salida')})",
                f"{resultado.get('resultado')} · {pasos} pasos")

    if ruta == "/api/vectores":
        return (DESTINO[ruta],
                f"{datos.get('operacion')} · {len(datos.get('vectores', []))} "
                f"vectores · modo={modo}", f"{pasos} pasos")

    if ruta == "/api/matrices":
        return (DESTINO[ruta], f"{datos.get('operacion')} · modo={modo}",
                f"{pasos} pasos")

    if ruta == "/api/ecuacion-matricial":
        return (DESTINO[ruta], f"A·X = B · modo={modo}",
                f"{resultado.get('tipo_solucion')}")

    if ruta == "/api/inversa":
        existe = "existe inversa" if resultado.get("existe") else "no invertible"
        return (DESTINO[ruta], f"método={datos.get('metodo')} · modo={modo}",
                f"{existe} · {pasos} pasos")

    if ruta == "/api/determinante":
        matriz = datos.get("matriz", [])
        resumen = f"{resultado.get('multiplicaciones')} multiplicaciones"
        return (DESTINO[ruta],
                f"método={datos.get('metodo')} · {len(matriz)}×{len(matriz)} · "
                f"modo={modo}",
                f"det = {resultado.get('resultado')} · {resumen}")

    if ruta == "/api/determinante/recomendar":
        return (DESTINO[ruta], f"n={datos.get('n')}",
                f"recomendado: {resultado.get('recomendado')}")

    if ruta in ("/api/biseccion", "/api/falsa-posicion"):
        r = resultado.get("resultado", {})
        cont = resultado.get("continuidad", {})
        if resultado.get("bloqueada"):
            return (DESTINO[ruta],
                    f"f(x)={datos.get('funcion')} · [{datos.get('a')}, "
                    f"{datos.get('b')}] · E={datos.get('tolerancia')}",
                    f"BLOQUEADO: f no es continua ({cont.get('total')} "
                    "sospecha(s)); no se iteró")
        return (DESTINO[ruta],
                f"f(x)={datos.get('funcion')} · [{datos.get('a')}, "
                f"{datos.get('b')}] · E={datos.get('tolerancia')}",
                f"raíz ≈ {r.get('raiz')} · {r.get('iteraciones')} iteraciones · "
                "continuidad: " + (
                    "sin señales" if cont.get("sin_senales")
                    else f"{cont.get('total')} sospecha(s)"))

    if ruta == "/api/newton-raphson":
        r = resultado.get("resultado", {})
        return (DESTINO[ruta],
                f"f(x)={datos.get('funcion')} · x0={datos.get('x0')} · "
                f"E={datos.get('tolerancia')}",
                f"raíz ≈ {r.get('raiz')} · {r.get('iteraciones')} iteraciones · "
                f"residuo {r.get('residuo')} · {r.get('motivo')}")

    if ruta == "/api/intervalos":
        return (DESTINO[ruta], f"f(x)={datos.get('funcion')}",
                f"{len(resultado.get('intervalos', []))} intervalo(s) · "
                f"{len(resultado.get('descartados', []))} descartado(s) · "
                f"{len(resultado.get('raices_exactas', []))} raíz(ces) exacta(s)")

    if ruta == "/api/grafica":
        return (DESTINO[ruta],
                f"f(x)={datos.get('funcion')} · x∈[{datos.get('x_min'):.6g}, "
                f"{datos.get('x_max'):.6g}]",
                f"{len(resultado.get('curva', []))} tramo(s)")

    if ruta == RUTA_EXPORTAR:
        return (DESTINO[ruta],
                f"{datos.get('formato')} · {datos.get('modulo')} · "
                + ("con pasos" if datos.get("incluir_pasos", True)
                   else "sin pasos") + f" · modo={modo}",
                f"{resultado.get('archivo')} · "
                f"{_bytes_legibles(resultado.get('bytes', 0))}")

    return (DESTINO.get(ruta, ruta), "", "")


def _bytes_legibles(n):
    return f"{n} B" if n < 1024 else f"{n / 1024:.1f} KB"


def _registrar(metodo, ruta, codigo, milisegundos, recibidos, enviados, detalle):
    """Imprime la línea de la petición y, si hay, su línea de detalle."""

    if codigo < 300:
        color_estado = "verde"
    elif codigo < 400:
        color_estado = "cian"
    elif codigo < 500:
        color_estado = "amarillo"
    else:
        color_estado = "rojo"

    color_metodo = "azul" if metodo == "GET" else "magenta"
    hora = time.strftime("%H:%M:%S")

    linea = "  ".join([
        _c(f"[{hora}]", "tenue"),
        _c(f"{metodo:<4}", color_metodo, "negrita"),
        f"{ruta:<30}",
        _c(str(codigo), color_estado, "negrita"),
        _c(f"{milisegundos:>6.1f} ms", "tenue"),
        _c(f"↓ {_bytes_legibles(recibidos)}  ↑ {_bytes_legibles(enviados)}", "tenue"),
    ])

    with _candado:
        print(linea)

        if detalle:
            destino, entrada, salida = detalle.get("calculo", ("", "", ""))
            if destino:
                print("           " + _c("↳ ", "tenue") + _c(destino, "cian"))
            if entrada:
                print("             " + _c("entrada: ", "tenue") + entrada)
            if salida:
                print("             " + _c("salida:  ", "tenue") + salida)
            if detalle.get("error"):
                print("             " + _c("error:   " + detalle["error"], "amarillo"))

        sys.stdout.flush()


class Manejador(BaseHTTPRequestHandler):

    def _iniciar_registro(self):
        self._t0 = time.perf_counter()
        self._codigo = 0
        self._recibidos = 0
        self._enviados = 0
        self._detalle = {}

    def send_response(self, codigo, mensaje=None):
        self._codigo = codigo
        super().send_response(codigo, mensaje)

    def _terminar_registro(self, metodo, ruta):
        if ruta in RUTAS_SILENCIOSAS:
            return

        milisegundos = (time.perf_counter() - self._t0) * 1000
        _registrar(metodo, ruta, self._codigo, milisegundos,
                   self._recibidos, self._enviados, self._detalle)

    def _enviar_json(self, cuerpo, estado=200):
        datos = json.dumps(_serializar(cuerpo)).encode("utf-8")
        self._enviados = len(datos)
        self.send_response(estado)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def _enviar_archivo(self, ruta, tipo):
        try:
            contenido = ruta.read_bytes()
        except OSError:
            self.send_error(404, "Archivo no encontrado")
            return

        self._enviados = len(contenido)
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

    def do_GET(self):
        self._iniciar_registro()
        ruta = self.path.split("?", 1)[0]

        if ruta in ("/", "/index.html"):
            self._enviar_archivo(SRC / "web" / "index.html", "text/html; charset=utf-8")
        elif ruta == "/api/estado":
            self._enviar_json({"ok": True})
        elif ruta == "/api/ejercicios":
            ejercicios = catalogo_ejercicios()
            self._enviar_json({
                "ok": True,
                "metodos": [
                    {"clave": clave, "nombre": nombre}
                    for clave, nombre in METODOS_EJERCICIOS
                ],
                "ejercicios": ejercicios,
            })
            total = sum(len(lista) for lista in ejercicios.values())
            self._detalle = {"calculo": (
                "metodos.ejercicios.catalogo", "",
                f"{total} ejercicios en {len(ejercicios)} métodos",
            )}
        elif ruta == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self.send_error(404, "Ruta no encontrada")

        self._terminar_registro("GET", ruta)

    def do_POST(self):
        self._iniciar_registro()
        ruta = self.path
        self._procesar_post(ruta)
        self._terminar_registro("POST", ruta)

    def _procesar_post(self, ruta):
        funcion = RUTAS.get(ruta)

        if ruta == RUTA_EXPORTAR:
            funcion = _exportar

        if funcion is None:
            self._detalle = {"error": "ruta no encontrada"}
            self._enviar_json({"error": "Ruta no encontrada."}, 404)
            return

        try:
            longitud = int(self.headers.get("Content-Length", 0))
            cuerpo = self.rfile.read(longitud) if longitud else b"{}"
            self._recibidos = len(cuerpo)
            datos = json.loads(cuerpo.decode("utf-8") or "{}")
        except (ValueError, json.JSONDecodeError):
            self._detalle = {"error": "cuerpo de la petición inválido"}
            self._enviar_json({"error": "Cuerpo de la petición inválido."}, 400)
            return

        try:
            resultado = funcion(datos)
            if ruta == RUTA_EXPORTAR:
                self._responder_exportacion(datos, *resultado)
                return
        except ValueError as error:
            self._detalle = {"error": str(error),
                             "calculo": (DESTINO.get(ruta, ""), "", "")}
            self._enviar_json({"error": str(error)}, 400)
            return
        except (IndexError, KeyError, TypeError):
            self._detalle = {"error": "datos incompletos o con formato inválido"}
            self._enviar_json(
                {"error": "Datos incompletos o con formato inválido."}, 400
            )
            return

        try:
            self._detalle = {"calculo": _descripcion_peticion(ruta, datos, resultado)}
        except Exception:
            self._detalle = {}  # El registro nunca debe romper la respuesta.

        self._enviar_json({"ok": True, **resultado})

    def _responder_exportacion(self, datos, contenido, mime, archivo):
        """Entrega el archivo generado como descarga (no JSON)."""

        try:
            self._detalle = {"calculo": _descripcion_peticion(
                RUTA_EXPORTAR, {**datos, "modo": (datos.get("datos") or {})
                                .get("modo", "fraccion")},
                {"archivo": archivo, "bytes": len(contenido)},
            )}
        except Exception:
            self._detalle = {}

        self._enviados = len(contenido)
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header(
            "Content-Disposition", f'attachment; filename="{archivo}"'
        )
        self.send_header("Access-Control-Expose-Headers", "Content-Disposition")
        self.end_headers()
        self.wfile.write(contenido)

    def log_message(self, formato, *args):
        pass  # Reemplazado por el registro propio de _registrar().


def _banner(puerto, host="127.0.0.1"):
    url = f"http://{host}:{puerto}"
    lineas = [
        [("Calculadora de Álgebra Lineal", "negrita", "verde")],
        [("Sirviendo web/index.html y la API de metodos/", "tenue")],
        [("", )],
        [("Local:    ", "tenue"), (url, "cian", "negrita")],
        [("Detener:  ", "tenue"), ("Ctrl+C", "negrita")],
        [("", )],
        [("Endpoints", "negrita")],
    ]

    lineas.append([("GET  ", "azul"), ("/api/estado", ), ("  (sin registro)", "tenue")])
    lineas.append([("GET  ", "azul"), (f"{'/api/ejercicios':<24}", ),
                   ("metodos.ejercicios.catalogo", "tenue")])

    for ruta, destino in DESTINO.items():  # incluye /api/exportar
        lineas.append([("POST ", "magenta"), (f"{ruta:<30}", ), (destino, "tenue")])

    print()
    print(_caja(lineas))
    print()
    print("  " + _c("Registro de peticiones:", "negrita"))
    print()


def iniciar(puerto=PUERTO):
    # En hosting (Render, etc.) la plataforma define PORT y exige escuchar en 0.0.0.0.
    host = "127.0.0.1"
    if os.environ.get("PORT", "").isdigit():
        host, puerto = "0.0.0.0", int(os.environ["PORT"])

    try:
        servidor = ThreadingHTTPServer((host, puerto), Manejador)
    except OSError as error:
        print(_c(f"\n  No se pudo abrir el puerto {puerto}: {error.strerror}.", "rojo"))
        print("  Cierre el otro servidor o use otro puerto: python server.py 8001\n")
        sys.exit(1)

    _banner(puerto, host)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n  " + _c("Servidor detenido.", "tenue") + "\n")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar(int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else PUERTO)
