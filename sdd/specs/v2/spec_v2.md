Estado: implementado

# Spec v2 — Resumen (specs 004–010)

Resumen consolidado de las specs `004`–`010`. Los originales se eliminaron; su
texto completo sigue en el historial de git (`git log -- sdd/specs/v2`).
Las menciones a la GUI de Tkinter eran de la época en que existía; se eliminó
en la spec 009 y la web es la única interfaz.

---

## Reglas permanentes (todo módulo o cambio nuevo debe cumplirlas)

Esto es lo que más importa de la v2. El checklist completo paso a paso está en
`sdd/plan.md`; aquí van las reglas que el LLM no debe olvidar.

### A. Exportar a PNG / PDF (spec 006)

Todo módulo con resultado **debe poder exportarse**. Al agregar un método:

- `src/features/exportar.py` debe aceptarlo: recibe el diccionario estándar de
  `metodos/` (tipo, entradas, pasos, resultado, comprobación) y lo convierte en
  líneas de texto; de ahí salen PNG y PDF. **No recalcula**; el procedimiento en
  texto (`procedimiento_texto()`) vive en el módulo de `metodos/`.
- `server.py`: registrar el módulo en `CALCULOS[...]` para que
  `POST /api/exportar` (`{"modulo", "datos", "formato", "incluir_pasos"}`)
  recalcule con `metodos/` y devuelva el archivo adjunto. Agregar la ruta a
  `DESTINO` y a `_descripcion_peticion()`.
- Respeta el modo fracciones/decimales, la opción "Incluir pasos" y pone en
  `titulo_documento()` el título y nombre del archivo
  (`<metodo>-<fecha>.png|pdf`). Pivote marcado en texto ("pivote en columna N"),
  no solo por color. Si el módulo usa símbolos nuevos (`↔`, etc.), añadirlos a
  la transliteración del PDF / fuente bitmap.
