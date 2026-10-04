Estado: implementado

# 004 — Diseño visual (temas y mejoras de interfaz)

**Archivos destino:** `gui.py`, `index.html` y, para la consola, `server.py`
(no toca `metodos/`: es solo presentación).

Esta spec es la **casa de los cambios de diseño visual** de la v2. Empezó con
el modo oscuro/claro y ahí sigue su detalle; los ajustes visuales posteriores
(sidebar, pestaña del navegador, consola del servidor, etc.) se registran en
"Cambios posteriores".

## Propósito

La primera funcionalidad de esta spec: permitir que el usuario cambie entre un **tema claro** (el diseño actual) y un
**tema oscuro** en las dos interfaces de la calculadora, `gui.py` (Tkinter) y
`index.html` (web), con un control visible y fácil de encontrar. El cambio es
puramente visual: no altera ningún cálculo, dato capturado ni resultado
mostrado.

(Convenciones generales de implementación e integración: ver `sdd/plan.md`.)

## Requisitos funcionales

### Comunes a las dos interfaces

- Existen dos temas: **claro** y **oscuro**. El tema claro debe verse igual
  que hoy (la paleta actual no cambia).
- Un **control de cambio de tema** siempre visible en el sidebar (parte
  inferior, junto al indicador de estado del servidor en la web), con
  etiqueta clara del tema al que se cambiará (por ejemplo "Modo oscuro" /
  "Modo claro") y un ícono, para que el usuario nunca dude de qué hace.
- **El cambio es inmediato y no pierde nada:** los datos ya capturados en el
  formulario, la pestaña activa y los resultados/pasos ya mostrados se
  conservan al cambiar de tema. No se recalcula ni se reinicia la vista.
- **Todo el contenido cambia de tema**, sin zonas que se queden "claras" en un
  tema oscuro: sidebar, panel, formularios y campos de captura, tablas de
  matriz, stepper y tarjetas de resultado/comprobación, acordeones,
  pestañas, modal de errores, áreas de texto del procedimiento, y botones
  (incluidos los deshabilitados).
- **Los colores semánticos se conservan en ambos temas** (verde = éxito/única,
  ámbar = infinitas, rojo = error/incompatible, neutro), ajustados en
  luminosidad para mantener contraste. El pivote resaltado y las filas
  afectadas siguen distinguiéndose claramente.
- **Legibilidad:** texto normal con contraste mínimo 4.5:1 sobre su fondo en
  ambos temas (criterio WCAG AA); en particular, verificar el texto sobre
  las tarjetas de colores y sobre las celdas de pivote.
- Los dos temas se definen **en un solo lugar por interfaz** (paleta central),
  no repartidos por el código.

### Interfaz web (`index.html`)

- Los colores se manejan como **variables CSS** (`:root` para el claro y un
  bloque para el oscuro, activado con un atributo en `<html>`, por ejemplo
  `data-theme="dark"`). Los ~60 colores que había escritos directamente en el
  CSS (hex y `rgba`) pasan a variables para que el tema los controle.
- **Tema inicial:** el que el usuario eligió la última vez (guardado en
  `localStorage`); si no hay elección guardada, se sigue la preferencia del
  sistema (`prefers-color-scheme`). El acceso a `localStorage` va protegido
  con `try/catch`: si falla, la página funciona igual, solo sin recordar.
- El tema se aplica **antes de pintar** la página para evitar el parpadeo de
  "claro" al abrir en modo oscuro.
- Sigue siendo un solo archivo autocontenido, sin librerías externas.

### Interfaz de escritorio (`gui.py`)

- Los colores eran constantes de módulo (`COLOR_FONDO`, `COLOR_SIDEBAR`,
  `COLOR_BOTON`, `COLOR_BOTON_ACT`, `COLOR_TEXTO_SB`) y había valores escritos
  directamente (`bg="white"` en las áreas de texto, colores del botón
  deshabilitado en `RoundedButton`, etc.). Se centralizan en un diccionario de
  temas (claro/oscuro) y el resto del código deja de usar colores sueltos.
- Debe cubrir también los widgets nativos de Tk/ttk que no toman el color
  por sí solos: `ttk.Notebook` (pestañas), `Entry`, `OptionMenu`,
  `Radiobutton`, `Text`, `messagebox` no (es del sistema; se acepta que
  conserve su estilo).
- **Sin reconstruir la vista:** al cambiar de tema se recolorean los widgets
  existentes (recorriendo el árbol de widgets) para no perder lo capturado
  ni el resultado mostrado. Los `RoundedButton` (dibujados en `Canvas`) se
  redibujan con los colores nuevos.
