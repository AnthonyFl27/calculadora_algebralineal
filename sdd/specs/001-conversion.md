Estado: implementado

# 001 — Conversión de bases numéricas

**Archivo destino:** `metodos/conversion.py`

## Propósito

Convertir números entre las bases decimal, binaria, octal y hexadecimal,
mostrando en el procedimiento la combinación lineal (suma de potencias de la
base) que da origen a cada número, no solo el resultado.

(Convenciones generales de implementación e integración con la GUI: ver
`sdd/plan.md`.)

## Funcionalidad 1 — Decimal → (Binario / Octal / Hexadecimal)

- El usuario ingresa un número decimal (entero; puede incluir signo).
- El usuario selecciona a qué base quiere convertirlo: binaria, octal o
  hexadecimal (una a la vez, no las tres al mismo tiempo).
- El procedimiento muestra el proceso de conversión (divisiones sucesivas
  entre la base y los residuos obtenidos, en orden) y el número resultante en
  la base elegida.

## Funcionalidad 2 — (Binario / Octal / Decimal) → Decimal

- El usuario ingresa un número y selecciona la base en la que está escrito
  ese número (binario, octal o decimal).
- El programa valida que los dígitos ingresados sean válidos para la base
  elegida (por ejemplo, rechazar un "2" si la base seleccionada es binaria).
- El procedimiento debe mostrar explícitamente la **combinación lineal** que
  genera el número decimal, es decir, cada dígito multiplicado por la
  potencia de la base que le corresponde, sumado todo. Ejemplo conceptual
  para 101₂: `1×2² + 0×2¹ + 1×2⁰ = 4 + 0 + 1 = 5`.
- El resultado final es el número equivalente en decimal.

## Notas de diseño

- Los cuatro casos de "decimal → otra base" y los tres casos de "otra base →
  decimal" pueden convivir en una sola vista con selector de "dirección" y
  selector de "base", para no multiplicar pantallas innecesariamente; queda a
  criterio de implementación mientras el usuario pueda elegir claramente base
  y dirección de la conversión.
- Se debe soportar números negativos al menos para el caso decimal de
  entrada/salida (signo-magnitud es suficiente, no se pide complemento a 2).
- No hay número de dígitos fijo: el módulo debe funcionar para cualquier
  cantidad de dígitos que el usuario ingrese.

## Cambios posteriores

### Habilitar hexadecimal → decimal en la interfaz (GUI y web)

`metodos/conversion.py` (`base_a_decimal()` / `resolver()`) ya soportaba
hexadecimal como base de entrada desde la implementación original: es
genérico sobre cualquier base definida en `NOMBRES_BASE` (2, 8, 10, 16), sin
necesitar ningún cambio de lógica. El bug estaba solo en las interfaces, que
restringían manualmente las opciones del selector de base cuando la
dirección era "otra base → decimal":

- `gui.py` (`VistaConversion.BASES_A_DECIMAL`) listaba
  `["binario", "octal", "decimal"]`, sin `"hexadecimal"`.
- `index.html` (`vistaConversion()`, constante `BASES_A_DECIMAL`) tenía la
  misma lista incompleta, duplicada en JavaScript.

Se agregó `"hexadecimal"` a ambas listas. Con esto, la dirección
"Otra base → Decimal" ahora ofrece binario, octal, hexadecimal y decimal por
igual, tanto en la GUI de Tkinter como en la versión web, reutilizando el
mismo `resolver()` y el mismo endpoint `/api/conversion` de `server.py` (que
tampoco tenía restricción propia: recibe `base_entrada`/`base_salida` como
enteros y delega directo en `metodos/conversion.py`). Verificado con
`curl -X POST /api/conversion` (`"2F"` en base 16 → `47` en decimal) y
revisando el árbol de sintaxis de `gui.py`/`server.py`.
