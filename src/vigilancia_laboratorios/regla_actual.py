"""Procedimiento actual: evalúa todos los tramos posibles de la serie.

Interpretación del equipo (documentada en el README): para cada pareja
(inicio, fin) el programa vuelve a sumar los lotes del tramo desde cero. Hay
Θ(n²) tramos y cada suma cuesta hasta n, así que el costo es Θ(n³). Es la
lectura coherente con que el histórico de tres años tarde "varios días".
"""

from modelo import SIN_TRAMO, Contador, Tramo, sumar


def tramo_actual(serie: list[int], contador: Contador | None = None) -> Tramo:
    """Encuentra el tramo de mayor exceso sumando cada tramo desde cero.

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
        for fin in range(inicio, n):
            total = 0
            for k in range(inicio, fin + 1):  # vuelve a sumar todo el tramo
                total += serie[k]
            sumar(contador, "sumas", fin - inicio + 1)
            sumar(contador, "comparaciones")
            if total > mejor[0]:
                mejor = (total, inicio, fin)
    return mejor
