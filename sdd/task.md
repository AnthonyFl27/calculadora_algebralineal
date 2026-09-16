# Tareas de implementación

Desglose entregable de `sdd/plan.md`, dividido en subtareas por módulo.
Cada módulo sigue el ciclo definido en el plan: **Implementar → Integrar en
la interfaz → Cerrar**. Las tareas se marcan `[x]` al completarse; no se
borran tareas ya hechas.

Este archivo se actualiza cada vez que se agregue una spec nueva en `sdd/`
(se añade su bloque de tareas siguiendo el mismo formato).

---

## 001 — Conversión de bases numéricas

Spec: `sdd/001-conversion.md`

### Implementación (`metodos/conversion.py`)

- [x] Crear el archivo `metodos/conversion.py` con docstring de módulo
      (propósito, sin librerías externas).
- [x] Implementar la conversión **decimal → binario** con el procedimiento de
      divisiones sucesivas y residuos.
- [x] Implementar la conversión **decimal → octal** con el procedimiento de
      divisiones sucesivas y residuos.
- [x] Implementar la conversión **decimal → hexadecimal** con el
      procedimiento de divisiones sucesivas y residuos (incluyendo dígitos
      A-F).
- [x] Soportar números decimales negativos en las conversiones anteriores
      (signo-magnitud).
- [x] Implementar la conversión **binario → decimal**, mostrando la
      combinación lineal (dígito × potencia de la base, sumada).
- [x] Implementar la conversión **octal → decimal**, mostrando la
      combinación lineal correspondiente.
- [x] Implementar la conversión **decimal → decimal** (caso trivial/echo)
      solo si aplica según cómo quede diseñada la selección de base, para
      mantener consistencia de la interfaz.
- [x] Implementar validación de dígitos según la base seleccionada (por
      ejemplo, rechazar dígitos ≥ 2 en binario, ≥ 8 en octal, no
      hexadecimales fuera de 0-9A-F).
- [x] Definir una estructura de resultado estándar (tipo diccionario) que
      incluya: número de entrada, base de entrada, base de salida, pasos del
      procedimiento y resultado final, reutilizable por la GUI.
- [x] Reutilizar `metodos/general_metodos.py` donde aplique (formateo de
      texto), sin duplicar lógica ya existente. (No aplicó: el formateo que
      necesita este módulo es distinto al de fracciones/matrices, así que se
      resolvió con `procedimiento_texto()` propio en `conversion.py`.)

### Integración en la interfaz (`gui.py`)

- [x] Diseñar la vista de conversión (selector de dirección: "a otra base" /
      "a decimal", selector de base, campo de entrada del número).
- [x] Mostrar el procedimiento paso a paso (divisiones o combinación lineal,
      según el caso) en el área de resultados, con el mismo estilo que las
      demás vistas.
- [x] Mostrar el resultado final de forma clara y destacada.
- [x] Agregar validación de errores amigable con `messagebox` (campos
      vacíos, dígitos inválidos para la base, formato incorrecto).
- [x] Agregar la entrada "Conversión de bases" a la lista `METODOS` del
      sidebar, reutilizando `RoundedButton`, paleta de colores y fuentes ya
      definidas.

### Cierre

- [x] Probar manualmente desde la GUI todos los casos: decimal→binario,
      decimal→octal, decimal→hexadecimal, binario→decimal, octal→decimal, y
      casos con número negativo y con dígito inválido. (Probado vía script
      que monta la vista real y llama `convertir()`; falta una pasada visual
      del usuario en su propia máquina para el visto bueno final de estética.)
- [x] Marcar `Estado: implementado` en `sdd/001-conversion.md`.
- [x] Actualizar la fila del módulo 001 en la tabla de seguimiento de
      `sdd/plan.md`.

---

## 002 — Operaciones vectoriales y matriciales

Spec: `sdd/002-vectores-matrices.md`

### Implementación (`metodos/vectores_matrices.py`)

- [ ] Crear el archivo `metodos/vectores_matrices.py` con docstring de
      módulo (propósito, sin librerías externas).
