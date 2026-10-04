Estado: implementado

# 008 — Web adaptable a móviles

**Archivos destino:** `src/web/index.html` (único archivo de código que cambia),
`AGENTS.md`, `sdd/plan.md`, `sdd/task.md`, `sdd/specs/v2/004-diseño-visual.md`
(nota en "Cambios posteriores").

## Propósito

Que la interfaz web (servida por `server.py`, también desplegada en Render) se
use sin problemas en **cualquier teléfono o tableta**, en vertical y
horizontal, desde **320 px de ancho**. Nada debe quedar cortado y la página no
debe tener scroll horizontal. En escritorio el aspecto y el comportamiento no
cambian.

Las specs 004, 005 y 006 ya afirman "ventana angosta: una columna, sin scroll
horizontal", pero solo se cumplió para tarjetas y listas, no para el layout
general (sidebar), las matrices y las tablas. Esta spec lo corrige.

## Diagnóstico (medido a 390×844)

| # | Problema |
|---|----------|
| 1 | El sidebar es una columna fija (210 px; 150 px bajo 720 px) que ocupa ~40 % de la pantalla; el panel queda en ~240 px. |
| 2 | El contenido se corta: tarjetas de Inicio, columnas de la matriz de Gauss-Jordan y el selector Fracciones/Decimales. |
| 3 | Contenedores con centrado flex + scroll horizontal (`.marco-matriz` y similares): cuando el contenido es más ancho, la parte izquierda **no se puede alcanzar** con scroll. |
| 4 | Campos con 13 px: iOS Safari hace zoom automático al enfocarlos. |
| 5 | Objetivos táctiles menores de 44 px (puntos del stepper, botón de exportar, pestañas, campos, botones de paso). |
| 6 | `100vh` falla con la barra de direcciones dinámica; no hay `viewport-fit=cover` ni `safe-area`. |
| 7 | Menú de exportar, modal y toast sin límite al ancho de la pantalla. |
| 8 | Los estados `:hover` se quedan "pegados" en pantallas táctiles. |

## Excepción a la regla de sincronía

Esta spec es **solo web**. La GUI de escritorio (Tkinter, `src/main.py`) no es
un contexto móvil, por lo que **no se modifica**. Tampoco se toca
`src/metodos/` ni la lógica de `server.py`; `index.html` sigue sin calcular
nada, sin librerías externas y con los colores solo en sus variables CSS.

## Requisitos funcionales

### 8.1 Navegación (sidebar)
- **Breakpoint único: 768 px.** Con ancho **≤ 768 px** se usa la vista móvil
  (cubre teléfonos y tabletas verticales); con más ancho, la vista de
  escritorio actual. Reemplaza al `@media (max-width: 720px)` existente.
- En vista móvil el sidebar deja de ser columna: pasa a una **barra superior**
  con el título, un botón de menú (hamburguesa) y el estado del servidor.
- Las opciones se abren en un **drawer superpuesto** que cubre la altura de la
  pantalla, con scroll propio y el botón de tema claro/oscuro dentro.
- El drawer se cierra al **elegir un módulo**, al **tocar fuera** (overlay) y
  con **`Esc`**. Al cerrarse, el foco vuelve al botón de menú. El botón de menú
  declara `aria-expanded` y `aria-controls`, y el foco se gestiona al abrir.
- El estado "replegado" de escritorio (`sidebar-colapsado` en `localStorage`)
  **no** afecta ni se modifica desde la vista móvil. Al volver a ancho de
  escritorio (rotar o redimensionar) se restaura ese estado.
- En escritorio no cambia nada.

### 8.2 Layout general
- El panel usa menos relleno (≈ 12–16 px) y permite que sus hijos flex/grid se
  encojan; ningún ancestro fija un ancho mínimo.
- Altura de la app con unidades de viewport dinámicas (con respaldo para
  navegadores sin soporte). `viewport-fit=cover` y `safe-area` en la barra
  superior, el panel y el toast.
- Las filas de controles (parámetros, radios Fracciones/Decimales, botones)
  pasan a la línea siguiente cuando no caben; los botones principales ocupan el
  ancho completo o van en columna si no caben.

### 8.3 Matrices y tablas
- **Centrado sin pérdida del borde izquierdo:** en todo contenedor con scroll
  horizontal, el contenido se centra solo si cabe; si no cabe, empieza en el
  borde izquierdo y se puede recorrer completo.
- Las celdas de entrada de matrices y vectores tienen ancho fluido con mínimo
  usable. La app **no limita** el tamaño de la matriz (solo exige enteros
  ≥ 1), por lo que si no cabe en pantalla, el **contenedor** hace scroll
  horizontal dentro de sí mismo, nunca la página. Tamaño de referencia para
  pruebas: **8 ecuaciones × 8 variables** (más la columna de términos
  independientes).
