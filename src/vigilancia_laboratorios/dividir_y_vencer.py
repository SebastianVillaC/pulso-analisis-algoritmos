"""Tramo de mayor exceso por dividir y vencer, Θ(n log n).

Recurrencia: T(n) = 2·T(n/2) + Θ(n). El tramo óptimo está completo en la
mitad izquierda, completo en la mitad derecha o cruza el centro; el que cruza
se arma con el mejor sufijo de la izquierda y el mejor prefijo de la derecha.
"""

from modelo import SIN_TRAMO, Contador, Tramo, sumar


def tramo_dyv(serie: list[int], contador: Contador | None = None) -> Tramo:
    """Encuentra el tramo de mayor exceso acumulado por dividir y vencer.

    Args:
        serie: Diferencias por lote de un laboratorio, en orden cronológico.
        contador: Contador de operaciones opcional (sumas y comparaciones).

    Returns:
        (suma, inicio, fin) del tramo no vacío de mayor exceso acumulado.
        SIN_TRAMO si la serie está vacía.
    """
    if not serie:
        return SIN_TRAMO
    return _resolver(serie, 0, len(serie) - 1, contador)


def _resolver(
    serie: list[int], bajo: int, alto: int, contador: Contador | None
) -> Tramo:
    """Resuelve el subproblema serie[bajo..alto] (no vacío).

    Args:
        serie: Diferencias por lote.
        bajo: Primer índice del subproblema.
        alto: Último índice del subproblema.
        contador: Contador de operaciones opcional.

    Returns:
        El mejor tramo dentro de serie[bajo..alto].
    """
    if bajo == alto:  # caso base: un solo lote
        return (serie[bajo], bajo, bajo)
    medio = (bajo + alto) // 2
    izquierdo = _resolver(serie, bajo, medio, contador)
    derecho = _resolver(serie, medio + 1, alto, contador)
    cruzado = _tramo_cruzado(serie, bajo, medio, alto, contador)
    sumar(contador, "comparaciones", 2)
    mejor = izquierdo
    if derecho[0] > mejor[0]:
        mejor = derecho
    if cruzado[0] > mejor[0]:
        mejor = cruzado
    return mejor


def _tramo_cruzado(
    serie: list[int], bajo: int, medio: int, alto: int,
    contador: Contador | None,
) -> Tramo:
    """Calcula el mejor tramo que contiene a serie[medio] y serie[medio + 1].

    Args:
        serie: Diferencias por lote.
        bajo: Primer índice del subproblema.
        medio: Último índice de la mitad izquierda.
        alto: Último índice del subproblema.
        contador: Contador de operaciones opcional.

    Returns:
        (suma, inicio, fin) del mejor tramo que cruza el centro.
    """
    total = 0
    mejor_izq = serie[medio]
    inicio = medio
    for i in range(medio, bajo - 1, -1):  # mejor sufijo de la izquierda
        total += serie[i]
        sumar(contador, "sumas")
        sumar(contador, "comparaciones")
        if total > mejor_izq:
            mejor_izq = total
            inicio = i
    total = 0
    mejor_der = serie[medio + 1]
    fin = medio + 1
    for j in range(medio + 1, alto + 1):  # mejor prefijo de la derecha
        total += serie[j]
        sumar(contador, "sumas")
        sumar(contador, "comparaciones")
        if total > mejor_der:
            mejor_der = total
            fin = j
    return (mejor_izq + mejor_der, inicio, fin)
