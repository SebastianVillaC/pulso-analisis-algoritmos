"""Pruebas con assert de la operación 4 (vigilancia de laboratorios).

Ejecutar desde la raíz del repositorio:

    python src/vigilancia_laboratorios/pruebas.py
"""

import random
from collections.abc import Callable

from datos import generar_pequena
from dividir_y_vencer import tramo_dyv
from estrategia import tramo_kadane
from exhaustivo import tramo_acumulado
from modelo import SIN_TRAMO, Contador, Tramo, suma_tramo
from regla_actual import tramo_actual

SEMILLA = 2026
INSTANCIAS_ALEATORIAS = 200

SOLUCIONES: list[Callable[[list[int], Contador | None], Tramo]] = [
    tramo_actual, tramo_acumulado, tramo_dyv, tramo_kadane,
]

# Ejemplo resuelto a mano en el README: 8 lotes de un laboratorio.
EJEMPLO_A_MANO = [-20, 35, -10, 40, -60, 15, 25, -5]


def probar_casos_limite() -> None:
    """Verifica serie vacía, un lote, todo negativo y todo positivo."""
    for solucion in SOLUCIONES:
        assert solucion([], None) == SIN_TRAMO
        assert solucion([7], None) == (7, 0, 0)
        assert solucion([-7], None) == (-7, 0, 0)
        # Todo negativo: el tramo es el lote menos negativo.
        assert solucion([-30, -5, -12], None) == (-5, 1, 1)
        # Todo positivo: el tramo es la serie completa.
        assert solucion([3, 1, 4, 1, 5], None) == (14, 0, 4)
        # Ceros y un único pico.
        assert solucion([0, 0, 9, 0], None)[0] == 9


def probar_ejemplo_a_mano() -> None:
    """Verifica el ejemplo de 8 lotes: tramo 1..3 con exceso 65."""
    for solucion in SOLUCIONES:
        assert solucion(EJEMPLO_A_MANO, None) == (65, 1, 3), solucion


def probar_aleatorias() -> None:
    """Compara las 4 soluciones en series aleatorias con semilla fija.

    Verifica además la restricción del negocio: la suma reportada es la suma
    real del tramo reportado y es la mayor posible, y la serie original no se
    modifica.
    """
    rng = random.Random(SEMILLA)
    for _ in range(INSTANCIAS_ALEATORIAS):
        serie = generar_pequena(rng)
        copia = list(serie)
        esperado = tramo_acumulado(serie, None)[0]
        for solucion in SOLUCIONES:
            suma, inicio, fin = solucion(serie, None)
            assert suma == esperado, (solucion, serie)
            assert 0 <= inicio <= fin < len(serie), (solucion, serie)
            assert suma_tramo(serie, inicio, fin) == suma, (solucion, serie)
        assert serie == copia, "la serie original no se modifica"


def probar_contador() -> None:
    """Verifica que el contador refleja la complejidad de cada solución."""
    serie = list(range(-50, 50))
    n = len(serie)
    conteos: list[int] = []
    for solucion in SOLUCIONES:
        contador: Contador = {}
        solucion(serie, contador)
        conteos.append(sum(contador.values()))
    # n(n+1)/2 tramos, cada uno con una suma y una comparación.
    assert conteos[1] == n * (n + 1)
    assert conteos[0] > conteos[1] > conteos[2] > conteos[3]


def main() -> None:
    """Ejecuta todas las pruebas e informa el resultado."""
    probar_casos_limite()
    probar_ejemplo_a_mano()
    probar_aleatorias()
    probar_contador()
    print("OK: casos límite, ejemplo a mano, contador y "
          f"{INSTANCIAS_ALEATORIAS} instancias aleatorias "
          f"(semilla {SEMILLA}).")


if __name__ == "__main__":
    main()
