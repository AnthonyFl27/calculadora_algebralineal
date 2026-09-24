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
2. **Implementar.** Se crea el archivo correspondiente en `metodos/`
   siguiendo esa spec y las convenciones generales del proyecto (sin
   librerías matemáticas externas, reutilizando `general_metodos.py` cuando
   aplique, etc.).
3. **Integrar en las interfaces.** Se conecta el módulo nuevo a las dos
   interfaces, sin duplicar cálculos en ninguna:
   - **Escritorio:** entrada en el sidebar de `gui.py`, reutilizando los
     componentes visuales existentes (`RoundedButton`, paleta de colores,
     fuentes, área de resultados).
   - **Web:** endpoint `POST /api/...` en `server.py` (con su bloque de
     datos ya formateado) y su vista en `index.html`.
4. **Probar y cerrar el ciclo.** Se corren las pruebas de `tests/`, se
   prueba manualmente en ambas interfaces (`python gui.py` y
   `python server.py`) y se marca la spec como `implementado` (ver tabla de
   seguimiento) antes de pasar al siguiente módulo.

No se trabajan varios módulos nuevos a la vez sin terminar el ciclo del
anterior, salvo que el usuario indique lo contrario explícitamente.

## Organización de archivos dentro de `sdd/`

- `sdd/plan.md` — este archivo. Metodología, convenciones y seguimiento.
- `sdd/task.md` — desglose de tareas por spec y su avance.
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

Las specs no se reescriben para "quitarles" contenido ya implementado; solo
se actualiza su estado. Si un módulo cambia de comportamiento más adelante,
se agrega una sección "Cambios posteriores" a su spec en vez de reescribir la
original.

## Convenciones generales del proyecto

(Aplican a todos los módulos, presentes y futuros; se repiten aquí para no
depender de recordarlas spec por spec.)

- Sin librerías matemáticas externas (NumPy, SciPy, SymPy, etc.). Solo
  librería estándar de Python (`fractions`, `math` para UI, etc.).
- Un archivo por módulo dentro de `metodos/`. La lógica matemática vive ahí,
  nunca en `gui.py`, `server.py` ni `index.html`.
- Reutilizar `metodos/general_metodos.py` para formateo de números,
  impresión de matrices, comprobaciones, etc., en vez de duplicar lógica.
- Todo módulo debe poder mostrar el procedimiento paso a paso, no solo el
  resultado final.
- Ambas interfaces mantienen el mismo diseño: sidebar a la izquierda para
  elegir método/módulo, panel derecho con el formulario y los resultados.
  `gui.py` reutiliza sus componentes visuales; `index.html` es un solo
  archivo (HTML, CSS y JS) sin librerías externas.
- Un módulo nuevo = una entrada nueva en el sidebar de cada interfaz. Los
  métodos existentes nunca se reemplazan, solo se agregan nuevos.
- Toda funcionalidad debe existir en ambas interfaces. `server.py` solo
  traduce entre JSON y `metodos/`; `index.html` solo presenta.
- Validación de errores amigable, nunca tracebacks crudos: `messagebox` en
  `gui.py`; en la web, `server.py` responde `{"error": "..."}` con código 400
  y `index.html` muestra el mensaje.
- Cada módulo de `metodos/` nuevo debe tener pruebas en `tests/`.

## Seguimiento de módulos

| # | Spec | Módulo | Estado |
|---|------|--------|--------|
| 000 | — | Gauss-Jordan | implementado (previo a SDD) |
| 000 | — | Pivoteo | implementado (previo a SDD) |
| 001 | `sdd/specs/v1/001-conversion.md` | Conversión de bases numéricas | implementado |
| 002 | `sdd/specs/v1/002-vectores-matrices.md` | Operaciones vectoriales y matriciales | implementado |
| 003 | `sdd/specs/v1/003-diseño-visual-html.md` | Diseño visual web (index.html) | implementado |

Esta tabla se actualiza cada vez que se agrega una spec nueva o se cierra el
ciclo de una existente.

## Cómo se agregan módulos nuevos a futuro

Cuando el usuario traiga un módulo nuevo:

1. Se crea `sdd/specs/v2/NNN-nombre.md` (o la carpeta de la versión en
   curso) con su especificación, usando el siguiente número disponible.
2. Se agrega una fila a la tabla de seguimiento con estado `pendiente` y
   sus tareas a `sdd/task.md`.
3. Se sigue el ciclo de la sección "Metodología" hasta marcarlo
   `implementado`.

Las specs ya implementadas no se tocan salvo para documentar cambios de
comportamiento explícitamente pedidos; sirven como contexto histórico
confiable de lo que la calculadora ya hace.
