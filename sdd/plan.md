# Plan de trabajo (Spec-Driven Development)

Este documento aterriza **cómo** se va a llevar a cabo el proyecto, no
**qué** hace cada módulo (eso vive en las specs individuales dentro de
`sdd/`). Aquí se define la metodología, la organización de archivos y el
seguimiento del avance.

## Metodología

El proyecto se construye en ciclos cortos, módulo por módulo, siguiendo
Spec-Driven Development:

1. **Especificar.** Antes de escribir código, se redacta o se ajusta la spec
   del módulo en `sdd/specs/` (una spec por módulo, dentro de la carpeta de
   la versión en curso; ver "Organización de archivos" abajo). La spec describe comportamiento y requisitos, no implementación.
2. **Implementar.** Se crea el archivo correspondiente en `src/metodos/`
   siguiendo esa spec y las convenciones generales del proyecto (sin
   librerías matemáticas externas, reutilizando `general_metodos.py` cuando
   aplique, etc.).
3. **Integrar en las interfaces.** Se conecta el módulo nuevo a las dos
   interfaces, sin duplicar cálculos en ninguna. El detalle de qué hay que
   tocar está en "Checklist para un método o módulo nuevo" (más abajo):
   sidebar, tarjeta de Inicio, salida de resultados, consola del servidor,
   ejercicios de práctica, temas y documentación.
4. **Probar y cerrar el ciclo.** Desde la raíz del proyecto se corren las
   pruebas de `src/tests/` (`python -m unittest discover -s src/tests -t src`)
   y de `src/features/` (`python -m unittest discover -s src/features/tests -t src`),
   se prueba manualmente en ambas interfaces (`python src/main.py` y
   `python server.py`) y se marca la spec como
   `implementado` (ver tabla de seguimiento) antes de pasar al siguiente
   módulo.

No se trabajan varios módulos nuevos a la vez sin terminar el ciclo del
anterior, salvo que el usuario indique lo contrario explícitamente.

## Organización de archivos dentro de `sdd/`

- `sdd/plan.md` — este archivo. Metodología, convenciones y seguimiento.
- `sdd/task.md` — solo lo **en curso o pendiente**: tareas de la spec que se
  está trabajando y pendientes abiertos. Al cerrar una spec, su bloque se
  borra (el detalle vive en la spec y en la tabla de seguimiento de abajo).
- `sdd/specs/vN/NNN-nombre-del-modulo.md` — una spec por módulo o
  funcionalidad, agrupada por versión. `v1/` contiene las specs ya
  implementadas; `v2/` es para las nuevas. La numeración (`001`, `002`,
  `003`, ...) es global y continúa entre versiones (la primera spec de `v2`
  sería `004`). Cada spec:
  - Empieza con un estado: `Estado: pendiente` o `Estado: implementado`.
  - Describe el propósito y los requisitos funcionales del módulo, sin
    detalles de código.
  - Una vez implementado el módulo, la spec **no se borra**: pasa a ser
    contexto de referencia (para el LLM y para quien retome el proyecto),
    documentando qué se decidió construir y por qué.

Las specs ya implementadas no se reescriben ni se les quita contenido; solo
se actualiza su estado. Si un módulo cambia de comportamiento más adelante,
se agrega una sección "Cambios posteriores" a su spec en vez de reescribir la
original. Sirven como contexto histórico confiable de lo que la calculadora
hace.

## Convenciones generales del proyecto

Aplican a todos los módulos, presentes y futuros.

- **Sin librerías matemáticas externas** (NumPy, SciPy, SymPy, etc.): solo
  librería estándar de Python.
- **Todo el código fuente vive en `src/`**, salvo `server.py`, que queda en
  la raíz para que se ejecute con `python server.py` sin navegar carpetas
  (agrega `src/` a `sys.path`). `AGENTS.md` y `sdd/` también quedan fuera.
- **La lógica vive en `src/metodos/`**, un archivo por módulo, reutilizando
  `general_metodos.py`. `src/main.py`, `server.py` y `src/web/index.html` solo
  presentan: `server.py` traduce entre JSON y `metodos/`; `index.html` nunca
  calcula.
