# Tareas de implementación

Desglose entregable de `sdd/plan.md`, dividido en subtareas por módulo.
Cada módulo sigue el ciclo definido en el plan: **Implementar → Integrar en
la interfaz → Cerrar**. Las tareas se marcan `[x]` al completarse; no se
borran tareas ya hechas.

Este archivo se actualiza cada vez que se agregue una spec nueva en `sdd/`
(se añade su bloque de tareas siguiendo el mismo formato).

---

## 001 — Conversión de bases numéricas

Spec: `sdd/specs/001-conversion.md`

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
- [x] Marcar `Estado: implementado` en `sdd/specs/001-conversion.md`.
- [x] Actualizar la fila del módulo 001 en la tabla de seguimiento de
      `sdd/plan.md`.

---

## 002 — Operaciones vectoriales y matriciales

Spec: `sdd/specs/002-vectores-matrices.md`

### Implementación (`metodos/vectores_matrices.py`)

- [x] Crear el archivo `metodos/vectores_matrices.py` con docstring de
      módulo (propósito, sin librerías externas).
- [x] Implementar **suma de vectores** de dimensión `n` arbitraria, con
      desglose componente por componente.
- [x] Implementar **resta de vectores** de dimensión `n` arbitraria, con
      desglose componente por componente.
- [x] Implementar **multiplicación de un vector por un escalar**, con
      desglose componente por componente.
- [x] Implementar la verificación de **combinación lineal**: dado un
      conjunto de vectores `v1..vk` y un vector objetivo `v`, plantear el
      sistema de ecuaciones correspondiente.
- [x] Conectar el planteamiento anterior con el motor de resolución de
      sistemas ya existente (`metodos/gauss_jordan.py` y/o
      `metodos/pivote.py`) para resolverlo, en vez de reimplementar la
      resolución.
- [x] A partir de la resolución, determinar si el vector objetivo es o no
      combinación lineal del conjunto, y en caso afirmativo reportar los
      escalares encontrados.
- [x] Implementar **suma de matrices**, validando primero que ambas tengan
      las mismas dimensiones (filas × columnas) y devolviendo un error
      controlado si no coinciden.
- [x] Implementar **resta de matrices**, con la misma validación de
      dimensiones.
- [x] Implementar **multiplicación de una matriz por un escalar**.
- [x] Implementar **multiplicación de matrices A × B**, validando que las
      columnas de `A` coincidan con las filas de `B`, con error controlado si
      no se cumple.
- [x] Implementar el planteamiento de una **ecuación matricial A·X = B**:
      construir la matriz aumentada `[A | B]` a partir de `A` y `B`
      capturados por el usuario.
- [x] Delegar la resolución de esa matriz aumentada al motor de sistemas ya
      existente (Gauss-Jordan y/o Pivoteo), sin reimplementar el algoritmo de
      resolución.
- [x] Definir una estructura de resultado estándar (tipo diccionario) para
      cada operación (vectores, matrices, ecuación matricial) que incluya
      pasos del procedimiento y resultado final, reutilizable por la GUI.
- [x] Reutilizar `metodos/general_metodos.py` para formateo/impresión donde
      aplique.

### Integración en la interfaz (`gui.py`)

- [x] Diseñar la vista (o sub-vistas/pestañas) para: operaciones con
      vectores, operaciones con matrices, y ecuación matricial A·X = B,
      dentro de una misma entrada del sidebar o como entradas separadas
      (decidir en el momento de construir la vista, priorizando claridad).
- [x] Formulario para capturar vectores de dimensión `n` variable (el
      usuario indica `n` antes de capturar, igual que "Ecuaciones"/
      "Variables" en la vista de sistemas lineales).
- [x] Formulario para capturar matrices de dimensiones variables para suma,
      resta y multiplicación (por escalar y entre matrices).
- [x] Formulario para capturar `A` y `B` en la ecuación matricial `A·X = B`.
- [x] Mostrar el procedimiento paso a paso de cada operación en el área de
      resultados, con el mismo estilo que las demás vistas.
- [x] Mostrar el resultado final de forma clara y destacada, incluyendo la
      conclusión de "es/no es combinación lineal" y la solución de la
      ecuación matricial cuando exista.
- [x] Agregar validación de errores amigable con `messagebox` (dimensiones
      incompatibles, campos vacíos, columnas de A distintas a filas de B,
      etc.).
