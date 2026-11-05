"""
Escenas geométricas por módulo (spec 014).

Cada función recibe el resultado que ya calculó `metodos/` y arma la *escena*
(ver `escena.py`) que pintan la web, el PNG y el PDF. No recalculan nada del
método: solo traducen sus números a geometría.

- `escena_sistema()`: Gauss-Jordan y Pivoteo (y la ecuación matricial). Una
  recta (2 incógnitas) o un plano (3) por ecuación y su conjunto solución.
- `escena_vectores()`: suma, resta, vector por escalar y combinación lineal.
  Flechas desde el origen, regla del paralelogramo / punta con cola.
- `escena_inversa()`: el cuadrado (cubo) unitario y su imagen bajo A y bajo
  A⁻¹.
- `escena_producto()`: A × B como transformaciones: el cuadrado (cubo)
  unitario, su imagen bajo B y luego bajo A (= imagen bajo A·B).
- `escena_determinante()`: las columnas de A y el paralelogramo (2×2) o
  paralelepípedo (3×3) que forman; su área o volumen es |det A|.

Spec 015: las escenas de la inversa, del producto y del determinante traen
además `animacion`: cuadros precalculados de M(t) = (1 − t)·I + t·A (en el
producto, dos tramos: I → B y B → A·B) que la web recorre con un deslizador.
"""

from fractions import Fraction

from metodos import escena as E

NOMBRES_VARIABLES = ("x1", "x2", "x3")


# ----------------------------------------------------------------------
# Sistemas de ecuaciones
# ----------------------------------------------------------------------

def _ecuaciones_validas(matriz, n, escena):
    """Filas con algún coeficiente distinto de cero (las que se dibujan).
    Las filas `0 = c` se explican en un aviso, no se dibujan."""

    validas = []
    for k, fila in enumerate(matriz, start=1):
        coeficientes, termino = fila[:n], fila[n]
        if any(c != 0 for c in coeficientes):
            validas.append((k, coeficientes, termino))
        elif termino != 0:
            escena["avisos"].append(
                f"La ecuación {k} queda 0 = {E.numero_texto(termino)}: no se "
                "cumple nunca, por eso no hay solución (no se dibuja).")
        else:
            escena["avisos"].append(
                f"La ecuación {k} es 0 = 0: no aporta nada y no se dibuja.")
    return validas


def _recta_de_ecuacion(coeficientes, termino, serie, etiqueta):
    a, b = Fraction(coeficientes[0]), Fraction(coeficientes[1])
    c = Fraction(termino)
    norma2 = float(a * a + b * b)
    p = (float(a * c) / norma2, float(b * c) / norma2)
    return E.recta(p, (-float(b), float(a)), serie, etiqueta)


def _puntos_de_interes_2d(validas, solucion):
    """Puntos que conviene tener a la vista: cortes con los ejes, cruces entre
    rectas y la solución."""

    puntos = []
    if solucion is not None:
        puntos.append(E.punto_float(solucion))
    for _, (a, b), c in validas:
        if a != 0:
            puntos.append([float(c / a), 0.0])
        if b != 0:
            puntos.append([0.0, float(c / b)])
    for i, (_, (a1, b1), c1) in enumerate(validas):
        for _, (a2, b2), c2 in validas[i + 1:]:
            det = a1 * b2 - a2 * b1
            if det != 0:
                puntos.append([float((c1 * b2 - c2 * b1) / det),
                               float((a1 * c2 - a2 * c1) / det)])
    return puntos


