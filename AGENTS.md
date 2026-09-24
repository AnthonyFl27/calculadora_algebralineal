# AGENTS.md

## Contexto del proyecto

Este proyecto es una **calculadora de álgebra lineal** desarrollada para una clase de la materia, cuyo objetivo es resolver sistemas de ecuaciones lineales (matrices aumentadas) aplicando distintos métodos de resolución. Originalmente se implementaron dos métodos: **Gauss-Jordan** y **Pivoteo** (Gauss-Jordan con pivoteo parcial); después se añadieron los demás módulos.

El programa está escrito en **Python** y tiene **dos interfaces** que comparten exactamente la misma lógica matemática (`metodos/`):

- **Interfaz de escritorio (Tkinter)**: se lanza con `python gui.py`. Muestra un panel principal con una barra lateral (sidebar) desde la cual el usuario elige el método u operación que desea usar.
- **Interfaz web (HTML)**: se lanza con `python server.py` y se abre `http://127.0.0.1:8000` en el navegador. Ofrece el mismo tipo de flujo con una vista visual más cuidada (tablas por paso, pivote resaltado, comprobación).

Actualmente la calculadora incluye: resolución de sistemas (**Gauss-Jordan** y **Pivoteo**, o Gauss-Jordan con pivoteo parcial), **conversión** entre bases numéricas, **operaciones con vectores** (suma, resta, escalar, combinación lineal), **operaciones con matrices** (suma, resta, escalar, multiplicación A × B) y **ecuación matricial**.

## Regla fundamental impuesta por el profesor

**No está permitido usar librerías matemáticas externas** como NumPy, SciPy o SymPy. Toda la lógica de resolución de matrices (eliminación, pivoteo, manejo de fracciones, verificación de resultados, etc.) debe implementarse manualmente utilizando únicamente la librería estándar de Python. Esta restricción es intencional: el objetivo del profesor es que el proceso algebraico se programe "a mano", sin apoyarse en paquetes que ya resuelven el problema internamente.

Además de esta restricción, se busca que la calculadora sea **funcional, fácil de usar e intuitiva**, priorizando una experiencia clara para quien la use, más allá de solo cumplir con el cálculo matemático correcto.

## Qué se busca con este proyecto

- Ofrecer una herramienta visual e interactiva para resolver sistemas de ecuaciones lineales paso a paso.
- Permitir comparar distintos métodos de resolución sobre la misma matriz.
- Mostrar no solo el resultado final, sino también el procedimiento (pasos intermedios) y una comprobación del resultado obtenido.
- Mantener el código libre de librerías matemáticas externas, respetando la restricción académica impuesta.
- Ir mejorando de manera incremental lo que ya existe, en lugar de reescribir el proyecto desde cero: se parte de la base actual y se añaden o ajustan funcionalidades según se necesite.

## Estructura general del proyecto

- **`gui.py`**: interfaz gráfica de escritorio (Tkinter). Aquí el usuario elige el método desde la barra lateral, captura los datos y visualiza resultados y pasos. No contiene lógica matemática propia, solo se encarga de la presentación.
- **`server.py`**: servidor HTTP local (solo librería estándar: `http.server`, `json`). Expone la lógica de `metodos/` como endpoints JSON y además sirve `index.html`. Tampoco contiene lógica matemática propia: recibe los datos del formulario web, llama a las mismas funciones que usa `gui.py` y responde con el resultado y los pasos ya formateados. Escucha en `127.0.0.1:8000`.
  - `GET /` y `/index.html` sirven la página; `GET /api/estado` indica que el servidor está vivo.
  - `POST /api/sistema` (Gauss-Jordan / Pivoteo), `/api/conversion`, `/api/vectores`, `/api/matrices` y `/api/ecuacion-matricial` reciben un JSON y devuelven `{"ok": true, ...}` o `{"error": "..."}` con código 400.
  - Las funciones `_armar_bloque_sistema` y `_armar_bloque_operacion` construyen el "bloque": el diccionario con celdas ya formateadas (fracción o decimal según el `modo`) que el navegador dibuja como tablas.
- **`index.html`**: interfaz web de una sola página (HTML, CSS y JavaScript en el mismo archivo, sin librerías externas). Tiene su propia barra lateral y usa `fetch()` para llamar a los endpoints de `server.py`. **No funciona abierto con doble clic**: necesita que `server.py` esté corriendo. Solo presenta datos; nunca calcula.
- **`metodos/`**: carpeta donde vive toda la lógica matemática del proyecto, separada de las interfaces. Contiene:
  - `gauss_jordan.py`: método de **Gauss-Jordan**.
  - `pivote.py`: método de **Pivoteo**.
  - `conversion.py`: conversión entre bases numéricas.
  - `vectores_matrices.py`: operaciones con vectores y matrices, combinación lineal y ecuación matricial.
  - `general_metodos.py`: **utilidades generales** compartidas (fracciones y decimales, formateo de resultados y verificación de soluciones).
- **`tests/`**: pruebas de `vectores_matrices` y de su vista en `gui.py`.
- **`sdd/`**: documentación de Spec-Driven Development. `plan.md` (metodología), `task.md` (tareas y avance) y `specs/`, organizado por versión: `specs/v1/` contiene las specs ya implementadas y `specs/v2/` es para las specs nuevas.

## Regla de sincronía entre interfaces

Toda lógica nueva va en `metodos/`. Si se añade o cambia una funcionalidad, debe reflejarse en las dos interfaces (`gui.py` y `server.py` + `index.html`) sin duplicar cálculos en ninguna de ellas.

## Enfoque de trabajo

Este proyecto se irá construyendo de manera progresiva: se parte de lo ya implementado (interfaces de escritorio y web funcionales, con sus métodos operativos) y se continuará mejorando, corrigiendo o ampliando según las necesidades de la clase, siempre respetando la restricción de no usar librerías matemáticas externas.