- [x] Agregar la(s) entrada(s) correspondiente(s) a la lista `METODOS` del
      sidebar, reutilizando los componentes visuales ya definidos.

### Cierre

- [x] Probar manualmente desde la GUI: suma/resta de vectores, escalar por
      vector, combinación lineal (caso positivo y caso negativo), suma/resta
      de matrices (incluyendo dimensiones incompatibles), escalar por
      matriz, multiplicación de matrices (incluyendo caso incompatible), y
      ecuación matricial A·X = B (incluyendo sistema sin solución única).
      Validado con 5 pruebas de integración que montan la vista Tkinter real
      y ejecutan sus controles, además de 12 pruebas unitarias del motor.
- [x] Marcar `Estado: implementado` en `sdd/specs/002-vectores-matrices.md`.
- [x] Actualizar la fila del módulo 002 en la tabla de seguimiento de
      `sdd/plan.md`.

---

## 003 — Diseño visual web (index.html)

Spec: `sdd/specs/003-diseño-visual-html.md`

### Servidor local (`server.py`)

- [x] Crear `server.py` con docstring de módulo (propósito: exponer
      `metodos/` vía HTTP usando solo librería estándar, sin lógica
      matemática propia).
- [x] Implementar el servidor HTTP (basado en `http.server`) que sirve
      `index.html` como archivo estático.
- [x] Definir los endpoints JSON necesarios, uno por método: Gauss-Jordan,
      Pivoteo, Conversión de bases, y Vectores y matrices (vectores,
      matrices, ecuación `A·X = B`), reutilizando directamente las funciones
      de `metodos/` ya existentes.
- [x] Implementar la serialización de resultados a JSON, incluyendo la
      conversión de objetos `Fraction` a texto sin alterar el cálculo.
- [x] Manejar errores de los módulos de `metodos/` (por ejemplo
      `ValueError`) devolviendo una respuesta JSON de error clara, sin
      tracebacks crudos.

### Implementación (`index.html`)

- [x] Crear `index.html` como archivo único autocontenido (HTML, CSS y
      JavaScript inline, sin frameworks ni dependencias externas).
- [x] Reproducir el layout general de `gui.py`: sidebar fija con la lista de
      métodos y panel derecho con formulario + área de resultados
      monoespaciada.
- [x] Reproducir en CSS la paleta de colores y tipografías equivalentes a
      las definidas en `gui.py` (`COLOR_FONDO`, `COLOR_SIDEBAR`,
      `COLOR_BOTON`, `COLOR_BOTON_ACT`, fuentes de título/normal/mono).
- [x] Construir la vista de Gauss-Jordan / Pivoteo: captura de ecuaciones y
      variables, generación dinámica de la matriz aumentada, selector de
      formato fracción/decimal, resolución, mostrar pasos y comprobación de
      resultado, todo vía `fetch` al servidor local.
- [x] Construir la vista de Conversión de bases: selector de dirección y
      base, campo de número, procedimiento y resultado.
- [x] Construir la vista de Vectores y matrices con sus tres sub-vistas
      (vectores, matrices, ecuación `A·X = B`), replicando el
      comportamiento de `VistaVectoresMatrices` en `gui.py`.
- [x] Agregar validación de errores amigable en la propia página (mensajes
      claros ante campos vacíos, dimensiones incompatibles, respuestas de
      error del servidor, etc.), sin tracebacks ni JSON crudo visible. Se
      implementó un modal propio (equivalente a `messagebox`) para errores y
      avisos.

### Cierre

- [x] Levantar `server.py` y probar todos los endpoints con `curl`:
      Gauss-Jordan (caso única), Pivoteo (caso incompatible), Conversión
      decimal→hexadecimal y caso de dígito inválido, Vectores (suma y
      combinación lineal), Matrices (multiplicación incompatible), y
      Ecuación matricial (solución única); además de la ruta estática `/`
      y una ruta 404. Todos los resultados coinciden con la lógica de
      `metodos/` ya validada en los cierres de 001 y 002. Falta una pasada
      visual del usuario en su propia máquina (abrir el navegador) para el
      visto bueno final de estética, ya que la skill de automatización de
      navegador no estaba disponible en esta sesión.
- [x] Marcar `Estado: implementado` en `sdd/specs/003-diseño-visual-html.md`.
- [x] Actualizar la fila del módulo 003 en la tabla de seguimiento de
      `sdd/plan.md`.
