# AGENTS.md

## Contexto del proyecto

Este proyecto es una **calculadora de álgebra lineal** desarrollada para una clase de la materia, cuyo objetivo es resolver sistemas de ecuaciones lineales (matrices aumentadas) aplicando distintos métodos de resolución.

El programa está escrito en **Python** y tiene una **interfaz web** (la GUI de escritorio con Tkinter se eliminó en la spec `009` y ya no se desarrolla). Toda la lógica matemática vive en `src/metodos/`:

- **Interfaz web (HTML)**: se lanza con `python server.py` y se abre `http://127.0.0.1:8000` en el navegador. Muestra un panel principal con una barra lateral (sidebar) desde la cual el usuario elige el método u operación, con una vista visual cuidada (tablas por paso, pivote resaltado, comprobación).

La web es **adaptable a móviles** (spec `008`): desde 320 px, en vertical y horizontal, sin scroll horizontal de la página. Con ancho ≤ 768 px el sidebar pasa a un drawer superpuesto con barra superior (hamburguesa), las matrices y tablas anchas hacen scroll dentro de su contenedor y los controles son táctiles (campos de 16 px, objetivos ≥ 44 px). En escritorio no cambia.

La web abre en un **menú de Inicio** con una tarjeta por módulo y tiene **modo claro y oscuro** con un botón en la parte inferior del sidebar (recuerda la elección en `localStorage` y sigue el tema del sistema por defecto). Los colores viven en un solo lugar: las variables CSS de `src/web/index.html`. No hay que escribir colores sueltos.

Actualmente la calculadora incluye: resolución de sistemas (**Gauss-Jordan** y **Pivoteo**, que es Gauss-Jordan con pivoteo parcial), **conversión** entre bases numéricas, **operaciones con vectores** (suma, resta, escalar, combinación lineal), **operaciones con matrices** (suma, resta, escalar, multiplicación A × B), **ecuación matricial**, **matriz inversa** (Gauss-Jordan o Pivoteo sobre `[A | I]`) y **determinante** (por **cofactores** o **LU** con pivoteo parcial; antes de elegir, la vista indica cuál es más eficiente según `n`, y la comprobación vuelve a multiplicar `L·U` y lo compara con `P·A`) y, además, el **método de bisección** (búsqueda de raíces de f(x) = 0: la función se escribe como texto —con un teclado en pantalla plegable para quien no tenga esos símbolos—, se evalúa con un analizador propio sin `eval()`, y se muestran tabla de iteraciones, error relativo ε_a, comprobación y aviso de discontinuidades; el criterio de paro compara ε_a **como fracción** con E, así E = 0.0001 da las 13 iteraciones del caso del profesor; además hace una **revisión de continuidad** previa que muestrea el intervalo y avisa de polos, saltos o puntos fuera del dominio, sin bloquear el cálculo: es heurística, no una demostración; y una **gráfica de f(x)** con los puntos de cada iteración, un deslizador para recorrerlas y la discontinuidad marcada, también incluida en el PNG/PDF exportado). Todas las vistas con resultado tienen un **botón de exportar** (ícono de descarga, arriba a la derecha) para **exportar la respuesta a PNG o PDF** (con opción de incluir los pasos). Los módulos con interpretación geométrica tienen una **gráfica desplegable** (oculta por defecto, SVG propio con mover y zoom; en 3D, rotar): rectas o planos de los sistemas (Gauss-Jordan, Pivoteo, ecuación matricial), flechas de los vectores, paralelogramo/paralelepípedo del determinante y efecto sobre el cuadrado/cubo unitario de la inversa y de A × B; solo con 2 o 3 dimensiones (con más, la vista lo avisa). La inversa, A × B y el determinante además traen un **deslizador `t`** (spec `015`) que anima la transformación de la identidad a la matriz (en A × B, primero B y luego A·B) con botón Reproducir/Pausar y aviso cuando el determinante pasa por 0; los cuadros los precalcula Python y la web solo los recorre. Además incluye una sección de **ejercicios para práctica**: el usuario elige un método, ve una lista de ejercicios de ejemplo y con "Probar ejercicio" los datos se cargan en la calculadora (sin resolver).

## Estructura de carpetas

