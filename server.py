"""
server.py
Servidor HTTP local que expone la lógica de metodos/ como endpoints JSON,
para que index.html pueda usarla desde el navegador mediante fetch().

No contiene lógica matemática propia: recibe los datos capturados en el
formulario web, llama directamente a las funciones ya existentes en
metodos/ (las mismas que usa gui.py) y devuelve el resultado -incluyendo
los pasos del procedimiento- en JSON. Usa únicamente la librería estándar
de Python (http.server, json).

Uso: python server.py [puerto]
Al iniciar muestra un banner y, por cada petición, una línea de registro con
la ruta, el código de estado, el tiempo y qué función de metodos/ se usó.
Luego abrir http://127.0.0.1:8000 en el navegador. index.html no funciona
si se abre directamente con doble clic: necesita este servidor corriendo,
igual que gui.py necesita "python gui.py".
"""

import json
import os
import sys
import threading
import time
from fractions import Fraction
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from metodos.general_metodos import formatear
from metodos.gauss_jordan import resolver as resolver_gauss_jordan
from metodos.pivote import resolver as resolver_pivote
from metodos.conversion import NOMBRES_BASE, resolver as resolver_conversion
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


def _resolver_inversa(datos):
    modo = datos.get("modo", "fraccion")
    metodo = datos.get("metodo", "gauss_jordan")
    resultado = matriz_inversa(datos.get("matriz", []), metodo, modo)

    return _armar_bloque_operacion(resultado, modo)


RUTAS = {
    "/api/sistema": _resolver_sistema,
    "/api/conversion": _resolver_conversion,
    "/api/vectores": _resolver_vectores,
    "/api/matrices": _resolver_matrices,
    "/api/ecuacion-matricial": _resolver_ecuacion_matricial,
    "/api/inversa": _resolver_inversa,
}


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
        f"{ruta:<24}",
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
            self._enviar_archivo(RAIZ / "index.html", "text/html; charset=utf-8")
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

    def log_message(self, formato, *args):
        pass  # Reemplazado por el registro propio de _registrar().


def _banner(puerto):
    url = f"http://127.0.0.1:{puerto}"
    lineas = [
        [("Calculadora de Álgebra Lineal", "negrita", "verde")],
        [("Sirviendo index.html y la API de metodos/", "tenue")],
        [("", )],
        [("Local:    ", "tenue"), (url, "cian", "negrita")],
        [("Detener:  ", "tenue"), ("Ctrl+C", "negrita")],
        [("", )],
        [("Endpoints", "negrita")],
    ]

    lineas.append([("GET  ", "azul"), ("/api/estado", ), ("  (sin registro)", "tenue")])
    lineas.append([("GET  ", "azul"), (f"{'/api/ejercicios':<24}", ),
                   ("metodos.ejercicios.catalogo", "tenue")])

    for ruta, destino in DESTINO.items():
        lineas.append([("POST ", "magenta"), (f"{ruta:<24}", ), (destino, "tenue")])

    print()
    print(_caja(lineas))
    print()
    print("  " + _c("Registro de peticiones:", "negrita"))
    print()


def iniciar(puerto=PUERTO):
    try:
        servidor = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
    except OSError as error:
        print(_c(f"\n  No se pudo abrir el puerto {puerto}: {error.strerror}.", "rojo"))
        print("  Cierre el otro servidor o use otro puerto: python server.py 8001\n")
        sys.exit(1)

    _banner(puerto)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n  " + _c("Servidor detenido.", "tenue") + "\n")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar(int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else PUERTO)
