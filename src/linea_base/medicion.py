"""Línea base del proceso nocturno (operaciones 1 y 2) y una referencia.

Ejecutar desde la raíz del repositorio (tarda alrededor de un minuto):

    python src/linea_base/medicion.py

Verifica que la implementación actual y la de referencia den el mismo
resultado, mide ambas en tamaños crecientes, extrapola la actual (Θ(n²)) a
1.450.000 resultados y estima la energía por noche y por año.

Produce:
    graficas/linea_base/tiempo_vs_n.png
    resultados/linea_base/resumen.md
"""

import random
import statistics
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from procesos import (  # noqa: E402
    Resultado,
    consolidar_hash,
    consolidar_lineal,
    lista_por_insercion,
    lista_por_monticulo,
)

SEMILLA = 2026
REPETICIONES = 3
FRACCION_PACIENTES = 0.88  # entre 8 % y 15 % de los resultados son repetidos
LLAMADAS = 9000
N_REAL = 1_450_000
POTENCIA_KW = 0.380
NOCHES_ANO = 365
HORAS_CLIENTE = 7.0  # duración actual informada por la Secretaría
TAMANOS_ACTUAL = [500, 1000, 2000, 4000, 8000, 16000]
TAMANOS_REFERENCIA = [500, 1000, 2000, 4000, 8000, 64000, 512000, N_REAL]

RAIZ = Path(__file__).resolve().parents[2]
DIR_GRAFICAS = RAIZ / "graficas" / "linea_base"
DIR_RESULTADOS = RAIZ / "resultados" / "linea_base"

Proceso = Callable[[list[Resultado]], list[Resultado]]


def generar_resultados(n: int, semilla: int) -> list[Resultado]:
    """Genera n resultados de laboratorio con pacientes repetidos.

    Args:
        n: Número de resultados.
        semilla: Semilla fija del generador.

    Returns:
        Resultados (documento, fecha en minutos, riesgo 0-100).
    """
    rng = random.Random(semilla)
    pacientes = max(1, int(n * FRACCION_PACIENTES))
    return [(rng.randrange(pacientes), rng.randrange(10_000_000),
             rng.randint(0, 100)) for _ in range(n)]


def proceso_actual(resultados: list[Resultado]) -> list[Resultado]:
    """Ops. 1 y 2 como se hacen hoy: búsqueda lineal e inserción.

    Args:
        resultados: Resultados del día.

    Returns:
        La lista de llamadas del día.
    """
    return lista_por_insercion(consolidar_lineal(resultados), LLAMADAS)


def proceso_referencia(resultados: list[Resultado]) -> list[Resultado]:
    """Ops. 1 y 2 con tabla hash y montículo top-k.

    Args:
        resultados: Resultados del día.

    Returns:
        La lista de llamadas del día.
    """
    return lista_por_monticulo(consolidar_hash(resultados), LLAMADAS)


def verificar() -> None:
    """Comprueba con assert que ambas versiones dan el mismo resultado."""
    rng = random.Random(SEMILLA)
    for _ in range(50):
        n = rng.randint(0, 400)
        datos = generar_resultados(n, rng.randrange(10**6))
        copia = list(datos)
        assert consolidar_lineal(datos) == consolidar_hash(datos)
        consolidados = consolidar_hash(datos)
        for k in (0, 1, 10, n):
            assert (lista_por_insercion(consolidados, k)
                    == lista_por_monticulo(consolidados, k))
        assert datos == copia, "los registros originales no se modifican"
        documentos = [r[0] for r in consolidados]
        assert len(documentos) == len(set(documentos)), "uno por paciente"
        assert set(documentos) == {r[0] for r in datos}, "nadie desaparece"


def cronometrar(proceso: Proceso, datos: list[Resultado]) -> float:
    """Mide el tiempo medio de un proceso, sin contar la generación de datos.

    Args:
        proceso: Función que procesa los resultados.
        datos: Resultados del día.

    Returns:
        El tiempo medio en segundos.
    """
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        proceso(datos)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.mean(tiempos)


