"""Estrategia recomendada: algoritmo de Kadane (programación dinámica), Θ(n).

Recurrencia: sea E[j] el mejor exceso de un tramo que TERMINA en el lote j.

    E[0] = x[0]
    E[j] = max(x[j], E[j - 1] + x[j])

La respuesta es max_j E[j]. Solo se necesita E[j - 1] para calcular E[j], así
que el espacio adicional es Θ(1).
"""

from modelo import SIN_TRAMO, Contador, Tramo, sumar


def tramo_kadane(serie: list[int], contador: Contador | None = None) -> Tramo:
    """Encuentra el tramo de mayor exceso acumulado en una sola pasada.

    Args:
        serie: Diferencias por lote de un laboratorio, en orden cronológico.
        contador: Contador de operaciones opcional (sumas y comparaciones).

    Returns:
        (suma, inicio, fin) del tramo no vacío de mayor exceso acumulado.
        SIN_TRAMO si la serie está vacía.
    """
    if not serie:
        return SIN_TRAMO
    actual = serie[0]  # E[j]: mejor tramo que termina en j
    inicio_actual = 0
    mejor: Tramo = (serie[0], 0, 0)
    for j in range(1, len(serie)):
        sumar(contador, "sumas")
        sumar(contador, "comparaciones", 2)
        if actual + serie[j] < serie[j]:  # conviene empezar de nuevo en j
            actual = serie[j]
            inicio_actual = j
        else:  # conviene extender el tramo que venía
            actual += serie[j]
        if actual > mejor[0]:
            mejor = (actual, inicio_actual, j)
    return mejor
