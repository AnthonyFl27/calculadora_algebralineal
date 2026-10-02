"""
metodos/conversion.py
Motor de conversión entre bases numéricas: decimal, binario, octal y
hexadecimal.

Cubre dos direcciones:
    - Decimal -> (binario | octal | hexadecimal), por divisiones sucesivas.
    - (Binario | octal | decimal) -> decimal, mostrando la combinación
      lineal de dígito * base^posición que genera el número.

No usa NumPy ni librerías externas: solo la librería estándar de Python.
"""

DIGITOS = "0123456789ABCDEF"

NOMBRES_BASE = {
    2: "binario",
    8: "octal",
    10: "decimal",
    16: "hexadecimal",
}


def _validar_base(base):
    if base not in NOMBRES_BASE:
        raise ValueError(f"Base no soportada: {base}")


def decimal_a_base(numero, base):
    """
    Convierte un entero decimal a la `base` indicada (2, 8 o 16) mediante
    divisiones sucesivas.

    Devuelve (texto_resultado, pasos), donde cada paso es un diccionario
    con dividendo, base, cociente y residuo.
    """

    _validar_base(base)

    signo = "-" if numero < 0 else ""
    valor = abs(numero)

    if valor == 0:
        return "0", [{
            "dividendo": 0,
            "base": base,
            "cociente": 0,
            "residuo": 0,
        }]

    pasos = []
    residuos = []

    while valor > 0:
        cociente = valor // base
        residuo = valor % base

        pasos.append({
            "dividendo": valor,
            "base": base,
            "cociente": cociente,
            "residuo": residuo,
        })

        residuos.append(residuo)
        valor = cociente

    digitos = "".join(DIGITOS[r] for r in reversed(residuos))

    return signo + digitos, pasos


def base_a_decimal(texto, base):
    """
    Convierte un número escrito en `base` (2, 8 o 10) a decimal, mostrando
    la combinación lineal dígito * base^posición.

    Devuelve (valor_decimal, terminos), donde cada término es un
    diccionario con dígito, valor del dígito, exponente y contribución.

    Lanza ValueError si algún dígito no es válido para la base indicada.
    """

    _validar_base(base)

    texto = texto.strip().upper()

    if texto == "":
        raise ValueError("Ingrese un número.")

    signo = 1

    if texto[0] in "+-":
        if texto[0] == "-":
            signo = -1
        texto = texto[1:]

    if texto == "":
        raise ValueError("Ingrese un número.")

    digitos_validos = DIGITOS[:base]
    cantidad = len(texto)
    terminos = []
    total = 0

    for posicion, caracter in enumerate(texto):

        if caracter not in digitos_validos:
            raise ValueError(
                f"'{caracter}' no es un dígito válido en base {base} "
                f"({NOMBRES_BASE[base]})."
            )

        valor_digito = digitos_validos.index(caracter)
        exponente = cantidad - 1 - posicion
        contribucion = valor_digito * (base ** exponente)

        terminos.append({
            "digito": caracter,
            "valor_digito": valor_digito,
            "base": base,
            "exponente": exponente,
            "contribucion": contribucion,
        })

        total += contribucion

    return signo * total, terminos


def resolver(numero_texto, base_entrada, base_salida):
    """
    Función principal del módulo.

    Exactamente una de las dos bases debe ser 10 (decimal); la otra debe
    ser 2, 8 o 16. Devuelve un diccionario listo para que CLI o GUI lo
    utilicen:

        tipo: "a_otra_base" | "a_decimal"
        numero_entrada, base_entrada, base_salida
        pasos: lista de pasos del procedimiento (divisiones o términos)
        resultado: texto del número convertido
    """

    _validar_base(base_entrada)
    _validar_base(base_salida)

    numero_texto = numero_texto.strip()

    if numero_texto == "":
        raise ValueError("Ingrese un número.")

    if base_entrada == 10 and base_salida == 10:
        try:
            valor = int(numero_texto)
        except ValueError:
            raise ValueError("Ingrese un número decimal entero válido.")

        return {
            "tipo": "a_otra_base",
            "numero_entrada": numero_texto,
            "base_entrada": base_entrada,
            "base_salida": base_salida,
            "pasos": [],
            "resultado": str(valor),
        }

    if base_entrada == 10:
        try:
            valor = int(numero_texto)
        except ValueError:
            raise ValueError("Ingrese un número decimal entero válido.")

        resultado, pasos = decimal_a_base(valor, base_salida)

        return {
            "tipo": "a_otra_base",
            "numero_entrada": numero_texto,
            "base_entrada": base_entrada,
            "base_salida": base_salida,
            "pasos": pasos,
            "resultado": resultado,
        }

    if base_salida == 10:
        valor, terminos = base_a_decimal(numero_texto, base_entrada)

        return {
            "tipo": "a_decimal",
            "numero_entrada": numero_texto,
            "base_entrada": base_entrada,
            "base_salida": base_salida,
            "pasos": terminos,
            "resultado": str(valor),
        }

    raise ValueError(
        "Conversión no soportada: una de las dos bases debe ser decimal."
    )


def procedimiento_texto(resultado):
    """Formatea los pasos de `resolver(...)` como texto legible."""

    tipo = resultado["tipo"]
    base_entrada = resultado["base_entrada"]
    base_salida = resultado["base_salida"]
    pasos = resultado["pasos"]

    lineas = []

    if not pasos:
        lineas.append(
            "El número ya está en la base solicitada, no se requieren "
            "operaciones."
        )
        return "\n".join(lineas)

    if tipo == "a_otra_base":

        lineas.append(
            f"Divisiones sucesivas entre {base_salida} "
            f"({NOMBRES_BASE[base_salida]}):\n"
        )

        for paso in pasos:
            residuo_texto = DIGITOS[paso["residuo"]]

            if paso["base"] <= 10:
                lineas.append(
                    f"{paso['dividendo']} ÷ {paso['base']} = "
                    f"{paso['cociente']}   residuo = {paso['residuo']}"
                )
            else:
                lineas.append(
                    f"{paso['dividendo']} ÷ {paso['base']} = "
                    f"{paso['cociente']}   residuo = {paso['residuo']} "
                    f"({residuo_texto})"
                )

        residuos_orden = " ".join(
            DIGITOS[paso["residuo"]] for paso in reversed(pasos)
        )

        lineas.append(
            "\nLos residuos leídos de abajo hacia arriba forman el "
            f"resultado: {residuos_orden}"
        )

    else:  # tipo == "a_decimal"

        lineas.append(
            f"Combinación lineal en base {base_entrada} "
            f"({NOMBRES_BASE[base_entrada]}):\n"
        )

        terminos_texto = []

        for termino in pasos:
            terminos_texto.append(
                f"{termino['valor_digito']}×{termino['base']}"
                f"^{termino['exponente']}"
            )

        suma_texto = " + ".join(terminos_texto)

        contribuciones_texto = " + ".join(
            str(termino["contribucion"]) for termino in pasos
        )

        lineas.append(f"{suma_texto}")
        lineas.append(f"= {contribuciones_texto}")

    lineas.append(f"\nResultado: {resultado['resultado']}")

    return "\n".join(lineas)
