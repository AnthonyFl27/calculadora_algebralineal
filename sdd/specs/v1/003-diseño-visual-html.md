Estado: implementado

# 003 — Diseño visual web (index.html)

**Archivos destino:** `index.html`, `server.py`

## Propósito

Ofrecer una segunda interfaz para la calculadora, esta vez en forma de página
web (`index.html`), que replique el mismo diseño visual y flujo de trabajo de
`gui.py` (sidebar con los métodos, panel de formulario y área de resultados
con el procedimiento paso a paso), pero ejecutándose en el navegador. Esta
interfaz web **no reimplementa ninguna lógica matemática**: delega siempre en
los mismos módulos ya existentes en `metodos/` (Gauss-Jordan, Pivoteo,
Conversión de bases, Vectores y matrices), igual que hace `gui.py` hoy.

(Convenciones generales de implementación e integración: ver `sdd/plan.md`.)

## Funcionalidad 1 — Réplica visual del diseño de `gui.py`

- `index.html` reproduce el mismo layout que la interfaz Tkinter: sidebar
  fija a la izquierda con la lista de métodos disponibles, y panel derecho
  con el formulario del método seleccionado y un área de resultados en
  fuente monoespaciada donde se muestra el procedimiento paso a paso.
- Debe usar una paleta de colores, tipografías y estilo de botones
  equivalentes (en CSS) a los ya definidos en `gui.py`
  (`COLOR_FONDO`, `COLOR_SIDEBAR`, `COLOR_BOTON`, `COLOR_BOTON_ACT`,
  `FUENTE_TITULO`, `FUENTE_MONO`, etc.), de modo que ambas interfaces se
  sientan como la misma calculadora.
- Debe incluir las mismas 4 entradas del sidebar que existen hoy en
  `METODOS` dentro de `gui.py`: Gauss-Jordan, Pivoteo, Conversión de bases, y
  Vectores y matrices (con sus sub-vistas de vectores, matrices, y ecuación
  `A·X = B`), con el mismo comportamiento funcional: capturar dimensiones,
  generar el formulario/matriz dinámicamente, resolver, mostrar pasos,
  comprobar resultado donde aplique, y elegir formato de salida
  (fracción/decimal).

## Funcionalidad 2 — Servidor local que expone `metodos/`

- Un script Python (`server.py`), usando **únicamente la librería estándar**
  (por ejemplo `http.server` y `json`, sin frameworks como Flask o Django),
  sirve `index.html` y expone la lógica de `metodos/` mediante peticiones
  HTTP hechas desde el navegador (`fetch`), respondiendo en formato JSON.
- Este servidor **no contiene lógica matemática propia**: solo recibe los
  datos capturados en el formulario web, llama directamente a las mismas
  funciones que ya usa `gui.py` (`metodos/gauss_jordan.py`,
  `metodos/pivote.py`, `metodos/conversion.py`,
  `metodos/vectores_matrices.py`, `metodos/general_metodos.py`), y devuelve
  el resultado —incluyendo los pasos del procedimiento— en un formato que
  `index.html` pueda renderizar.
- Como el navegador no puede ejecutar Python por sí solo, `index.html` no
  funciona en modo standalone (abrir el archivo con doble clic); requiere
  levantar `server.py` primero, de forma análoga a como hoy se ejecuta
  `python gui.py`. Este requisito debe quedar documentado con claridad para
  quien use el proyecto.

## Notas de diseño

- `index.html` debe ser un único archivo autocontenido: HTML, CSS y
  JavaScript inline en el mismo archivo, sin build ni frameworks de
  frontend (React, Vue, etc.) ni dependencias externas cargadas desde CDN.
- `server.py` es el único componente Python nuevo que introduce este
  módulo; su responsabilidad se limita a exponer `metodos/` vía HTTP, nunca
  a duplicar o reimplementar cálculo alguno.
- Los resultados devueltos por `metodos/` pueden incluir objetos `Fraction`;
  `server.py` es responsable de convertirlos a una representación
  serializable (texto) antes de enviarlos como JSON, sin alterar la lógica
  de cálculo en sí.
- `gui.py` y los métodos que ya expone (nunca se reemplazan ni se tocan)
  sirven como referencia funcional exacta de qué debe hacer cada vista
  equivalente en la web.

