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
