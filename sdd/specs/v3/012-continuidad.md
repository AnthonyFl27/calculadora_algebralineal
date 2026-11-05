Estado: implementado

# Spec 012 — Revisión de continuidad en la bisección

La bisección solo garantiza una raíz si f es **continua** en [a, b] (Teorema del
Valor Intermedio). Hasta la spec 011 la calculadora solo lo notaba *después* de
iterar (|f(raíz)| grande). Esta spec agrega una **revisión previa** del
intervalo y la muestra en la vista y en los archivos exportados. Cumple las
"Reglas permanentes" de `sdd/specs/v2/spec_v2.md`.

## Alcance y honestidad

Con números **no se puede demostrar** que una función sea continua. La revisión
es **heurística**: muestrea el intervalo y busca señales. Un salto más angosto
que el paso de muestreo puede pasar inadvertido y una función muy picuda puede
dar un falso aviso. Por eso la interfaz nunca dice "f es continua"; dice "no se
detectaron señales de discontinuidad" y recuerda que es una revisión numérica.

## Requisitos

- Módulo nuevo `src/metodos/continuidad.py` con `revisar_continuidad(f, a, b)`,
  reutilizable por los siguientes métodos de raíces. Solo librería estándar.
- Se evalúa f en 401 puntos equidistantes de [a, b] (400 subintervalos) y se
  buscan tres señales:
  1. **No definida:** puntos donde f no se puede evaluar (división entre cero,
     dominio, desbordamiento). El tramo se acota con una bisección
     (`sqrt(x^2-1)` en [−2, 2] → tramo [−1, 1]). Un punto con división entre
     cero se informa como polo.
  2. **Cambio de signo que no es una raíz:** entre dos muestras de signo
     distinto se parte el subintervalo (hasta agotar la precisión). Si |f| se
     acerca a 0 (≤ 1 % de la escala) es una raíz de verdad; si no, es un
     **polo** (|f| crece más de 10 veces: 1/x, tan x) o un **salto** (|x|/x).
  3. **Polo sin cambio de signo** (1/x², 1/(x−1)²): un máximo local de |f| se
     refina con una búsqueda ternaria; si crece más de 50 veces respecto de la
     muestra, hay una asíntota vertical.
- Una misma discontinuidad que detectan varias reglas se informa **una vez**
  (se fusionan las cercanas a 2 pasos de muestreo). Se detallan hasta 5; el
  total se informa aparte ("… y N más").
- Las ubicaciones se redactan con 6 cifras y el ruido numérico respecto de la
  escala del intervalo se muestra como `0` (no `−2.3e-19`).
- `evaluador.Funcion.evaluar_seguro(x)` devuelve `(valor, None)` o
  `(None, motivo)` sin lanzar errores; `__call__` lo reutiliza.
- **No bloquea el cálculo:** si hay señales, la bisección corre igual y se
  agrega una advertencia (la primera de la lista). Las sospechas no son error.
- `biseccion()` devuelve además `continuidad` (`muestras`, `sospechas`, `total`,
  `sin_senales`) y `comprobacion` pasa a tener `cerca_de_cero` (el criterio
  posterior de la spec 011) y `discontinuidad` (= señales previas **o** f(raíz)
  no cercano a 0). `correcto` sigue exigiendo `not discontinuidad`.

## Integración

- Web: tarjeta **Continuidad** justo después del planteamiento (verde ✓ sin
  señales, ámbar ! con las sospechas) y la comprobación separa "f(raíz) es
  cercano a 0" y "Sin señales de discontinuidad en [a, b]".
- Exportar PNG/PDF: `procedimiento_texto()` incluye el bloque
  (`continuidad_texto()`); la versión "sin pasos" también lo trae
  (sección **Continuidad**).
- Servidor: el bloque de `POST /api/biseccion` trae `continuidad`; la consola
  muestra "continuidad: sin señales / N sospecha(s)".
- Ejercicios: `bis-09` (polo de tan x) y `bis-10` (salto |x|/x); el catálogo
  admite `continuidad` en `resultado_esperado`.
- Pruebas: `src/tests/test_continuidad.py` (15 funciones continuas sin falsos
  avisos; polos, saltos y dominio), `test_biseccion.py`, `test_ejercicios.py`,
  `src/features/tests/test_exportar.py` y `test_server_exportar.py`.

## Decisiones tomadas al implementar

- Los mensajes evitan `«»` porque no están en la fuente bitmap del exportador.
- El aviso posterior de la spec 011 (|f(raíz)| no cercano a 0) se conserva; el
  nuevo aviso previo va primero.
- No se hizo el análisis sobre el árbol de la expresión (detectar denominadores
  que se anulan): queda como mejora posible, el muestreo ya cubre los casos
  comunes.
- Pendiente del usuario: visto bueno visual (claro/oscuro y móvil).
