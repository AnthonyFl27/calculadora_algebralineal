Estado: implementado

# Spec 019 — Método de Newton-Raphson

Tercer método de búsqueda de raíces de f(x) = 0 y el primer **método abierto**
(no usa intervalo ni cambio de signo). Toda la lógica vive en
`src/metodos/newton_raphson.py` y `src/metodos/derivada.py`; la web, el PNG y
el PDF solo presentan.

## Método

Desde una aproximación inicial x₀, la nueva aproximación es donde la recta
tangente corta el eje x:

    x_{n+1} = x_n − f(x_n) / f′(x_n)

- **Derivada:** `derivada.py` la calcula sola por derivación simbólica sobre el
  árbol de `evaluador.py` (suma, producto, cociente, potencia, cadena; sin
  `eval()`) y simplifica lo evidente. El usuario también puede escribirla; en
  ese caso se compara con una diferencia central en x₀ y, si no coincide, hay
  aviso y la comprobación no da «correcta».
- **Criterio de paro:** el mismo que bisección y Regula Falsi,
  ε_a/100 < E con ε_a = |(x_{n+1} − x_n)/x_{n+1}|·100 (ya desde la 1.ª
  iteración). Cada paso informa además el residuo |f(x_{n+1})| y el cambio
  |x_{n+1} − x_n|. También se detiene si f(x_n) = 0 (raíz exacta) o al agotar
  `max_iter` (1–200).
- **Fallos** (se explican en español): f′ = 0 o |f′| < 1e-12, f o f′ fuera del
  dominio, divergencia (|x| > 1e12). Si ocurre en la 1.ª iteración es
  `ValueError`; si ocurre después se conservan los pasos hechos y el resultado
  trae `convergio: False` y el `motivo` (`derivada_cero`, `no_evaluable`,
  `divergencia`, `max_iter`).
- **Continuidad:** solo **avisa** (no bloquea, a diferencia de bisección y
  Regula Falsi): se revisa en la ventana de la gráfica.

## Presentación

- **Servidor:** `POST /api/newton-raphson` con `funcion`, `derivada` (vacía =
  automática), `x0`, `tolerancia`, `max_iter`; bloque `tipo: "newton_raphson"`
  armado por `_armar_bloque_newton`. Exportar: `modulo: "newton-raphson"`.
- **Gráfica:** ventana alrededor de x₀ y las aproximaciones (ancho mínimo
  max(1, |x₀|/2)); `grafica.intervalo` es `null`, `grafica.inicio` es x₀ y cada
  punto de `iteraciones` trae `etiqueta` (`x1`, `x2`…) y `tangente`
  (`[[xₙ, f(xₙ)], [xₙ₊₁, 0]]`). La web dibuja la tangente de la iteración
  elegida con el deslizador. El PNG/PDF dibuja la misma gráfica sin tangentes.
- **Web:** tarjeta de Inicio y entrada de sidebar «Newton-Raphson». Reutiliza
  `vistaRaices(…, "newton_raphson")` (campos x₀ y derivada opcional en lugar de
  a, b y buscador) y `renderNewton`: gráfica, continuidad, tabla
  (n, xₙ, f(xₙ), f′(xₙ), xₙ₊₁, |Δx|, εa), paso a paso, veredicto y comprobación.
- **PNG/PDF:** `exportar.py` (`_documento_newton`), con y sin pasos.
- **Ejercicios:** `nr-01` … `nr-10` (los de la clase: x³ − x − 2 con x₀ = 1.5 y
  x³ − 2x − 5 con x₀ = 2; derivada manual, raíz doble, ciclo, derivada cero y
  salida del dominio).

## Decisiones

- Casos de referencia (documento de la clase): x³ − x − 2, x₀ = 1.5 →
  x₁ = 1.521739130, raíz 1.521379707 en 3 iteraciones (E = 1e-6).
- El método de la **secante** del mismo documento no se incluye aquí: sería la
  spec 020.
- Limitación heredada del evaluador: `log2(x)` y `log10(x)` no se pueden
  escribir (los nombres con dígitos no se reconocen); `log` y `ln` sí.

## Pruebas

`src/tests/test_newton_raphson.py` (derivada contra diferencia numérica, caso de
la clase, fallos), `test_ejercicios.py`, `src/features/tests/test_exportar.py`
y `test_server_exportar.py`.
