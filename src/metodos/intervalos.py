"""Búsqueda acotada de candidatos para métodos de raíces.

El muestreo no demuestra continuidad ni garantiza encontrar todas las raíces.
"""
import math
import time

from .continuidad import revisar_continuidad
from .evaluador import compilar, evaluar_numero

DESDE_POR_DEFECTO = -10
HASTA_POR_DEFECTO = 10
MAX_INTERVALOS = 8
MAX_RANGO = 2000
MAX_EVALUACIONES = 40000
MAX_SEGUNDOS = 4.0
PASO_POR_DEFECTO = 0.1


class _Limite(Exception):
    pass


class _FuncionLimitada:
    def __init__(self, f):
        self.f = f
        self.evaluaciones = 0
        self.inicio = time.monotonic()

    def evaluar_seguro(self, x):
        if self.evaluaciones >= MAX_EVALUACIONES or time.monotonic() - self.inicio > MAX_SEGUNDOS:
            raise _Limite
        self.evaluaciones += 1
        return self.f.evaluar_seguro(x)


def buscar_intervalos(funcion, desde=None, hasta=None, paso=PASO_POR_DEFECTO):
    f = compilar(funcion)
    if not f.usa_x:
        raise ValueError('La función debe depender de x (por ejemplo x^2 - 2).')
    automatico = desde is None and hasta is None
    if (desde is None) != (hasta is None):
        raise ValueError('Indica ambos límites del rango de búsqueda.')
    if automatico:
        desde, hasta = DESDE_POR_DEFECTO, HASTA_POR_DEFECTO
    else:
        desde = evaluar_numero(desde, 'El límite desde')
        hasta = evaluar_numero(hasta, 'El límite hasta')
    paso = evaluar_numero(paso, 'El paso')
    if desde >= hasta:
        raise ValueError('El rango debe cumplir desde < hasta.')
    if not math.isfinite(hasta - desde) or hasta - desde > MAX_RANGO:
        raise ValueError(f'El rango puede tener como máximo {MAX_RANGO} unidades.')
    if paso <= 0 or paso > MAX_RANGO:
        raise ValueError('El paso debe ser positivo y no superar el rango máximo.')

    limitada = _FuncionLimitada(f)
    intervalos, descartados, exactas, tabla = [], [], [], []
    agotado = False
    rangos = [(desde, hasta)] if not automatico else [(-10, 10), (-100, 100), (-1000, 1000)]
    final_desde, final_hasta = desde, hasta
    try:
        for lo, hi in rangos:
            final_desde, final_hasta = lo, hi
            n = math.ceil((hi - lo) / paso)
            if n > MAX_EVALUACIONES:
                agotado = True
                break
            previo = None
            for k in range(n + 1):
                x = hi if k == n else float(format(lo + k * paso, ".15g"))
                if previo is not None and x <= previo[0]:
                    raise ValueError('El paso es demasiado pequeño para este rango.')
                valor, motivo = limitada.evaluar_seguro(x)
                if len(tabla) < 201 and (k == 0 or k == n or k % max(1, n // 20) == 0):
                    tabla.append((x, valor))
                if valor == 0 and x not in exactas:
                    exactas.append(x)
                if previo is not None:
                    xa, va = previo
                    if va is not None and valor is not None and va != 0 and valor != 0 and (va > 0) != (valor > 0):
                        revision = revisar_continuidad(limitada, xa, x)
                        if revision['sin_senales']:
                            if not any(i['a'] == xa and i['b'] == x for i in intervalos):
                                intervalos.append({'a': xa, 'b': x, 'fa': va, 'fb': valor, 'origen': 'refinado'})
                        elif len(descartados) < 20:
                            descartados.append({'a': xa, 'b': x, 'motivo': revision['sospechas'][0]['mensaje']})
                previo = (x, valor)
            if automatico and (intervalos or exactas):
                break
            tabla = [] if automatico and (lo, hi) != rangos[-1] else tabla
    except _Limite:
        agotado = True
    intervalos.sort(key=lambda i: i['a'])
    return {'desde': final_desde, 'hasta': final_hasta, 'paso': paso,
            'tabla': tabla, 'intervalos': intervalos[:MAX_INTERVALOS],
            'total_intervalos': len(intervalos), 'descartados': descartados,
            'raices_exactas': sorted(set(exactas)), 'agotado': agotado,
            'evaluaciones': limitada.evaluaciones}