- Las tablas de resultado por paso usan menos relleno y fuente en pantallas
  angostas, dentro de su envoltorio con scroll horizontal propio y sin recorte
  a la izquierda.
- Cuadrículas (grupos de tablas y de vectores, tarjetas de Inicio y de
  ejercicios) pasan a **una columna** cuando no caben dos, sin anchos fijos
  mayores que la pantalla.
- Las pestañas de Vectores y matrices tienen **scroll horizontal propio** y
  todas son alcanzables.

### 8.4 Táctil e iOS
- Campos de entrada y selectores con **16 px** en vista móvil (evita el zoom de
  iOS). No se desactiva el zoom del usuario (sin `maximum-scale`).
- Objetivos táctiles de **≥ 44×44 px**: botones, pestañas, botón de exportar,
  opciones de menús y navegación del stepper. En móvil los puntos del stepper
  se reemplazan por un **contador + botones grandes** (anterior/siguiente).
- Las celdas **no** usan `inputmode="decimal"/"numeric"` (la app acepta
  fracciones como `1/2` y negativos, y esos teclados de iOS no tienen `/` ni
  `-`). Sí llevan `autocomplete="off"`, `autocapitalize="off"`,
  `autocorrect="off"`, `spellcheck="false"` y `enterkeyhint="next"`.
- Controles con `touch-action: manipulation`; los estilos `:hover` solo se
  aplican en dispositivos con hover, para que no queden pegados en táctil.

### 8.5 Superpuestos
- **Modal:** sin ancho mínimo que desborde, ancho máximo de pantalla menos 32 px
  y scroll interno si el texto es largo.
- **Toast:** separado 16 px de los bordes y por encima de la safe-area inferior.
- **Menú de exportar:** el botón y su lista quedan siempre dentro de la pantalla
  (sin desbordes laterales). La descarga de PNG/PDF (`POST /api/exportar` →
  archivo adjunto, disparada por JS) debe funcionar en **iOS Safari y Chrome
  Android**; si algún navegador no la admite, se ofrece una alternativa
  (p. ej. abrir el archivo en una pestaña) sin tocar `server.py`.

### 8.6 Orientación y tamaños
- Funciona en vertical y horizontal; con altura corta (≈ 360 px) el drawer y
  los modales tienen scroll.
- Anchos objetivo: **320, 360, 375, 390, 412, 430, 600, 768 y 1024 px**.

## Fuera de alcance

- Cambios en la GUI de escritorio, en `src/metodos/` o en la lógica de
  `server.py`.
- PWA, instalación o modo offline.
- Rediseño visual: se conservan paleta, tipografía y estilo.

## Casos de prueba esperados (manuales)

La apariencia no la cubren las pruebas unitarias; se prueba con la emulación de
dispositivo de las DevTools y, al menos, una vez en un iPhone y un Android real.

| Prueba | Resultado esperado |
|--------|--------------------|
| Cada ancho de 8.6 en cada módulo (Inicio, Gauss-Jordan, Pivoteo, Conversión, Vectores y matrices con todas sus pestañas, Ejercicios) | `document.documentElement.scrollWidth <= clientWidth` |
| Matriz de referencia 8×8 (+ columna de términos) a 320 px | Se ve y se edita completa; el scroll es solo del contenedor y la columna izquierda es alcanzable |
| Resolver con pasos a 360 px | Tablas por paso, stepper, resultado y comprobación sin recortes |
| Abrir y cerrar el drawer (botón, overlay, `Esc`, elegir módulo) | Funciona y el foco vuelve al botón de menú |
| Girar el dispositivo o redimensionar entre móvil y escritorio | Sin pérdida de datos; estado de escritorio restaurado |
| Plegar el sidebar en escritorio, pasar a móvil y volver | El estado plegado de escritorio se conserva y no se modifica desde móvil |
| Enfocar un campo en iOS Safari | No hace zoom automático |
| Escribir `1/2` y `-3` en una celda desde el teclado móvil | Se pueden teclear ambos |
| Exportar PNG y PDF desde móvil | Se descarga o abre el archivo |
| Modal de error, toast y menú de exportar a 320 px | Completamente dentro de la pantalla |
| Modo claro y oscuro en móvil | Contraste correcto; cambiar de tema no borra datos ni resultados |
| Altura corta (≈ 360 px, horizontal) | Drawer y modales con scroll; nada inalcanzable |
| Escritorio ≥ 1024 px | Idéntico al actual |
| `python -m unittest discover -s src/tests -t src` y `... -s src/features/tests -t src` | Pasan (incluye contraste 4.5:1 en ambos temas) |

