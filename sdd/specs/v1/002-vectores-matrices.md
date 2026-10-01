Estado: implementado

# 002 — Operaciones vectoriales y matriciales

**Archivo destino:** `metodos/vectores_matrices.py`

## Propósito

Cubrir operaciones básicas con vectores en ℝⁿ y con matrices, incluyendo la
verificación de combinación lineal y la resolución de ecuaciones matriciales
simples apoyándose en los métodos de resolución de sistemas ya construidos
(Gauss-Jordan / Pivoteo).

(Convenciones generales de implementación e integración con la GUI: ver
`sdd/plan.md`.)

## 2.1 — Vectores en ℝⁿ

- **Suma y resta de vectores.** El usuario define dos (o más) vectores de la
  misma dimensión `n` y el programa calcula la suma o la resta, mostrando la
  operación componente por componente.
- **Multiplicación de un vector por un escalar.** El usuario da un escalar y
  un vector; el programa muestra cada componente multiplicada por el
  escalar.
- **Combinación lineal.** El usuario da un conjunto de vectores
  `v₁, v₂, ..., vₖ` y un vector objetivo `v`. El programa determina si `v` es
  combinación lineal de ese conjunto, es decir, si existen escalares
  `c₁, ..., cₖ` tales que `c₁v₁ + c₂v₂ + ... + cₖvₖ = v`. Debe mostrarse el
  planteamiento del sistema de ecuaciones resultante y su resolución
  (reutilizando el motor de sistemas lineales ya existente), concluyendo si
  existe o no dicha combinación y, si existe, con qué escalares.
- La dimensión `n` de los vectores **no está fija de antemano**: la interfaz
  debe permitir que el usuario indique cuántas componentes tiene cada vector
  antes de capturarlo (igual que ya se hace con "Ecuaciones" y "Variables" en
  la vista de sistemas lineales).

## 2.2 — Operaciones matriciales básicas

- **Suma y resta de matrices**, validando primero que ambas matrices tengan
  exactamente las mismas dimensiones (filas × columnas); si no coinciden, se
  informa el error sin intentar operar.
- **Multiplicación de una matriz por un escalar.**
- **Multiplicación de matrices A × B**, validando primero que el número de
  columnas de `A` sea igual al número de filas de `B`; si no se cumple, se
  informa el error sin intentar operar.
- Todas estas operaciones deben mostrar el procedimiento (no solo el
  resultado final), consistente con el resto de la calculadora.

## 2.3 — Ecuaciones matriciales

- Evaluación y resolución computacional de sistemas planteados como ecuación
  matricial `A·X = B`.
- **Debe reutilizar el motor de resolución de sistemas ya construido**
  (Gauss-Jordan y/o Pivoteo de `metodos/gauss_jordan.py` /
  `metodos/pivote.py`), en vez de reimplementar la resolución desde cero.
  Este submódulo se apoya en el trabajo previo del proyecto, armando la
  matriz aumentada `[A | B]` a partir de la ecuación matricial y delegando la
  resolución al método ya existente.

## Notas de diseño

- Vectores y matrices comparten módulo porque conceptualmente son la misma
  familia de operaciones ("álgebra de matrices/vectores"), pero en la GUI
  pueden separarse en pestañas o sub-vistas dentro de la misma entrada del
  sidebar (por ejemplo "Vectores y Matrices"), o bien como entradas separadas
  del sidebar si mejora la claridad — se decide al momento de construir la
  vista, priorizando que el usuario nunca se sienta perdido.

## Cambios posteriores

### 2.4 — Matriz inversa

**Estado:** implementado.

#### Propósito

