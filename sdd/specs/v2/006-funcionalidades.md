Estado: implementado

# 006 — Funcionalidades: exportar respuestas (PNG y PDF)

**Archivos destino:** `features/exportar.py` y `features/__init__.py` (nuevos), `features/tests/`, `server.py`, `gui.py`,
`index.html`.

## Propósito

Que el usuario pueda **guardar su respuesta** (datos, procedimiento, resultado
y comprobación) como imagen **PNG** o documento **PDF**, para entregarla,
imprimirla o estudiarla después. Se accede desde un **ícono de menú (☰)** en la
esquina superior derecha del panel; al pulsarlo se despliegan las opciones de
exportación. La spec deja el menú preparado para sumar más funcionalidades
generales en el futuro (por eso se llama "funcionalidades").

(Convenciones generales de implementación e integración: ver `sdd/plan.md`.)

## Viabilidad y enfoque

Es posible sin librerías externas:

- **PDF:** se escribe a mano (estructura PDF 1.4 en texto, fuente base
  Courier para respetar alineación de matrices, codificación WinAnsi para
  acentos). Solo `io`/`zlib` de la librería estándar.
- **PNG:** se escribe a mano con `zlib` + `struct` (firma, `IHDR`, `IDAT`,
  `IEND`, CRC32). El texto se dibuja con una **fuente bitmap monoespaciada
  incluida en el código** (cubre ASCII, vocales con tilde, ñ, ¿ ¡ y los
  símbolos que usa la calculadora: × − ÷ ← → ✓ |).
- **Carpeta propia:** `metodos/` es exclusiva de los métodos matemáticos. Lo
  que no es un método (exportar y futuras funcionalidades) vive en
  `features/`, que puede importar de `metodos/` pero no al revés.
- **Una sola implementación** en `features/exportar.py`, usada por las dos
  interfaces: el archivo resultante es el mismo en la GUI y en la web, y
  `index.html` sigue sin calcular ni dibujar el documento.

## Flujo de usuario

1. El usuario resuelve algo (Gauss-Jordan, Pivoteo, Conversión, Vectores y
   matrices).
2. En la esquina superior derecha del panel hay un ícono de menú (☰, tres
   líneas, color de acento de la paleta). Mientras **no hay resultado** está
   deshabilitado (atenuado, con tooltip "Resuelve primero para exportar").
3. Al pulsarlo se despliega un menú con:
   - **Exportar como PNG**
   - **Exportar como PDF**
   - Casilla **"Incluir pasos"** (marcada por defecto).
4. Al elegir un formato:
   - **Web:** el navegador descarga el archivo (`<metodo>-<fecha>.png|pdf`).
   - **GUI:** se abre el diálogo "Guardar como" con ese nombre sugerido.
5. Un aviso breve confirma ("Archivo guardado") o, si falla, un mensaje
   amigable (modal / `messagebox`), nunca un traceback.
6. El menú se cierra al elegir una opción, al pulsar fuera de él o con `Esc`.

## Requisitos funcionales

### Comunes a las dos interfaces

- **Ícono y menú desplegable** en la esquina superior derecha de la vista de
  cada módulo con resultado: Gauss-Jordan, Pivoteo, Conversión de bases y
  Vectores y matrices (todas sus pestañas). No aparece en Inicio ni en
  Ejercicios.
- **Contenido del documento**, en este orden: título del método/operación,
  fecha y hora, datos de entrada, pasos (si "Incluir pasos"), resultado final
  (con su tipo: única / infinitas / incompatible, si aplica) y comprobación
  (si existe). Respeta el modo **fracciones / decimales** vigente.
- **Fuente de verdad del documento:** `features/exportar.py` recibe el
  resultado estándar de `metodos/` (el mismo diccionario con tipo, entradas,
  pasos, resultado y comprobación) y lo convierte en un modelo de líneas de
  texto; de ese modelo salen PNG y PDF. No recalcula nada: reutiliza
  `procedimiento_texto()` / formateo de `general_metodos.py`.
- **Paginación y tamaño:** el PDF reparte el contenido en páginas A4 si no
  cabe; el PNG es una sola imagen alta con ancho fijo y fondo claro (siempre
  legible al imprimir, sin depender del tema activo).
- **Colores:** el documento exportado usa una paleta propia de impresión
  definida en un solo lugar de `features/exportar.py` (fondo blanco, texto
  oscuro, acento de resultado); la UI usa solo la paleta central
  (`PALETAS`, variables CSS).
- **Errores amigables:** exportar sin resultado, fallo al escribir el archivo o
  formato desconocido muestran mensaje en español, sin traceback.
- **Sin estado entre sesiones:** no se guarda historial de exportaciones.

### Interfaz web (`index.html`, `server.py`)

- Endpoint `POST /api/exportar` en `server.py`: recibe el mismo cuerpo que el
  endpoint de resolución del módulo más `formato` (`png`/`pdf`) e
  `incluir_pasos`; el servidor llama a la lógica existente y a
  `features/exportar.py` y responde el archivo con `Content-Type` y
  `Content-Disposition: attachment`. Errores: `{"error": "..."}` con 400.
- La consola del servidor registra la petición (formato, módulo, tamaño en
  bytes) como las demás; la ruta se agrega a `DESTINO` y a
  `_descripcion_peticion()` y aparece en el banner de arranque.
- `index.html` usa `fetch()` y descarga el blob; menú accesible (foco visible,
  `Enter`/`Esc`, `aria-haspopup`, `aria-expanded`), adaptable a pantallas
  angostas y con el sidebar replegado.

