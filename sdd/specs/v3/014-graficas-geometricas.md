Estado: implementado

# Spec 014 — Gráficas geométricas (2D y 3D) en los demás módulos

La spec 013 agregó la gráfica de la bisección. Esta spec lleva la misma idea a
los módulos de álgebra lineal **que tienen una interpretación geométrica**:
cuando el problema tiene 2 o 3 dimensiones se dibuja (rectas, planos, flechas,
paralelogramos, cubos); con más dimensiones no hay nada que dibujar y la vista
lo dice con un aviso.

Cumple las "Reglas permanentes" de `sdd/specs/v2/spec_v2.md` (exportar
PNG/PDF, móvil, temas) y copia de la 013: sección **desplegable**, **sin
librerías**, SVG propio e interacción (mover, zoom, restablecer).

## Qué módulos llevan gráfica

| Módulo | Qué se dibuja | Dimensión |
|---|---|---|
| Gauss-Jordan y Pivoteo | Cada ecuación es una recta (2 incógnitas) o un plano (3). La solución es el punto donde se cruzan; sin solución (paralelas / sin punto común) y con infinitas (rectas o planos que coinciden, o una recta de intersección) se ven también. | 2D y 3D |
| Vectores (suma, resta, escalar, combinación lineal) | Flechas desde el origen; la suma/resta con la regla del paralelogramo (punta con cola); en la combinación lineal, los múltiplos de cada vector hasta el objetivo. | 2D y 3D |
| Determinante | Los vectores columna de A y el paralelogramo (2×2) o paralelepípedo (3×3) que forman; su área/volumen es \|det A\| (aplastado si det = 0). | 2D y 3D |
| Matriz inversa | El cuadrado (cubo) unitario, su imagen bajo A y la de A⁻¹: A deforma, A⁻¹ lo devuelve. Singular: la imagen queda aplastada. | 2D y 3D |
| Ecuación matricial A·X = B | Igual que un sistema, para la columna de B que se elija (selector si B tiene varias). | 2D y 3D |
| Multiplicación A × B | El cuadrado (cubo) unitario transformado por B y luego por A (la composición es A·B). | 2D y 3D |

**No llevan gráfica** (decisión): Conversión de bases (no es geométrica) y suma,
resta y producto por escalar de matrices (una suma de matrices no tiene una
imagen geométrica natural; las flechas de los vectores columna no aportan nada
sobre el cálculo). Los vectores de más de 3 componentes, los sistemas con más
de 3 incógnitas y las matrices de más de 3×3 no se grafican: la vista muestra
"La gráfica solo está disponible para 2 o 3 dimensiones".

## Reglas de diseño

- **Una escena, tres pintores.** Python (`src/metodos/escena.py` y
  `escenas.py`) decide **qué** se dibuja y devuelve una *escena* en JSON;
  la web (SVG interactivo), el PNG y el PDF solo la pintan. La web nunca
  calcula contenido matemático (intersecciones, recortes, imágenes de
  matrices). Lo único que se calcula en la web es presentación: marcas de los
  ejes y la cámara 3D (rotar/ampliar).
- **Formato de la escena:** `dim` (2 o 3), `ejes`, `ventana` (2D) o `caja`
  (3D) inicial, `camara` inicial (3D), `elementos`, `leyenda`, `avisos`.
  Elementos: `recta` (2D, infinita: punto + dirección), `segmento`, `flecha`,
  `punto`, `poligono` (planos recortados a la caja, caras, paralelogramos,
  con relleno translúcido). Cada elemento trae `serie` (índice de color),
  `etiqueta` opcional y `guion`.
- **2D** siempre con escala igual en x e y (los ángulos y áreas se ven como
  son); arrastrar mueve, rueda/pellizco/botones hacen zoom, doble clic o
  "Restablecer vista" vuelve. **3D**: arrastrar rota (azimut y elevación),
  rueda/pellizco/botones hacen zoom, "Restablecer vista" vuelve a la cámara
  inicial; proyección ortogonal, caja y ejes con marcas; los elementos se
  ordenan por profundidad.
- **Sección desplegable** igual que la 013 (`crearSeccionDesplegable`),
  **oculta por defecto**, con título "Gráfica" (o el que corresponda).