Opcional: un script de Playwright en `src/features/tests/` (fuera de la
calculadora, como `prueba_web_menu.js`) que recorra los anchos y compruebe el
`scrollWidth`.

**Pendiente del usuario:** visto bueno visual en sus dispositivos y despliegue
en Render.

## Cambios y decisiones tomadas al implementar

Todo en `src/web/index.html`; no se tocaron `src/main.py`, `src/metodos/` ni la
lógica de `server.py`. Los 10 requisitos se cumplieron; estas son las decisiones
que la spec no fijaba:

- **Un único breakpoint (768 px)**, compartido por el CSS (`@media`) y el JS
  (`MQ_MOVIL = matchMedia("(max-width: 768px)")`). Hay dos ajustes finos
  dentro de la vista móvil: tablas de resultado más compactas bajo 480 px y,
  bajo 380 px, el estado del servidor de la barra superior queda solo como punto.
- **Barra superior + drawer.** `.topbar` es fija (`sticky`) con hamburguesa,
  título y un segundo indicador de estado; el monitor del servidor actualiza
  ambos indicadores con una sola petición. El drawer deja el panel `inert`
  mientras está abierto y bloquea el scroll de fondo. Para que `focus()` entre
  al abrirlo, `visibility` cambia sin retraso al abrir.
- **`sidebar-colapsado` en móvil:** solo se quita la clase `colapsado` mientras
  dura la vista móvil; nunca se escribe en `localStorage`. Al ensanchar, se
  restaura el valor guardado.
- **Centrado seguro con márgenes `auto`** (`.marco-matriz`, `.marco-tabla`,
  `.tabs`) en vez de `justify-content: safe center`, que no es fiable en todos
  los navegadores. Los contenedores con scroll horizontal centran solo si
  cabe. En escritorio el resultado es el mismo salvo antialiasing de bordes.
- **Celdas:** `clamp(56px, 15vw, 68px)` en móvil. Nada limita el tamaño de la
  matriz: si no cabe, hace scroll su contenedor (referencia 8×8 a 320 px).
- **Etiquetas con su campo:** `crearControles()` agrupa cada etiqueta de texto
  con su campo en un `label.campo`, para que no queden separados al saltar de
  línea (y tocar la etiqueta enfoca el campo).
- **Celdas sin `inputmode`:** `crearCelda()` agrega `autocomplete`,
  `autocapitalize`, `autocorrect`, `spellcheck` y `enterkeyhint`, pero no
  `inputmode`, porque los teclados numéricos de iOS no tienen `/` ni `-`.
- **Stepper:** en móvil se oculta la fila de puntos (CSS) y quedan el contador
  y los botones grandes; en escritorio no cambia.
- **Menú de exportar:** en móvil el botón es de 44 px, tiene fondo propio y su
  contenedor pegajoso se ancla bajo la barra superior
  (`top: calc(56px + env(safe-area-inset-top))`).
- **Descarga PNG/PDF:** se mantiene `<a download>` con un blob. Como
  alternativa, en móvil (o si el navegador no admite `download`) el aviso
  incluye un enlace "Abrir" que abre el archivo en otra pestaña; la URL del
  blob vive 60 s (antes 1 s). No se tocó `server.py`.
- **Modal y toast:** el modal usa `min/max-width` con `100vw − 32px`, `dvh` y
  scroll interno (válido también en escritorio); el toast va de borde a borde
  con 16 px de margen en móvil.
- **Extra no previsto:** la tarjeta de resultado (`pre.tarjeta-cuerpo-mono`)
  desbordaba la página con números grandes; se añadió `overflow-wrap: anywhere`.
- **Servidor sin cambios, pero ojo:** `server.py` convierte los sistemas de
  Gauss-Jordan/Pivoteo con `float()`, así que esas celdas no aceptan `1/2`
  (las de vectores y matrices sí). No es parte de esta spec.

**Verificación.** `python -m unittest discover -s src/tests -t src` (63) y
`... -s src/features/tests -t src` (30) en verde. Además,
`src/features/tests/prueba_web_movil.js` (Playwright, opcional; ver su
cabecera) recorre los 9 anchos de 8.6 en todos los módulos y pestañas, el
drawer, la matriz 8×8 a 320 px, los tamaños táctiles, las descargas, el tema y
el contraste: 261 comprobaciones sin fallos en Chromium. A 1024 y 1280 px la
web es idéntica a la anterior, salvo antialiasing en las esquinas de las
pestañas.
