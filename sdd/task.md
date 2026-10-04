# Tareas de implementación

Solo lo que está **en curso o pendiente**. Lo ya hecho vive en cada spec
(`sdd/specs/`) y en la tabla de seguimiento de `sdd/plan.md`.

Cada spec nueva agrega aquí su bloque de tareas (**Implementar → Integrar en
las interfaces → Cerrar**, ver el checklist de `sdd/plan.md`). Al terminar el
ciclo, el bloque se borra y solo se conservan las tareas que sigan abiertas.

---

## Pendientes

Ninguno por ahora.

---

## Specs en curso

### 008 — Web adaptable a móviles (`sdd/specs/v2/008-adaptable-movil.md`)

Solo `src/web/index.html`. Cada paso se comprueba a 360 px y a escritorio
(≥ 1024 px) antes de seguir.

**Implementar**
- [ ] 1. Base: `viewport-fit=cover`, altura con `dvh` (respaldo `vh`),
      `safe-area`, `min-width: 0` en `.panel` y padding reducido bajo 768 px.
- [ ] 2. Navegación móvil (≤ 768 px): barra superior + botón de menú + estado
      del servidor; drawer con overlay, scroll propio y botón de tema dentro.
- [ ] 3. JS del drawer: cierra al elegir módulo, overlay y `Esc`; foco vuelve al
      botón; `aria-expanded`/`aria-controls`; sin tocar ni persistir
      `sidebar-colapsado` en móvil; restaura el estado de escritorio al
      ensanchar.
- [ ] 4. Centrado seguro (`safe center` / `margin: 0 auto`) en `.marco-matriz` y
      demás contenedores flex con `overflow-x: auto` (revisar todos).
- [ ] 5. Celdas de matriz/vectores con ancho fluido y mínimo usable; scroll
      interno del contenedor para matrices grandes (referencia 8×8 a 320 px).
- [ ] 6. Tablas por paso (`tabla-matriz`) compactas en angosto, con scroll
      propio sin recorte a la izquierda.
- [ ] 7. Cuadrículas a una columna (`grupo-tablas`, `grupo-vectores`, Inicio,
      ejercicios); pestañas de Vectores y matrices con scroll horizontal.
- [ ] 8. Filas de controles con `flex-wrap`; radios Fracciones/Decimales y
      botones principales sin recortes.
- [ ] 9. Táctil: 16 px en campos y `select` en móvil, objetivos ≥ 44 px,
      stepper con contador + botones grandes, atributos de las celdas (sin
      `inputmode`), `touch-action: manipulation`, `:hover` dentro de
      `@media (hover: hover)`.
- [ ] 10. Superpuestos: modal, toast y menú de exportar dentro de la pantalla a
      320 px; revisar la descarga PNG/PDF en iOS y Android.

**Integrar**
- [ ] Revisar que el escritorio (≥ 1024 px) queda idéntico y que el tema
      claro/oscuro y el recuerdo en `localStorage` siguen funcionando.
- [ ] Recorrer todos los módulos y pestañas en los anchos 320, 360, 375, 390,
      412, 430, 600, 768 y 1024 px comprobando `scrollWidth <= clientWidth`.
- [ ] (Opcional) Script de Playwright en `src/features/tests/`.

**Cerrar**
- [ ] `python -m unittest discover -s src/tests -t src` y
      `python -m unittest discover -s src/features/tests -t src` en verde.
- [ ] Spec 008 en `implementado` con "Cambios y decisiones tomadas al
      implementar"; fila de `sdd/plan.md` actualizada.
- [ ] Nota en "Cambios posteriores" de la spec 004 (el "ventana angosta: una
      columna" ahora cubre sidebar, matrices y tablas).
- [ ] `AGENTS.md`: descripción de la interfaz web (navegación adaptable a
      móviles, breakpoint 768 px) y mención de la spec `008`.
- [ ] Borrar este bloque de `sdd/task.md`.
- [ ] Pendiente del usuario: visto bueno en sus dispositivos (iPhone/Android) y
      despliegue en Render.
