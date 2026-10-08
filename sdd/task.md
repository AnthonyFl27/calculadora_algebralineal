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

---

## Specs en curso

### Spec 010 — Determinante (`sdd/specs/v2/010-determinante.md`)

**Implementar**
- [x] `src/metodos/determinante.py`: `recomendar_metodo(n)`, cofactores (fila/columna elegible, por defecto la de más ceros), LU con pivoteo parcial (`P·A = L·U`), contador de multiplicaciones, comprobación con el otro método.
- [x] `src/tests/test_determinante.py` (casos normales, borde y errores).

**Integrar en la web**
- [x] `server.py`: `POST /api/determinante` y `POST /api/determinante/recomendar`, bloque formateado, `DESTINO`, `_descripcion_peticion()`, banner, `CALCULOS` para exportar.
- [x] `src/web/index.html`: entrada `determinante` en `METODOS` (+ícono), vista con recomendación antes de elegir, stepper, tarjetas de resultado/comprobación, fracción/decimal, exportar.
- [x] Revisión claro/oscuro y 320/375 px; correr `prueba_web_movil.js`.
- [x] Ejercicios de práctica (≥ 6) en `ejercicios.py`, `vista_previa()`, carga sin resolver y pruebas en `test_ejercicios.py`.

**Cerrar**
- [ ] Pruebas en verde, spec en `implementado`, fila en `plan.md`, bloque borrado y `AGENTS.md` actualizado.
- [ ] Pendiente del usuario: visto bueno visual.
