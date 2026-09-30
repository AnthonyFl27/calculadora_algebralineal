Estado: implementado

# 004 — Modo oscuro y modo claro

**Archivos destino:** `gui.py`, `index.html`
(no toca `metodos/` ni `server.py`: es solo presentación).

## Propósito

Permitir que el usuario cambie entre un **tema claro** (el diseño actual) y un
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
  `data-theme="dark"`). Hoy hay unos 60 colores escritos directamente en el
  CSS fuera de `:root` (hex y `rgba`); todos deben pasar a variables para que
  el tema los controle.
- **Tema inicial:** el que el usuario eligió la última vez (guardado en
  `localStorage`); si no hay elección guardada, se sigue la preferencia del
  sistema (`prefers-color-scheme`). El acceso a `localStorage` va protegido
  con `try/catch`: si falla, la página funciona igual, solo sin recordar.
- El tema se aplica **antes de pintar** la página para evitar el parpadeo de
  "claro" al abrir en modo oscuro.
- Sigue siendo un solo archivo autocontenido, sin librerías externas.

### Interfaz de escritorio (`gui.py`)

- Hoy los colores son constantes de módulo (`COLOR_FONDO`, `COLOR_SIDEBAR`,
  `COLOR_BOTON`, `COLOR_BOTON_ACT`, `COLOR_TEXTO_SB`) y hay valores escritos
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