- **Colores** solo por variables CSS (serie 1–6, ejes, solución) en claro y
  oscuro. El PNG/PDF usa la paleta de impresión.
- **Exportar:** la gráfica va siempre (con y sin pasos) con una leyenda en
  texto, usando una vista fija: 2D con la ventana inicial; 3D con la cámara
  inicial. El plano 3D se dibuja relleno claro + contorno; la recta o punto de
  intersección se dibuja encima.
- Los números se convierten a decimal solo para dibujar; el cálculo con
  fracciones no se toca.
- **Móvil:** las reglas de la 013 (sin scroll horizontal, controles ≥ 44 px,
  `touch-action: none` sobre el lienzo).

## Pasos de implementación (cada uno cierra su ciclo antes del siguiente)

1. Base 2D + sistemas de 2 incógnitas (Gauss-Jordan y Pivoteo).
2. Base 3D + sistemas de 3 incógnitas.
3. Vectores (2D y 3D).
4. Determinante (2×2 y 3×3).
5. Matriz inversa (2×2 y 3×3).
6. Ecuación matricial (selector de columna de B).
7. Multiplicación de matrices A × B.
8. Cierre: documentación, prueba móvil y estado `implementado`.

## Pruebas

`src/tests/test_escenas.py` (recortes, intersecciones, casos de solución
única / paralelas / infinitas / sin gráfica, JSON sin NaN) y, en
`src/features/tests/`, pruebas del PNG/PDF con escena.

## Decisiones tomadas al implementar

- **Sin librerías**, como la 013: SVG propio. Una librería 3D (Three.js,
  Plotly) no habría resuelto lo importante (que Python decida la geometría y
  que el PNG/PDF la dibuje igual) y habría obligado a rehacer polos,
  recortes y temas.
- **La proyección 3D es presentación:** la cámara (azimut/elevación, zoom) y
  las marcas de los ejes se calculan en la web; la fórmula es la misma de
  `features/escena_exportar.proyectar_3d` (con prueba). Todo lo matemático
  (planos recortados a la caja, rectas de corte, imágenes de matrices) viene de
  Python.
- **Formato:** `escena.py` define la escena; el exportador reutiliza el plan de
  primitivas de la 013 y agrega la primitiva `poligono` (relleno + borde; en el
  PNG con línea de barrido, en el PDF con `f`/`S`). En PNG/PDF los rellenos son
  colores ya mezclados con el papel (sin transparencia), por eso los ejes se
  dibujan después de los planos.
- **Caja 3D cúbica** (las tres dimensiones con la misma longitud, margen
  `MARGEN_CAJA`) y 2D con escala igual en x e y: ángulos y áreas se ven como
  son.
- **Sistemas:** las ecuaciones `0 = c` se explican en un aviso; con sistemas sin
  solución de 3 planos se dibujan las rectas donde se cortan de dos en dos
  (línea discontinua). La ecuación matricial grafica una escena por columna de
  B (selector "Gráfica de:" en la web; el archivo exportado trae hasta
  `MAX_ESCENAS_EXPORTADAS` = 4 columnas).
- **Vectores:** suma con regla del paralelogramo (2 vectores) o punta con cola;
  resta como flecha de la punta de b a la de a; combinación lineal con los
  múltiplos encadenados; si b no es combinación se dibuja con línea
  discontinua y un aviso.
- **Inversa y A × B:** muestran el cuadrado/cubo unitario y sus imágenes;
  A × B solo si ambas matrices son cuadradas de 2×2 o 3×3.
- **Sin gráfica:** conversión de bases y suma, resta y escalar de matrices
  (decisión de la spec). Con otras dimensiones, la vista muestra el aviso y el
  archivo exportado no trae la sección.
- **Móvil:** el dedo sobre la gráfica la mueve o la rota (`touch-action:
  none`); la página se desplaza tocando fuera de ella.
- **Pruebas:** `src/tests/test_escenas.py` (escenas de cada módulo y recortes
  2D/3D), `src/features/tests/test_exportar.py` (escenas en PNG/PDF) y
  `prueba_web_movil.js` (abre las gráficas en los 9 anchos y ambos temas).
- **Pendiente del usuario:** visto bueno visual (claro/oscuro, móvil, y los
  PNG/PDF exportados).