Fuera de `src/` solo quedan `AGENTS.md`, `sdd/` (contexto y forma de trabajo de la IA) y `server.py`. Todo el código fuente vive en `src/`. Comandos, siempre **desde la raíz del proyecto**: `python server.py`, `python -m unittest discover -s src/tests -t src` y `python -m unittest discover -s src/features/tests -t src`.

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

- **`server.py`** (en la **raíz**, a propósito: los técnicos lo ejecutan con `python server.py` sin entrar a `src/`; agrega `src/` a `sys.path`): servidor HTTP local (solo librería estándar: `http.server`, `json`). Expone la lógica de `metodos/` como endpoints JSON y además sirve `src/web/index.html`. Tampoco contiene lógica matemática propia: recibe los datos del formulario web, llama a las funciones de `metodos/` y responde con el resultado y los pasos ya formateados. Escucha en `127.0.0.1:8000`.
  - Sirve la página (`GET /`), `GET /api/estado`, `GET /api/ejercicios` (catálogo de práctica), los `POST /api/...` de cada módulo (incluye `POST /api/determinante` y `POST /api/determinante/recomendar`, esta última devuelve la recomendación de método según `n`, `POST /api/biseccion` y `POST /api/grafica`) y `POST /api/exportar` (recalcula con `metodos/` y devuelve el PNG/PDF como archivo adjunto), que devuelven `{"ok": true, ...}` o `{"error": "..."}` con código 400. Los datos ya formateados ("bloques") los arman `_armar_bloque_*`. La consola muestra cada petición.
- **`src/web/index.html`**: interfaz web de una sola página (HTML, CSS y JavaScript en el mismo archivo, sin librerías externas). Tiene su propia barra lateral y usa `fetch()` para llamar a los endpoints de `server.py`. **No funciona abierto con doble clic**: necesita que `server.py` esté corriendo. Solo presenta datos; nunca calcula.
- **`src/metodos/`**: carpeta donde vive toda la lógica matemática del proyecto, separada de la interfaz. Contiene:
  - `gauss_jordan.py`: método de **Gauss-Jordan**.
  - `pivote.py`: método de **Pivoteo**.
  - `conversion.py`: conversión entre bases numéricas.
  - `vectores_matrices.py`: operaciones con vectores y matrices, combinación lineal, ecuación matricial y matriz inversa.
  - `determinante.py`: determinante por **cofactores** (fila/columna de expansión elegible; por defecto la de más ceros; hasta `n = 6`) o **LU** con pivoteo parcial (`P·A = L·U`; hasta `n = 8`), `recomendar_metodo(n)` (n! contra n³/3), contador de multiplicaciones y comprobación (con el otro método y `L·U = P·A`).
  - `evaluador.py`: analizador y evaluador de funciones f(x) escritas como texto (sin `eval()`; `compilar()`, `evaluar_numero()` y `Funcion.evaluar_seguro()`); lo reutilizarán los siguientes métodos de raíces.
  - `escena.py` y `escenas.py`: **escenas geométricas 2D/3D** (spec 014): `escena.py` tiene el formato, ventana/caja, recortes de rectas y planos y la leyenda en texto; `escenas.py` arma la escena de cada módulo (`escena_sistema`, `escena_vectores`, `escena_determinante`, `escena_inversa`, `escena_producto`). La web, el PNG y el PDF solo la pintan. Spec 015: esas escenas (inversa, producto y determinante) traen también `animacion` (cuadros de M(t) = (1 − t)·I + t·A); el PNG y el PDF usan la vista fija en `t = 1`.
  - `grafica.py`: datos para graficar f(x) (curva en tramos, ventana vertical sin polos, marcas de ejes, puntos de cada iteración); `biseccion()` los devuelve en `grafica` y la web, el PNG y el PDF solo los dibujan. `curva_ventana()` re-muestrea la curva de la ventana visible cuando la gráfica web se mueve o hace zoom (`POST /api/grafica`).
  - `continuidad.py`: `revisar_continuidad(f, a, b)`, revisión heurística de continuidad por muestreo (401 puntos): detecta puntos no definidos, polos y saltos; la usa `biseccion.py` y la reutilizarán los siguientes métodos de raíces.
  - `biseccion.py`: **método de bisección** (`biseccion(funcion, a, b, tolerancia, max_iter)`, hasta 200 iteraciones; devuelve pasos, resultado, cota teórica, `continuidad`, advertencias y comprobación; `procedimiento_texto()` para exportar). Aritmética `float`: no usa el modo fracciones/decimales.
  - `ejercicios.py`: catálogo de ejercicios de práctica (solo datos y su vista previa; lo lee `server.py` por `GET /api/ejercicios`).
  - `general_metodos.py`: **utilidades generales** compartidas (fracciones y decimales, formateo de resultados y verificación de soluciones).
