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