def medir(proceso: Proceso, tamanos: list[int]) -> dict[int, float]:
    """Mide un proceso en varios tamaños.

    Args:
        proceso: Función que procesa los resultados.
        tamanos: Tamaños a medir.

    Returns:
        Tiempo medio en segundos por tamaño.
    """
    tiempos: dict[int, float] = {}
    for n in tamanos:
        tiempos[n] = cronometrar(proceso, generar_resultados(n, SEMILLA + n))
        print(f"{proceso.__name__:<20} n={n:>8}  {tiempos[n]:.4f} s")
    return tiempos


def graficar(actual: dict[int, float], referencia: dict[int, float],
             archivo: Path) -> None:
    """Dibuja el tiempo de ambas versiones frente a n.

    Args:
        actual: Tiempos del proceso actual.
        referencia: Tiempos del proceso de referencia.
        archivo: Ruta del PNG de salida.
    """
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=130)
    ax.plot(list(actual), list(actual.values()), color="#1baf7a", marker="^",
            linestyle="--", linewidth=2, label="Actual: búsqueda lineal + "
            "inserción Θ(n²)")
    ax.plot(list(referencia), list(referencia.values()), color="#2a78d6",
            marker="o", linewidth=2, label="Referencia: tabla hash + "
            "montículo top-k")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n: resultados de laboratorio del día (escala log)")
    ax.set_ylabel("Tiempo medio (s, escala log)")
    ax.set_title("Línea base: operaciones 1 y 2 del proceso nocturno")
    ax.grid(True, which="major", color="#e6e6e6", linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)


def resumir(actual: dict[int, float], referencia: dict[int, float]) -> str:
    """Extrapola al volumen real y calcula la energía por noche y por año.

    Args:
        actual: Tiempos del proceso actual.
        referencia: Tiempos del proceso de referencia.

    Returns:
        El resumen en Markdown.
    """
    n_max = max(actual)
    c = actual[n_max] / n_max ** 2
    h_actual = c * N_REAL ** 2 / 3600
    h_ref = referencia[N_REAL] / 3600
    filas = [
        ("Actual (medición Python, extrapolada c·n²)", h_actual),
        ("Actual (cifra informada por la Secretaría)", HORAS_CLIENTE),
        ("Referencia hash + montículo (medida en n real)", h_ref),
    ]
    lineas = [
        "# Línea base — operaciones 1 y 2", "",
        f"Semilla {SEMILLA}, {REPETICIONES} repeticiones. "
        f"Factor al duplicar n del actual: "
        f"{actual[n_max] / actual[n_max // 2]:.2f} (esperado 4,00).", "",
        f"Constante del actual: c = {c:.3e} s por n². "
        f"n real = {N_REAL} resultados.", "",
        "| Proceso | Horas por noche | ¿Cabe en 4 h? | kWh por noche "
        "| kWh por año |", "|---|---|---|---|---|",
    ]
    for nombre, horas in filas:
        kwh = POTENCIA_KW * horas
        cabe = "Sí" if horas <= 4 else "No"
        lineas.append(f"| {nombre} | {horas:.4g} | {cabe} | {kwh:.4g} "
                      f"| {kwh * NOCHES_ANO:.4g} |")
    return "\n".join(lineas) + "\n"


def main() -> None:
    """Verifica, mide, grafica y resume la línea base."""
    DIR_GRAFICAS.mkdir(parents=True, exist_ok=True)
    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)
    verificar()
    print("OK: actual y referencia coinciden en 50 instancias.")
    actual = medir(proceso_actual, TAMANOS_ACTUAL)
    referencia = medir(proceso_referencia, TAMANOS_REFERENCIA)
    graficar(actual, referencia, DIR_GRAFICAS / "tiempo_vs_n.png")
    texto = resumir(actual, referencia)
    (DIR_RESULTADOS / "resumen.md").write_text(texto, encoding="utf-8")
    print()
    print(texto)


if __name__ == "__main__":
    main()
