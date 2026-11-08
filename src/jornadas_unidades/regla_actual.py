"""Regla que usa hoy el coordinador: asignación por orden de llegada.

Interpretación del equipo (documentada en el README): las solicitudes se
revisan en el orden en que llegaron; cada una se compara con todas las
jornadas ya aceptadas y se acepta solo si no se cruza con ninguna. Nunca se
revoca una jornada aceptada. Costo: Θ(n·a), con a las jornadas aceptadas, que
en el peor caso es Θ(n²).
"""

from modelo import Contador, Jornada, se_cruzan, sumar


def asignar_por_llegada(
    solicitudes: list[Jornada], contador: Contador | None = None
) -> list[Jornada]:
    """Reproduce el procedimiento actual: orden de llegada, rechazando cruces.

    Args:
        solicitudes: Solicitudes en el orden en que llegaron.
        contador: Contador de operaciones opcional (comparaciones).

    Returns:
        Las jornadas aceptadas, en el orden en que se aceptaron.
    """
    aceptadas: list[Jornada] = []
    for solicitud in solicitudes:
        if not _se_cruza_con_aceptadas(solicitud, aceptadas, contador):
            aceptadas.append(solicitud)
    return aceptadas


def _se_cruza_con_aceptadas(
    solicitud: Jornada,
    aceptadas: list[Jornada],
    contador: Contador | None = None,
) -> bool:
    """Compara una solicitud con cada jornada ya aceptada.

    Args:
        solicitud: Solicitud que se está revisando.
        aceptadas: Jornadas aceptadas hasta el momento.
        contador: Contador de operaciones opcional.

    Returns:
        True si la solicitud se cruza con alguna jornada aceptada.
    """
    for jornada in aceptadas:
        sumar(contador, "comparaciones")
        if se_cruzan(solicitud, jornada):
            return True
    return False