- **Tema inicial: claro.** La elección **no se guarda entre sesiones** (queda
  fuera de alcance para no introducir archivos de configuración); la web sí
  la recuerda por ser trivial con `localStorage`.

## Notas de diseño

- Sidebar: ya es oscuro en el tema claro (`#2c3e50`). En el tema oscuro debe
  seguir diferenciándose del panel (más oscuro o con borde), no fundirse con
  él.
- Paleta oscura propuesta (ajustable al implementar, siempre cumpliendo el
  contraste): fondo `#1e2429`, superficies/tarjetas `#262d33`, bordes
  `#39434b`, texto `#e6eaed`, texto secundario `#9aa7b0`; acentos verde
  `#1abc9c`, ámbar `#f39c12`, rojo `#e74c3c` con fondos de tarjeta en
  versión translúcida u oscurecida.
- Fuera de alcance: más de dos temas, selector de colores personalizado,
  guardar el tema de la GUI entre sesiones, sincronizar el tema entre GUI y
  web.

## Cambios y decisiones tomadas al implementar

- **Contraste del tema claro.** La spec pedía 4.5:1 en ambos temas, pero el
  tema claro debe verse igual que hoy y su paleta original ya tiene pares por
  debajo de ese umbral (blanco sobre `#1abc9c` en botones activos: 2.4:1;
  texto tenue `#8a979d`: 3.0:1; pivote `#0e8c73` sobre su fondo: 3.4:1). Se
  respetó "igual que hoy" y el 4.5:1 se garantiza en el **tema oscuro**.
  Mejorar el contraste del claro queda como mejora futura aparte.
- **Web:** en oscuro el acento de botones activos es `#0f7f6b` (blanco sobre
  él: 4.9:1) y el sidebar es más oscuro que el panel.
- **GUI:** el recoloreo usa la base de opciones de Tk (para widgets creados
  después del cambio) más un recorrido del árbol de widgets (para los ya
  creados). El botón de tema es un `RoundedButton` al pie del sidebar.
  `ttk.Notebook` se configura con `ttk.Style`; en el tema claro se restauran
  los valores por defecto de ttk para que se vea como antes.

## Casos de prueba esperados

| Caso | Resultado esperado |
|------|--------------------|
| Web: primera visita con el sistema en oscuro | Abre en oscuro, sin parpadeo |
| Web: elegir claro, recargar | Se mantiene claro (`localStorage`) |
| Web: `localStorage` bloqueado | Funciona; el tema cambia pero no se recuerda |
| Web/GUI: cambiar de tema con una matriz capturada y un resultado a la vista | Datos y resultado intactos, todo recoloreado |
| Web/GUI: recorrer todas las vistas y pestañas en oscuro | Ninguna zona queda con colores del tema claro |
| Web/GUI: tarjetas verde/ámbar/roja, pivote resaltado, botón deshabilitado | Se distinguen y cumplen contraste en ambos temas |
| Cambiar de tema varias veces seguidas | Sin errores ni acumulación de widgets/estilos |

## Cambios posteriores

- **Web: sidebar replegable.** Se añadió un botón con ícono de panel lateral en la cabecera del
  sidebar, junto a "Calculadora", que lo repliega a una franja de 56 px (solo
  queda el botón) y lo vuelve a desplegar. El estado se recuerda en
  `localStorage` (clave `sidebar-colapsado`, protegido con `try/catch`). Solo
  afecta a `index.html`; la GUI no lo incluye.
- **Web: se quitó la nota "Requiere: python server.py"** del pie del sidebar;
  el indicador "Server connected/disconnected" se conserva.
- **Web: título e ícono de la pestaña.** El título es "Calculadora" (antes
  "Calculadora de Matrices") y se añadió un ícono de calculadora (SVG
  incrustado como `data:` URI en `index.html`, color de acento `#1abc9c`).
- **Consola de `server.py`.** El arranque muestra un banner con la URL y los
  endpoints, y cada petición se registra en una línea (hora, método, ruta,
  estado, tiempo, bytes) con el detalle del cálculo (función de `metodos/`,
  entrada y salida) o del error. `/api/estado` no se registra. Solo
  presentación: no cambia las respuestas ni `metodos/`.
- **Web: punto de estado con el sidebar replegado.** Al replegar el sidebar
  queda visible, al pie, el punto del estado del servidor (verde = conectado,
  rojo = desconectado) sin su texto; el texto aparece como tooltip al pasar el
  cursor.
