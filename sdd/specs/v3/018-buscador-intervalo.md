Estado: implementado

# Spec 018 — Buscador de intervalo para bisección y Regula Falsi

Cuando el profesor da solo la función, el estudiante debe encontrar un [a, b]
con f continua y f(a)·f(b) < 0. El buscador hace automáticamente lo que se hace
a mano: una tabla de valores y buscar el cambio de signo. La lógica vive en
`src/metodos/intervalos.py` (`buscar_intervalos(funcion, desde=-10, hasta=10)`);
la web solo muestra y copia los valores.

## Procedimiento

1. **Tabla de valores:** f en los enteros de `desde` a `hasta` (`tabla`; `None`
   donde f no está definida).
2. **Cambio de signo:** pares consecutivos con signo contrario; si f(x) = 0 en un
   punto de la tabla se reporta en `raices_exactas`.
3. **Continuidad:** cada candidato pasa por `revisar_continuidad`. Si cruza un
   polo o un salto (p. ej. tan cerca de π/2) va a `descartados` y ese tramo se
   recorre de nuevo con paso 0.1 (`origen: "refinado"`).
4. **Sin ningún cambio de signo:** se repite todo el rango con paso 0.1.

Es una ayuda numérica, no una demostración: dos raíces en un mismo tramo
(f cambia de signo dos veces) pasan inadvertidas. Hasta 8 intervalos.

## Presentación

- **Servidor:** `POST /api/intervalos` (`{funcion, desde?, hasta?}`), números ya
  formateados; consola con intervalos, descartados y raíces exactas.
- **Web:** botón «Buscar intervalo automáticamente» bajo a y b (bisección y
  Regula Falsi); explica el procedimiento, lista los intervalos como botones que
  llenan a y b, los descartados con su motivo y la tabla de valores (plegable).
  Móvil: botones de 44 px que ajustan el texto; sin scroll horizontal.
- **Exportar PNG/PDF, ejercicios:** no aplica (es una ayuda del formulario, no
  un resultado de método).

## Pruebas

`src/tests/test_intervalos.py` (polinomios, dos raíces, tan con polo y refinado,
raíz exacta, sin raíces, 1/x, dominio, y que cada sugerencia converge en ambos
métodos).

## Cambios posteriores

La spec 021 sustituye el rango fijo por búsqueda adaptable con paso decimal configurable y límites de trabajo; la continuidad es una revisión numérica, no una demostración.
