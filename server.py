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

from metodos.general_metodos import matriz_texto, texto_comprobacion
from metodos.gauss_jordan import resolver as resolver_gauss_jordan
from metodos.pivote import resolver as resolver_pivote
from metodos.conversion import (
    NOMBRES_BASE,
    resolver as resolver_conversion,
    procedimiento_texto as procedimiento_conversion_texto,
)
from metodos.vectores_matrices import (
    combinacion_lineal,
    ecuacion_matricial,
    multiplicar_matrices,
    multiplicar_matriz_escalar,
    multiplicar_vector_escalar,
    procedimiento_texto as procedimiento_vectores_matrices_texto,
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
    """Convierte Fraction (y estructuras anidadas) a texto serializable."""

    if isinstance(valor, Fraction):
        return str(valor)
    if isinstance(valor, (list, tuple)):
        return [_serializar(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _serializar(v) for k, v in valor.items()}
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


def _resolver_sistema(datos):
    metodo = datos.get("metodo")
    funcion = RESOLVER_SISTEMA.get(metodo)

    if funcion is None:
        raise ValueError(f"Método no soportado: {metodo}")

    modo = datos.get("modo", "fraccion")
    matriz = _matriz_desde_texto(datos.get("matriz", []))
    resultado = funcion(matriz, modo)

    return {
        "tipo": resultado["tipo"],
        "soluciones": resultado["soluciones"],
        "matriz_inicial": matriz_texto(resultado["matriz_inicial"], modo),
        "matriz_final": matriz_texto(resultado["matriz_final"], modo),
        "pasos": [
            {
                "operacion": paso["operacion"],
                "matriz": matriz_texto(paso["matriz"], modo),
            }
            for paso in resultado["pasos"]
        ],
        "comprobacion": texto_comprobacion(resultado["comprobacion"], modo),
    }


def _resolver_conversion(datos):
    numero = datos.get("numero", "")
    base_entrada = int(datos.get("base_entrada"))
    base_salida = int(datos.get("base_salida"))

    resultado = resolver_conversion(numero, base_entrada, base_salida)

    return {
        "procedimiento": procedimiento_conversion_texto(resultado),
        "numero_entrada": resultado["numero_entrada"],
        "resultado": resultado["resultado"],
        "nombre_base_entrada": NOMBRES_BASE[resultado["base_entrada"]],
        "nombre_base_salida": NOMBRES_BASE[resultado["base_salida"]],
    }


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

    return {"procedimiento": procedimiento_vectores_matrices_texto(resultado, modo)}


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

    return {"procedimiento": procedimiento_vectores_matrices_texto(resultado, modo)}


def _resolver_ecuacion_matricial(datos):
    modo = datos.get("modo", "fraccion")
    resultado = ecuacion_matricial(
        datos.get("matriz_a", []), datos.get("matriz_b", []), modo
    )

    return {"procedimiento": procedimiento_vectores_matrices_texto(resultado, modo)}


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
