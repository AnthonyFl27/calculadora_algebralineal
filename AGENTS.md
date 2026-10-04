# AGENTS.md

## Contexto del proyecto

Este proyecto es una **calculadora de álgebra lineal** desarrollada para una clase de la materia, cuyo objetivo es resolver sistemas de ecuaciones lineales (matrices aumentadas) aplicando distintos métodos de resolución.

El programa está escrito en **Python** y tiene **dos interfaces** que comparten exactamente la misma lógica matemática (`src/metodos/`):

- **Interfaz de escritorio (Tkinter)**: se lanza con `python src/main.py`. Muestra un panel principal con una barra lateral (sidebar) desde la cual el usuario elige el método u operación que desea usar.
- **Interfaz web (HTML)**: se lanza con `python server.py` y se abre `http://127.0.0.1:8000` en el navegador. Ofrece el mismo tipo de flujo con una vista visual más cuidada (tablas por paso, pivote resaltado, comprobación).

La web es **adaptable a móviles** (spec `008`): desde 320 px, en vertical y horizontal, sin scroll horizontal de la página. Con ancho ≤ 768 px el sidebar pasa a un drawer superpuesto con barra superior (hamburguesa), las matrices y tablas anchas hacen scroll dentro de su contenedor y los controles son táctiles (campos de 16 px, objetivos ≥ 44 px). En escritorio no cambia. La GUI de Tkinter no se adapta (no es un contexto móvil).

Ambas interfaces abren en un **menú de Inicio** con una tarjeta por módulo y tienen **modo claro y oscuro** con un botón en la parte inferior del sidebar (la web recuerda la elección en `localStorage` y sigue el tema del sistema por defecto; la GUI arranca en claro). Los colores viven en un solo lugar por interfaz: `PALETAS` en `src/main.py` y las variables CSS de `src/web/index.html`. No hay que escribir colores sueltos.

Actualmente la calculadora incluye: resolución de sistemas (**Gauss-Jordan** y **Pivoteo**, que es Gauss-Jordan con pivoteo parcial), **conversión** entre bases numéricas, **operaciones con vectores** (suma, resta, escalar, combinación lineal), **operaciones con matrices** (suma, resta, escalar, multiplicación A × B), **ecuación matricial** y **matriz inversa** (Gauss-Jordan o Pivoteo sobre `[A | I]`). Todas las vistas con resultado tienen un **botón de exportar** (ícono de descarga, arriba a la derecha) para **exportar la respuesta a PNG o PDF** (con opción de incluir los pasos). Además incluye una sección de **ejercicios para práctica**: el usuario elige un método, ve una lista de ejercicios de ejemplo y con "Probar ejercicio" los datos se cargan en la calculadora (sin resolver).

## Estructura de carpetas

Fuera de `src/` solo quedan `AGENTS.md`, `sdd/` (contexto y forma de trabajo de la IA) y `server.py`. Todo el código fuente vive en `src/`. Comandos, siempre **desde la raíz del proyecto**: `python server.py`, `python src/main.py`, `python -m unittest discover -s src/tests -t src` y `python -m unittest discover -s src/features/tests -t src`.

## Regla fundamental impuesta por el profesor

**No está permitido usar librerías matemáticas externas** como NumPy, SciPy o SymPy. Toda la lógica de resolución de matrices (eliminación, pivoteo, manejo de fracciones, verificación de resultados, etc.) debe implementarse manualmente utilizando únicamente la librería estándar de Python. Esta restricción es intencional: el objetivo del profesor es que el proceso algebraico se programe "a mano", sin apoyarse en paquetes que ya resuelven el problema internamente.

Además de esta restricción, se busca que la calculadora sea **funcional, fácil de usar e intuitiva**, priorizando una experiencia clara para quien la use, más allá de solo cumplir con el cálculo matemático correcto.

## Qué se busca con este proyecto

- Ofrecer una herramienta visual e interactiva para resolver sistemas de ecuaciones lineales paso a paso.
- Permitir comparar distintos métodos de resolución sobre la misma matriz.
- Mostrar no solo el resultado final, sino también el procedimiento (pasos intermedios) y una comprobación del resultado obtenido.
- Mantener el código libre de librerías matemáticas externas, respetando la restricción académica impuesta.
- Mejorar de manera incremental lo que ya existe, sin reescribir el proyecto desde cero.

## Estructura general del proyecto