## Cambios posteriores — Mejora visual e interactividad de los pasos

La primera versión de `index.html` cumple el objetivo funcional (réplica
exacta de `gui.py`, delegando todo el cálculo en `metodos/`), pero su
presentación se siente básica: el procedimiento paso a paso se muestra
como un único bloque de texto monoespaciado dentro de un `<pre>`, igual
que el widget `Text` de Tkinter. Eso es aceptable para una interfaz de
escritorio, pero en la web se puede aprovechar mejor el medio sin perder
la simplicidad ni las restricciones del proyecto.

**Objetivo de esta mejora:** que la calculadora web se sienta más
interactiva y menos plana al mostrar el procedimiento, manteniendo el
resto de la interfaz simple y funcional (sin frameworks, sin
dependencias externas, sin tocar la lógica matemática de `metodos/`).

### Qué debe cambiar

- La presentación de "pasos" (en Gauss-Jordan/Pivoteo, Conversión de
  bases, y Vectores y matrices) deja de mostrarse como un solo bloque de
  texto continuo. En su lugar, cada paso del procedimiento se presenta
  como una unidad visual independiente (tipo tarjeta o elemento de una
  secuencia/timeline), con su propia operación destacada (por ejemplo la
  notación `F2 -> F2 + 3F1`) y su matriz o cálculo correspondiente.
- Las matrices dejan de renderizarse únicamente como texto alineado con
  espacios; se muestran como una tabla/grid real en HTML, de modo que se
  pueda resaltar visualmente el pivote de cada paso y, si aplica, las
  filas o elementos afectados por esa operación.
- El resultado final (tipo de sistema, solución, o resultado de la
  operación vectorial/matricial) se destaca en su propia tarjeta o
  bloque visual diferenciado, en vez de aparecer como texto plano al
  final del mismo `<pre>`.
- La comprobación (`A_original · X = B_original`) incluye una señal
  visual clara de correcto/incorrecto (color o ícono), sin perder el
  detalle numérico de la comparación que ya se muestra hoy.
- Se permiten transiciones o animaciones CSS sutiles (por ejemplo al
  cambiar de paso o al revelar el resultado), siempre livianas y sin
  afectar la funcionalidad.

### Qué se mantiene igual

- Sigue siendo un único archivo `index.html` autocontenido (HTML, CSS y
  JavaScript inline), sin frameworks ni dependencias externas por CDN.
- El mismo layout general (sidebar + panel derecho) y la misma paleta de
  colores base ya definidas en la Funcionalidad 1.
- `server.py` sigue sin contener lógica matemática propia: si necesita
  devolver los pasos de forma estructurada (por ejemplo, cada matriz
  como una lista de filas/celdas en vez de un texto ya formateado) para
  que `index.html` pueda renderizarlos de forma interactiva, ese cambio
  es solo de **serialización/formato de transporte**, nunca de cálculo;
  el valor de cada celda se sigue obteniendo con las funciones de
  formateo de `metodos/general_metodos.py`.
- La calculadora de escritorio (`gui.py`) no se toca ni se le exige
  replicar esta mejora visual; ambas interfaces pueden divergir en
  presentación siempre que compartan la misma lógica de `metodos/`.

## Cambios posteriores — Indicador de estado del servidor

Como `index.html` depende por completo de `server.py` (no funciona en modo
standalone, ver Funcionalidad 2), se agregó un indicador visual en la
esquina inferior izquierda del sidebar, justo encima de la nota "Requiere:
python server.py", que muestra si el servidor sigue respondiendo:

- Un punto de color (`.estado-punto`) verde (`conectado`) o rojo
  (`desconectado`), con el texto "Server connected" / "Server disconnected"
  al lado.
- `server.py` expone un endpoint nuevo `GET /api/estado` que responde
  `{"ok": true}`; no ejecuta ninguna lógica de `metodos/`, es solo una
  señal de "el servidor sigue vivo".
- `index.html` hace `fetch("/api/estado")` una vez al cargar la página y
  luego cada 5 segundos (`setInterval`); si la petición falla o responde
  con un estado distinto de 2xx, el indicador pasa a rojo/desconectado.
- Es un cambio puramente de presentación e infraestructura (un endpoint de
  salud, sin parámetros ni cálculo): no toca `metodos/` ni la lógica de
  ningún otro endpoint existente.
