Estado: implementado

# 005 — Ejercicios para práctica

**Archivos destino:** `metodos/ejercicios.py` (nuevo, solo datos), `server.py`
(endpoint de lectura), `gui.py`, `index.html`, `tests/`.

## Propósito

Que el usuario pueda **practicar** con ejercicios ya preparados: elige un
método, ve una lista de ejercicios de ejemplo y, con un botón **"Probar
ejercicio"**, los datos se cargan solos en la calculadora de ese método, listos
para resolver. Así no tiene que inventar ni teclear matrices para ver cómo
funciona cada método.

(Convenciones generales de implementación e integración: ver `sdd/plan.md`.)

## Flujo de usuario

1. **Inicio.** Debajo de las tarjetas de métodos hay un **separador** (línea
   divisoria) y, bajo él, una sección aparte para lo que se vaya agregando más
   allá de los métodos. Su primera tarjeta es **"Ejercicios para práctica"**.
2. **Elegir método.** Al pulsarla se abre una pantalla con la pregunta
   **"¿Para qué método te gustaría tener ejercicios de ejemplo y práctica?"** y
   los métodos ya existentes como opciones (Gauss-Jordan, Pivoteo, Conversión
   de bases, Vectores y matrices).
3. **Lista de ejercicios.** Al elegir un método aparece la lista de ejercicios
   de ese método. Cada ejercicio muestra: título, dificultad (básico /
   intermedio / avanzado), una breve descripción de qué se practica y una
   vista previa de los datos (por ejemplo la matriz aumentada).
4. **Probar ejercicio.** Cada ejercicio tiene un botón **"Probar ejercicio"**:
   abre la vista del método con los datos **ya cargados** en el formulario. El
   usuario pulsa Resolver (no se resuelve solo), de modo que el ejercicio es
   una práctica y no una respuesta servida.
5. **Volver.** Desde la lista se puede regresar a la elección de método, y
   desde esta a Inicio.

## Requisitos funcionales

### Comunes a las dos interfaces

- **Sección en Inicio:** separador + tarjeta "Ejercicios para práctica"
  (ícono, nombre y una línea de descripción), con el mismo estilo que las
  tarjetas de métodos. El diseño deja espacio para añadir más tarjetas en esa
  sección en el futuro sin tocar la de métodos.
- **Sidebar:** nueva entrada **"Ejercicios"** debajo de los métodos, separada de
  ellos por otro separador (un módulo nuevo = una entrada nueva en el sidebar);
  queda resaltada mientras se está en cualquier pantalla de esta sección.
- **Catálogo único de ejercicios:** vive en `metodos/ejercicios.py` (solo
  datos, sin lógica matemática ni librerías externas). Ni `gui.py` ni
  `index.html` escriben ejercicios a mano: los leen de ese catálogo.
- **Cada ejercicio** tiene: `id`, `titulo`, `dificultad`, `descripcion`,
  `datos` (lo necesario para rellenar el formulario del método) y
  `resultado_esperado` (p. ej. `unica`, `infinitas`, `incompatible`, o el valor
  de una conversión), usado por las pruebas y opcionalmente como pista; no se
  muestra como solución.
- **Contenido mínimo por método:**
  - *Gauss-Jordan* y *Pivoteo*: al menos 5 ejercicios cada uno, que cubran
    solución única, infinitas soluciones y sistema incompatible, con tamaños
    distintos (2×2, 3×3, alguno no cuadrado); en Pivoteo, al menos uno donde el
    pivote natural sea 0 o muy pequeño y el intercambio de filas importe.
  - *Conversión de bases*: al menos 5 (decimal→binario, octal, hexadecimal;
    binario/octal/hexadecimal→decimal; un negativo).
  - *Vectores y matrices*: al menos un ejercicio por cada operación ya
    disponible (suma, resta y escalar de vectores; combinación lineal; suma,
    resta, escalar y multiplicación de matrices; ecuación matricial e
    inversa, incluyendo un caso no invertible). "Probar ejercicio" abre la
    pestaña correspondiente a la operación.
- **Cargar datos sin resolver:** "Probar ejercicio" rellena campos y selectores
  (tamaño, método, operación, bases, etc.) y deja la vista lista; conserva el
  comportamiento normal de la vista (validaciones, Resolver, Mostrar pasos,
  Comprobar).
- **Las vistas de métodos aceptan datos iniciales opcionales.** Sin ellos se
  comportan exactamente como hoy; no se duplica la lógica del formulario.
- **Temas y paleta:** solo colores de la paleta central (`PALETAS`, variables
  CSS); se ve bien en modo claro y oscuro, y cambiar de tema con esta sección
  a la vista no pierde nada.
- **Sin estado entre sesiones:** no se guarda progreso, ejercicios resueltos ni
  historial.

