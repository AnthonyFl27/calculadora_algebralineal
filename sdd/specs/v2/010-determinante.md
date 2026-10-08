Estado: pendiente

# 010 — Determinante de una matriz (cofactores y LU)

**Archivos destino:** `src/metodos/determinante.py` (nuevo), `src/tests/test_determinante.py` (nuevo),
`src/metodos/ejercicios.py`, `server.py`, `src/web/index.html`, `AGENTS.md`, `sdd/plan.md`, `sdd/task.md`.

## Propósito

Enunciado del profesor: *"Escribí el código para encontrar el determinante de
una matriz. Debe permitir seleccionar entre cofactores y LU, indicando, antes
de seleccionar, cuál sería la más eficiente."*

Dada una matriz cuadrada `A` de `n × n`, calcular `det(A)` con el método que
el usuario elija (**cofactores** o **LU**), mostrando el procedimiento paso a
paso y una comprobación. **Antes de que el usuario elija**, la calculadora le
indica cuál de los dos es más eficiente para el tamaño `n` que tiene entre
manos y por qué.

## Métodos

### Cofactores (expansión de Laplace)

`det(A) = Σ_j a_ij · C_ij`, con `C_ij = (−1)^(i+j) · M_ij`, desarrollando
recursivamente sobre una fila o columna hasta llegar a 1×1 (caso base) o 2×2
(`ad − bc`, que se muestra directo).

- El usuario puede **elegir la fila o columna de expansión**; por defecto se
  usa la que tenga **más ceros** (si hay empate, la primera), porque cada cero
  elimina un menor completo. Se indica cuál se eligió y por qué.
- Los términos con `a_ij = 0` se muestran como omitidos, no se calculan.
- Costo: del orden de `n!` multiplicaciones en el peor caso.

### LU (con pivoteo parcial)

Factoriza `P·A = L·U` (Doolittle: `L` triangular inferior con 1 en la
diagonal, `U` triangular superior, `P` de permutación) y calcula
`det(A) = (−1)^s · u₁₁ · u₂₂ · … · uₙₙ`, donde `s` es el número de
intercambios de filas.

- Pivoteo parcial: si el pivote de una columna es 0 se busca una fila
  inferior con elemento distinto de 0 e intercambia (cuenta para `s`). Si no
  hay ninguna, `det(A) = 0` (matriz singular): se registra la columna sin
  pivote como paso `sin_pivote` y se **continúa** con la siguiente columna,
  para que `P·A = L·U` se siga cumpliendo y pueda comprobarse.
- Se muestran las matrices `P`, `L` y `U` finales, los pasos de eliminación
  (multiplicador `l_ik = a_ik / a_kk` y fila afectada) y el producto de la
  diagonal de `U` con el signo.
- Costo: del orden de `n³/3` multiplicaciones.
- Aritmética exacta con `Fraction` (sin errores de redondeo), como el resto
  del proyecto. **No se usa ninguna librería externa.**

## Recomendación de eficiencia (antes de elegir)

Al indicar `n` (y antes de pulsar calcular) la vista muestra un recuadro
**"¿Cuál conviene?"** con el conteo aproximado de multiplicaciones de cada
método y una recomendación:

| n | Cofactores (≈ n!) | LU (≈ n³/3) | Recomendado |
|---|-------------------|-------------|-------------|
| 1–2 | trivial | trivial | Cofactores (fórmula directa, nada que factorizar) |
| 3 | ~6–9 | ~9 | Cofactores (o LU, prácticamente igual) |
| ≥ 4 | crece factorialmente (24, 120, 720…) | crece cúbicamente (21, 42, 72…) | **LU** |

- La recomendación **depende solo de `n`** (no de los valores), con una
  excepción informativa: si se indica la matriz y tiene una fila/columna con
  casi todo ceros, se menciona que cofactores mejora en ese caso.
- La lógica que genera la recomendación vive en `metodos/determinante.py`
  (función `recomendar_metodo(n)`) y devuelve los conteos y un texto en
  español; la web **solo muestra** ese resultado (pide al servidor, no calcula).
- El usuario puede elegir **cualquiera de los dos** igualmente; la
  recomendación es una guía, no una restricción. El método recomendado se
  marca con una etiqueta ("Recomendado") en el selector.
- Tras calcular, el resultado muestra cuántas multiplicaciones hizo
  realmente el método elegido (contador real), para comparar con la
  estimación.

## Requisitos funcionales

- **Validación previa:** `A` cuadrada y no vacía; si no, error amigable sin
  operar (mismo estilo que la inversa). Celdas con enteros, decimales y
  fracciones (`3/4`), vía `parsear_numero`.
- **Tamaño:** `n` lo indica el usuario antes de capturar `A`. Máximo **`n = 8`**
  para LU; para cofactores el máximo es **`n = 6`** (más allá el
  procedimiento paso a paso es inmanejable: 720+ términos); si el usuario
  elige cofactores con `n > 6` se le informa con un mensaje amigable y se le
  sugiere LU.
- **Procedimiento paso a paso** en ambos métodos (en la web: stepper, como
  los sistemas y la inversa).
- **Resultado destacado:** `det(A)` en tarjeta (verde); si es 0, tarjeta
  ámbar "A es singular (no tiene inversa)". Esto conecta con el módulo de
  matriz inversa sin tocarlo.
