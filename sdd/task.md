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

---

## 003 (continuación) — Mejora visual e interactividad de los pasos

Spec: `sdd/specs/003-diseño-visual-html.md`, sección
"Cambios posteriores — Mejora visual e interactividad de los pasos".

### Formato de transporte (`server.py`)

- [x] Cambiar la respuesta de `/api/sistema` (y de los demás endpoints que
      devuelven procedimiento paso a paso) para incluir, además o en vez
      del texto ya formateado, una representación **estructurada** de cada
      matriz (filas/celdas como listas, no un string ya alineado con
      espacios), reutilizando `formatear()` de
      `metodos/general_metodos.py` para el valor de cada celda. Se agregó
      `_formatear_matriz()` (grillas numéricas puras) y
      `_formatear_estructura()` (pasos/entradas con metadatos mezclados,
      p. ej. índices de fila/columna) en `server.py`, y se creó
      `_armar_bloque_sistema()`/`_armar_bloque_operacion()` para dar forma
      a la respuesta de cada endpoint. Todos los endpoints (`/api/sistema`,
      `/api/conversion`, `/api/vectores`, `/api/matrices`,
      `/api/ecuacion-matricial`) ya devuelven datos estructurados en vez de
      texto pre-renderizado. Verificado con `curl` y comparando contra la
      lógica ya validada de `metodos/`.
- [x] Incluir en cada paso la información necesaria para resaltar el
      pivote y la(s) fila(s)/celda(s) afectadas por esa operación
      (columna/fila del pivote, filas involucradas en "eliminar" o
      "intercambio"), sin recalcular nada nuevo: esta información ya se
      conoce en `metodos/gauss_jordan.py` y `metodos/pivote.py` a partir
      de la tupla de operación (`intercambio`, `normalizar`, `eliminar`).
      Se agregó el índice de columna del pivote a la tupla interna de cada
      paso (sin tocar ningún cálculo) y se expone junto con `tipo`,
      `fila`/`fila_pivote`/`fila_a`/`fila_b` en `resultado["pasos"]`.
      `combinacion_lineal` y `ecuacion_matricial` reutilizan esta misma
      estructura para sus resoluciones internas vía
      `_armar_bloque_sistema()`.
- [x] Mantener la validación y el manejo de errores ya existente
      (`ValueError` -> JSON de error, sin tracebacks); este cambio es solo
      de serialización, no debe tocar ninguna función de cálculo. Se
      volvió a probar con `curl`: dígito inválido en conversión,
      dimensiones incompatibles en matrices, y campo vacío en el sistema
      lineal siguen devolviendo el mismo JSON de error de siempre. Los 17
      tests unitarios/de integración existentes siguen en verde.

### Implementación (`index.html`)

- [x] Reemplazar el `<pre>` de "Mostrar pasos" (Gauss-Jordan/Pivoteo) por
      una secuencia de pasos navegable (tarjetas o timeline), donde cada
      paso muestre su operación destacada y su matriz como una tabla HTML
      real, con el pivote y las celdas afectadas resaltados visualmente.
      Se implementó como un "stepper" con puntos de navegación clicables
      más botones Anterior/Siguiente (`crearStepperGenerico()`), y cada
      paso resalta la celda de pivote (`.celda-pivote`) y las filas
      involucradas (`.fila-resaltada`) usando la metadata `columna`/
      `fila`/`fila_pivote` que ahora expone `server.py`.
- [x] Rediseñar el bloque de "Resultado" (tipo de sistema + solución) como
      una tarjeta/resumen visual diferenciado, en vez de texto plano al
      final del área de resultados. Tarjeta con ícono, color por tipo
      (verde=única, ámbar=infinitas, rojo=incompatible) y borde de acento
      (`tarjetaResultadoSistema()`).
- [x] Rediseñar el bloque de "Comprobación" agregando un indicador visual
      de correcto/incorrecto (color o ícono), conservando el detalle
      numérico de `A_original · X` vs `B_original` que ya se muestra
      (`tarjetaComprobacion()`; usa el nuevo campo `comprobacion.correcto`
      que devuelve `server.py`).
