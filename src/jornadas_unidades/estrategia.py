"""Programación de las jornadas de una unidad móvil.

Estrategia: programación dinámica de intervalos ponderados. Maximiza el número
de pacientes de alto riesgo atendidos sin que dos jornadas se crucen.

Recurrencia (jornadas ordenadas por hora de fin, numeradas 1..n):

    M[0] = 0
    M[j] = max(M[j - 1], v_j + M[p(j)])

donde v_j son los pacientes de la jornada j y p(j) es cuántas jornadas
anteriores terminan a más tardar cuando j empieza.

Incluye también el voraz de terminación más temprana, que maximiza el número
de jornadas y sirve como contraste.
"""

from modelo import Contador, Jornada, se_cruzan, sumar


def ordenar_por_fin(solicitudes: list[Jornada]) -> list[Jornada]:
    """Ordena las solicitudes por hora de fin, sin modificar la lista original.

    Args:
        solicitudes: Solicitudes del mes de una subregión.

    Returns:
        Una lista nueva, de la jornada que termina primero a la última.
    """
    return sorted(solicitudes, key=lambda jornada: (jornada[1], jornada[0]))


def contar_compatibles(
    fines: list[int], inicio: int, hasta: int, contador: Contador | None = None
) -> int:
    """Cuenta con búsqueda binaria cuántos fines no pasan de un inicio.

    Args:
        fines: Horas de fin en orden creciente.
        inicio: Hora de inicio de la jornada que se analiza.
        hasta: Solo se miran fines[0], ..., fines[hasta - 1].
        contador: Contador de operaciones opcional.

    Returns:
        Cuántos de esos fines son menores o iguales que inicio.
    """
    bajo = 0
    alto = hasta
    while bajo < alto:
        medio = (bajo + alto) // 2
        sumar(contador, "comparaciones")
        if fines[medio] <= inicio:  # <=: tocarse en un extremo no es cruce
            bajo = medio + 1
        else:
            alto = medio
    return bajo


def calcular_p(
    orden: list[Jornada], contador: Contador | None = None
) -> list[int]:
    """Calcula p(j) para cada jornada de una lista ordenada por hora de fin.

    Args:
        orden: Jornadas ordenadas por fin; orden[0] es la jornada 1.
        contador: Contador de operaciones opcional.

    Returns:
        La lista p, con p[j] = cuántas jornadas anteriores a j terminan a más
        tardar cuando j empieza. La posición 0 no se usa.
    """
    fines = [jornada[1] for jornada in orden]
    p = [0] * (len(orden) + 1)
    for j in range(1, len(orden) + 1):
        p[j] = contar_compatibles(fines, orden[j - 1][0], j - 1, contador)
    return p


def llenar_tabla(
    orden: list[Jornada], p: list[int], contador: Contador | None = None
) -> list[int]:
    """Llena la tabla M de izquierda a derecha.

    Args:
        orden: Jornadas ordenadas por hora de fin.
        p: Lista devuelta por calcular_p.
        contador: Contador de operaciones opcional.

    Returns:
        La tabla M, donde M[j] es el máximo de pacientes usando solo las
        jornadas 1..j. M[0] = 0 es el caso base.
    """
    n = len(orden)
    mejor = [0] * (n + 1)
    for j in range(1, n + 1):
        no_aceptar = mejor[j - 1]
        aceptar = orden[j - 1][2] + mejor[p[j]]
        sumar(contador, "celdas")
        mejor[j] = aceptar if aceptar > no_aceptar else no_aceptar
    return mejor


def reconstruir(
    orden: list[Jornada], p: list[int], mejor: list[int]
) -> list[Jornada]:
    """Recupera las jornadas de una solución óptima recorriendo M hacia atrás.

    Args:
        orden: Jornadas ordenadas por hora de fin.
        p: Lista devuelta por calcular_p.
        mejor: Tabla M devuelta por llenar_tabla.

    Returns:
        Las jornadas elegidas, ordenadas por hora de fin.
    """
    elegidas: list[Jornada] = []
    j = len(orden)
    while j > 0:
        if orden[j - 1][2] + mejor[p[j]] > mejor[j - 1]:  # la jornada j entró
            elegidas.append(orden[j - 1])
            j = p[j]  # salta las jornadas que se cruzan con j
        else:
            j -= 1
    elegidas.reverse()
    return elegidas


def seleccionar_jornadas(
    solicitudes: list[Jornada], contador: Contador | None = None
) -> list[Jornada]:
    """Elige las jornadas que atiende la unidad, sin cruces.

    Criterio declarado en el README: maximizar el número de pacientes de alto
    riesgo atendidos (programación dinámica de intervalos ponderados).

    Args:
        solicitudes: Solicitudes del mes de una subregión.
        contador: Contador de operaciones opcional (comparaciones de la
            búsqueda binaria y celdas de la tabla).

    Returns:
        Las jornadas elegidas, ordenadas por hora de inicio. Optimiza el
        criterio que el equipo declaró en el README.
    """
    orden = ordenar_por_fin(solicitudes)
    p = calcular_p(orden, contador)
    mejor = llenar_tabla(orden, p, contador)
    elegidas = reconstruir(orden, p, mejor)
    return sorted(elegidas, key=lambda jornada: (jornada[0], jornada[1]))


def hay_cruce(jornadas: list[Jornada]) -> bool:
    """Indica si alguna pareja de jornadas se cruza.

    Convención: una jornada que empieza justo cuando otra termina NO se cruza
    con ella (ver modelo.se_cruzan y el apartado Supuestos del README).

    Args:
        jornadas: Jornadas a revisar.

    Returns:
        True si dos jornadas se cruzan; False en caso contrario.
    """
    por_inicio = sorted(jornadas, key=lambda jornada: (jornada[0], jornada[1]))
    # Basta comparar cada jornada con la anterior que termina más tarde: si
    # no se cruza con esa, no se cruza con ninguna de las anteriores.
    mas_tardia: Jornada | None = None
    for jornada in por_inicio:
        if mas_tardia is not None and se_cruzan(mas_tardia, jornada):
            return True
        if mas_tardia is None or jornada[1] > mas_tardia[1]:
            mas_tardia = jornada
    return False


def terminacion_temprana(
    solicitudes: list[Jornada], contador: Contador | None = None
) -> list[Jornada]:
    """Voraz de terminación más temprana: maximiza el NÚMERO de jornadas.

    No es la estrategia recomendada; se usa como contraste para mostrar que
    maximizar jornadas no es lo mismo que maximizar pacientes atendidos.

    Args:
        solicitudes: Solicitudes del mes de una subregión.
        contador: Contador de operaciones opcional.

    Returns:
        Las jornadas elegidas, ordenadas por hora de inicio.
    """
    elegidas: list[Jornada] = []
    ultimo_fin = None
    for jornada in ordenar_por_fin(solicitudes):
        sumar(contador, "comparaciones")
        if ultimo_fin is None or jornada[0] >= ultimo_fin:
            elegidas.append(jornada)
            ultimo_fin = jornada[1]
    return elegidas