- **`src/main.py`** (antes `gui.py`): interfaz gráfica de escritorio (Tkinter). Aquí el usuario elige el método desde la barra lateral, captura los datos y visualiza resultados y pasos. No contiene lógica matemática propia, solo se encarga de la presentación.
- **`server.py`** (en la **raíz**, a propósito: los técnicos lo ejecutan con `python server.py` sin entrar a `src/`; agrega `src/` a `sys.path`): servidor HTTP local (solo librería estándar: `http.server`, `json`). Expone la lógica de `metodos/` como endpoints JSON y además sirve `src/web/index.html`. Tampoco contiene lógica matemática propia: recibe los datos del formulario web, llama a las mismas funciones que usa `src/main.py` y responde con el resultado y los pasos ya formateados. Escucha en `127.0.0.1:8000`.
  - Sirve la página (`GET /`), `GET /api/estado`, `GET /api/ejercicios` (catálogo de práctica), los `POST /api/...` de cada módulo y `POST /api/exportar` (recalcula con `metodos/` y devuelve el PNG/PDF como archivo adjunto), que devuelven `{"ok": true, ...}` o `{"error": "..."}` con código 400. Los datos ya formateados ("bloques") los arman `_armar_bloque_*`. La consola muestra cada petición.
- **`src/web/index.html`**: interfaz web de una sola página (HTML, CSS y JavaScript en el mismo archivo, sin librerías externas). Tiene su propia barra lateral y usa `fetch()` para llamar a los endpoints de `server.py`. **No funciona abierto con doble clic**: necesita que `server.py` esté corriendo. Solo presenta datos; nunca calcula.
- **`src/metodos/`**: carpeta donde vive toda la lógica matemática del proyecto, separada de las interfaces. Contiene:
  - `gauss_jordan.py`: método de **Gauss-Jordan**.
  - `pivote.py`: método de **Pivoteo**.
  - `conversion.py`: conversión entre bases numéricas.
  - `vectores_matrices.py`: operaciones con vectores y matrices, combinación lineal, ecuación matricial y matriz inversa.
  - `ejercicios.py`: catálogo de ejercicios de práctica (solo datos y su vista previa; lo leen `src/main.py` directamente y `server.py` por `GET /api/ejercicios`).
  - `general_metodos.py`: **utilidades generales** compartidas (fracciones y decimales, formateo de resultados y verificación de soluciones).
- **`src/features/`**: funcionalidades generales que **no son métodos matemáticos** (por ahora `exportar.py`: exportar respuestas a PNG/PDF, escrito a mano con la librería estándar, y su fuente bitmap, generada con `src/features/tools/generar_fuente.py`; sus pruebas están en `src/features/tests/`, se corren desde la raíz con `python -m unittest discover -s src/features/tests -t src`; ahí también está `prueba_web_movil.js`, un script opcional de Playwright que revisa la vista móvil de la web, ver su cabecera). `src/metodos/` es exclusivamente para métodos y operaciones matemáticas; lo demás va aquí.
- **`src/tests/`**: pruebas de `vectores_matrices`, del catálogo de ejercicios, del contraste de colores (4.5:1 en ambos temas) y de las vistas de `main.py` (vectores y matrices, inicio y ejercicios). Se corren desde la raíz con `python -m unittest discover -s src/tests -t src` (los tests importan la GUI como `main`).
- **`sdd/`**: documentación de Spec-Driven Development. `plan.md` (metodología), `task.md` (tareas y avance) y `specs/`, organizado por versión: `specs/v1/` contiene las specs ya implementadas y `specs/v2/` es para las specs nuevas (la última es la `008`, web adaptable a móviles).

## Regla de sincronía entre interfaces

Toda lógica nueva va en `src/metodos/`. Toda funcionalidad nueva o modificada se refleja en las dos interfaces (`src/main.py` y `server.py` + `src/web/index.html`), sin duplicar cálculos.

## Regla para cambios visuales en la web

`src/web/index.html` es una sola página para móvil y escritorio: lo móvil son reglas `@media` (≤ 768, ≤ 480 y ≤ 380 px), no otra versión. Los colores por variables CSS y el contenido nuevo valen para ambos sin trabajo extra. Pero todo cambio visual (elementos anchos, tamaños fijos, filas con varios controles) debe revisarse a 320 px y 375 px: sin scroll horizontal de la página, tablas y matrices anchas en un contenedor con scroll interno, controles táctiles ≥ 44 px y campos de 16 px. No agregar colores sueltos; usar las variables.

## Cómo agregar módulos o métodos nuevos

Se sigue la metodología y el checklist de `sdd/plan.md` (spec, lógica, impresión en ambas interfaces, consola del servidor, ejercicios de práctica, temas y documentación).
