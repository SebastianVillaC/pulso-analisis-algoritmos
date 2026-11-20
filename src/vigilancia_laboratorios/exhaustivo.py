"""Solución exhaustiva con suma acumulada: todos los tramos en Θ(n²).

Revisa los mismos n(n + 1)/2 tramos que la regla actual, pero reutiliza la
suma del tramo [inicio, fin - 1] para obtener la de [inicio, fin]. Es exacta
por construcción y sirve para verificar las estrategias rápidas.
"""

from modelo import SIN_TRAMO, Contador, Tramo, sumar


def tramo_acumulado(
    serie: list[int], contador: Contador | None = None
) -> Tramo:
    """Encuentra el tramo de mayor exceso revisando todos los tramos.

    Args:
        serie: Diferencias por lote de un laboratorio, en orden cronológico.
        contador: Contador de operaciones opcional (sumas y comparaciones).

    Returns:
        (suma, inicio, fin) del tramo no vacío de mayor exceso acumulado; ante
        empates, el primero encontrado. SIN_TRAMO si la serie está vacía.
    """
    if not serie:
        return SIN_TRAMO
    mejor: Tramo = (serie[0], 0, 0)
    n = len(serie)
    for inicio in range(n):
        total = 0
        for fin in range(inicio, n):
            total += serie[fin]  # reutiliza la suma del tramo anterior
            sumar(contador, "sumas")
            sumar(contador, "comparaciones")
            if total > mejor[0]:
                mejor = (total, inicio, fin)
    return mejor