### Interfaz web (`index.html`, `server.py`)

- `server.py` expone el catálogo con `GET /api/ejercicios` (solo lectura, sin
  lógica matemática), con la forma
  `{"ok": true, "ejercicios": {"<método>": [ {...}, ... ]}}`. La consola del
  servidor registra la petición como las demás.
- `index.html` pide el catálogo con `fetch()` al abrir la sección; si falla,
  muestra el mensaje de error amigable (modal existente), sin JSON crudo.
- Las tarjetas y la lista se adaptan a pantallas angostas (una columna, sin
  scroll horizontal) y los botones son accesibles (foco visible, `Enter`).
- Con el sidebar replegado la navegación sigue funcionando.

### Interfaz de escritorio (`gui.py`)

- `gui.py` importa el catálogo directamente desde `metodos/ejercicios.py`.
- Las pantallas de esta sección (elección de método y lista de ejercicios) son
  vistas nuevas montadas en el panel derecho, con los componentes existentes
  (`RoundedButton`, `Frame`, `Label`) y recoloreables con el cambio de tema.
- La lista es desplazable si no cabe en la ventana.

## Notas de diseño

- El separador de Inicio es una línea fina del mismo estilo que el del sidebar
  (color de borde de la paleta), seguida de un pequeño encabezado de sección
  (por ejemplo "Práctica") para que se entienda que es un grupo distinto al de
  los métodos.
- Dificultad como etiqueta de color neutro/semántico discreto (verde =
  básico, ámbar = intermedio, rojo = avanzado), con texto legible (contraste
  4.5:1 en oscuro).
- Los ejercicios son **datos de práctica**, no un examen: no hay puntaje ni
  corrección automática.

## Fuera de alcance

- Generar ejercicios aleatorios, puntajes, historial o progreso, mostrar la
  solución completa dentro de la lista, editar o agregar ejercicios desde la
  interfaz, y cronómetros o modos de evaluación.

## Casos de prueba esperados

| Caso | Resultado esperado |
|------|--------------------|
| Inicio | Separador y tarjeta "Ejercicios para práctica" debajo de las de métodos |
| Pulsar la tarjeta | Aparece la pregunta y los 4 métodos como opciones |
| Elegir Gauss-Jordan | Lista con ≥ 5 ejercicios (título, dificultad, datos) |
| "Probar ejercicio" en Gauss-Jordan | Se abre la vista con la matriz cargada y sin resolver; Resolver da el tipo esperado |
| "Probar ejercicio" en Pivoteo / Conversión | Datos, método y bases cargados correctamente |
| "Probar ejercicio" en Vectores y matrices | Se abre la pestaña de la operación con los datos cargados |
| Cada ejercicio del catálogo, resuelto con `metodos/` | Coincide con su `resultado_esperado` (prueba automática en `tests/`) |
| Volver desde la lista / desde la elección | Regresa a la pantalla anterior / a Inicio |
| Web: `GET /api/ejercicios` | `{"ok": true, "ejercicios": {...}}` con los 4 métodos |
| Web: catálogo no disponible | Modal de error amigable |
| Cambiar de tema con la sección a la vista | Todo recoloreado, sin perder la pantalla |
| Web: ventana angosta | Una columna, sin scroll horizontal |

## Cambios y decisiones tomadas al implementar

- **Vista previa calculada en `metodos/ejercicios.py`.** `catalogo()` añade a
  cada ejercicio un campo `vista_previa` (texto de varias líneas con los
  datos) para que la web y la GUI muestren exactamente lo mismo sin duplicar
  el formato.
- **Datos iniciales por parámetro.** Las vistas de método aceptan un
  `ejercicio` opcional (`mostrarVista(metodo, ejercicio)` en la web,
  `mostrar_vista(fabrica, nombre, ejercicio)` en la GUI); sin él se comportan
  como siempre. "Probar ejercicio" nunca resuelve solo.
- **Navegación.** La pantalla de elección tiene "← Inicio"; la lista tiene
  "← Elegir otro método"; el sidebar ("Ejercicios") queda resaltado en ambas.
  Al probar un ejercicio se resalta el método que se abre.
- **Dificultad** con colores semánticos de la paleta (verde/ámbar/rojo) en las
  dos interfaces; en la GUI, `EtiquetaDificultad` se recolorea con el tema.
- **GUI:** la lista es un `Canvas` desplazable (barra y rueda del ratón).
- **Pruebas:** `tests/test_ejercicios.py` (catálogo contra `metodos/`),
  `tests/test_gui_ejercicios.py` (los 34 ejercicios se cargan y se resuelven;
  flujo Inicio → elección → lista → probar; tema) y `tests/test_gui_inicio.py`.
