"""
server.py
Servidor HTTP local que expone la lógica de metodos/ como endpoints JSON,
para que index.html pueda usarla desde el navegador mediante fetch().

No contiene lógica matemática propia: recibe los datos capturados en el
formulario web, llama directamente a las funciones ya existentes en
metodos/ (las mismas que usa gui.py) y devuelve el resultado -incluyendo
los pasos del procedimiento- en JSON. Usa únicamente la librería estándar
de Python (http.server, json).

Uso: python server.py
Luego abrir http://127.0.0.1:8000 en el navegador. index.html no funciona
si se abre directamente con doble clic: necesita este servidor corriendo,
igual que gui.py necesita "python gui.py".
"""

import json
from fractions import Fraction
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from metodos.general_metodos import formatear
from metodos.gauss_jordan import resolver as resolver_gauss_jordan
from metodos.pivote import resolver as resolver_pivote
from metodos.conversion import NOMBRES_BASE, resolver as resolver_conversion
from metodos.vectores_matrices import (
    combinacion_lineal,
    ecuacion_matricial,
    multiplicar_matrices,
    multiplicar_matriz_escalar,
    multiplicar_vector_escalar,
    resta_matrices,
    resta_vectores,
    suma_matrices,
    suma_vectores,
)

RAIZ = Path(__file__).resolve().parent
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
    """Convierte la matriz capturada en el navegador a floats, igual que
    VistaSistemaLineal.obtener_matriz en gui.py."""

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
    }


def _resolver_sistema(datos):
    metodo = datos.get("metodo")
    funcion = RESOLVER_SISTEMA.get(metodo)

    if funcion is None:
        raise ValueError(f"Método no soportado: {metodo}")

    modo = datos.get("modo", "fraccion")
    matriz = _matriz_desde_texto(datos.get("matriz", []))
    resultado = funcion(matriz, modo)

    return _armar_bloque_sistema(resultado, modo)


def _resolver_conversion(datos):
    numero = datos.get("numero", "")
    base_entrada = int(datos.get("base_entrada"))
    base_salida = int(datos.get("base_salida"))

    resultado = resolver_conversion(numero, base_entrada, base_salida)

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

    return bloque


def _resolver_vectores(datos):
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

    return _armar_bloque_operacion(resultado, modo)


def _resolver_matrices(datos):
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

    return _armar_bloque_operacion(resultado, modo)


def _resolver_ecuacion_matricial(datos):
    modo = datos.get("modo", "fraccion")
    resultado = ecuacion_matricial(
        datos.get("matriz_a", []), datos.get("matriz_b", []), modo
    )

    return _armar_bloque_operacion(resultado, modo)


RUTAS = {
    "/api/sistema": _resolver_sistema,
    "/api/conversion": _resolver_conversion,
    "/api/vectores": _resolver_vectores,
    "/api/matrices": _resolver_matrices,
    "/api/ecuacion-matricial": _resolver_ecuacion_matricial,
}


class Manejador(BaseHTTPRequestHandler):

    def _enviar_json(self, cuerpo, estado=200):
        datos = json.dumps(_serializar(cuerpo)).encode("utf-8")
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

        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

    def do_GET(self):
        ruta = self.path.split("?", 1)[0]

        if ruta in ("/", "/index.html"):
            self._enviar_archivo(RAIZ / "index.html", "text/html; charset=utf-8")
        else:
            self.send_error(404, "Ruta no encontrada")

    def do_POST(self):
        funcion = RUTAS.get(self.path)

        if funcion is None:
            self._enviar_json({"error": "Ruta no encontrada."}, 404)
            return

        try:
            longitud = int(self.headers.get("Content-Length", 0))
            cuerpo = self.rfile.read(longitud) if longitud else b"{}"
            datos = json.loads(cuerpo.decode("utf-8") or "{}")
        except (ValueError, json.JSONDecodeError):
            self._enviar_json({"error": "Cuerpo de la petición inválido."}, 400)
            return

        try:
            resultado = funcion(datos)
        except ValueError as error:
            self._enviar_json({"error": str(error)}, 400)
            return
        except (IndexError, KeyError, TypeError):
            self._enviar_json(
                {"error": "Datos incompletos o con formato inválido."}, 400
            )
            return

        self._enviar_json({"ok": True, **resultado})

    def log_message(self, formato, *args):
        pass  # Silenciar el log por defecto de http.server en consola.


def iniciar(puerto=PUERTO):
    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
    print(f"Calculadora disponible en: http://127.0.0.1:{puerto}")
    print("Presione Ctrl+C para detener el servidor.")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar()
