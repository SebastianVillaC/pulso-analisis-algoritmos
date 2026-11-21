"""Operaciones 1 y 2 del proceso nocturno: implementación actual y referencia.

No son las dos operaciones trabajadas a fondo en el proyecto (3 y 4). Se
implementan para medir la línea base del proceso actual, identificar las
operaciones críticas y estimar el ahorro de una alternativa de referencia.

Un resultado es (documento, fecha, riesgo): documento identifica al paciente,
fecha en minutos (mayor = más reciente) y riesgo entre 0 y 100.
"""

import heapq

Resultado = tuple[int, int, int]


def clave_prioridad(resultado: Resultado) -> tuple[int, int]:
    """Clave de llamada: mayor riesgo y, a igual riesgo, el más antiguo.

    Args:
        resultado: (documento, fecha, riesgo).

    Returns:
        Una clave que ordena de forma ascendente según la prioridad.
    """
    return (-resultado[2], resultado[1])


def consolidar_lineal(resultados: list[Resultado]) -> list[Resultado]:
    """Op. 1 actual: busca cada paciente recorriendo la lista consolidada.

    Costo Θ(n·m), con m pacientes distintos (m ≈ 0,88·n): cuadrático.

    Args:
        resultados: Resultados del día, en orden de llegada.

    Returns:
        Un resultado por paciente, el más reciente, en orden de aparición.
    """
    consolidados: list[Resultado] = []
    for resultado in resultados:
        encontrado = False
        for i, previo in enumerate(consolidados):
            if previo[0] == resultado[0]:
                if resultado[1] > previo[1]:
                    consolidados[i] = resultado
                encontrado = True
                break
        if not encontrado:
            consolidados.append(resultado)
    return consolidados


def lista_por_insercion(pacientes: list[Resultado], k: int) -> list[Resultado]:
    """Op. 2 actual: ordena todo por inserción y toma los k primeros.

    Costo Θ(n²) en el caso promedio y en el peor caso.

    Args:
        pacientes: Un resultado por paciente.
        k: Capacidad diaria del centro de contacto.

    Returns:
        Los k pacientes de mayor prioridad, en orden de llamada.
    """
    orden = list(pacientes)  # la lista original no se modifica
    for i in range(1, len(orden)):
        actual = orden[i]
        clave = clave_prioridad(actual)
        j = i - 1
        while j >= 0 and clave_prioridad(orden[j]) > clave:
            orden[j + 1] = orden[j]
            j -= 1
        orden[j + 1] = actual
    return orden[:k]


def consolidar_hash(resultados: list[Resultado]) -> list[Resultado]:
    """Op. 1 de referencia: tabla hash por documento, Θ(n) esperado.

    Args:
        resultados: Resultados del día, en orden de llegada.

    Returns:
        Un resultado por paciente, el más reciente, en orden de aparición.
    """
    posicion: dict[int, int] = {}
    consolidados: list[Resultado] = []
    for resultado in resultados:
        i = posicion.get(resultado[0])
        if i is None:
            posicion[resultado[0]] = len(consolidados)
            consolidados.append(resultado)
        elif resultado[1] > consolidados[i][1]:
            consolidados[i] = resultado
    return consolidados


def lista_por_monticulo(pacientes: list[Resultado], k: int) -> list[Resultado]:
    """Op. 2 de referencia: selección top-k con montículo, Θ(n log k).

    Args:
        pacientes: Un resultado por paciente.
        k: Capacidad diaria del centro de contacto.

    Returns:
        Los k pacientes de mayor prioridad, en orden de llamada.
    """
    return heapq.nsmallest(k, pacientes, key=clave_prioridad)
