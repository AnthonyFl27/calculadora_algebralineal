Estado: implementado

# Spec 021 — Búsqueda adaptable de intervalos

Para Regula Falsi, mejorar el buscador compartido con bisección sin alterar la entrada manual. Buscar en puntos decimales, ampliar progresivamente el rango automático con límites de trabajo o respetar el rango indicado. Reportar ceros muestreados y candidatos de signo opuesto con extremos finitos; descartar señales numéricas de discontinuidad. El muestreo no demuestra continuidad ni encuentra todas las raíces. El usuario puede seleccionar candidatos y se completa el primero tras solicitar la búsqueda. No sobrescribir ediciones realizadas mientras se espera la respuesta. Las pruebas cubren dominio, polos, raíces pares, múltiples raíces y límites.


La búsqueda automática amplía [-10, 10] a [-100, 100] y [-1000, 1000] si no encuentra candidatos ni ceros; el rango manual se respeta. Paso predeterminado 0.1; límite de 40000 evaluaciones o 4 segundos. Los resultados son candidatos, no una prueba de continuidad.

## Cambios posteriores

En Regula Falsi se conserva el formulario original. La búsqueda se activa al terminar de escribir la función y llena directamente los campos editables Extremo a y Extremo b. El motivo de la sugerencia se muestra como texto breve junto a los campos. Si cambia la función, se descarta la sugerencia anterior. Los valores introducidos por el usuario o cargados con un ejercicio se conservan. El buscador detallado sigue disponible en bisección.