def _escena_sistema_2d(resultado, modo):
    matriz = resultado["matriz_inicial"]
    escena = E.nueva_escena(2, NOMBRES_VARIABLES[:2])
    validas = _ecuaciones_validas(matriz, 2, escena)
    tipo = resultado["tipo"]

    solucion = None
    if tipo == "unica":
        solucion = [Fraction(x) for x in resultado["comprobacion"]["X"]]

    for orden, (k, coef, termino) in enumerate(validas):
        serie = E.serie_de(orden)
        texto = E.ecuacion_texto(coef, termino, NOMBRES_VARIABLES, modo)
        escena["elementos"].append(
            _recta_de_ecuacion(coef, termino, serie, None))
        E.leyenda(escena, serie, "recta", f"({k}) {texto}")

    if tipo == "unica":
        etiqueta = E.coordenadas_texto(solucion, modo)
        escena["elementos"].append(
            E.punto(solucion, "solucion", etiqueta, grosor="fuerte"))
        E.leyenda(escena, "solucion", "punto", f"Solución {etiqueta}")
        resumen = f"se cruzan en {etiqueta}"
    elif tipo == "infinitas":
        _, coef, termino = validas[0]
        resalte = _recta_de_ecuacion(coef, termino, "solucion", None)
        resalte["grosor"] = "fuerte"
        escena["elementos"].append(resalte)
        E.leyenda(escena, "solucion", "recta",
                  "Soluciones: todos los puntos de la recta")
        escena["avisos"].append(
            "Las ecuaciones representan la misma recta: todos sus puntos "
            "son solución.")
        resumen = "coinciden en una misma recta (infinitas soluciones)"
    else:
        if len(validas) == 2:
            (_, (a1, b1), _), (_, (a2, b2), _) = validas
            if a1 * b2 - a2 * b1 == 0:
                escena["avisos"].append(
                    "Las dos rectas son paralelas: nunca se cruzan, por eso "
                    "no hay solución.")
        if not escena["avisos"]:
            escena["avisos"].append(
                "Las rectas no se cruzan todas en un mismo punto: no hay "
                "solución.")
        resumen = "no hay un punto común a todas las rectas"

    puntos = _puntos_de_interes_2d(validas, solucion)
    escena["ventana"] = E.ventana_2d(puntos)
    escena["resumen"] = (
        f"Gráfica de {len(validas)} recta(s) en el plano x1–x2: {resumen}.")
    return escena


