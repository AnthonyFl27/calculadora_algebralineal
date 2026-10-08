Estado: implementado

# Spec v1 — Resumen (specs 001–003)

Resumen consolidado de las specs `001`–`003`. Los originales se eliminaron; su
texto completo sigue en el historial de git (`git log -- sdd/specs/v1`).
La GUI de Tkinter que mencionaban fue eliminada en la spec 009 (ver
`../v2/spec_v2.md`): aquí solo se conserva lo que sigue vigente en la web.

Previo a SDD (spec 000) ya existían **Gauss-Jordan** y **Pivoteo**
(`src/metodos/gauss_jordan.py`, `pivote.py`).

---

## 001 — Conversión de bases numéricas

**Lógica:** `src/metodos/conversion.py`.

- **Decimal → binario / octal / hexadecimal** (una base a la vez): muestra las
  divisiones sucesivas y los residuos en orden. Admite signo (signo-magnitud;
  no se pide complemento a 2).
- **Binario / octal / hexadecimal / decimal → decimal:** valida que los
  dígitos sean válidos para la base elegida (rechaza un `2` en binario) y
  muestra la **combinación lineal** (cada dígito × potencia de la base), p. ej.
  `1×2² + 0×2¹ + 1×2⁰ = 5`.
- Una sola vista con selector de dirección y de base. Sin límite de dígitos.
- Cambio posterior: el selector "otra base → decimal" no incluía hexadecimal en
  la interfaz (la lógica ya lo soportaba); se agregó, sin tocar `metodos/`.

## 002 — Vectores y matrices

**Lógica:** `src/metodos/vectores_matrices.py`.

- **Vectores en ℝⁿ:** suma, resta, escalar por vector y **combinación lineal**
  (¿`v` es combinación de `v₁…vₖ`? Plantea el sistema y lo resuelve con el
  motor de Gauss-Jordan/Pivoteo, concluyendo con qué escalares). La dimensión
  `n` la indica el usuario antes de capturar.
- **Matrices:** suma y resta (valida mismas dimensiones), escalar, y `A × B`
  (valida columnas de A = filas de B). Si no se cumple, error sin operar.
- **Ecuación matricial `A·X = B`:** arma `[A | B]` y **reutiliza** el motor de
  sistemas; no reimplementa la resolución.
- Todas muestran procedimiento paso a paso, no solo el resultado.
- Vectores y matrices comparten módulo y entrada del sidebar ("Vectores y
  matrices"), con pestañas/sub-vistas por operación.

### 2.4 — Matriz inversa (cambio posterior)

- Gauss-Jordan sobre `[A | I]` → `[I | A⁻¹]`, a elección **Gauss-Jordan** (por
  defecto) o **Pivoteo**. Si una columna no tiene pivote, `A` es singular: se
  informa que la inversa no existe y qué fila quedó en ceros.
- Valida `A` cuadrada y no vacía; celdas con enteros, decimales y fracciones.
- **Comprobación por ambos lados:** `A·A⁻¹` y `A⁻¹·A` deben dar `I`
  (reutiliza la multiplicación de matrices).
- **Decisión de diseño:** `gauss_jordan()` y `gauss_jordan_pivoteo()` ganaron
  el parámetro opcional `columnas_variables=None` (por defecto se comportan
  igual que antes; la inversa lo llama con `n`). Se descartó resolver `A·X = I`
  columna por columna porque no muestra la reducción `[A | I] → [I | A⁻¹]`
  que se enseña en clase.
- Función: `matriz_inversa(matriz, metodo="gauss_jordan", modo="fraccion")`;
  resultado estándar con `operacion`, `entradas`, `matriz_aumentada`, `pasos`,
  `existe`, `motivo`, `resultado` y `comprobacion`. Endpoint `POST /api/inversa`
  (reusa `_armar_bloque_sistema()`); vive como pestaña dentro de "Vectores y
  matrices". Caso de prueba principal: la matriz 3×3 de la práctica 2.2, que no
  es invertible (det = 0). Pruebas en `src/tests/test_vectores_matrices.py`.

## 003 — Interfaz web (`index.html` + `server.py`)

- **`server.py`** (solo librería estándar: `http.server`, `json`) sirve
  `index.html` y expone `metodos/` como endpoints JSON. **No tiene lógica
  matemática**: recibe datos, llama a `metodos/`, convierte `Fraction` a texto
  y responde con los pasos ya formateados. La web no funciona abriéndola con
  doble clic: necesita `server.py` corriendo.
- **`index.html`** es un único archivo autocontenido (HTML + CSS + JS inline),
  sin frameworks, sin CDN. Layout: sidebar con los métodos + panel con
  formulario y resultados.
- **Presentación de pasos:** cada paso es una tarjeta/elemento de secuencia con
  su operación destacada (`F2 -> F2 + 3F1`); las matrices son tablas HTML reales
  con el **pivote** y las **filas afectadas** resaltados; el resultado final va
  en su propia tarjeta; la comprobación lleva una señal clara de
  correcto/incorrecto sin perder el detalle numérico; transiciones CSS sutiles.
- **Formato fracción / decimal** disponible en todas las vistas.
- `GET /api/estado` → `{"ok": true}`; la web lo consulta al cargar y cada 5 s
  y muestra un punto verde/rojo ("Server connected/disconnected") al pie del
  sidebar. No ejecuta lógica de `metodos/`.
- Si `server.py` necesita devolver pasos estructurados (matrices como listas de
  celdas) es solo transporte; el valor de cada celda sale de
  `general_metodos.py`.