Dada una matriz cuadrada `A` de `n × n`, encontrar su inversa `A⁻¹` (tal que
`A·A⁻¹ = A⁻¹·A = I`) **si existe**, y si no existe, decirlo y explicar por
qué. Caso de referencia (práctica 2.2, problema 1: "encontrar la inversa de
la matriz, si existe"):

```
A = |  1  -2  -1 |
    | -1   5   6 |
    |  5  -4   5 |
```

Esta matriz en particular **no es invertible** (su determinante es 0: al
reducir, `F3 − 5·F1 = 2·(F2 + F1)`), así que el programa debe concluir
"la inversa no existe" mostrando el procedimiento que lo demuestra. Sirve
como caso de prueba principal del módulo.

#### Método

Gauss-Jordan sobre la matriz ampliada `[A | I]` (`I` = identidad `n × n`),
hasta llegar a `[I | A⁻¹]`. Se puede elegir entre **Gauss-Jordan** y
**Pivoteo** (igual que en la vista de sistemas), con Gauss-Jordan por
defecto.

- Si el bloque izquierdo llega a `I`, el bloque derecho es `A⁻¹`.
- Si en algún momento no se encuentra pivote en una columna (queda una fila
  con ceros en el bloque izquierdo), `A` es singular: **la inversa no
  existe**. Se informa cuál fila quedó en ceros.

#### Requisitos funcionales

- **Validación previa:** `A` debe ser cuadrada y no vacía; si no lo es, se
  informa el error sin intentar operar (mismo estilo que suma/multiplicación
  de matrices). Las celdas aceptan enteros, decimales y fracciones (`3/4`),
  como en el resto del módulo.
- La dimensión `n` no está fija: el usuario la indica antes de capturar `A`
  (igual que en las demás sub-vistas).
- **Procedimiento paso a paso** (intercambio, normalizar, eliminar) sobre la
  matriz ampliada `[A | I]`, con la misma presentación que los sistemas
  lineales (en la web: stepper con pivote resaltado; en la GUI: texto).
- **Resultado destacado:** o bien `A⁻¹` completa, o bien la conclusión "A no
  es invertible (matriz singular)" con su motivo.
- **Comprobación por ambos lados** cuando existe: mostrar `A · A⁻¹` y
  `A⁻¹ · A` y verificar que ambos dan `I`
  (reutilizando la multiplicación de matrices ya implementada).
- Formato de salida fracción/decimal según el `modo` ya existente.

#### Reutilización y decisiones de diseño

- **Es posible con el motor actual, con un ajuste mínimo.** Hoy
  `gauss_jordan()` y `gauss_jordan_pivoteo()` asumen que solo la **última**
  columna es el término independiente (`variables = columnas - 1`), por lo
  que no reducen `[A | I]` completa como bloque de `n` columnas.
  Se agrega un parámetro opcional `columnas_variables=None` a ambas
  funciones (por defecto se comporta exactamente igual que hoy); para la
  inversa se llama con `columnas_variables=n`. Así se reutiliza el mismo
  algoritmo y las mismas tuplas de pasos (`intercambio`, `normalizar`,
  `eliminar`), sin copiar código ni tocar el comportamiento de los sistemas
  existentes.
- Alternativa descartada: `ecuacion_matricial(A, I)` (resolver `A·X = I`
  columna por columna). Funciona sin tocar el motor, pero muestra `n`
  resoluciones separadas en vez de una sola reducción `[A | I] → [I | A⁻¹]`,
  que es como se enseña y se pide en clase.
- La nueva lógica vive en `metodos/vectores_matrices.py` (función
  `matriz_inversa(matriz, metodo="gauss_jordan", modo="fraccion")`), con la
  estructura de resultado estándar del módulo: `operacion`, `entradas`,
  `matriz_aumentada`, `pasos`, `existe`, `motivo`, `resultado` (`A⁻¹` o
  `None`) y `comprobacion`.
- **Interfaces:** nueva sub-vista/pestaña "Matriz inversa" dentro de la
  entrada "Vectores y Matrices" (no una entrada nueva del sidebar, porque es
  la misma familia de operaciones). En web: endpoint `POST /api/inversa` en
  `server.py`, reusando `_armar_bloque_sistema()` para los pasos.
- Fuera de alcance: cálculo de determinante o método de la adjunta (no se
  pidió; el criterio de existencia es el rango por pivotes).

#### Pruebas

Los casos (matriz de la imagen, 2×2, con intercambio de filas, 1×1, con
fracciones, no cuadrada y con fila de ceros, con ambos métodos) están en
`tests/test_vectores_matrices.py`.
