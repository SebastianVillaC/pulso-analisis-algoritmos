"""Tipos y regla de cruce compartidos por las soluciones de la operación 3.

La regla de cruce vive solo aquí para que la estrategia, la solución
exhaustiva y la regla actual usen exactamente la misma convención.
"""

# (inicio, fin, pacientes_alto_riesgo); inicio y fin en minutos.
Jornada = tuple[int, int, int]

# Contador de operaciones elementales: nombre de la operación -> veces.
Contador = dict[str, int]


def se_cruzan(a: Jornada, b: Jornada) -> bool:
    """Indica si dos jornadas ocupan la unidad móvil al mismo tiempo.

    Convención del equipo: si una jornada termina exactamente cuando la otra
    empieza, NO se cruzan, porque la hora de fin ya incluye el desplazamiento
    de la unidad.

    Args:
        a: Inicio, fin y pacientes de una jornada.
        b: Inicio, fin y pacientes de la otra jornada.

    Returns:
        True si los intervalos [inicio, fin) de ambas jornadas se solapan.
    """
    return a[0] < b[1] and b[0] < a[1]


def sumar(contador: Contador | None, clave: str, cantidad: int = 1) -> None:
    """Suma una cantidad al contador de operaciones, si se pidió contar.

    Args:
        contador: Diccionario de conteos, o None si no se está contando.
        clave: Nombre de la operación elemental.
        cantidad: Cuántas operaciones se suman.
    """
    if contador is not None:
        contador[clave] = contador.get(clave, 0) + cantidad


def total_pacientes(jornadas: list[Jornada]) -> int:
    """Suma los pacientes de alto riesgo de un conjunto de jornadas.

    Args:
        jornadas: Jornadas elegidas.

    Returns:
        El total de pacientes de alto riesgo atendidos.
    """
    total = 0
    for jornada in jornadas:
        total += jornada[2]
    return total
