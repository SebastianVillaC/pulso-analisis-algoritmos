"""Solución exhaustiva: prueba todos los subconjuntos de solicitudes.

Es la solución exacta con la que se verifica la estrategia. Su costo es
Θ(n·2ⁿ), así que solo se ejecuta con instancias pequeñas (n <= 20).
"""

from itertools import product

from modelo import Contador, Jornada, sumar


def seleccionar_exhaustivo(
    solicitudes: list[Jornada], contador: Contador | None = None
) -> list[Jornada]:
    """Elige el mejor subconjunto sin cruces probando todos los subconjuntos.

    Las solicitudes se ordenan por hora de inicio; así, un subconjunto no
    tiene cruces si cada jornada elegida empieza cuando la elegida anterior
    ya terminó (tocarse en un extremo no es cruce).

    Args:
        solicitudes: Solicitudes del mes de una subregión.
        contador: Contador de operaciones opcional (subconjuntos explorados y
            comparaciones).

    Returns:
        Un subconjunto óptimo para el mismo criterio (máximo de pacientes de
        alto riesgo), ordenado por hora de inicio.
    """
    orden = sorted(solicitudes, key=lambda jornada: (jornada[0], jornada[1]))
    n = len(orden)
    mejor_total = 0
    mejor_interruptores: tuple[int, ...] = (0,) * n
    for interruptores in product((0, 1), repeat=n):  # un subconjunto
        sumar(contador, "subconjuntos")
        total = _evaluar_subconjunto(orden, interruptores, contador)
        if total > mejor_total:
            mejor_total = total
            mejor_interruptores = interruptores
    return [orden[i] for i in range(n) if mejor_interruptores[i] == 1]


def _evaluar_subconjunto(
    orden: list[Jornada],
    interruptores: tuple[int, ...],
    contador: Contador | None = None,
) -> int:
    """Calcula los pacientes de un subconjunto, o -1 si tiene un cruce.

    Args:
        orden: Solicitudes ordenadas por hora de inicio.
        interruptores: interruptores[i] == 1 si la solicitud i se acepta.
        contador: Contador de operaciones opcional.

    Returns:
        La suma de pacientes del subconjunto, o -1 si dos jornadas se cruzan.
    """
    ultimo_fin = None
    total = 0
    for i, aceptada in enumerate(interruptores):
        if aceptada == 1:
            sumar(contador, "comparaciones")
            if ultimo_fin is not None and orden[i][0] < ultimo_fin:
                return -1  # se cruza con la anterior elegida
            ultimo_fin = orden[i][1]
            total += orden[i][2]
    return total
