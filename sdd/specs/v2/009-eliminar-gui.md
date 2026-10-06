Estado: implementado

# 009 — Eliminar la GUI de Tkinter: la web es la única interfaz

**Archivos destino:** `src/main.py` (se elimina), `src/tests/test_gui_*.py` y
`src/features/tests/test_gui_exportar.py` (se eliminan), `src/tests/test_contraste.py`,
`AGENTS.md`, `sdd/plan.md`, `sdd/task.md`.

## Propósito

Dejar de desarrollar la interfaz de escritorio hecha con Tkinter y quedarse
solo con la versión web (`python server.py` + `src/web/index.html`). Se acaba
la regla de mantener dos interfaces sincronizadas.

## Requisitos

- Se elimina `src/main.py` (la GUI, antes `gui.py`) y sus pruebas.
- `src/metodos/`, `server.py` y `src/features/` no cambian de comportamiento;
  solo se quitan referencias a `main.py`, la GUI y el CLI en comentarios.
- El contraste 4.5:1 se sigue probando, ahora solo para la web
  (`ContrasteWebTests`); se quita la prueba de `PALETAS`.
- Los colores viven solo en las variables CSS de `src/web/index.html`.
- La documentación (`AGENTS.md`, `sdd/plan.md`) deja de exigir cambios en dos
  interfaces y de mencionar Tkinter, `PALETAS` o `python src/main.py`.

## Notas

- Las specs `001`–`008` no se reescriben (son contexto histórico): las
  menciones a la GUI que contienen describen lo que se hizo en su momento.
- Verificación: `python -m unittest discover -s src/tests -t src` (35) y
  `python -m unittest discover -s src/features/tests -t src` (20) en verde.
