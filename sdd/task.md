# Tareas de implementación

Seguimiento de tareas de `sdd/plan.md`. Solo se mantiene lo que está **en
curso o pendiente**; el detalle de lo ya hecho vive en cada spec
(`sdd/specs/`), que sigue siendo la referencia de qué se construyó y por qué.

Cada spec nueva agrega aquí su bloque de tareas (ciclo: **Implementar →
Integrar en la interfaz → Cerrar**). Al terminar el ciclo, se condensa su
bloque en una fila de "Módulos cerrados" y solo se conservan las tareas que
sigan abiertas.

---

## Módulos cerrados

| # | Spec | Módulo |
|---|------|--------|
| 001 | `sdd/specs/v1/001-conversion.md` | Conversión de bases (incluye hexadecimal → decimal) |
| 002 | `sdd/specs/v1/002-vectores-matrices.md` | Vectores, matrices, ecuación matricial y matriz inversa (2.4) |
| 003 | `sdd/specs/v1/003-diseño-visual-html.md` | Interfaz web: `server.py` + `index.html`, pasos visuales e indicador de estado |
| 004 | `sdd/specs/v2/004-modo-oscuro-claro.md` | Modo oscuro y claro (GUI y web) |

---

## Pendientes

- [ ] Visto bueno visual del usuario (en su máquina) del diseño de pasos de la
      web (spec 003): jsdom valida comportamiento, no apariencia.
- [ ] Visto bueno visual de la pestaña "Matriz inversa" en ambas interfaces
      (spec 002, 2.4).
- [ ] Visto bueno visual de ambos temas, claro y oscuro (spec 004), sobre todo
      en la web.
- [ ] Mejora futura (spec 004): subir el contraste del tema claro a 4.5:1
      (hoy se conserva idéntico al diseño original).

---

## Specs en curso

(Ninguna por ahora. La siguiente spec lleva el número `005`.)