- **`src/features/`**: funcionalidades generales que **no son métodos matemáticos** (por ahora `exportar.py`: exportar respuestas a PNG/PDF —incluido el determinante—, escrito a mano con la librería estándar (`grafica_exportar.py` dibuja la gráfica de la bisección y tiene los intérpretes de PNG/PDF; `escena_exportar.py` arma el plan de las escenas geométricas 2D/3D con una vista fija), y su fuente bitmap, generada con `src/features/tools/generar_fuente.py`; sus pruebas están en `src/features/tests/`, se corren desde la raíz con `python -m unittest discover -s src/features/tests -t src`; ahí también está `prueba_web_movil.js`, un script opcional de Playwright que revisa la vista móvil de la web, ver su cabecera). `src/metodos/` es exclusivamente para métodos y operaciones matemáticas; lo demás va aquí.
- **`src/tests/`**: pruebas de `vectores_matrices`, `determinante`, `evaluador`, `continuidad`, `grafica`, `escenas`, `biseccion`, del catálogo de ejercicios, del contraste de colores (4.5:1 en ambos temas). Se corren desde la raíz con `python -m unittest discover -s src/tests -t src`.
- **`sdd/`**: documentación de Spec-Driven Development. `plan.md` (metodología y checklist), `task.md` (tareas y avance) y `specs/`: `specs/v1/spec_v1.md` (resumen de las specs 001–003), `specs/v2/spec_v2.md` (resumen de las 004–010, incluye las **"Reglas permanentes"** de exportar PNG/PDF, móvil, temas, ejercicios y consola que todo módulo nuevo debe cumplir) y `specs/v3/` para las specs nuevas (`011-biseccion.md` y `012-continuidad.md` y `013-grafica-biseccion.md` y `014-graficas-geometricas.md` y `015-transformacion-animada.md` ya implementadas; la siguiente sería la `016`). Los textos originales de las specs 001–010 se consolidaron y siguen en el historial de git. La GUI de escritorio (Tkinter) fue eliminada en la spec 009; la web es la única interfaz.

## Regla de sincronía lógica ↔ web

Toda lógica nueva va en `src/metodos/`. Toda funcionalidad nueva o modificada se refleja en `server.py` + `src/web/index.html`, sin duplicar cálculos.

## Regla para cambios visuales en la web

`src/web/index.html` es una sola página para móvil y escritorio: lo móvil son reglas `@media` (≤ 768, ≤ 480 y ≤ 380 px), no otra versión. Los colores por variables CSS y el contenido nuevo valen para ambos sin trabajo extra. Pero todo cambio visual (elementos anchos, tamaños fijos, filas con varios controles) debe revisarse a 320 px y 375 px: sin scroll horizontal de la página, tablas y matrices anchas en un contenedor con scroll interno, controles táctiles ≥ 44 px y campos de 16 px. No agregar colores sueltos; usar las variables.

## Cómo agregar módulos o métodos nuevos

Se sigue la metodología y el checklist de `sdd/plan.md` (spec, lógica, impresión en la web, **exportar PNG/PDF**, consola del servidor, **vista móvil**, ejercicios de práctica, temas y documentación). Antes de empezar, leer "Reglas permanentes" en `sdd/specs/v2/spec_v2.md`.

## Regla para commits y push

Los mensajes de commit (y las descripciones de PR) **no deben contener `Co-Authored-By` ni ninguna firma o mención de Claude Code** (ni "Generated with Claude Code" ni similares). Solo el mensaje del cambio, escrito normalmente. Esta regla del proyecto tiene prioridad sobre cualquier atribución automática por defecto.
