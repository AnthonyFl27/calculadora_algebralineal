Estado: implementado

# Spec 015 — Transformación animada de la matriz (deslizador `t`)

La spec 014 dibuja el efecto de una matriz sobre el cuadrado (cubo) unitario,
pero solo el **antes y el después**. Esta spec agrega un **deslizador `t`**
(de 0 a 1) que muestra el camino entre la identidad y la matriz: la figura se
deforma poco a poco. Así se ve cuándo el cuadrado (cubo) se aplasta
(det = 0), se voltea (det < 0) o se estira.

No es un módulo nuevo: es una mejora de las gráficas que ya existen. Cumple
las "Reglas permanentes" de `sdd/specs/v2/spec_v2.md` (exportar PNG/PDF,
móvil, temas) y las reglas de diseño de la spec 014 (sin librerías, una
escena y tres pintores, sección desplegable).

## Dónde aparece

| Gráfica existente | Qué anima | Dimensión |
|---|---|---|
| Matriz inversa | Identidad → A. Si existe A⁻¹, se muestra aparte la imagen final de A⁻¹ (sin animar). | 2×2 y 3×3 |
| Multiplicación A × B | Dos tramos: `t` de 0 a 0.5 lleva la identidad a B; de 0.5 a 1 lleva B a A·B (se aplica primero B y luego A). | 2×2 y 3×3 |
| Determinante | Identidad → A, con el valor de det de la figura en cada paso. | 2×2 y 3×3 |

**No se anima** (decisión): sistemas, vectores y ecuación matricial (no hay
una transformación que interpolar) ni matrices de más de 3×3 (sin gráfica,
como hasta ahora).

## Qué significa `t`

La matriz intermedia es **M(t) = (1 − t)·I + t·A**: una interpolación lineal
entre la identidad y A. Es la forma más simple de "deformar poco a poco" y
llega exactamente a A en `t = 1`.

Advertencia que debe decir la vista (texto corto junto al deslizador):
las figuras intermedias **no son transformaciones lineales de las que
estudia la materia**, sino una ayuda visual para ver el recorrido; solo
`t = 0` (identidad) y `t = 1` (A) tienen significado algebraico. En
particular, el determinante de M(t) no cambia de signo de forma "natural":
puede pasar por 0 en un `t` intermedio y eso se señala (ver abajo).

## Reglas de diseño

- **Python calcula, la web solo muestra.** La escena (`src/metodos/escenas.py`)
  agrega `animacion`: una lista de **cuadros** precalculados (21 por defecto,
  `t = 0, 0.05, …, 1`; en A × B, 21 por tramo), cada uno con los polígonos y
  flechas de la figura en ese `t` y su `det M(t)`. La web recorre los cuadros
  con el deslizador y **no multiplica ni interpola matrices**. Los números van
  a `float` solo para dibujar; el cálculo con fracciones no se toca.
- **Formato:** `animacion = {"pasos": [...], "paso_final": índice}`. Cada
  paso trae `t`, `elementos` (mismos tipos de la 014: `poligono`, `flecha`)
  y `det` (texto). La escena base (`elementos`) sigue siendo la del
  `t = 1`, así que **PNG, PDF y la web sin animar funcionan igual que hoy**.
- **Ventana y caja fijas.** La ventana 2D / caja 3D se calcula con la unión de
  **todos** los cuadros, para que la cámara no salte mientras se mueve el
  deslizador (si no, la figura parecería quedarse quieta mientras el
  encuadre cambia).
- **Controles:** deslizador `t` (con etiqueta y valor), botón **Reproducir /
  Pausar** (avanza un cuadro cada ~60 ms y se detiene al llegar a `t = 1`),
  y "Restablecer vista" sin cambios. El deslizador responde a teclado
  (flechas). Con `prefers-reduced-motion` no arranca la reproducción sola y
  el botón Reproducir queda disponible.
- **Aviso de determinante cero.** Si el det del cuadro es 0 (o muy cerca, con
  tolerancia fija), la leyenda lo indica: "En este t la figura está aplastada".
- **Exportar:** PNG y PDF muestran la vista fija en `t = 1` (como ahora) y,
  si la matriz pasa por det = 0 en el camino, una línea de texto en la
  leyenda. No se exporta la animación.
