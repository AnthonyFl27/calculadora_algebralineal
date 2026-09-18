# Plan de trabajo (Spec-Driven Development)

Este documento aterriza **cómo** se va a llevar a cabo el proyecto, no
**qué** hace cada módulo (eso vive en las specs individuales dentro de
`sdd/`). Aquí se define la metodología, la organización de archivos y el
seguimiento del avance.

## Metodología

El proyecto se construye en ciclos cortos, módulo por módulo, siguiendo
Spec-Driven Development:

1. **Especificar.** Antes de escribir código, se redacta o se ajusta la spec
   del módulo en `sdd/` (una spec por módulo, ver "Organización de archivos"
   abajo). La spec describe comportamiento y requisitos, no implementación.
2. **Implementar.** Se crea el archivo correspondiente en `metodos/`
   siguiendo esa spec y las convenciones generales del proyecto (sin
   librerías matemáticas externas, reutilizando `general_metodos.py` cuando
   aplique, etc.).
3. **Integrar en la interfaz.** Se conecta el módulo nuevo a `gui.py`
   (y a `cli.py` si aplica) agregando su entrada al sidebar, reutilizando los
   componentes visuales ya existentes (`RoundedButton`, paleta de colores,
   fuentes, área de resultados).
4. **Cerrar el ciclo.** Se marca la spec correspondiente como
   `implementado` (ver tabla de seguimiento) y se prueba manualmente desde la
   GUI antes de pasar al siguiente módulo.

No se trabajan varios módulos nuevos a la vez sin terminar el ciclo del
anterior, salvo que el usuario indique lo contrario explícitamente.

## Organización de archivos dentro de `sdd/`

- `sdd/plan.md` — este archivo. Metodología, convenciones y seguimiento.
- `sdd/NNN-nombre-del-modulo.md` — una spec por módulo o funcionalidad,
  numerada en orden de aparición (`001`, `002`, `003`, ...). Cada spec:
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
  nunca en `gui.py` ni en `cli.py`.
- Reutilizar `metodos/general_metodos.py` para formateo de números,
  impresión de matrices, comprobaciones, etc., en vez de duplicar lógica.
- Todo módulo debe poder mostrar el procedimiento paso a paso, no solo el
  resultado final.
- La interfaz mantiene siempre el mismo diseño: sidebar a la izquierda para
  elegir método/módulo, panel derecho con el formulario y los resultados,
  reutilizando los componentes visuales ya definidos en `gui.py`.
- Un módulo nuevo = una entrada nueva en la lista `METODOS` del sidebar. Los
  métodos existentes nunca se reemplazan, solo se agregan nuevos.
- Validación de errores amigable con `messagebox`, nunca tracebacks crudos.

## Seguimiento de módulos

| # | Spec | Módulo | Estado |
|---|------|--------|--------|
| 000 | — | Gauss-Jordan | implementado (previo a SDD) |
| 000 | — | Pivoteo | implementado (previo a SDD) |
| 001 | `sdd/specs/001-conversion.md` | Conversión de bases numéricas | implementado |
| 002 | `sdd/specs/002-vectores-matrices.md` | Operaciones vectoriales y matriciales | implementado |
| 003 | `sdd/specs/003-diseño-visual-html.md` | Diseño visual web (index.html) | implementado |

Esta tabla se actualiza cada vez que se agrega una spec nueva o se cierra el
ciclo de una existente.

## Cómo se agregan módulos nuevos a futuro

Cuando el usuario traiga un módulo nuevo:

1. Se crea `sdd/NNN-nombre.md` con su especificación (siguiente número
   disponible).
2. Se agrega una fila a la tabla de seguimiento con estado `pendiente`.
3. Se sigue el ciclo de la sección "Metodología" hasta marcarlo
   `implementado`.

Las specs ya implementadas no se tocan salvo para documentar cambios de
comportamiento explícitamente pedidos; sirven como contexto histórico
confiable de lo que la calculadora ya hace.