- **Dos interfaces sincronizadas:** toda funcionalidad existe en `src/main.py` y en
  `server.py` + `src/web/index.html`, con el mismo diseño (sidebar + panel) y sin
  duplicar cálculos. Los métodos existentes nunca se reemplazan, solo se
  agregan nuevos.
- **Procedimiento paso a paso**, no solo el resultado final.
- **Errores amigables, nunca tracebacks:** `messagebox` en la GUI; en la web,
  `{"error": "..."}` con código 400 y un modal.
- **Colores solo en la paleta central** de cada interfaz (`PALETAS` en
  `src/main.py`, variables CSS en `src/web/index.html`).
- **Pruebas** en `src/tests/` para cada módulo nuevo, y **ejercicios de práctica**
  para cada método nuevo.

## Checklist para un método o módulo nuevo

Cada vez que se pida un método, operación o módulo nuevo (ejemplo: "agrega
el método de Cramer"), el LLM debe cubrir **todo** lo siguiente, no solo la
parte matemática. Se usa como lista de tareas al redactar la spec y su bloque
en `sdd/task.md`.

### 1. Lógica (`src/metodos/`)

- [ ] Archivo nuevo `src/metodos/<modulo>.py` con docstring de módulo; reutiliza
      `general_metodos.py` (fracciones, `formatear()`, comprobaciones) y los
      motores existentes (`gauss_jordan.py`, `pivote.py`) en vez de
      reimplementarlos.
- [ ] Devuelve un diccionario estándar con el resultado **y los pasos** del
      procedimiento (tipo, entradas, pasos, resultado, comprobación cuando
      aplique), y errores controlados con `ValueError` (mensajes en español).
- [ ] Pruebas en `src/tests/` (casos normales, casos borde y errores).

### 2. Cómo se imprime el resultado (las dos interfaces)

- [ ] **Escritorio:** función `procedimiento_texto()` (o equivalente) que
      muestra pasos y resultado en el área de texto monoespaciada, con
      fracción o decimal según el modo elegido.
- [ ] **Servidor:** endpoint `POST /api/<ruta>` en `server.py` que solo
      traduce JSON ↔ `metodos/`; arma un *bloque* con celdas ya formateadas
      (`_armar_bloque_sistema` / `_armar_bloque_operacion` o una función
      nueva) y responde `{"ok": true, ...}` o `{"error": "..."}` con 400.
- [ ] **Web:** la vista en `src/web/index.html` dibuja tablas reales por paso
      (stepper, pivote y filas afectadas resaltados), tarjeta de resultado
      (verde = éxito/única, ámbar = infinitas, rojo = error/incompatible) y
      tarjeta de comprobación, reutilizando los componentes existentes.
      `index.html` solo presenta; nunca calcula.
- [ ] Modo de visualización **fracciones / decimales** disponible y respetado
      en ambas interfaces.

### 3. Consola del servidor

- [ ] Agregar la ruta a `DESTINO` y su caso en `_descripcion_peticion()` de
      `server.py`, para que la consola muestre la función de `metodos/`
      usada, la entrada y la salida (o el error) de cada petición, y aparezca
      en el banner de arranque.

### 4. Navegación y diseño

- [ ] **Escritorio:** entrada en la lista `METODOS` de `src/main.py` (el sidebar y
      las tarjetas de Inicio salen de ahí) y su texto en `DESCRIPCIONES`.
- [ ] **Web:** entrada en `METODOS` de `src/web/index.html` con `clave`, `nombre`,
      `icono` (añadirlo a `ICONOS` si es nuevo), `descripcion` y `vista`;
      el sidebar y las tarjetas de Inicio salen de esa lista.
- [ ] Mismo nombre y misma descripción en ambas interfaces.
- [ ] Se ve bien en modo claro y oscuro (contraste 4.5:1 en oscuro) y el
      cambio de tema no pierde datos ni resultados.
- [ ] Vista adaptable (web: pantallas angostas y sidebar replegado; GUI: el
      recoloreo por árbol de widgets cubre los widgets nuevos; si se crea un
      widget con color propio, registrarlo en `_recolorear`).
- [ ] **Web móvil (spec 008):** se revisa a 320 px y 375 px (vertical) sin
      scroll horizontal de la página; las tablas o matrices anchas van en un
      contenedor con scroll interno; controles táctiles ≥ 44 px y campos de
      16 px; los colores siempre por variables CSS. Se corre
      `src/features/tests/prueba_web_movil.js` (ver su cabecera) cuando el
      cambio toque la vista.

### 5. Ejercicios de práctica

- [ ] Agregar el método a `METODOS_EJERCICIOS` y sus ejercicios a `EJERCICIOS`
      en `src/metodos/ejercicios.py` (al menos 5; con casos básico, intermedio y
      avanzado y los casos límite del método, p. ej. sin solución). Cada uno:
      `id`, `titulo`, `dificultad`, `descripcion`, `datos` y
      `resultado_esperado`; añadir su caso a `vista_previa()`.
- [ ] Hacer que la vista del método acepte un `ejercicio` opcional y cargue
      sus datos **sin resolver** (`cargar_ejercicio` en `src/main.py`; parámetro
      `ejercicio` de la vista en `src/web/index.html`), sin cambiar su comportamiento
      por defecto.
- [ ] Pruebas: extender `src/tests/test_ejercicios.py` (cada ejercicio coincide con
      lo que calcula `metodos/`) y `src/tests/test_gui_ejercicios.py` (se carga y
      se resuelve sin errores).

### 6. Documentación y cierre

- [ ] Spec nueva `sdd/specs/vN/NNN-nombre.md` (`Estado: pendiente`), fila en
      la tabla de seguimiento y su bloque en `sdd/task.md` **antes** de
      programar.
- [ ] Al terminar: spec en `implementado` (con "Cambios y decisiones tomadas
      al implementar" si hubo), fila actualizada, bloque borrado de
      `sdd/task.md` (dejando solo lo que siga abierto) y `AGENTS.md`
      actualizado (funcionalidades, archivos, endpoints, pruebas).
- [ ] Si el cambio es solo visual, se documenta en "Cambios posteriores" de la
      spec 004 (diseño visual); si cambia el comportamiento de un módulo,
      en la sección "Cambios posteriores" de la spec de ese módulo.
- [ ] Pendiente del usuario: visto bueno visual en su máquina (las pruebas
      con `jsdom` y de Tkinter validan comportamiento, no apariencia).

## Seguimiento de módulos

| # | Spec | Módulo | Estado |
|---|------|--------|--------|
| 000 | — | Gauss-Jordan | implementado (previo a SDD) |
| 000 | — | Pivoteo | implementado (previo a SDD) |
| 001 | `sdd/specs/v1/001-conversion.md` | Conversión de bases numéricas | implementado |
| 002 | `sdd/specs/v1/002-vectores-matrices.md` | Operaciones vectoriales y matriciales | implementado |
| 002 (2.4) | `sdd/specs/v1/002-vectores-matrices.md` | Matriz inversa (cambio posterior) | implementado |
| 003 | `sdd/specs/v1/003-diseño-visual-html.md` | Diseño visual web (index.html) | implementado |
| 004 | `sdd/specs/v2/004-diseño-visual.md` | Diseño visual: modo oscuro/claro y mejoras de interfaz (GUI y web) | implementado |
| 005 | `sdd/specs/v2/005-ejercicios-practica.md` | Ejercicios para práctica (GUI y web) | implementado |
| 006 | `sdd/specs/v2/006-funcionalidades.md` | Funcionalidades: exportar respuestas a PNG y PDF (GUI y web) | implementado |
| 007 | `sdd/specs/v2/007-reestructura-src.md` | Reestructura: código fuente en `src/` (`gui.py` → `src/main.py`) | implementado |
| 008 | `sdd/specs/v2/008-adaptable-movil.md` | Web adaptable a móviles (solo `index.html`; la GUI queda fuera) | implementado |

Esta tabla es el único seguimiento de módulos: se actualiza cada vez que se
agrega una spec nueva (estado `pendiente`) o se cierra el ciclo de una
existente. Un módulo nuevo sigue el ciclo de "Metodología" y el checklist de
arriba.
