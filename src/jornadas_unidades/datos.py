"""Generador de solicitudes sintéticas de jornadas, con semilla fija.

Estructura representativa del caso:
- Las horas se expresan en minutos desde el inicio del periodo (día 0, 00:00).
- Cada jornada empieza entre las 06:00 y las 16:00 de algún día, en múltiplos
  de 30 minutos, y dura entre 2 y 10 horas (incluido el desplazamiento).
- Los pacientes de alto riesgo pendientes del municipio van de 1 a 80.
- La densidad es constante: unas 4 solicitudes por día, la del mes más
  cargado del caso (120 solicitudes en 30 días). Así, n = 120 equivale a un
  mes real y los tamaños mayores alargan el periodo sin cambiar la forma de
  los datos.
"""

import random

from modelo import Jornada

MINUTOS_POR_DIA = 24 * 60
SOLICITUDES_POR_DIA = 4
HORA_MIN_INICIO = 6 * 60
HORA_MAX_INICIO = 16 * 60
DURACION_MIN = 2 * 60
DURACION_MAX = 10 * 60
PASO_MINUTOS = 30
PACIENTES_MIN = 1
PACIENTES_MAX = 80


def dias_del_periodo(n: int) -> int:
    """Calcula cuántos días abarca un periodo con n solicitudes.

    Args:
        n: Número de solicitudes.

    Returns:
        Los días del periodo, con al menos 1.
    """
    return max(1, -(-n // SOLICITUDES_POR_DIA))  # techo de n / 4


def generar_solicitud(rng: random.Random, dias: int) -> Jornada:
    """Genera una solicitud aleatoria dentro de un periodo.

    Args:
        rng: Generador de números aleatorios con semilla.
        dias: Días que abarca el periodo.

    Returns:
        Una jornada (inicio, fin, pacientes) con horas en minutos.
    """
    dia = rng.randrange(dias)
    pasos_inicio = (HORA_MAX_INICIO - HORA_MIN_INICIO) // PASO_MINUTOS
    hora = HORA_MIN_INICIO + rng.randint(0, pasos_inicio) * PASO_MINUTOS
    pasos_duracion = (DURACION_MAX - DURACION_MIN) // PASO_MINUTOS
    duracion = DURACION_MIN + rng.randint(0, pasos_duracion) * PASO_MINUTOS
    inicio = dia * MINUTOS_POR_DIA + hora
    pacientes = rng.randint(PACIENTES_MIN, PACIENTES_MAX)
    return (inicio, inicio + duracion, pacientes)


def generar_solicitudes(n: int, semilla: int) -> list[Jornada]:
    """Genera n solicitudes en orden de llegada (aleatorio), reproducibles.

    Args:
        n: Número de solicitudes.
        semilla: Semilla fija del generador.

    Returns:
        Las solicitudes en el orden en que "llegaron".
    """
    rng = random.Random(semilla)
    dias = dias_del_periodo(n)
    return [generar_solicitud(rng, dias) for _ in range(n)]


def generar_pequena(rng: random.Random, n_max: int = 10) -> list[Jornada]:
    """Genera una instancia pequeña y muy cruzada para las pruebas.

    Usa horas en un solo día (0 a 20 h) para que haya muchos cruces.

    Args:
        rng: Generador de números aleatorios con semilla.
        n_max: Máximo de solicitudes de la instancia.

    Returns:
        Entre 1 y n_max solicitudes.
    """
    solicitudes: list[Jornada] = []
    for _ in range(rng.randint(1, n_max)):
        inicio = rng.randint(0, 20) * 60
        fin = inicio + rng.randint(1, 6) * 60
        solicitudes.append((inicio, fin, rng.randint(0, 15)))
    return solicitudes