- UI: botón de **descarga** arriba a la derecha de la vista (menú: PNG, PDF,
  casilla "Incluir pasos"). Deshabilitado sin resultado (tooltip "Resuelve
  primero para exportar"); solo se habilita mientras el último cálculo correcto
  sigue a la vista. No aparece en Inicio ni en Ejercicios. Menú accesible
  (foco visible, `Enter`/`Esc`, `aria-haspopup`, `aria-expanded`).
- El documento exportado usa su **propia paleta de impresión** (fondo blanco,
  texto oscuro), independiente del tema de la web.
- Pruebas: `src/features/tests/test_exportar.py` y `test_server_exportar.py`.

### B. Móvil (spec 008): una sola página, reglas `@media`

`src/web/index.html` es **una sola página** para móvil y escritorio; lo móvil
son reglas `@media` (≤ 768 px, con ajustes a ≤ 480 y ≤ 380), no otra versión.
Todo cambio visual o vista nueva se revisa a **320 px y 375 px** (y los anchos
320, 360, 375, 390, 412, 430, 600, 768, 1024):

- **Sin scroll horizontal de la página** (`scrollWidth <= clientWidth`). Las
  matrices y tablas anchas hacen scroll **dentro de su contenedor**, centradas
  solo si caben (márgenes `auto`, nunca `justify-content: center` que oculta el
  borde izquierdo). El tamaño de la matriz no se limita; referencia: 8×8 + columna
  de términos a 320 px.
- Campos de entrada y selectores a **16 px** (evita el zoom de iOS);
  objetivos táctiles **≥ 44×44 px** (botones, pestañas, exportar, stepper).
- Celdas **sin** `inputmode` (los teclados numéricos de iOS no tienen `/` ni
  `-`); sí `autocomplete/autocapitalize/autocorrect="off"`, `spellcheck="false"`,
  `enterkeyhint="next"`. Se usa `crearCelda()`.
- Filas de controles que pasan a la línea siguiente; cuadrículas a una columna
  cuando no caben dos; `crearControles()` agrupa etiqueta + campo en
  `label.campo`.
- Stepper: en móvil, contador + botones grandes (se ocultan los puntos).
- Sidebar ≤ 768 px → **drawer superpuesto** con barra superior (hamburguesa),
  se cierra al elegir módulo, tocar fuera o `Esc`; el foco vuelve al botón.
  El estado "replegado" de escritorio (`sidebar-colapsado` en `localStorage`)
  nunca se modifica desde móvil.
- Modal, toast y menú de exportar siempre dentro de la pantalla (ancho máx.
  `100vw − 32px`, scroll interno, `safe-area`). Alturas con `dvh`.
- `:hover` solo en dispositivos con hover; `touch-action: manipulation`.
- Números grandes: `overflow-wrap: anywhere` en las tarjetas de resultado.
- Descarga PNG/PDF: `<a download>` con blob; en móvil el aviso ofrece "Abrir".
- Verificación: `src/features/tests/prueba_web_movil.js` (Playwright, opcional;
  ver su cabecera). **Agregar el módulo nuevo a sus listas de módulos.** Las
  pruebas validan medidas, no apariencia: el visto bueno visual es del usuario.

### C. Temas claro / oscuro (spec 004)

- **Los colores viven solo en las variables CSS** de `src/web/index.html`
  (`:root` claro + bloque oscuro con `data-theme="dark"`). Nada de hex/`rgba`
  sueltos.
- Contraste de texto **4.5:1 en ambos temas** (`src/tests/test_contraste.py`).
  Colores semánticos: verde = éxito/única, ámbar = infinitas/singular, rojo =
  error/incompatible. Token `--acento-texto` para texto/símbolos de acento.
  Los controles deshabilitados quedan exentos.
- Cambiar de tema no pierde datos, pestaña ni resultados (no recalcula).
- Tema inicial: el guardado en `localStorage` (con `try/catch`), si no, el del
  sistema; se aplica antes de pintar para evitar parpadeo.

### D. Navegación, ejercicios y consola

- Un módulo nuevo = entrada en `METODOS` (`clave`, `nombre`, `icono` —añadirlo
  a `ICONOS` si es nuevo—, `descripcion`, `vista`); el sidebar y las tarjetas de
  Inicio salen de esa lista. Inicio tiene una tarjeta por módulo; debajo, tras
  un separador, la sección "Práctica".
- **Ejercicios de práctica** (spec 005) para cada método nuevo: agregarlo a
  `METODOS_EJERCICIOS` y sus ejercicios a `EJERCICIOS` en
  `src/metodos/ejercicios.py` (≥ 5, básico/intermedio/avanzado y casos límite),
  cada uno con `id`, `titulo`, `dificultad`, `descripcion`, `datos` y
  `resultado_esperado`, más su caso en `vista_previa()`. La vista del método
  acepta un `ejercicio` opcional (`mostrarVista(metodo, ejercicio)`) que carga
  los datos **sin resolver**. Prueba: extender `src/tests/test_ejercicios.py`.
- **Consola del servidor** (spec 004): cada ruta nueva en `DESTINO` y
  `_descripcion_peticion()` (muestra función de `metodos/`, entrada y salida o
  error); aparece en el banner de arranque. `/api/estado` no se registra.
- Errores amigables siempre (`{"error": "..."}` con 400 + modal), nunca
  tracebacks. Fracciones/decimales respetado en toda la salida.

---

## 004 — Diseño visual (temas y mejoras)

Casa de los cambios visuales. Implementó: temas claro/oscuro (regla C),
**sidebar replegable** a 56 px (botón en la cabecera; estado en
`sidebar-colapsado`; con el sidebar replegado queda visible el punto de estado
del servidor con tooltip), título "Calculadora" e ícono SVG de calculadora en la
pestaña, quitar la nota "Requiere: python server.py", **banner y log de la
consola** de `server.py` (hora, método, ruta, estado, tiempo, bytes + detalle del
cálculo), y el **menú de Inicio** (vista por defecto, título "Calculadora de
Álgebra Lineal", una tarjeta por módulo y entrada "Inicio" en el sidebar; sin
estado propio, es solo navegación). Decisión: el contraste 4.5:1 se garantizó
primero en oscuro y luego también en claro oscureciendo solo los colores de
texto (fondos, bordes y puntos de estado no cambian).

## 005 — Ejercicios para práctica

Catálogo único en `src/metodos/ejercicios.py` (solo datos; `catalogo()` añade
`vista_previa` para no duplicar formato), expuesto en `GET /api/ejercicios`.
Flujo: tarjeta "Ejercicios para práctica" en Inicio → "¿Para qué método…?" →
lista (título, dificultad con etiqueta verde/ámbar/rojo, descripción, vista
previa) → **"Probar ejercicio"** abre la vista con los datos cargados **sin
resolver**. Navegación "← Inicio" / "← Elegir otro método"; el sidebar
("Ejercicios", bajo un separador) queda resaltado. Mínimos: ≥ 5 por método;
Gauss-Jordan/Pivoteo cubren única/infinitas/incompatible y tamaños variados
(Pivoteo con pivote 0 o pequeño); Vectores y matrices cubre cada operación
(incluida inversa no invertible). Sin puntajes, historial ni progreso.

## 006 — Exportar respuestas (PNG y PDF)

Ver regla A. Detalles de implementación: todo escrito **a mano con la librería
estándar** (PDF 1.4 en texto con fuente Courier/WinAnsi y `zlib`; PNG con `zlib`
+ `struct` y **fuente bitmap incluida** en `_fuente_exportar.py`, generada con
`src/features/tools/generar_fuente.py`; Pillow solo en desarrollo). Vive en
`features/` (no en `metodos/`, que es solo matemáticas; `features/` puede
importar de `metodos/` pero no al revés). Orden del documento: título, fecha y
hora, datos, pasos (opcional), resultado (con tipo), comprobación. PDF en páginas
A4; PNG único de ancho fijo. El ícono pasó de ☰ a descarga (Font Awesome
`nf-fa-download`, SVG de 20 px en botón de 34 px). Toast "Archivo guardado".

## 007 — Reestructura a `src/`

Código fuente en `src/` (`metodos/`, `features/`, `tests/`, `web/index.html`);
`server.py` **queda en la raíz** a propósito (`python server.py` sin entrar a
carpetas; agrega `src/` a `sys.path`). `AGENTS.md` y `sdd/` quedan fuera. Los
imports (`from metodos...`) no cambian. Todo se corre desde la raíz:
`python server.py`, `python -m unittest discover -s src/tests -t src` y
`... -s src/features/tests -t src`.

## 008 — Web adaptable a móviles

Ver regla B (resume los requisitos y decisiones). Solo tocó `index.html`;
breakpoint único 768 px compartido por CSS y JS (`MQ_MOVIL`). Verificado con
`prueba_web_movil.js`. **Pendiente conocido:** `server.py` convierte los
sistemas de Gauss-Jordan/Pivoteo con `float()`, así que esas celdas no aceptan
`1/2` (las de vectores/matrices sí); no es parte de la spec.

## 009 — Eliminar la GUI de Tkinter

Se eliminaron `src/main.py` y sus pruebas (`test_gui_*`). La web es la única
interfaz; se acabó la regla de mantener dos interfaces sincronizadas. El
contraste 4.5:1 se prueba solo para la web. Los colores viven solo en variables
CSS.

## 010 — Determinante (cofactores y LU)

**Lógica:** `src/metodos/determinante.py` (archivo propio, no dentro de
`vectores_matrices.py`; reutiliza `parsear_numero`/`_matriz` y `formatear`).
Enunciado del profesor: elegir entre cofactores y LU, **indicando antes de
elegir cuál es más eficiente**.

- **Cofactores:** expansión de Laplace recursiva hasta 2×2 (`ad − bc`). Fila o
  columna elegible; por defecto la de **más ceros** (empate: la primera);
  términos con `a_ij = 0` se muestran omitidos. Máximo **n = 6**. La expansión
  elegida solo aplica al nivel superior.
- **LU con pivoteo parcial:** `P·A = L·U` (Doolittle), `det = (−1)^s · Πuᵢᵢ`.
  Máximo **n = 8**. Con columna sin pivote registra un paso `sin_pivote` y
  **continúa** (para que `P·A = L·U` siga cumpliéndose); `det = 0`.
- Aritmética exacta con `Fraction`. Validación: cuadrada y no vacía; celdas con
  enteros, decimales y fracciones.
- **Recomendación antes de elegir:** `recomendar_metodo(n)` compara `n!` contra
  `n³/3`: n = 1–2 cofactores (trivial), n = 3 cofactores (≈ igual), n ≥ 4 LU.
  Depende solo de `n`. Devuelve también `cofactores_disponible`, `lu_disponible`,
  `maximo_cofactores`, `maximo_lu` para que la web deshabilite opciones sin
  duplicar límites. Es una guía, no una restricción; el recomendado lleva la
  etiqueta "Recomendado". Endpoint `POST /api/determinante/recomendar`.
- Tras calcular, se muestra el **contador real de multiplicaciones** (incluye
  las divisiones de los multiplicadores de LU; las estimaciones son de orden de
  magnitud).
- **Resultado:** tarjeta verde con `det(A)`; si es 0, tarjeta ámbar "A es
  singular (no tiene inversa)".
- **Comprobación:** se recalcula con el otro método (cofactores solo si
  n ≤ 6); con LU **siempre** se vuelve a multiplicar `L·U` y `P·A` y se verifica
  que `L` sea triangular inferior con unos en la diagonal y `U` triangular
  superior (`comprobacion.factorizacion`). Para n = 7–8 es la única
  comprobación. En la web: tarjeta "L·U coincide con P·A"; también sale en
  PNG/PDF.
- Estructura de resultado: `operacion`, `metodo`, `entradas`, `pasos`,
  `resultado`, `singular`, `multiplicaciones`, `recomendacion`, `comprobacion`;
  LU además `P`, `L`, `U`, `intercambios`; cofactores además `expansion`.
  Errores con `ValueError` en español.
- Entrada propia en sidebar e Inicio ("Determinante"), no pestaña de "Vectores
  y matrices". Endpoint `POST /api/determinante`; `CALCULOS["determinante"]` para
  exportar. 7 ejercicios (`det-01`…`det-07`). Descartado: Sarrus, determinante
  vía Gauss-Jordan, adjunta/Cramer.
- Pruebas: `src/tests/test_determinante.py`, `test_ejercicios.py`,
  `src/features/tests/test_exportar.py` y `test_server_exportar.py`.
  Pendiente del usuario: visto bueno visual (claro/oscuro y la tarjeta
  "L·U coincide con P·A" en móvil).
