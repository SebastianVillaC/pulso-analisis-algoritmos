"""Tipos y utilidades compartidos por las soluciones de la operación 4.

Cada lote de un laboratorio se representa con un entero: la diferencia entre
su tasa de resultados positivos (índice de riesgo >= 70) y la tasa esperada
para la población que atiende, en puntos por mil. Puede ser negativa.
"""

# (suma, inicio, fin): exceso acumulado del tramo y sus índices (inclusive).
Tramo = tuple[int, int, int]

# Contador de operaciones elementales: nombre de la operación -> veces.
Contador = dict[str, int]

# Resultado para una serie vacía: no hay tramo (fin < inicio).
SIN_TRAMO: Tramo = (0, 0, -1)


def sumar(contador: Contador | None, clave: str, cantidad: int = 1) -> None:
    """Suma una cantidad al contador de operaciones, si se pidió contar.

    Args:
        contador: Diccionario de conteos, o None si no se está contando.
        clave: Nombre de la operación elemental.
        cantidad: Cuántas operaciones se suman.
    """
    if contador is not None:
        contador[clave] = contador.get(clave, 0) + cantidad


def suma_tramo(serie: list[int], inicio: int, fin: int) -> int:
    """Calcula la suma de serie[inicio..fin], ambos extremos incluidos.

    Args:
        serie: Diferencias por lote, en puntos por mil.
        inicio: Índice del primer lote del tramo.
        fin: Índice del último lote del tramo.

    Returns:
        El exceso acumulado del tramo (0 si el tramo es vacío).
    """
    total = 0
    for k in range(inicio, fin + 1):
        total += serie[k]
    return total