def _cruz_f(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def _punto_f(a, b):
    return sum(x * y for x, y in zip(a, b))


def _interseccion_dos_planos(n1, d1, n2, d2):
    """Recta de corte de dos planos (Fractions): (punto, dirección) o None
    si son paralelos o coinciden."""

    c = _cruz_f(n1, n2)
    cc = _punto_f(c, c)
    if cc == 0:
        return None
    a = _cruz_f(n2, c)
    b = _cruz_f(c, n1)
    punto = [(d1 * a[i] + d2 * b[i]) / cc for i in range(3)]
    return punto, c


def _recta_solucion_3d(resultado):
    """(punto, dirección) de la solución de un sistema con una variable libre
    (rango 2), leídos de la forma reducida; None si no es ese caso."""

    libres = resultado["variables_libres"]
    if len(libres) != 1:
        return None
    final = resultado["matriz_final"]
    libre = libres[0]
    punto, direccion = [Fraction(0)] * 3, [Fraction(0)] * 3
    punto, direccion = list(punto), list(direccion)
    direccion[libre] = Fraction(1)
    for fila, columna in enumerate(resultado["pivotes"]):
        punto[columna] = Fraction(final[fila][3])
        direccion[columna] = -Fraction(final[fila][libre])
    return punto, direccion


def _puntos_de_interes_3d(validas, solucion, extra):
    puntos = []
    if solucion is not None:
        puntos.append(E.punto_float(solucion))
    puntos += [E.punto_float(p) for p in extra]
    for _, coef, termino in validas:
        for eje in range(3):
            if coef[eje] != 0:
                corte = [Fraction(0)] * 3
                corte[eje] = Fraction(termino) / Fraction(coef[eje])
                puntos.append(E.punto_float(corte))
    return puntos


def _escena_sistema_3d(resultado, modo):
    matriz = resultado["matriz_inicial"]
    escena = E.nueva_escena(3, NOMBRES_VARIABLES)
    validas = _ecuaciones_validas(matriz, 3, escena)
    tipo = resultado["tipo"]

    solucion, extra, recta_comun = None, [], None
    if tipo == "unica":
        solucion = [Fraction(x) for x in resultado["comprobacion"]["X"]]
    elif tipo == "infinitas":
        recta_comun = _recta_solucion_3d(resultado)
        if recta_comun is not None:
            extra.append(recta_comun[0])

    # Caja: lo que hay que ver (solución, cortes con los ejes) y el origen.
    caja = E.caja_3d(_puntos_de_interes_3d(validas, solucion, extra))
    escena["caja"] = caja
    escena["camara"] = E.camara_inicial()

    for orden, (k, coef, termino) in enumerate(validas):
        serie = E.serie_de(orden)
        poligono = E.recortar_plano_caja(
            [float(c) for c in coef], float(termino), caja)
        texto = E.ecuacion_texto(coef, termino, NOMBRES_VARIABLES, modo)
        if poligono:
            escena["elementos"].append(E.poligono(poligono, serie))
        else:
            escena["avisos"].append(
                f"El plano de la ecuación {k} queda fuera de la vista.")
        E.leyenda(escena, serie, "poligono", f"({k}) {texto}")

    if tipo == "unica":
        etiqueta = E.coordenadas_texto(solucion, modo)
        base = [float(solucion[0]), float(solucion[1]), caja["z"][0]]
        escena["elementos"].append(
            E.segmento(solucion, base, "solucion", guion=True))
        escena["elementos"].append(
            E.punto(solucion, "solucion", etiqueta, grosor="fuerte"))
        E.leyenda(escena, "solucion", "punto", f"Solución {etiqueta}")
        resumen = f"se cortan en {etiqueta}"
    elif tipo == "infinitas":
        if recta_comun is not None:
            tramo = E.recortar_recta_caja(
                [float(c) for c in recta_comun[0]],
                [float(c) for c in recta_comun[1]], caja)
            if tramo:
                escena["elementos"].append(
                    E.segmento(tramo[0], tramo[1], "solucion", grosor="fuerte"))
            E.leyenda(escena, "solucion", "recta",
                      "Soluciones: todos los puntos de la recta de corte")
            escena["avisos"].append(
                "Los planos se cortan en una recta: todos sus puntos son "
                "solución.")
            resumen = "se cortan en una recta (infinitas soluciones)"
        else:
            _, coef, termino = validas[0]
            poligono = E.recortar_plano_caja(
                [float(c) for c in coef], float(termino), caja)
            if poligono:
                escena["elementos"].append(E.poligono(poligono, "solucion"))
            E.leyenda(escena, "solucion", "poligono",
                      "Soluciones: todos los puntos del plano")
            escena["avisos"].append(
                "Todas las ecuaciones representan el mismo plano: todos sus "
                "puntos son solución.")
            resumen = "coinciden en un mismo plano (infinitas soluciones)"
    else:
        # Sin punto común: se dibujan las rectas donde se cortan los planos
        # de dos en dos para ver por qué no coinciden.
        cortes = 0
        for i, (_, c1, d1) in enumerate(validas):
            for _, c2, d2 in validas[i + 1:]:
                corte = _interseccion_dos_planos(
                    [Fraction(c) for c in c1], Fraction(d1),
                    [Fraction(c) for c in c2], Fraction(d2))
                if corte is None:
                    continue
                tramo = E.recortar_recta_caja(
                    [float(c) for c in corte[0]], [float(c) for c in corte[1]],
                    caja)
                if tramo:
                    escena["elementos"].append(
                        E.segmento(tramo[0], tramo[1], 5, guion=True))
                    cortes += 1
        if cortes:
            E.leyenda(escena, 5, "recta",
                      "Recta donde se cortan dos planos (línea discontinua)")
        if len(validas) == 2:
            escena["avisos"].append(
                "Los dos planos son paralelos: nunca se cortan, por eso no "
                "hay solución.")
        else:
            escena["avisos"].append(
                "Los planos no tienen ningún punto en común: no hay "
                "solución.")
        resumen = "no hay un punto común a todos los planos"

    escena["resumen"] = (
        f"Gráfica 3D de {len(validas)} plano(s): {resumen}.")
    return escena


def escena_sistema(resultado, modo="fraccion"):
    """Escena de un sistema ya resuelto (`resultado` de gauss_jordan/pivote).

    Una recta por ecuación si hay 2 incógnitas; un plano si hay 3. Con otra
    cantidad de incógnitas la escena es "no disponible"."""

    n = len(resultado["matriz_inicial"][0]) - 1
    if n == 2:
        return _escena_sistema_2d(resultado, modo)
    if n == 3:
        return _escena_sistema_3d(resultado, modo)
    return E.no_disponible(
        "La gráfica de los sistemas solo está disponible con 2 o 3 "
        "incógnitas.")


# ----------------------------------------------------------------------
# Vectores
# ----------------------------------------------------------------------

EJES_VECTORES = ("x", "y", "z")
MOTIVO_VECTORES = ("La gráfica solo está disponible para vectores de 2 o 3 "
                   "componentes.")


def _sumar(a, b):
    return [Fraction(x) + Fraction(y) for x, y in zip(a, b)]


def _cerrar_escena(escena, puntos):
    """Pone la ventana (2D) o la caja y la cámara (3D) para ver `puntos`."""

    flotantes = [E.punto_float(p) for p in puntos]
    if escena["dim"] == 2:
        escena["ventana"] = E.ventana_2d(flotantes)
    else:
        escena["caja"] = E.caja_3d(flotantes)
        escena["camara"] = E.camara_inicial()


def _flecha_vector(escena, vector, serie, etiqueta, desde=None, **estilo):
    origen = desde if desde is not None else [Fraction(0)] * len(vector)
    destino = _sumar(origen, vector)
    escena["elementos"].append(E.flecha(origen, destino, serie, etiqueta, **estilo))
    return destino


def _escena_suma(e, modo):
    vectores = [[Fraction(x) for x in v] for v in e["vectores"]]
    dim = len(vectores[0])
    escena = E.nueva_escena(dim, EJES_VECTORES[:dim])
    cero = [Fraction(0)] * dim
    puntos = [cero]

    parcial = cero
    sumas = []
    for i, v in enumerate(vectores):
        serie = E.serie_de(i)
        _flecha_vector(escena, v, serie, f"v{i + 1}")
        E.leyenda(escena, serie, "flecha", f"v{i + 1} = {E.coordenadas_texto(v, modo)}")
        if i > 0:                      # copia punta con cola, desde la suma parcial
            _flecha_vector(escena, v, serie, None, desde=parcial, guion=True)
        parcial = _sumar(parcial, v)
        sumas.append(parcial)
        puntos.append(parcial)
        puntos.append(v)
    if len(vectores) == 2:             # regla del paralelogramo
        escena["elementos"].insert(0, E.poligono(
            [cero, vectores[0], parcial, vectores[1]], "solucion"))
        escena["avisos"].append(
            "Regla del paralelogramo: la suma es la diagonal desde el origen; "
            "las flechas discontinuas son los vectores colocados punta con cola.")
    else:
        escena["avisos"].append(
            "Las flechas discontinuas son los vectores colocados punta con "
            "cola; la suma llega al mismo punto.")
    _flecha_vector(escena, parcial, "solucion", "suma", grosor="fuerte")
    E.leyenda(escena, "solucion", "flecha", f"Suma = {E.coordenadas_texto(parcial, modo)}")
    _cerrar_escena(escena, puntos)
    escena["resumen"] = (f"Suma de {len(vectores)} vectores de {dim} componentes: "
                         f"{E.coordenadas_texto(parcial, modo)}.")
    return escena


def _escena_resta(e, modo):
    a = [Fraction(x) for x in e["vector_a"]]
    b = [Fraction(x) for x in e["vector_b"]]
    dim = len(a)
    escena = E.nueva_escena(dim, EJES_VECTORES[:dim])
    cero = [Fraction(0)] * dim
    resultado = [x - y for x, y in zip(a, b)]

    _flecha_vector(escena, a, 0, "a")
    _flecha_vector(escena, b, 1, "b")
    _flecha_vector(escena, resultado, "solucion", "a-b", grosor="fuerte")
    _flecha_vector(escena, resultado, "solucion", None, desde=b, guion=True)
    E.leyenda(escena, 0, "flecha", f"a = {E.coordenadas_texto(a, modo)}")
    E.leyenda(escena, 1, "flecha", f"b = {E.coordenadas_texto(b, modo)}")
    E.leyenda(escena, "solucion", "flecha",
              f"a - b = {E.coordenadas_texto(resultado, modo)}")
    escena["avisos"].append(
        "a - b es la flecha que va de la punta de b a la punta de a (línea "
        "discontinua); la flecha desde el origen es la misma.")
    _cerrar_escena(escena, [cero, a, b, resultado])
    escena["resumen"] = (f"Resta de dos vectores de {dim} componentes: "
                         f"{E.coordenadas_texto(resultado, modo)}.")
    return escena


def _escena_escalar(e, modo):
    v = [Fraction(x) for x in e["vector"]]
    k = Fraction(e["escalar"])
    dim = len(v)
    escena = E.nueva_escena(dim, EJES_VECTORES[:dim])
    cero = [Fraction(0)] * dim
    resultado = [k * x for x in v]

    _flecha_vector(escena, v, 0, "v")
    _flecha_vector(escena, resultado, "solucion", "k·v", grosor="fuerte")
    E.leyenda(escena, 0, "flecha", f"v = {E.coordenadas_texto(v, modo)}")
    E.leyenda(escena, "solucion", "flecha",
              f"{E.numero_texto(k, modo)}·v = {E.coordenadas_texto(resultado, modo)}")
    if k == 0:
        escena["elementos"].append(E.punto(cero, "solucion", "0"))
        escena["avisos"].append("k = 0: el resultado es el vector cero (un punto en el origen).")
    elif k < 0:
        escena["avisos"].append("k es negativo: el vector cambia de sentido.")
    elif abs(k) < 1:
        escena["avisos"].append("0 < |k| < 1: el vector se acorta.")
    elif abs(k) > 1:
        escena["avisos"].append("|k| > 1: el vector se alarga.")
    _cerrar_escena(escena, [cero, v, resultado])
    escena["resumen"] = (f"Vector multiplicado por {E.numero_texto(k, modo)}: "
                         f"{E.coordenadas_texto(resultado, modo)}.")
    return escena


def _escena_combinacion(r, modo):
    vectores = [[Fraction(x) for x in v] for v in r["entradas"]["vectores"]]
    objetivo = [Fraction(x) for x in r["entradas"]["objetivo"]]
    dim = len(objetivo)
    escena = E.nueva_escena(dim, EJES_VECTORES[:dim])
    cero = [Fraction(0)] * dim
    puntos = [cero, objetivo]

    for i, v in enumerate(vectores):
        serie = E.serie_de(i)
        _flecha_vector(escena, v, serie, f"v{i + 1}")
        E.leyenda(escena, serie, "flecha", f"v{i + 1} = {E.coordenadas_texto(v, modo)}")
        puntos.append(v)

    if r["es_combinacion"]:
        escalares = [Fraction(c) for c in r["escalares"]]
        parcial = cero
        for i, (c, v) in enumerate(zip(escalares, vectores)):
            multiplo = [c * x for x in v]
            etiqueta = f"{E.numero_texto(c, modo)}·v{i + 1}"
            _flecha_vector(escena, multiplo, E.serie_de(i), etiqueta,
                           desde=parcial, guion=True, grosor="fuerte")
            parcial = _sumar(parcial, multiplo)
            puntos.append(parcial)
        _flecha_vector(escena, objetivo, "solucion", "b", grosor="fuerte")
        E.leyenda(escena, "solucion", "flecha", f"b = {E.coordenadas_texto(objetivo, modo)}")
        terminos = " + ".join(
            f"{E.numero_texto(c, modo)}·v{i + 1}" for i, c in enumerate(escalares))
        escena["avisos"].append(
            f"b = {terminos}: las flechas discontinuas, puestas punta con "
            "cola, llegan a b.")
        if r["tipo_solucion"] == "infinitas":
            escena["avisos"].append(
                "Hay infinitas formas de escribir b; se dibuja una de ellas.")
        resumen = "b es combinación lineal de los vectores"
    else:
        _flecha_vector(escena, objetivo, "solucion", "b", grosor="fuerte", guion=True)
        E.leyenda(escena, "solucion", "flecha", f"b = {E.coordenadas_texto(objetivo, modo)}")
        escena["avisos"].append(
            "b no es combinación lineal de los vectores: no hay escalares "
            "que lleven hasta b, queda fuera de lo que ellos generan.")
        resumen = "b no es combinación lineal de los vectores"
    _cerrar_escena(escena, puntos)
    escena["resumen"] = f"Combinación lineal de {len(vectores)} vectores de {dim} componentes: {resumen}."
    return escena


def escena_vectores(resultado, modo="fraccion"):
    """Escena de una operación con vectores ya calculada (`resultado` de
    suma_vectores, resta_vectores, multiplicar_vector_escalar o
    combinacion_lineal). Vectores de 2 o 3 componentes; si no, no disponible."""

    operacion = resultado["operacion"]
    entradas = resultado["entradas"]
    muestra = (entradas.get("vectores", [None])[0] if "vectores" in entradas
               else entradas.get("vector", entradas.get("vector_a")))
    if muestra is None or len(muestra) not in (2, 3):
        return E.no_disponible(MOTIVO_VECTORES)

    if operacion == "suma_vectores":
        return _escena_suma(entradas, modo)
    if operacion == "resta_vectores":
        return _escena_resta(entradas, modo)
    if operacion == "escalar_vector":
        return _escena_escalar(entradas, modo)
    if operacion == "combinacion_lineal":
        return _escena_combinacion(resultado, modo)
    return E.no_disponible("Esta operación no tiene gráfica.")


# ----------------------------------------------------------------------
# Matrices: columnas, paralelogramo y paralelepípedo
# ----------------------------------------------------------------------

MOTIVO_MATRIZ = "La gráfica solo está disponible para matrices de 2×2 o 3×3."


def _columnas(matriz):
    return [[Fraction(fila[j]) for fila in matriz] for j in range(len(matriz[0]))]


def _forma_de_columnas(columnas):
    """Polígonos del paralelogramo (2 columnas) o de las 6 caras del
    paralelepípedo (3 columnas) que generan las columnas desde el origen."""

    dim = len(columnas[0])
    cero = [Fraction(0)] * dim
    if dim == 2:
        c1, c2 = columnas
        return [[cero, c1, _sumar(c1, c2), c2]]
    c1, c2, c3 = columnas
    c12, c13, c23 = _sumar(c1, c2), _sumar(c1, c3), _sumar(c2, c3)
    c123 = _sumar(c12, c3)
    return [[cero, c1, c12, c2], [cero, c1, c13, c3], [cero, c2, c23, c3],
            [c3, c13, c123, c23], [c2, c12, c123, c23], [c1, c12, c123, c13]]


def _puntos_de_forma(columnas):
    puntos = [p for cara in _forma_de_columnas(columnas) for p in cara]
    return puntos


def _escena_determinante(resultado, modo):
    matriz = resultado["entradas"]["matriz"]
    n = len(matriz)
    if n not in (2, 3) or len(matriz[0]) != n:
        return E.no_disponible(MOTIVO_MATRIZ)

    det = Fraction(resultado["resultado"])
    columnas = _columnas(matriz)
    escena = E.nueva_escena(n, EJES_VECTORES[:n])

    for cara in _forma_de_columnas(columnas):
        escena["elementos"].append(E.poligono(cara, "solucion"))
    for j, c in enumerate(columnas):
        _flecha_vector(escena, c, E.serie_de(j), f"c{j + 1}", grosor="fuerte")
        E.leyenda(escena, E.serie_de(j), "flecha",
                  f"c{j + 1} = {E.coordenadas_texto(c, modo)}")

    magnitud = E.numero_texto(abs(det), modo)
    nombre = "Área" if n == 2 else "Volumen"
    E.leyenda(escena, "solucion", "poligono",
              f"{nombre} = |det A| = {magnitud}  (det A = {E.numero_texto(det, modo)})")

    if det == 0:
        escena["avisos"].append(
            "det A = 0: " + (
                "las dos columnas son paralelas, el paralelogramo se aplasta "
                "en un segmento (área 0)." if n == 2 else
                "las tres columnas están en un mismo plano, el sólido se "
                "aplasta (volumen 0).")
            + " Por eso la matriz no tiene inversa.")
    elif n == 2:
        escena["avisos"].append(
            "det A > 0: de c1 a c2 se gira en sentido antihorario." if det > 0
            else "det A < 0: de c1 a c2 se gira en sentido horario "
                 "(la orientación se invierte).")
    else:
        escena["avisos"].append(
            "det A > 0: c1, c2, c3 siguen la regla de la mano derecha." if det > 0
            else "det A < 0: c1, c2, c3 invierten la orientación (mano izquierda).")

    puntos = [[Fraction(0)] * n] + _puntos_de_forma(columnas)
    _agregar_animacion(escena, puntos, [{
        "nombre": "Identidad → A", "desde": _identidad(n), "hasta": matriz,
        "serie": "solucion", "flechas": E.serie_de,
        "etiqueta": lambda j: f"c{j + 1}"}], 0, modo)
    _cerrar_escena(escena, puntos)
    escena["resumen"] = (
        f"Columnas de una matriz {n}×{n} y su {nombre.lower()} "
        f"|det A| = {magnitud}.")
    return escena


def escena_determinante(resultado, modo="fraccion"):
    """Escena de un determinante ya calculado (`resultado` de
    `determinante()`): las columnas y la figura que forman."""

    return _escena_determinante(resultado, modo)


# ----------------------------------------------------------------------
# Matriz inversa
# ----------------------------------------------------------------------

def _det_pequeno(matriz):
    """Determinante de una matriz 2×2 o 3×3 (solo para rotular el área)."""

    m = [[Fraction(x) for x in fila] for fila in matriz]
    if len(m) == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _identidad(n):
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


# ----------------------------------------------------------------------
# Transformación animada (spec 015)
# ----------------------------------------------------------------------

PASOS_ANIMACION = 20   # pasos por tramo (el tramo trae PASOS + 1 cuadros con ambos extremos)


def _interpolar(m0, m1, s):
    """(1 - s)·m0 + s·m1, entrada por entrada, con fracciones exactas."""

    return [[(1 - s) * Fraction(a) + s * Fraction(b) for a, b in zip(f0, f1)]
            for f0, f1 in zip(m0, m1)]


def _cuadro_animacion(m, tramo, final):
    """Elementos de la figura que generan las columnas de `m`, y su det."""

    elementos = []
    fantasma = tramo.get("fantasma")
    if fantasma is not None:
        for cara in _forma_de_columnas(_columnas(fantasma["matriz"])):
            elementos.append(E.poligono(cara, fantasma["serie"], guion=True))
    for cara in _forma_de_columnas(_columnas(m)):
        elementos.append(E.poligono(cara, tramo["serie"]))
    origen = [Fraction(0)] * len(m)
    for j, c in enumerate(_columnas(m)):
        etiqueta = tramo["etiqueta"](j) if final else None
        elementos.append(E.flecha(origen, c, tramo["flechas"](j), etiqueta,
                                  grosor="fuerte"))
    return elementos, _det_pequeno(m)


def _agregar_animacion(escena, puntos, tramos, desde, modo):
    """Agrega a `escena` la animación de la matriz (spec 015).

    `tramos`: lista de dicts con `desde` y `hasta` (matrices), `nombre`,
    `serie` (color de la figura), `flechas(j)` y `etiqueta(j)`, y opcional
    `fantasma` ({"matriz", "serie"}: figura de fondo con línea discontinua).
    Cada tramo se recorre en `PASOS_ANIMACION` pasos; el deslizador `t` va de
    0 a 1 sobre todos los tramos. `desde` es el índice del primer elemento de
    la escena base que la animación reemplaza (los anteriores quedan fijos).
    Los puntos de todos los cuadros se agregan a `puntos`: la ventana o la
    caja los contiene a todos y la cámara no salta."""

    total = len(tramos)
    pasos = []
    signo_anterior = None
    for i, tramo in enumerate(tramos):
        for k in range(0 if i == 0 else 1, PASOS_ANIMACION + 1):
            s = Fraction(k, PASOS_ANIMACION)
            m = _interpolar(tramo["desde"], tramo["hasta"], s)
            final = i == total - 1 and k == PASOS_ANIMACION
            elementos, det = _cuadro_animacion(m, tramo, final)
            signo = (det > 0) - (det < 0)
            # aplastado: det = 0, o el signo cambió respecto al cuadro anterior
            # (el det pasó por 0 entre los dos)
            aplastado = det == 0 or (signo_anterior not in (None, 0)
                                     and signo != signo_anterior)
            signo_anterior = signo
            for e in elementos:
                if e["tipo"] == "poligono":
                    puntos.extend(e["puntos"])
            pasos.append({
                "t": E.a_float((i + s) / total),
                "tramo": i,
                "elementos": elementos,
                "det": E.numero_texto(det, modo),
                "aplastado": aplastado,
            })
    escena["animacion"] = {
        "pasos": pasos,
        "paso_final": len(pasos) - 1,
        "reemplaza_desde": desde,
        "tramos": [t["nombre"] for t in tramos],
    }


def escena_inversa(resultado, modo="fraccion"):
    """Escena de una matriz inversa ya calculada: el cuadrado (cubo) unitario,
    su imagen bajo A y, si existe, la imagen bajo A⁻¹."""

    matriz = resultado["entradas"]["matriz"]
    n = len(matriz)
    if n not in (2, 3) or len(matriz[0]) != n:
        return E.no_disponible(MOTIVO_MATRIZ)

    figura = "cuadrado" if n == 2 else "cubo"
    medida = "Área" if n == 2 else "Volumen"
    columnas = _columnas(matriz)
    escena = E.nueva_escena(n, EJES_VECTORES[:n])
    puntos = [[Fraction(0)] * n]

    unitaria = _forma_de_columnas(_columnas(_identidad(n)))
    for cara in unitaria:
        escena["elementos"].append(E.poligono(cara, 5, guion=True))
        puntos += cara
    E.leyenda(escena, 5, "poligono", f"{figura.capitalize()} unitario")

    inversa = resultado["resultado"] if resultado["existe"] else None
    if inversa is not None:
        for cara in _forma_de_columnas(_columnas(inversa)):
            escena["elementos"].append(E.poligono(cara, 0))
            puntos += cara
    desde_animada = len(escena["elementos"])
    for cara in _forma_de_columnas(columnas):
        escena["elementos"].append(E.poligono(cara, 1))
        puntos += cara

    det = _det_pequeno(matriz)
    for j, c in enumerate(columnas):
        _flecha_vector(escena, c, 1, f"A·e{j + 1}", grosor="fuerte")
    E.leyenda(escena, 1, "poligono",
              f"Imagen por A: {medida.lower()} |det A| = {E.numero_texto(abs(det), modo)}")
    if inversa is not None:
        E.leyenda(escena, 0, "poligono",
                  f"Imagen por A⁻¹: {medida.lower()} 1/|det A| = "
                  f"{E.numero_texto(1 / abs(det), modo)}")
        escena["avisos"].append(
            f"A transforma el {figura} unitario en la figura naranja; A⁻¹ "
            f"deshace esa transformación (lleva la figura naranja de vuelta "
            f"al {figura}).")
    else:
        escena["avisos"].append(
            f"A no es invertible (det A = 0): aplasta el {figura} unitario en "
            + ("un segmento o un punto" if n == 2 else "un plano, una recta o un punto")
            + " y ninguna transformación puede devolverlo.")

    _agregar_animacion(escena, puntos, [{
        "nombre": "Identidad → A", "desde": _identidad(n), "hasta": matriz,
        "serie": 1, "flechas": lambda j: 1,
        "etiqueta": lambda j: f"A·e{j + 1}"}], desde_animada, modo)
    _cerrar_escena(escena, puntos)
    escena["resumen"] = (
        f"Efecto de una matriz {n}×{n} sobre el {figura} unitario"
        + (": tiene inversa." if inversa is not None else ": no tiene inversa."))
    return escena


# ----------------------------------------------------------------------
# Multiplicación de matrices
# ----------------------------------------------------------------------

MOTIVO_PRODUCTO = ("La gráfica del producto solo está disponible cuando A y B "
                   "son matrices cuadradas de 2×2 o 3×3.")


def escena_producto(resultado, modo="fraccion"):
    """Escena de A × B ya calculado: el cuadrado (cubo) unitario, su imagen
    bajo B y la imagen final bajo A·B (primero se aplica B y luego A)."""

    a = resultado["entradas"]["matriz_a"]
    b = resultado["entradas"]["matriz_b"]
    n = len(a)
    if (n not in (2, 3) or any(len(f) != n for f in a)
            or len(b) != n or any(len(f) != n for f in b)):
        return E.no_disponible(MOTIVO_PRODUCTO)

    figura = "cuadrado" if n == 2 else "cubo"
    medida = "área" if n == 2 else "volumen"
    producto = resultado["resultado"]
    escena = E.nueva_escena(n, EJES_VECTORES[:n])
    puntos = [[Fraction(0)] * n]

    for cara in _forma_de_columnas(_columnas(_identidad(n))):
        escena["elementos"].append(E.poligono(cara, 5, guion=True))
        puntos += cara
    desde_animada = len(escena["elementos"])
    for cara in _forma_de_columnas(_columnas(b)):
        escena["elementos"].append(E.poligono(cara, 0))
        puntos += cara
    for cara in _forma_de_columnas(_columnas(producto)):
        escena["elementos"].append(E.poligono(cara, "solucion"))
        puntos += cara

    for j, c in enumerate(_columnas(b)):
        _flecha_vector(escena, c, 0, f"B·e{j + 1}")
    for j, c in enumerate(_columnas(producto)):
        _flecha_vector(escena, c, "solucion", f"AB·e{j + 1}", grosor="fuerte")

    E.leyenda(escena, 5, "poligono", f"{figura.capitalize()} unitario")
    E.leyenda(escena, 0, "poligono",
              f"Imagen por B: {medida} |det B| = "
              f"{E.numero_texto(abs(_det_pequeno(b)), modo)}")
    E.leyenda(escena, "solucion", "poligono",
              f"Imagen por A·B: {medida} |det(A·B)| = "
              f"{E.numero_texto(abs(_det_pequeno(producto)), modo)}")
    escena["avisos"].append(
        f"A·B aplica primero B y luego A: lleva el {figura} unitario a la "
        "figura roja. El orden importa: en general A·B y B·A no son iguales.")

    _agregar_animacion(escena, puntos, [
        {"nombre": "Identidad → B", "desde": _identidad(n), "hasta": b,
         "serie": 0, "flechas": lambda j: 0,
         "etiqueta": lambda j: f"B·e{j + 1}"},
        {"nombre": "B → A·B", "desde": b, "hasta": producto,
         "serie": "solucion", "flechas": lambda j: "solucion",
         "etiqueta": lambda j: f"AB·e{j + 1}",
         "fantasma": {"matriz": b, "serie": 0}},
    ], desde_animada, modo)
    _cerrar_escena(escena, puntos)
    escena["resumen"] = (
        f"Efecto del producto A·B de matrices {n}×{n} sobre el {figura} unitario.")
    return escena
