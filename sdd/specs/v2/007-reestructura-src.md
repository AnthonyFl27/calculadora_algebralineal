Estado: implementado

# 007 — Reestructura: código fuente en `src/`

**Archivos destino:** `server.py` (queda en la raíz), `src/` (nuevo), `AGENTS.md`, `sdd/plan.md`.

## Propósito

Separar el **código fuente** del **contexto y forma de trabajo de la IA**
(`AGENTS.md` y `sdd/`) para mantener un mejor orden. Sin cambios de
comportamiento: solo se mueven archivos y se ajustan rutas.

## Estructura resultante

```
.
├── AGENTS.md
├── server.py          ← punto de entrada web (en la raíz a propósito)
├── sdd/               ← plan, task y specs (contexto para la IA)
└── src/
    ├── main.py        ← antes gui.py (interfaz de escritorio)
    ├── web/index.html ← antes index.html (raíz)
    ├── metodos/
    ├── features/      (con tests/ y tools/)
    └── tests/
```

## Requisitos

- `server.py` queda **fuera de `src/`**: los técnicos lo ejecutan con
  `python server.py` sin navegar a ninguna carpeta. Para poder importar
  `metodos/` y `features/`, agrega `src/` a `sys.path` al arrancar y sirve
  `src/web/index.html`.
- `gui.py` pasa a `src/main.py`; se lanza con `python src/main.py`.
- Los imports (`from metodos...`, `from features...`) **no cambian**: `src/`
  es la raíz de importación (Python agrega la carpeta del script a `sys.path`).
- Los tests importan la GUI como `main` (`import main as gui`). Los que
  necesitan `server` agregan la raíz del proyecto a `sys.path`.
- Todo se corre **desde la raíz del proyecto**:
  - `python server.py` · `python src/main.py`
  - `python -m unittest discover -s src/tests -t src`
  - `python -m unittest discover -s src/features/tests -t src`
- Los movimientos se hicieron con `git mv` para conservar el historial.

## Cambios y decisiones tomadas al implementar

- Se agregó `src/tests/__init__.py` para que `discover -t src` funcione.
- Las specs de `v1/` y `v2/` anteriores conservan sus rutas originales
  (`gui.py`, `index.html`, `metodos/`…) por ser contexto histórico; ahora
  `gui.py` = `src/main.py`, `index.html` = `src/web/index.html` y
  `metodos/`, `features/`, `tests/` viven bajo `src/`.
