Estado: implementado

# Spec 016 — Bisección: primero graficar, luego decidir la continuidad

El profesor pide que el primer paso de la bisección sea **graficar f(x)** y que,
en base a eso, se determine si f es continua; **solo si es continua se aplica el
método**. Todo lo decide el backend (`src/metodos/`); la web, el PNG y el PDF
solo presentan.

## Orden de `biseccion()`

1. **Gráfica** (`grafica.datos_grafica(f, a, b, continuidad)`): curva, ventana,
   marcas y discontinuidades, sin iteraciones (`iteraciones: []`, `raiz: None`).
2. **Continuidad** (`continuidad.revisar_continuidad`, spec 012). Si hay
   cualquier señal de discontinuidad (polo, salto o punto no definido) el
   método **se bloquea**: `biseccion()` devuelve `bloqueada: True`,
   `motivo_bloqueo`, `pasos: []`, `resultado: None`, `comprobacion: None` y la
   gráfica con la discontinuidad marcada. No se itera.
3. **Cambio de signo** f(a)·f(b) < 0 (`ValueError` si no lo hay; ahora se pide
   *después* de la continuidad: `1/x²` en [−1, 1] se reporta como discontinua).
4. **Iteraciones**; al terminar `grafica.agregar_iteraciones()` añade los
   puntos c y la raíz a la misma gráfica.

Es una revisión numérica (401 puntos), no una demostración: un salto más angosto
que el paso de muestreo puede pasar inadvertido.

## Presentación

- **Web:** "Paso 1 · Gráfica de f(x)" (visible por defecto), "Paso 2 ·
  Continuidad" (veredicto "f es continua" / "f NO es continua") y "Paso 3 ·
  Iteraciones". Bloqueada: tarjeta "Método no aplicado" y nada más (sin
  deslizador de iteraciones). El servidor devuelve `bloqueada` en el bloque.
- **PNG/PDF:** Paso 1 (gráfica) → Paso 2 (continuidad) → Paso 3 (procedimiento
  o resultado); bloqueada: "Método no aplicado" con el motivo. Sigue exportando.
- **Consola:** la línea de resultado dice `BLOQUEADO: f no es continua`.
- **Ejercicios:** `bis-07`, `bis-09` y `bis-10` ahora esperan `bloqueada`.

## Pruebas

`test_biseccion.py` (bloqueo de 1/x, tan, |x|/x, sqrt en dominio parcial; orden
continuidad → signo; caso continuo), `test_grafica.py`, `test_ejercicios.py` y
las de exportar/servidor.
