# Tareas de implementación

Solo lo que está **en curso o pendiente**. Lo ya hecho vive en cada spec
(`sdd/specs/`) y en la tabla de seguimiento de `sdd/plan.md`.

Cada spec nueva agrega aquí su bloque de tareas (**Implementar → Integrar en
la web → Cerrar**, ver el checklist de `sdd/plan.md`). Al terminar el
ciclo, el bloque se borra y solo se conservan las tareas que sigan abiertas.

---

## Pendientes

- [x] Spec 008 (web adaptable a móviles): visto bueno visual en un iPhone y un
      Android reales (comprobar también que PNG y PDF se descargan o se abren
      desde el aviso "Abrir") y despliegue en Render. Las pruebas automáticas
      (`unittest` y `src/features/tests/prueba_web_movil.js`) validan medidas y
      comportamiento en Chromium, no apariencia.
- [x] Spec 010 (determinante): visto bueno visual en la máquina del usuario
      (modo claro y oscuro, y la tarjeta "L·U coincide con P·A" en móvil). Las
      pruebas automáticas validan comportamiento y medidas, no apariencia.
- [x] Spec 011 (bisección): visto bueno visual en la máquina del usuario (modo
      claro y oscuro, y la tabla de iteraciones en móvil). Las pruebas
      automáticas validan comportamiento y medidas, no apariencia.
- [x] Spec 012 (continuidad en la bisección): visto bueno visual en la máquina
      del usuario (tarjeta "Continuidad" en modo claro y oscuro y en móvil).
      Las pruebas automáticas validan comportamiento, no apariencia.
- [x] Spec 013 (gráfica de la bisección): visto bueno visual en la máquina del
      usuario (web en claro/oscuro y móvil, y los PNG/PDF exportados), y
      confirmar con el profesor que la gráfica cumple lo que pide.
- [x] Spec 014 (gráficas geométricas): visto bueno visual en la máquina del
      usuario al terminar cada paso (claro/oscuro, móvil y PNG/PDF).
- [ ] Spec 015 (transformación animada): visto bueno visual en la máquina del
      usuario (deslizador `t` en claro/oscuro y móvil, y los PNG/PDF en
      `t = 1`), y confirmar que la interpolación `(1 − t)·I + t·A` es la que
      se quiere mostrar.
- [ ] Spec 018 (buscador de intervalo): visto bueno visual en la máquina del
      usuario (botón y sugerencias en claro/oscuro y móvil).
- [ ] Spec 017 (Regula Falsi): visto bueno visual en la máquina del usuario
      (secante en la gráfica en claro/oscuro y móvil, y los PNG/PDF), y
      confirmar con el profesor el criterio de paro (ε_a entre aproximaciones).

- [ ] Spec 019 (Newton-Raphson): visto bueno visual en la máquina del usuario
      (tangente en la gráfica en claro/oscuro y móvil, y los PNG/PDF), y
      confirmar con el profesor el criterio de paro (ε_a) y si se pide la
      secante (spec 020).

- [ ] Spec 020 (secante): visto bueno visual en la máquina del usuario
      (secante en la gráfica en claro/oscuro y móvil, y los PNG/PDF), y
      confirmar con el profesor el criterio de paro (ε_a) y los ejercicios.

- [ ] Spec 021 (intervalos adaptables): visto bueno visual en móvil y escritorio.

---

## Specs en curso

Ninguna por ahora.
