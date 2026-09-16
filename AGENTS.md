# AGENTS.md

## Contexto del proyecto

Este proyecto es una **calculadora de álgebra lineal** desarrollada para una clase de la materia, cuyo objetivo es resolver sistemas de ecuaciones lineales (matrices aumentadas) aplicando distintos métodos de resolución. Actualmente se cuenta con dos métodos implementados: **Gauss-Jordan** y **Pivoteo** (Gauss-Jordan con pivoteo parcial).

El programa está escrito en **Python** y se ejecuta mediante una interfaz gráfica hecha con **Tkinter**, que despliega ventanas, botones y campos de captura. Al lanzar la aplicación (`gui.py`), se muestra un panel principal con una barra lateral (sidebar) desde la cual el usuario elige el método con el que desea resolver su sistema de ecuaciones. También existe una versión de consola (`cli.py`) que ofrece el mismo flujo de trabajo en modo texto.

## Regla fundamental impuesta por el profesor

**No está permitido usar librerías matemáticas externas** como NumPy, SciPy o SymPy. Toda la lógica de resolución de matrices (eliminación, pivoteo, manejo de fracciones, verificación de resultados, etc.) debe implementarse manualmente utilizando únicamente la librería estándar de Python. Esta restricción es intencional: el objetivo del profesor es que el proceso algebraico se programe "a mano", sin apoyarse en paquetes que ya resuelven el problema internamente.

Además de esta restricción, se busca que la calculadora sea **funcional, fácil de usar e intuitiva**, priorizando una experiencia clara para quien la use, más allá de solo cumplir con el cálculo matemático correcto.

## Qué se busca con este proyecto

- Ofrecer una herramienta visual e interactiva para resolver sistemas de ecuaciones lineales paso a paso.
- Permitir comparar distintos métodos de resolución sobre la misma matriz.
- Mostrar no solo el resultado final, sino también el procedimiento (pasos intermedios) y una comprobación del resultado obtenido.
- Mantener el código libre de librerías matemáticas externas, respetando la restricción académica impuesta.
- Ir mejorando de manera incremental lo que ya existe, en lugar de reescribir el proyecto desde cero: se parte de la base actual y se añaden o ajustan funcionalidades según se necesite.

## Estructura general del proyecto

- **`gui.py`**: interfaz gráfica principal (Tkinter). Aquí el usuario elige el método desde la barra lateral, captura la matriz y visualiza resultados y pasos. No contiene lógica matemática propia, solo se encarga de la presentación.
- **`cli.py`**: versión de consola con el mismo flujo que la interfaz gráfica, pensada para uso en terminal.
- **`metodos/`**: carpeta donde vive toda la lógica matemática del proyecto, separada de la interfaz. Actualmente contiene tres módulos:
  - Un módulo para el método de **Gauss-Jordan**.
  - Un módulo para el método de **Pivoteo**.
  - Un módulo de **utilidades generales**, compartido por los demás métodos, que se encarga de tareas básicas como el manejo de fracciones y decimales, formateo de resultados y verificación de soluciones.

## Enfoque de trabajo

Este proyecto se irá construyendo de manera progresiva: se parte de lo ya implementado (interfaz gráfica funcional y dos métodos de resolución operativos) y se continuará mejorando, corrigiendo o ampliando según las necesidades de la clase, siempre respetando la restricción de no usar librerías matemáticas externas.
