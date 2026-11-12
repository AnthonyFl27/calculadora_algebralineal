Estado: implementado

# Spec 020 — Método de la secante

Variante de la vista de **Newton-Raphson** (se elige «con la derivada» o «con
la secante» al entrar) para buscar raíces de f(x) = 0 sin derivada.
Es la alternativa a Newton-Raphson cuando no se quiere calcular f′(x): usa dos
aproximaciones y una recta secante. Toda la lógica vive en
`src/metodos/secante.py`; la web, el PNG y el PDF solo presentan.

## Método

Se eligen x₀ y x₁ (distintos); la nueva aproximación es donde la recta secante
por (x₀, f(x₀)) y (x₁, f(x₁)) corta el eje x:

    x_{n+1} = x_n − f(x_n)·(x_n − x_{n−1}) / [f(x_n) − f(x_{n−1})]

En cada iteración se desplazan las aproximaciones (x₀ ← x₁, x₁ ← x₂).

- **Sin derivada ni intervalo:** no pide cambio de signo ni conserva un
  intervalo que encierre la raíz.
- **Criterio de paro:** el mismo que los demás métodos,
  ε_a/100 < E con ε_a = |(x_{n+1} − x_n)/x_{n+1}|·100. Cada paso informa el
  residuo |f(x_{n+1})| y el cambio |x_{n+1} − x_n|. También se detiene si
  f(x_n) = 0 (raíz exacta) o al agotar `max_iter` (1–200).
- **Precauciones del profesor:** si f(x_n) − f(x_{n−1}) = 0 (|·| < 1e-12) la
  fórmula no está definida (`denominador_cero`); un denominador < 1e-6 produce
  un aviso de paso inestable y la comprobación no da «correcta»; x₀ = x₁ es
  error de entrada; salir del dominio y divergir (|x| > 1e12) se explican. Si
  el fallo ocurre en la 1.ª iteración es `ValueError`; si ocurre después se
  conservan los pasos hechos y `convergio` es `False` con su `motivo`.
- **Continuidad:** solo **avisa** (no bloquea), como Newton-Raphson.

## Presentación

- **Servidor:** `POST /api/secante` con `funcion`, `x0`, `x1`, `tolerancia`,
  `max_iter`; bloque `tipo: "secante"` (`_armar_bloque_secante`). Exportar:
  `modulo: "secante"`.
- **Gráfica:** misma ventana que Newton-Raphson; `grafica.intervalo` es `null`,
  `inicio` es x₀ e `inicio2` es x₁; cada punto de `iteraciones` trae
  `etiqueta` (`x2`, `x3`…) y `secante` (`[[xₙ₋₁, f(xₙ₋₁)], [xₙ₊₁, 0]]`).
- **Web:** no es un módulo aparte: la vista de Newton-Raphson trae un selector
  «¿Cómo quieres resolverlo?» (derivada o secante) que cambia los campos (x₀ y
  derivada opcional, o x₀ y x₁), el título y el endpoint. Usa `vistaRaices` y
  `renderSecante`:
  gráfica, continuidad, tabla (n, xₙ₋₁, xₙ, f(xₙ₋₁), f(xₙ), xₙ₊₁, |Δx|, εa),
  paso a paso con el desplazamiento de las aproximaciones, veredicto y
  comprobación.
- **PNG/PDF:** `exportar.py` (`_documento_secante`), con y sin pasos.
- **Ejercicios:** viven en la tarjeta de Newton-Raphson, cada uno con
  `variante` («derivada» o «secante», se muestra como etiqueta). `sec-01` … 
  `sec-09`; `sec-01` es el ejemplo del profesor (x³ − x − 2, x₀ = 1, x₁ = 2,
  E = 0.0001: 6 iteraciones hasta 1.521380) y una prueba compara su tabla.

## Decisiones

- Se pidió como **opción dentro de Newton-Raphson** (no como módulo aparte); el
  motor sigue siendo independiente (`secante.py`) y los PNG/PDF se titulan
  «Método de la secante».
- Caso de referencia: x³ − x − 2, x₀ = 1, x₁ = 2 → x₂ = 1.333333333, raíz
  1.521379707 en 7 iteraciones (E = 1e-6).

## Pruebas

`src/tests/test_secante.py`, `test_ejercicios.py`, y
`src/features/tests/test_exportar.py` y `test_server_exportar.py`.