- **Web: adaptable a móviles (spec 008).** El "ventana angosta: una columna,
  sin scroll horizontal" ahora también cubre el layout general: con ≤ 768 px
  el sidebar pasa a un drawer con barra superior, y las matrices, las tablas,
  las pestañas y los controles se adaptan desde 320 px. Ver
  `sdd/specs/v2/008-adaptable-movil.md`.

### Menú de inicio

Archivos: `gui.py`, `index.html` (no toca
`metodos/` ni `server.py`). Se mantiene en ambas interfaces por la regla de
sincronía de `AGENTS.md`.

**Propósito.** Hoy al abrir la calculadora se muestra directamente
Gauss-Jordan. Se añade una pantalla de **Inicio** como punto de entrada, desde
la que el usuario elige el método u operación que quiere usar.

**Requisitos funcionales**

- **Vista de inicio por defecto:** al abrir cualquiera de las dos interfaces se
  muestra Inicio, no Gauss-Jordan.
- **Contenido:** título "Calculadora de Álgebra Lineal", una frase corta de
  subtítulo y una **cuadrícula de tarjetas**, una por módulo (Gauss-Jordan,
  Pivoteo, Conversión de bases, Vectores y matrices), cada una con ícono,
  nombre y una línea de descripción.
- **Navegación:** pulsar una tarjeta abre ese módulo, con el mismo efecto que
  su botón del sidebar (el botón correspondiente queda resaltado).
- **Sidebar:** nueva entrada **"Inicio"** (con ícono de casa) arriba de los
  módulos; queda resaltada cuando Inicio es la vista activa. También se puede
  volver a Inicio desde cualquier módulo. En la web, con el sidebar replegado
  todo lo anterior sigue funcionando (el sidebar no cambia de comportamiento).
- **Sin estado propio:** Inicio no guarda datos, historial ni estadísticas;
  es solo navegación. Los módulos conservan su comportamiento actual.
- **Temas y paleta:** usa solo los colores de la paleta central
  (`PALETAS` en `gui.py`, variables CSS en `index.html`), sin colores sueltos,
  y se ve bien en modo claro y oscuro; cambiar de tema con Inicio a la vista lo
  recolorea sin perder nada.
- **Una sola lista por interfaz:** nombre, ícono y descripción de cada módulo
  salen de la misma lista que construye el sidebar, para no duplicar textos.
- **Web:** la cuadrícula se adapta al ancho (menos columnas en pantallas
  angostas); las tarjetas son botones accesibles (foco visible, `Enter`).
- **GUI:** las tarjetas se construyen con los componentes existentes
  (`RoundedButton`/`Frame`) y se recolorean con el recorrido de widgets del
  cambio de tema.

**Fuera de alcance:** historial de operaciones, accesos recientes, estadísticas,
ajustes, buscador.

**Casos de prueba esperados**

| Caso | Resultado esperado |
|------|--------------------|
| Abrir la web / la GUI | Se muestra Inicio con las 4 tarjetas; "Inicio" resaltado en el sidebar |
| Pulsar cada tarjeta | Abre el módulo correcto y resalta su botón en el sidebar |
| Pulsar "Inicio" desde un módulo | Vuelve al menú |
| Cambiar de tema en Inicio | Todo recoloreado, sin zonas del tema anterior |
| Web: ventana angosta | Tarjetas en una sola columna, sin scroll horizontal |
| Web: sidebar replegado y volver a desplegar | Inicio y navegación intactos |


## Cambios posteriores

- **Contraste 4.5:1 también en el tema claro.** Se oscurecieron solo los
  colores de texto que no llegaban: botón activo (`--color-boton-act`
  `#0e7a67`, blanco encima 5.3:1), `--texto-suave-2/3` y `--texto-tenue`,
  `--exito-texto`, `--alerta-texto`, `--error-texto` y `--pivote-texto`
  (y sus equivalentes de `PALETAS["claro"]` en la GUI: `boton_act`,
  `dif_*`). Los colores de fondo, bordes y puntos de estado no cambian.
- **Token `--acento-texto`** (web): verde de acento para texto/símbolos
  (`=`, `÷`, flecha del acordeón). Antes usaban el relleno `--color-boton-act`,
  que en oscuro daba solo 2.6–3.4:1. Ajustes menores en oscuro:
  `--texto-suave-3` y `--error-texto`.
- Quedan fuera los controles **deshabilitados** (WCAG los exime).
- `tests/test_contraste.py` fija el 4.5:1 para ambos temas de web y GUI.

