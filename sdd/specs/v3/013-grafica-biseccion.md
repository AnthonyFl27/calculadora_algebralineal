Estado: implementado

# Spec 013 — Gráfica de la bisección

El profesor pide una **gráfica** del método de bisección. En la spec 011 quedó
fuera de alcance; esta spec la agrega en la web y en los archivos exportados.
Cumple las "Reglas permanentes" de `sdd/specs/v2/spec_v2.md` (exportar PNG/PDF,
móvil, temas).

## Qué se dibuja

- La curva de f(x) en [a, b]; los **puntos c** de cada iteración; el **intervalo
  [a, b] vigente**; la **raíz aproximada**; los ejes y = 0 (y x = 0 si cae
  dentro), rejilla y marcas con números "bonitos" (pasos 1-2-5).
- Las **discontinuidades** detectadas por la spec 012: línea naranja
  discontinua si es un punto (polo, salto) y banda si es un tramo fuera del
  dominio.
- **Polos:** la curva se corta en dos tramos (no se unen los dos lados de la
  asíntota) y se recorta a la ventana vertical en el borde. La ventana ignora
  los valores extremos (cuantiles 10 %–90 %) cuando hay señales de
  discontinuidad; sin ellas incluye toda la curva. Siempre contiene y = 0.
- La raíz o un punto c cuyo f queda fuera de la ventana (p. ej. f(raíz) ≈ 8502
  en tan x) se dibuja pegado al borde (`fuera: true` en los datos).

## Requisitos

- **Lógica en un solo lugar:** `src/metodos/grafica.py` (`datos_grafica`,
  `marcas`) decide curva, ventana, marcas y puntos. `biseccion()` devuelve la
  clave `grafica`; la web, el PNG y el PDF **solo dibujan** esos datos (misma
  gráfica en los tres). Solo librería estándar; todo finito (JSON sin NaN).
- **Web** (`src/web/index.html`): SVG propio, sin librerías, entre la tarjeta
  de continuidad y la tabla de iteraciones. Un **deslizador** (≥ 44 px) elige
  hasta qué iteración se muestran los puntos c y el intervalo vigente (0 =
  intervalo inicial); debajo, el estado de esa iteración. Se redibuja con el
  ancho real del contenedor (`ResizeObserver`), así el texto no se encoge en
  móvil. Colores solo por variables CSS (claro y oscuro); `role="img"` con
  `aria-label`.
- **Exportar PNG/PDF:** la sección "Gráfica de f(x)" va **siempre** (con y sin
  pasos) más una leyenda en texto. `src/features/grafica_exportar.py` arma un
  *plan* de primitivas (rectángulos, líneas, polilíneas, círculos, textos) y
  dos intérpretes: un rasterizador para el PNG (líneas con suavizado de Wu,
  fuente bitmap del exportador) y operadores vectoriales para el PDF. Paleta
  de impresión propia (`grafica_*` en `PALETA_IMPRESION`). En el PDF la figura
  puede pasar a la página siguiente y su título viaja con ella. Se numeran las
  primeras 5 iteraciones (c1…c5); una etiqueta que pisaría otra se omite.
- Modelo de documento: nueva entrada `(GRAFICA, datos)`; `_ancho_maximo` y
  los escritores la tratan aparte.

## Pruebas

`src/tests/test_grafica.py` (marcas, ventana, polo en dos tramos, recorte sin
tramos planos, tramo fuera del dominio, JSON sin NaN), `test_exportar.py`
(la gráfica entra al documento, pixeles de curva y raíz en el PNG, trazos
vectoriales en el PDF, título de sección con su figura) y
`test_server_exportar.py` (el bloque trae `grafica`).

## Decisiones tomadas al implementar

- **Interactiva (añadido después):** en la web la gráfica se mueve y se
  acerca/aleja. Arrastrar (ratón o un dedo) mueve la vista; la rueda hace
  zoom sobre el cursor (Shift: solo x, Alt: solo y); el pellizco de dos dedos,
  los botones + / − y las teclas (flechas, + − 0) también; doble clic o
  "Restablecer vista" vuelve a la ventana inicial. Sigue siendo SVG propio,
  sin librerías: una librería (Plotly, Chart.js) no resolvía lo importante,
  que es volver a muestrear f al hacer zoom, y habría obligado a rehacer los
  polos, las bandas de discontinuidad y los colores por tema.
- **La web no evalúa f:** al mover o hacer zoom pide la curva de la ventana
  visible a `POST /api/grafica` (`grafica.curva_ventana`, 800 subintervalos y
  medio ancho/alto de relleno por lado, mismas reglas de polos y recorte). Se
  pide con un retraso de 70 ms; mientras llega, se redibuja lo que ya había.
  Los puntos c y la raíz traen `valor` (f real) para poder entrar en la vista.
- En pantallas táctiles el dedo sobre la gráfica la mueve y no desplaza la
  página (`touch-action: none`); se desplaza tocando fuera de ella.
- Las exportaciones PNG/PDF siguen mostrando la ventana inicial.
- La sección "Gráfica de f(x)" es desplegable y **empieza oculta** en cada
  cálculo; la "Tabla de iteraciones" también se puede ocultar (empieza
  visible). Ambas usan `crearSeccionDesplegable`: tarjeta-botón con título,
  una flecha que gira y `aria-expanded`. La
  tarjeta de la gráfica lleva borde marcado y sombra para destacar del fondo.
- La gráfica exportada no tiene deslizador: muestra todas las iteraciones.
- Pendiente del usuario: visto bueno visual (claro/oscuro, móvil, y los
  archivos PNG/PDF exportados).
