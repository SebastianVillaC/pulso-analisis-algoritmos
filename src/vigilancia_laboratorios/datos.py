"""Generador de series sintéticas de lotes de un laboratorio, con semilla fija.

Estructura representativa del caso:
- Cada lote aporta la diferencia entre su tasa de positivos y la esperada, en
  puntos por mil (entero). Un laboratorio bien calibrado oscila alrededor de
  0 (ruido normal con desviación de 40 puntos por mil).
- Cada ~5.000 lotes aparece un episodio de descalibración: entre 20 y 200
  lotes consecutivos con un exceso medio de +25 puntos por mil.
- Un laboratorio procesa ~30 lotes por día; tres años son ~33.000 lotes.
"""

import random

DESVIACION = 40
EXCESO_DESCALIBRADO = 25
LOTES_POR_EPISODIO = 5000
DURACION_MIN = 20
DURACION_MAX = 200


def generar_serie(n: int, semilla: int) -> list[int]:
    """Genera la serie de n lotes de un laboratorio, reproducible.

    Args:
        n: Número de lotes.
        semilla: Semilla fija del generador.

    Returns:
        Las diferencias por lote, en puntos por mil, en orden cronológico.
    """
    rng = random.Random(semilla)
    serie = [round(rng.gauss(0, DESVIACION)) for _ in range(n)]
    episodios = 1 + n // LOTES_POR_EPISODIO
    for _ in range(episodios):
        _insertar_descalibracion(serie, rng)
    return serie


def _insertar_descalibracion(serie: list[int], rng: random.Random) -> None:
    """Suma un exceso sostenido a un tramo aleatorio de la serie.

    Args:
        serie: Serie que se modifica (es la serie sintética recién creada).
        rng: Generador de números aleatorios con semilla.
    """
    if not serie:
        return
    duracion = min(len(serie), rng.randint(DURACION_MIN, DURACION_MAX))
    inicio = rng.randint(0, len(serie) - duracion)
    for k in range(inicio, inicio + duracion):
        serie[k] += EXCESO_DESCALIBRADO


def generar_pequena(rng: random.Random, n_max: int = 30) -> list[int]:
    """Genera una serie corta con valores pequeños, para las pruebas.

    Args:
        rng: Generador de números aleatorios con semilla.
        n_max: Máximo de lotes.

    Returns:
        Entre 1 y n_max valores enteros entre -50 y 50.
    """
    return [rng.randint(-50, 50) for _ in range(rng.randint(1, n_max))]