- [x] Aplicar el mismo criterio (pasos como secuencia visual, no bloque de
      texto plano) al procedimiento de la vista de Conversión de bases
      (divisiones sucesivas o combinación lineal de dígitos). Cada paso se
      muestra como una tarjeta de división (`÷`) o de término (`dígito ×
      base^exponente`) dentro del mismo stepper navegable.
- [x] Aplicar el mismo criterio a la vista de Vectores y matrices: pasos
      por componente/elemento en suma/resta/escalar, planteamiento y
      resolución de la combinación lineal, y resolución de la ecuación
      matricial `A·X = B`, sin perder ningún detalle del cálculo que se
      muestra actualmente en texto. Suma/resta/escalar y multiplicación de
      matrices usan una lista compacta de filas (`crearListaPasos()`);
      combinación lineal reutiliza el stepper de sistema lineal para su
      resolución interna y muestra los escalares como chips; ecuación
      matricial agrupa la resolución de cada columna de B en un acordeón
      (`crearAccordion()`) para no saturar la pantalla cuando B tiene
      varias columnas.
- [x] Agregar transiciones o animaciones CSS sutiles (por ejemplo al
      avanzar entre pasos o al revelar el resultado/comprobación),
      cuidando que sigan siendo livianas y no interfieran con la
      funcionalidad ni con la lectura del procedimiento. Se agregaron los
      keyframes `apareceSuave` (tarjetas, tablas, pasos) y
      `aparecerDesdeIzquierda` (filas de la lista compacta, con
      `animation-delay` escalonado), más transición de color/escala en los
      puntos del stepper.
- [x] Mantener `index.html` como archivo único autocontenido (sin
      frameworks ni dependencias externas por CDN) y sin alterar el
      layout general de sidebar + panel ni la paleta de colores base ya
      definidos. Verificado: sigue siendo un solo archivo HTML con CSS/JS
      inline, mismas variables de color (`--color-sidebar`,
      `--color-boton`, `--color-boton-act`, etc.) y mismo layout de
      sidebar + panel.
- [x] Revisar que el nuevo diseño de pasos siga siendo legible en pantallas
      angostas (el proyecto ya contempla un ajuste responsive básico para
      el sidebar). Las tablas de matriz van envueltas en un contenedor con
      `overflow-x: auto`, el stepper y sus controles usan `flex-wrap`, y
      la lista compacta de pasos apila en columna en pantallas angostas;
      se mantiene la media query existente que angosta el sidebar.

### Cierre

- [x] Probar el nuevo diseño de pasos en los cuatro métodos (Gauss-Jordan,
      Pivoteo, Conversión de bases, Vectores y matrices) con
      `server.py` corriendo de verdad. Como la skill de automatización de
      navegador no estaba disponible, se armó un arnés de pruebas con
      `jsdom` (Node) que carga `index.html` tal cual, ejecuta su
      JavaScript real y simula clics/entradas de usuario contra el
      servidor real por `fetch`. Se cubrieron: solución única (con
      navegación del stepper y celda de pivote resaltada), sistema
      incompatible (tarjeta roja + "No es posible comprobar"), infinitas
      soluciones (tarjeta ámbar, variable libre `t`), comprobación
      correcta, conversión decimal→hexadecimal, combinación lineal
      positiva (stepper anidado + chips de escalares), multiplicación de
      matrices, ecuación matricial con acordeón por columna de B, y la
      validación de error por campo vacío (modal). Todas las pruebas
      pasaron. Los 17 tests unitarios/de integración de Python siguen en
      verde. Falta una pasada visual real del usuario en su propia
      máquina para el visto bueno final de estética (jsdom valida
      comportamiento del DOM, no la apariencia).
- [ ] Confirmar con el usuario el visto bueno estético antes de cerrar el
      ciclo (esta mejora es explícitamente de percepción visual, no solo
      funcional).
- [x] Actualizar esta sección de `sdd/task.md` marcando las tareas
      completadas; la spec ya documenta el cambio en su sección "Cambios
      posteriores", así que no requiere un nuevo archivo ni cambiar su
      `Estado`.
