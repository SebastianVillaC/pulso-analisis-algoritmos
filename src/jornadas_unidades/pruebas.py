"""Pruebas con assert de la operación 3 (jornadas de las unidades móviles).

Ejecutar desde la raíz del repositorio:

    python src/jornadas_unidades/pruebas.py
"""

import random

from datos import generar_pequena
from estrategia import hay_cruce, seleccionar_jornadas, terminacion_temprana
from exhaustivo import seleccionar_exhaustivo
from modelo import Jornada, total_pacientes
from regla_actual import asignar_por_llegada

SEMILLA = 2026
INSTANCIAS_ALEATORIAS = 200


def h(horas: int) -> int:
    """Convierte horas a minutos para escribir los ejemplos de forma legible.

    Args:
        horas: Hora del día o duración en horas.

    Returns:
        El mismo valor en minutos.
    """
    return horas * 60


# Ejemplo resuelto a mano en el README (orden de llegada M1..M6).
M1: Jornada = (h(7), h(12), 4)
M2: Jornada = (h(6), h(9), 10)
M3: Jornada = (h(9), h(13), 8)
M4: Jornada = (h(12), h(16), 5)
M5: Jornada = (h(13), h(17), 12)
M6: Jornada = (h(15), h(18), 3)
EJEMPLO_A_MANO: list[Jornada] = [M1, M2, M3, M4, M5, M6]

# Contraejemplo del voraz por número de jornadas (condición contraria).
X: Jornada = (h(6), h(12), 50)
Y: Jornada = (h(6), h(8), 3)
Z: Jornada = (h(8), h(10), 3)
W: Jornada = (h(10), h(12), 3)
CONTRAEJEMPLO_VORAZ: list[Jornada] = [X, Y, Z, W]


def probar_casos_limite() -> None:
    """Verifica entrada vacía, un elemento, nada se cruza y todo se cruza."""
    assert seleccionar_jornadas([]) == []
    assert seleccionar_exhaustivo([]) == []
    assert asignar_por_llegada([]) == []
    assert hay_cruce([]) is False

    unica: Jornada = (h(8), h(10), 5)
    assert seleccionar_jornadas([unica]) == [unica]
    assert seleccionar_exhaustivo([unica]) == [unica]
    assert asignar_por_llegada([unica]) == [unica]

    # Nada se cruza: se aceptan todas (en cadena, tocándose en los extremos).
    cadena = [(h(10), h(11), 3), (h(8), h(9), 1), (h(9), h(10), 2)]
    esperado = sorted(cadena)
    assert seleccionar_jornadas(cadena) == esperado
    assert hay_cruce(cadena) is False

    # Todo se cruza: solo cabe una, la de más pacientes.
    cruzadas = [(h(8), h(12), 3), (h(9), h(11), 7), (h(10), h(13), 4)]
    assert seleccionar_jornadas(cruzadas) == [(h(9), h(11), 7)]
    assert hay_cruce(cruzadas) is True

    # Tocarse en un extremo no es cruce; solaparse un minuto sí lo es.
    assert hay_cruce([(h(8), h(10), 1), (h(10), h(12), 1)]) is False
    assert hay_cruce([(h(8), h(10) + 1, 1), (h(10), h(12), 1)]) is True

    # Pacientes en cero: la solución vale 0 aunque elija jornadas.
    ceros = [(h(8), h(10), 0), (h(9), h(11), 0)]
    assert total_pacientes(seleccionar_jornadas(ceros)) == 0


def probar_ejemplo_a_mano() -> None:
    """Verifica el ejemplo de 6 solicitudes resuelto a mano en el README."""
    elegidas = seleccionar_jornadas(EJEMPLO_A_MANO)
    assert elegidas == [M2, M3, M5], elegidas
    assert total_pacientes(elegidas) == 30
    assert total_pacientes(seleccionar_exhaustivo(EJEMPLO_A_MANO)) == 30


def probar_contraejemplo_regla_actual() -> None:
    """La asignación por orden de llegada atiende 9 pacientes; la PD, 30."""
    actual = asignar_por_llegada(EJEMPLO_A_MANO)
    assert actual == [M1, M4], actual
    assert total_pacientes(actual) == 9
    optimo = total_pacientes(seleccionar_jornadas(EJEMPLO_A_MANO))
    assert optimo - total_pacientes(actual) == 21


def probar_contraejemplo_voraz() -> None:
    """Más jornadas no es más pacientes: el voraz atiende 9 y la PD 50."""
    voraz = terminacion_temprana(CONTRAEJEMPLO_VORAZ)
    assert voraz == [Y, Z, W]
    assert total_pacientes(voraz) == 9
    assert seleccionar_jornadas(CONTRAEJEMPLO_VORAZ) == [X]
    # Si todas valieran lo mismo, el voraz sería óptimo (condición contraria).
    iguales = [(j[0], j[1], 1) for j in CONTRAEJEMPLO_VORAZ]
    assert len(terminacion_temprana(iguales)) == total_pacientes(
        seleccionar_jornadas(iguales)
    )


def probar_aleatorias() -> None:
    """Compara PD y exhaustiva en instancias pequeñas con semilla fija.

    En cada instancia verifica además la restricción del negocio: la
    programación elegida no tiene dos jornadas que se crucen, y lo elegido
    suma exactamente el óptimo.
    """
    rng = random.Random(SEMILLA)
    for _ in range(INSTANCIAS_ALEATORIAS):
        solicitudes = generar_pequena(rng, n_max=12)
        copia = list(solicitudes)
        dp = seleccionar_jornadas(solicitudes)
        exacta = seleccionar_exhaustivo(solicitudes)
        actual = asignar_por_llegada(solicitudes)
        assert solicitudes == copia, "la entrada original no se modifica"
        assert total_pacientes(dp) == total_pacientes(exacta), solicitudes
        assert not hay_cruce(dp), solicitudes
        assert not hay_cruce(exacta), solicitudes
        assert not hay_cruce(actual), solicitudes
        assert dp == sorted(dp), "devuelve ordenado por hora de inicio"
        assert total_pacientes(actual) <= total_pacientes(dp), solicitudes
        for jornada in dp:
            assert jornada in solicitudes, "solo se eligen solicitudes reales"


def main() -> None:
    """Ejecuta todas las pruebas e informa el resultado."""
    probar_casos_limite()
    probar_ejemplo_a_mano()
    probar_contraejemplo_regla_actual()
    probar_contraejemplo_voraz()
    probar_aleatorias()
    print(
        "OK: casos límite, ejemplo a mano, contraejemplos y "
        f"{INSTANCIAS_ALEATORIAS} instancias aleatorias (semilla {SEMILLA})."
    )


if __name__ == "__main__":
    main()