- **Móvil:** el deslizador mide al menos 44 px de alto, ocupa todo el ancho
  disponible sin scroll horizontal de la página, y el botón Reproducir es
  táctil (≥ 44 px). A 320 px el deslizador y el botón van en dos filas.
- **Colores:** solo variables CSS (las series ya definidas en la 014). No se
  agregan colores nuevos.
- **Ejercicios de práctica:** no hace falta un catálogo nuevo; los de
  inversa, A × B y determinante ya cargan matrices 2×2 y 3×3. Se agrega al
  menos un ejemplo con det < 0 y otro singular (det = 0) para que se vea el
  efecto.

## Pasos de implementación (cada uno cierra su ciclo antes del siguiente)

1. Lógica: función de interpolación y generación de cuadros en `escenas.py`
   (inversa y determinante, 2×2 y 3×3), con pruebas.
2. Web: deslizador, Reproducir/Pausar y aviso de det = 0 en la gráfica de
   la inversa y del determinante.
3. A × B (dos tramos) en lógica y web.
4. Ejemplos de práctica (det < 0 y singular) y comprobar PNG/PDF en `t = 1`.
5. Cierre: documentación (`AGENTS.md`, `plan.md`), prueba móvil
   (`prueba_web_movil.js` abre las gráficas con animación a los 9 anchos y
   ambos temas) y estado `implementado`.

## Pruebas

- `src/tests/test_escenas.py`: `t = 0` es la figura unitaria; `t = 1`
  coincide con la imagen de A (y de A·B); número de cuadros; ventana que
  contiene todos los cuadros; matriz singular reporta el det = 0 en el
  cuadro final; JSON sin NaN ni infinitos.
- `src/features/tests/test_exportar.py`: PNG/PDF siguen saliendo con la
  escena animada (vista fija en `t = 1`).
- `prueba_web_movil.js`: sin scroll horizontal con el deslizador a 320 y
  375 px; objetivos táctiles ≥ 44 px.

## Pendiente del usuario

Visto bueno visual (claro/oscuro, móvil, PNG/PDF) y confirmar que la
interpolación `(1 − t)·I + t·A` es la que quiere mostrar (la alternativa es
mostrar solo la imagen final con una flecha, sin recorrido).

## Decisiones tomadas al implementar

- **Cuadros:** `PASOS_ANIMACION = 20` por tramo (21 cuadros; A × B trae 41). Cada
  cuadro lleva `t`, `elementos`, `det` (texto) y `aplastado`. `aplastado` es
  verdadero si det = 0 o si el signo cambió respecto al cuadro anterior (el
  determinante pasó por 0 entre los dos).
- **Formato:** `escena["animacion"] = {pasos, paso_final, reemplaza_desde,
  tramos}`. `reemplaza_desde` es el índice del primer elemento de la escena base
  que se sustituye por los del cuadro; los anteriores (p. ej. el cuadrado
  unitario) quedan fijos. En A × B, el tramo 2 dibuja B como fantasma
  (discontinuo) y la figura que se mueve de B a A·B.
- **Web:** `crearControlAnimacion()` (compartida por 2D y 3D) pone el
  deslizador, Reproducir/Pausar (un cuadro cada 60 ms; se detiene si la gráfica
  sale de pantalla) y el aviso de figura aplastada. Al abrir se ve `t = 1`, igual
  que el PNG/PDF. Mover el deslizador pausa la reproducción.
- **Ejercicios:** se agregaron `vm-13` (producto 2×2, para ver el corte y el
  estiramiento) y `vm-14` (reflexión con det < 0, el cuadrado se aplasta en
  t = 0.5). Los singulares ya existían (`det-03`, `vm-12`) y `det-01` ya tiene
  det < 0.
- **Prueba móvil:** `prueba_web_movil.js` mueve el deslizador, reproduce y
  pausa, y comprueba alturas ≥ 44 px y que no haya scroll horizontal.
- **Pendiente del usuario:** visto bueno visual (claro/oscuro, móvil y PNG/PDF)
  y confirmar la interpolación `(1 − t)·I + t·A`.
