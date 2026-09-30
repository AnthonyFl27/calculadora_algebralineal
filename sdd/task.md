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
| 004 | `sdd/specs/v2/004-diseño-visual.md` | Diseño visual: modo oscuro/claro y mejoras de interfaz (GUI y web) |

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

### 004 (continuación) — Menú de inicio

Spec: `sdd/specs/v2/004-diseño-visual.md`, sección "Cambios posteriores —
Menú de inicio".

#### Interfaz web (`index.html`)

- [x] Definir la lista única de módulos con nombre, ícono y descripción y
      usarla para construir tanto el sidebar como las tarjetas.
- [x] Agregar la entrada "Inicio" (ícono de casa) al sidebar, arriba de los
      módulos, con su resaltado de activo.
- [x] Crear la vista de Inicio: título, subtítulo y cuadrícula de tarjetas
      (botones accesibles, foco visible) que abren cada módulo y resaltan su
      botón del sidebar.
- [x] Hacer de Inicio la vista por defecto al cargar la página.
- [x] Estilos solo con variables CSS (claro y oscuro) y cuadrícula adaptable
      (una columna en pantallas angostas).
- [ ] Comprobar el sidebar replegado (con Inicio activo y al navegar).

#### Interfaz de escritorio (`gui.py`)

- [x] Agregar la entrada "Inicio" a la lista `METODOS`/sidebar, con su
      resaltado de activo.
- [x] Crear la vista de Inicio con las tarjetas de módulo, usando
      `RoundedButton`/`Frame` y colores de `PALETAS`.
- [x] Hacer de Inicio la vista por defecto al abrir la ventana.
- [x] Verificar que el cambio de tema recolorea Inicio sin reconstruirla.

#### Pruebas y cierre

- [x] Prueba de la GUI (`tests/test_gui_inicio.py`): abre en Inicio, cada tarjeta lleva al módulo correcto,
      "Inicio" vuelve al menú y el cambio de tema funciona.
- [x] Arnés `jsdom` (web): carga en Inicio, cada tarjeta abre su módulo,
      resaltado del sidebar correcto y sin colores sueltos en el CSS nuevo.
      (Ejecutado desde el scratchpad, 12 comprobaciones; no se guardó en el
      repo.)
- [ ] Visto bueno visual del usuario en ambas interfaces.
- [x] Marcar el cambio como implementado en la spec y actualizar `AGENTS.md`
      (mencionar el menú de inicio).