- [ ] Implementar **suma de vectores** de dimensión `n` arbitraria, con
      desglose componente por componente.
- [ ] Implementar **resta de vectores** de dimensión `n` arbitraria, con
      desglose componente por componente.
- [ ] Implementar **multiplicación de un vector por un escalar**, con
      desglose componente por componente.
- [ ] Implementar la verificación de **combinación lineal**: dado un
      conjunto de vectores `v1..vk` y un vector objetivo `v`, plantear el
      sistema de ecuaciones correspondiente.
- [ ] Conectar el planteamiento anterior con el motor de resolución de
      sistemas ya existente (`metodos/gauss_jordan.py` y/o
      `metodos/pivote.py`) para resolverlo, en vez de reimplementar la
      resolución.
- [ ] A partir de la resolución, determinar si el vector objetivo es o no
      combinación lineal del conjunto, y en caso afirmativo reportar los
      escalares encontrados.
- [ ] Implementar **suma de matrices**, validando primero que ambas tengan
      las mismas dimensiones (filas × columnas) y devolviendo un error
      controlado si no coinciden.
- [ ] Implementar **resta de matrices**, con la misma validación de
      dimensiones.
- [ ] Implementar **multiplicación de una matriz por un escalar**.
- [ ] Implementar **multiplicación de matrices A × B**, validando que las
      columnas de `A` coincidan con las filas de `B`, con error controlado si
      no se cumple.
- [ ] Implementar el planteamiento de una **ecuación matricial A·X = B**:
      construir la matriz aumentada `[A | B]` a partir de `A` y `B`
      capturados por el usuario.
- [ ] Delegar la resolución de esa matriz aumentada al motor de sistemas ya
      existente (Gauss-Jordan y/o Pivoteo), sin reimplementar el algoritmo de
      resolución.
- [ ] Definir una estructura de resultado estándar (tipo diccionario) para
      cada operación (vectores, matrices, ecuación matricial) que incluya
      pasos del procedimiento y resultado final, reutilizable por la GUI.
- [ ] Reutilizar `metodos/general_metodos.py` para formateo/impresión donde
      aplique.

### Integración en la interfaz (`gui.py`)

- [ ] Diseñar la vista (o sub-vistas/pestañas) para: operaciones con
      vectores, operaciones con matrices, y ecuación matricial A·X = B,
      dentro de una misma entrada del sidebar o como entradas separadas
      (decidir en el momento de construir la vista, priorizando claridad).
- [ ] Formulario para capturar vectores de dimensión `n` variable (el
      usuario indica `n` antes de capturar, igual que "Ecuaciones"/
      "Variables" en la vista de sistemas lineales).
- [ ] Formulario para capturar matrices de dimensiones variables para suma,
      resta y multiplicación (por escalar y entre matrices).
- [ ] Formulario para capturar `A` y `B` en la ecuación matricial `A·X = B`.
- [ ] Mostrar el procedimiento paso a paso de cada operación en el área de
      resultados, con el mismo estilo que las demás vistas.
- [ ] Mostrar el resultado final de forma clara y destacada, incluyendo la
      conclusión de "es/no es combinación lineal" y la solución de la
      ecuación matricial cuando exista.
- [ ] Agregar validación de errores amigable con `messagebox` (dimensiones
      incompatibles, campos vacíos, columnas de A distintas a filas de B,
      etc.).
- [ ] Agregar la(s) entrada(s) correspondiente(s) a la lista `METODOS` del
      sidebar, reutilizando los componentes visuales ya definidos.

### Cierre

- [ ] Probar manualmente desde la GUI: suma/resta de vectores, escalar por
      vector, combinación lineal (caso positivo y caso negativo), suma/resta
      de matrices (incluyendo dimensiones incompatibles), escalar por
      matriz, multiplicación de matrices (incluyendo caso incompatible), y
      ecuación matricial A·X = B (incluyendo sistema sin solución única).
- [ ] Marcar `Estado: implementado` en `sdd/002-vectores-matrices.md`.
- [ ] Actualizar la fila del módulo 002 en la tabla de seguimiento de
      `sdd/plan.md`.