### Interfaz de escritorio (`gui.py`)

- Botón ☰ montado en la esquina superior derecha del panel, con el estilo de
  los botones existentes (`RoundedButton`/`Menubutton`), recoloreable con el
  cambio de tema (registrar en `_recolorear` si tiene color propio).
- Menú desplegable con las opciones y la casilla "Incluir pasos"; usa
  `filedialog.asksaveasfilename` y escribe los bytes que devuelve
  `features/exportar.py`.

## Notas de diseño

- El ícono sigue la referencia entregada por el usuario: tres líneas
  horizontales en color de acento, sin caja, arriba a la derecha del título.
- El PDF y el PNG deben leerse bien: matrices alineadas en columnas con fuente
  monoespaciada, pivote marcado con corchetes o `*` (no depende del color).
- Si se agregan más funcionalidades generales (p. ej. copiar resultado), van
  como nuevas opciones del mismo menú.

## Fuera de alcance

- Exportar a Word/Excel/LaTeX, enviar por correo, impresión directa, historial
  de exportaciones, exportar capturas de la pantalla tal cual (tablas
  coloreadas de la web) y editar el documento antes de guardarlo.

## Casos de prueba esperados

| Caso | Resultado esperado |
|------|--------------------|
| Sin resultado | Ícono ☰ deshabilitado con tooltip |
| Resolver Gauss-Jordan y abrir el menú | Se despliega con PNG, PDF e "Incluir pasos" |
| Exportar PDF (con pasos) | Archivo que empieza con `%PDF-` y termina en `%%EOF`; contiene datos, pasos, resultado y comprobación |
| Exportar PNG | Archivo con firma PNG válida, dimensiones > 0, descomprimible con `zlib` |
| "Incluir pasos" desmarcado | El documento omite los pasos y conserva datos y resultado |
| Modo decimales | El documento muestra decimales como la pantalla |
| Acentos y símbolos (`ñ`, `á`, `×`, `−`) | Se ven correctos en PNG y PDF |
| Sistema grande (muchos pasos) | PDF con varias páginas; PNG alto sin cortar contenido |
| Conversión de bases y Vectores/matrices | Exportan con su procedimiento y resultado |
| Web: `POST /api/exportar` | Respuesta con archivo adjunto; consola registra formato y bytes |
| Web: formato inválido / sin datos | `{"error": ...}` 400 y modal amigable |
| GUI: cancelar el diálogo "Guardar como" | No pasa nada, sin error |
| Cambiar de tema con el menú a la vista | Menú recoloreado; el documento exportado no cambia |
| Inicio y Ejercicios | No muestran el ícono |

## Cambios y decisiones tomadas al implementar

- **Carpeta `features/`** (no `metodos/`): `metodos/` es solo para métodos
  matemáticos. Contiene `exportar.py`, `_fuente_exportar.py` (fuente bitmap
  generada con `features/tools/generar_fuente.py`, Pillow solo en desarrollo)
  y `tests/`. Las pruebas se corren con
  `python -m unittest discover -s features/tests -t .`.
- **Títulos centralizados:** `titulo_documento()` en `features/exportar.py`
  da el título (y base del nombre del archivo) para las dos interfaces, p. ej.
  `gauss-jordan-20260930-1530.pdf`, `suma-de-vectores-...`.
- **Web:** `POST /api/exportar` recibe
  `{"modulo", "datos", "formato", "incluir_pasos"}`, donde `datos` es el mismo
  cuerpo de la ruta de resolución. El servidor recalcula con `metodos/`
  (función `_calcular_*` de cada módulo, reutilizada por las rutas normales) y
  responde el archivo adjunto. `index.html` recuerda el último cálculo correcto
  y habilita el menú solo mientras su resultado sigue a la vista; cambiar de
  pestaña en Vectores y matrices o limpiar lo deshabilita.
- **Aviso de éxito:** en la web, un toast discreto ("Archivo guardado: ...");
  en la GUI, `messagebox.showinfo` con la ruta.
- **Sin resultado:** el ícono queda atenuado con tooltip "Resuelve primero para
  exportar"; al pulsarlo, aviso. En la GUI, las opciones del menú aparecen
  deshabilitadas con esa misma leyenda.
- **GUI:** el ícono ☰ es un `Canvas` con tres líneas (no depende de que la
  fuente tenga el glifo), color `acento` de `PALETAS`, registrado en
  `_recolorear`. El menú se reconstruye al abrirse.
- **Pivote en el documento:** cada paso indica "pivote en columna N" en texto
  (no depende del color).
- **Pruebas:** `features/tests/test_exportar.py`, `test_server_exportar.py`,
  `test_gui_exportar.py` y `prueba_web_menu.js` (jsdom, a mano: necesita
  `npm install jsdom` y el servidor corriendo).

## Cambios posteriores

- **Ícono:** el botón ya no son las tres barras (☰) sino el ícono de
  **descarga** de Font Awesome (`nf-fa-download`): flecha de trazo grueso sobre
  una bandeja sólida con un punto, en tamaño compacto (web: botón de 34 px con
  SVG de 20 px; GUI: `Canvas` de 32 px dibujado con líneas, polígono y óvalo).
  Usa el color de acento (`--exito-texto` en la web, `acento` de `PALETAS` en
  la GUI). Textos de accesibilidad: "Exportar respuesta". El comportamiento del
  menú no cambia. Donde esta spec dice "☰" o "tres líneas", léase "ícono de
  descarga".
