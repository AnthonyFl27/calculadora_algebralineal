Estado: implementado

# Spec 011 — Método de Bisección (búsqueda de raíces)

Enunciado del profesor: *codificar un programa que resuelva f(x) = 0 mediante el
Método de Bisección.* Es el primer método de **búsqueda de raíces** del
proyecto (los demás son de álgebra lineal), así que entra como módulo nuevo con
entrada propia en el sidebar e Inicio. Cumple las "Reglas permanentes" de
`sdd/specs/v2/spec_v2.md` (exportar PNG/PDF, móvil, temas, ejercicios, consola).

## Algoritmo (según la guía del profesor)

1. Validar f(a)·f(b) < 0 (f continua en [a, b]); si no, error amigable.
2. c = (a + b) / 2.
3. Evaluar f(c). Si f(c) = 0, la raíz es c y termina.
4. Si f(a)·f(c) < 0 → la raíz está en [a, c] (b = c); si > 0 → en [c, b] (a = c).
5. Desde la 2.ª iteración: ε_a = |(c_nuevo − c_anterior) / c_nuevo| · 100 %.
6. Repetir hasta ε_a < E o llegar al máximo de iteraciones.

**Entradas:** f(x), a, b, tolerancia E, máximo de iteraciones.
**Salidas:** raíz aproximada, nº de iteraciones, f(raíz), ε_a final y tabla de
iteraciones (i, a, b, c, f(c), ε_a).

## Requisitos

- **Función escrita como texto** (`x^4 - 5x^3 + 0.5x^2 - 11x + 10`). Se analiza
  con un evaluador propio (`src/metodos/evaluador.py`); **nunca `eval()`**.
  Soporta `+ − * / ^` (y `**`), paréntesis, multiplicación implícita (`2x`,
  `3(x+1)`), `x`, constantes `pi` y `e`, y funciones `sin/sen cos tan asin acos
  atan sinh cosh tanh exp ln log(base 10) log2 sqrt cbrt abs`. Usa `math` de la
  librería estándar (permitida: no es una librería matemática externa).
- a, b y E también aceptan expresiones constantes (`pi/2`, `1e-4`).
- **Decisión sobre E:** el criterio de paro compara ε_a **como fracción** con E
  (ε_a/100 < E), mientras la tabla muestra ε_a en %. Así E = 0.0001 reproduce el
  caso del profesor (13 iteraciones, raíz 0.7639709473); comparando E contra el
  porcentaje saldrían 20. La vista lo aclara junto al campo ("0.0001 = 0.01 %").
- Validaciones con `ValueError` en español: función vacía o mal escrita, a ≥ b,
  E ≤ 0, máximo de iteraciones fuera de 1–200, f no evaluable (división entre
  cero, dominio) y **sin cambio de signo** (mensaje con f(a) y f(b); caso
  especial si un extremo ya es raíz).
- Aritmética en `float` (la función puede ser trascendente; no aplica el modo
  fracciones/decimales). Los números se muestran con 10 cifras significativas.
- **Resultado:** raíz, iteraciones, f(raíz), ε_a final y el motivo de paro
  (`tolerancia`, `raiz_exacta` o `max_iter`). Si se agotan las iteraciones sin
  alcanzar E se avisa (tarjeta ámbar), no es error.
- **Cota teórica** informativa: n ≥ log₂((b − a)/E) (error absoluto = E).
- **Comprobación:** se vuelve a evaluar f en la raíz y en los extremos del
  intervalo final (debe seguir habiendo cambio de signo) y se verifica que se
  alcanzó la tolerancia. **Advertencia de discontinuidad:** si |f(raíz)| no es
  menor que min(|f(a₀)|, |f(b₀)|) la bisección pudo converger a un polo (p. ej.
  1/x en [−1, 2]) y no a una raíz.
- **Procedimiento paso a paso:** tabla de iteraciones completa y un stepper con
  la decisión de cada iteración (signo de f(a)·f(c) y qué extremo se actualiza).
- Estructura de resultado: `operacion`, `entradas`, `inicial`, `pasos`,
  `resultado`, `cota_iteraciones`, `advertencias`, `comprobacion`.

## Integración

- Lógica: `src/metodos/evaluador.py` (reutilizable por los siguientes métodos
  de raíces) y `src/metodos/biseccion.py`.
- Web: `POST /api/biseccion`; entrada `biseccion` en `METODOS`; exportable
  (`CALCULOS["biseccion"]`, PNG/PDF con o sin pasos); consola del servidor.
- Ejercicios de práctica (≥ 5): caso del profesor, √2, x³−x−2, cos x = x,
  e⁻ˣ = x, sin cambio de signo, discontinuidad (1/x) y paro por máximo de
  iteraciones.
- Pruebas: `src/tests/test_evaluador.py`, `test_biseccion.py`,
  `test_ejercicios.py`; `src/features/tests/test_exportar.py` y
  `test_server_exportar.py`.

## Casos de referencia

| f(x) | [a, b] | E | Resultado |
|---|---|---|---|
| x⁴ − 5x³ + 0.5x² − 11x + 10 | [0.55, 1.1] | 0.0001 | 13 iteraciones, raíz ≈ 0.7639709473 |
| x² − 2 | [1, 2] | 0.0001 | ≈ 1.41421 |

La guía del profesor trae valores erróneos en su Ejercicio 1 (f(0.55) = +3.1098
y raíz 0.7691): los valores correctos son f(0.55) = +3.3609 y raíz ≈ 0.7640. No
se usan como referencia.

## Fuera de alcance

Regla Falsa, Newton-Raphson, Secante y Lin-Bairstow (solo se mencionan en la
guía como referencia); gráfica de f(x).

## Cambios y decisiones tomadas al implementar

- El evaluador (`evaluador.py`) también acepta `**`, `×`, `÷`, `²`, `³`, `π`,
  coma decimal, notación científica (`1e-4`; para el producto con la constante
  e se escribe `2*e`), mayúsculas y letras pegadas (`xe` = x·e). Las funciones
  exigen paréntesis (`sin(x)`, no `sin x`) para evitar ambigüedades. Límites:
  200 caracteres y 40 niveles de anidación.
- La advertencia de discontinuidad se evalúa también cuando no hay convergencia
  (1/x en [−1, 2] oscila y agota las iteraciones): salta si |f(raíz)| supera a
  max(|f(a₀)|, |f(b₀)|), o, con convergencia, si no es menor que
  min(|f(a₀)|, |f(b₀)|) (p. ej. tan(x) en [1, 2]).
- Un extremo que ya es raíz (f(a) = 0 o f(b) = 0) se rechaza con un mensaje
  propio, porque f(a)·f(b) < 0 no se cumple.
- La tabla de iteraciones de la web usa `white-space: nowrap`: si no cabe en
  móvil hace scroll dentro de su contenedor.
- Los textos exportados evitan símbolos fuera de la fuente bitmap (`Ea` en
  lugar de ε, `>=` en lugar de ≥).
- Ejercicios: `bis-01`…`bis-08` (incluye intervalo sin cambio de signo,
  discontinuidad y paro por máximo de iteraciones).
- Pendiente del usuario: visto bueno visual (claro/oscuro y móvil).

## Cambios posteriores

- Spec `012` (`012-continuidad.md`): la discontinuidad ahora también se revisa
  **antes** de iterar (muestreo del intervalo) y se muestra en una tarjeta
  "Continuidad"; el criterio posterior de esta spec sigue vigente.
