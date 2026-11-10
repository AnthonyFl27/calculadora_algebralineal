Estado: implementado

# Spec 017 — Método de Regula Falsi (falsa posición)

Segundo método de búsqueda de raíces de f(x) = 0. Sigue el mismo flujo que la
bisección (spec 016): **1) graficar f(x), 2) revisar la continuidad y 3) iterar
solo si f es continua**. Toda la lógica vive en `src/metodos/falsa_posicion.py`;
la web, el PNG y el PDF solo presentan.

## Método

Con f continua en [a, b] y f(a)·f(b) < 0, en cada iteración c es el punto donde
la **recta secante** por (a, f(a)) y (b, f(b)) corta el eje x:

    c = b − f(b)·(b − a) / (f(b) − f(a))

Se conserva el subintervalo con cambio de signo ([a, c] si f(a)·f(c) < 0, [c, b]
si > 0; si f(c) = 0, c es la raíz exacta).

- **Criterio de paro:** el mismo de la bisección, ε_a/100 < E con
  ε_a = |(c_nuevo − c_anterior)/c_nuevo|·100 desde la 2.ª iteración (ε_a como
  fracción contra E). Aquí es obligatorio mirar c y no el ancho del intervalo,
  porque un extremo suele quedarse fijo y [a, b] no tiende a 0.
- **Sin cota teórica** de iteraciones (no existe una simple): el resultado no
  trae `cota_iteraciones` y la web no muestra esa línea.
- **Aviso** al agotar `max_iter`: Regula Falsi puede ser lenta si un extremo se
  queda fijo; se sugiere subir el máximo, usar otra E o probar la bisección.
- Mismos errores que la bisección (a ≥ b, E ≤ 0, f sin x, f(a) o f(b) = 0, sin
  cambio de signo) y mismo bloqueo por discontinuidad (`bloqueada: True`).
- Reutiliza de `biseccion.py` la validación, el formato, la tabla de texto, el
  texto de continuidad y `f_cerca_de_cero()` (extraída de `biseccion()`;
  `_resultado_bloqueado()` ganó los parámetros `operacion` y `nombre`, sin
  cambiar la bisección). Reutiliza `continuidad.py` y `grafica.py`.

## Presentación

- **Servidor:** `POST /api/falsa-posicion` (mismo cuerpo que `/api/biseccion`);
  el bloque lo arma `_armar_bloque_biseccion(resultado, "falsa_posicion")`
  (`tipo: "falsa_posicion"`). Exportar: `modulo: "falsa-posicion"`.
- **Gráfica:** cada punto de `grafica.iteraciones` trae `secante`
  (`[[a, f(a)], [b, f(b)]]`); la web dibuja la recta secante de la iteración
  elegida con el deslizador. El PNG/PDF dibuja la misma gráfica sin secantes.
- **Web:** tarjeta de Inicio y entrada de sidebar «Regula Falsi». `vistaRaices(
  ejercicio, tipo)` y `METODOS_RAICES` comparten formulario y resultado con la
  bisección; el paso a paso muestra la fórmula de c con los valores.
- **PNG/PDF:** `exportar.py` (`_documento_biseccion` parametrizado), título
  «Método de Regula Falsi»; con y sin pasos, y bloqueada.
- **Consola:** misma línea que la bisección (`/api/falsa-posicion` en `DESTINO`).
- **Ejercicios:** `fp-01` … `fp-09` (básico, intermedio y avanzado: convergencia
  lenta con `x^10 − 1`, sin cambio de signo, 1/x bloqueada, iteraciones agotadas).

## Cambios y decisiones al implementar

- Se corrigió un error previo de la bisección en la web: con una función
  discontinua (bloqueada) `renderBiseccion` fallaba con `bloque.pasos.length`
  porque el servidor no envía `pasos`; ahora usa `(bloque.pasos || [])`.
- Casos de referencia (E = 0.0001): `x² − 2` en [1, 2] → 6 iteraciones,
  x ≈ 1.414201183; polinomio del profesor en [0.55, 1.1] → 5 iteraciones,
  x ≈ 0.7639219773 (la bisección necesita 13).

## Pruebas

`src/tests/test_falsa_posicion.py`, `test_ejercicios.py` (catálogo `falsa-posicion`),
`src/features/tests/test_exportar.py` y `test_server_exportar.py`.