- **Comprobación:** se recalcula el determinante con **el otro método** y se
  verifica que coincidan (para `n > 6` en que cofactores no aplica, se
  comprueba que `det(P)·det(A) = det(L)·det(U)`, es decir, que
  `P·A = L·U` se cumple multiplicando las matrices).
- Formato **fracción / decimal** respetado en toda la salida.
- **Exportar** a PNG/PDF como las demás vistas con resultado.

## Estructura de resultado (`metodos/determinante.py`)

Funciones públicas:

- `recomendar_metodo(n)` → `{"n", "cofactores": {"operaciones", "texto"}, "lu": {...}, "recomendado": "cofactores"|"lu", "motivo"}`.
- `determinante(matriz, metodo="lu", modo="fraccion", **opciones)` →
  diccionario estándar con: `operacion` (`"determinante"`), `metodo`,
  `entradas` (`matriz`, y `expansion` si aplica), `pasos` (lista de diccionarios
  con `tipo` y datos ya listos para presentar), `resultado` (`Fraction`),
  `singular` (bool), `multiplicaciones` (contador real), `recomendacion`
  (la de `recomendar_metodo`) y `comprobacion`
  (`{"metodo", "valor", "correcto"}`).
- Para LU además: `P`, `L`, `U`, `intercambios`. Para cofactores además:
  `expansion` (`{"tipo": "fila"|"columna", "indice"}`).
- Errores controlados con `ValueError` en español (método desconocido, no
  cuadrada, `n` excedido, fila/columna fuera de rango).

## Reutilización y decisiones de diseño

- Archivo nuevo `metodos/determinante.py`, **no** dentro de
  `vectores_matrices.py`: es un módulo con dos algoritmos propios y una
  recomendación; el módulo existente ya es grande. Reutiliza
  `parsear_numero`/`_matriz` de `vectores_matrices.py` (o los expone) y
  `formatear` de `general_metodos.py`.
- Entrada **nueva en el sidebar y en Inicio** ("Determinante"), no una
  pestaña de "Vectores y Matrices": el enunciado lo pide como método con
  selección propia y la lista de ejercicios del profesor lo trata aparte.
- Endpoints: `POST /api/determinante` (calcula) y `POST /api/determinante/recomendar`
  (solo recomendación según `n`; el cliente nunca calcula).
- Alternativas descartadas: Sarrus (solo 3×3, no cumple el enunciado);
  determinante vía Gauss-Jordan (ya existe el motor, pero el profesor pide
  explícitamente LU y cofactores).
- Fuera de alcance: método de la adjunta / `A⁻¹ = adj(A)/det(A)`, regla de
  Cramer, matrices no cuadradas, descomposición LU sin pivoteo como opción.

## Checklist (ver `sdd/plan.md`)

1. **Lógica:** `metodos/determinante.py` + `src/tests/test_determinante.py`
   (1×1, 2×2, 3×3, 4×4 con ceros, singular, con intercambio de filas,
   fracciones y decimales, no cuadrada, vacía, `n` excedido, ambos métodos
   coinciden en una batería de matrices, `P·A = L·U`, recomendación por `n`,
   contador de multiplicaciones LU < cofactores para `n ≥ 5`).
2. **Impresión:** `_armar_bloque_*` nuevo para determinante en `server.py`;
   vista con selector de método + recuadro de recomendación, stepper por paso,
   tarjeta de resultado y de comprobación, modo fracción/decimal.
3. **Consola del servidor:** rutas en `DESTINO`, `_descripcion_peticion()` y
   banner de arranque; `CALCULOS["determinante"]` para `/api/exportar`.
4. **Navegación y diseño:** entrada en `METODOS` (clave `determinante`, ícono
   nuevo en `ICONOS`), tarjeta de Inicio, temas claro/oscuro (4.5:1),
   revisión a 320 y 375 px sin scroll horizontal (matrices `P`, `L`, `U` y
   tablas anchas en contenedor con scroll interno, controles ≥ 44 px, campos
   de 16 px, solo variables CSS). Correr `prueba_web_movil.js`.
5. **Ejercicios de práctica:** método `determinante` en `METODOS_EJERCICIOS`
   y al menos 6 ejercicios en `EJERCICIOS` (2×2 básico, 3×3, 3×3 singular,
   4×4 con muchos ceros —donde cofactores gana—, 4×4 que exige intercambio de
   filas en LU, 4×4 con fracciones), con `vista_previa()` y carga sin
   resolver; extender `test_ejercicios.py`.
6. **Documentación:** al cerrar, spec en `implementado`, fila en `sdd/plan.md`,
   bloque borrado de `task.md` y `AGENTS.md` actualizado (funcionalidades,
   archivos, endpoints, pruebas).

## Criterios de aceptación

- Para `n = 4` la vista recomienda LU **antes** de que el usuario elija y lo
  marca en el selector; para `n = 2` recomienda cofactores.
- Ambos métodos devuelven el mismo `det(A)` en toda la batería de pruebas.
- Una matriz singular da `det = 0` con ambos métodos y la tarjeta ámbar.
- Cofactores con `n > 6` muestra un mensaje amigable, no un traceback.
- Las suites `src/tests` y `src/features/tests` pasan en verde.
