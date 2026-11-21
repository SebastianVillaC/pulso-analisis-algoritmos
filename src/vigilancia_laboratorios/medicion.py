"""Experimentos, gráficas y extrapolación de la operación 4.

Ejecutar desde la raíz del repositorio (tarda unos minutos):

    python src/vigilancia_laboratorios/medicion.py

Produce:
    graficas/vigilancia_laboratorios/tiempo_vs_n.png
    graficas/vigilancia_laboratorios/operaciones_vs_n.png
    resultados/vigilancia_laboratorios/mediciones.csv
    resultados/vigilancia_laboratorios/resumen.md
"""

import csv
import math
import statistics
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # solo se escriben archivos, no se abre ventana
import matplotlib.pyplot as plt  # noqa: E402

from datos import generar_serie  # noqa: E402
from dividir_y_vencer import tramo_dyv  # noqa: E402
from estrategia import tramo_kadane  # noqa: E402
from exhaustivo import tramo_acumulado  # noqa: E402
from modelo import Contador, Tramo  # noqa: E402
from regla_actual import tramo_actual  # noqa: E402

Solucion = Callable[[list[int], Contador | None], Tramo]
Fila = dict[str, float | int | str]

SEMILLA = 2026
REPETICIONES = 5
TAMANOS = [25, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600,
           33000, 51200, 102400, 204800]

ACTUAL = "Regla actual Θ(n³)"
CUADRATICA = "Todos los tramos con suma acumulada Θ(n²)"
DYV = "Dividir y vencer Θ(n log n)"
KADANE = "Kadane Θ(n)"

SOLUCIONES: dict[str, Solucion] = {
    ACTUAL: tramo_actual,
    CUADRATICA: tramo_acumulado,
    DYV: tramo_dyv,
    KADANE: tramo_kadane,
}
TOPES = {ACTUAL: 800, CUADRATICA: 6400, DYV: 204800, KADANE: 204800}

# Forma de la curva de cada solución, para extrapolar y para el factor
# esperado al duplicar n.
FORMAS: dict[str, Callable[[float], float]] = {
    ACTUAL: lambda n: n ** 3,
    CUADRATICA: lambda n: n ** 2,
    DYV: lambda n: n * math.log2(n),
    KADANE: lambda n: n,
}

ESTILOS = {
    ACTUAL: {"color": "#1baf7a", "marker": "^", "ls": "--"},
    CUADRATICA: {"color": "#eb6834", "marker": "s", "ls": "-"},
    DYV: {"color": "#6250d6", "marker": "D", "ls": "-."},
    KADANE: {"color": "#2a78d6", "marker": "o", "ls": "-"},
}

# Cifras del caso 2.
LABORATORIOS = 290
N_REAL = 33000  # lotes por laboratorio en tres años
EJECUCIONES_ANO = 365  # supuesto: la vigilancia se corre una vez al día
POTENCIA_KW = 0.380
VENTANA_H = 4.0

RAIZ = Path(__file__).resolve().parents[2]
DIR_GRAFICAS = RAIZ / "graficas" / "vigilancia_laboratorios"
DIR_RESULTADOS = RAIZ / "resultados" / "vigilancia_laboratorios"


def cronometrar(solucion: Solucion, serie: list[int]) -> float:
    """Mide el tiempo medio de una solución, sin contar la generación de datos.

    Args:
        solucion: Función que resuelve la instancia.
        serie: Instancia a resolver (la misma para todas las soluciones).

    Returns:
        El tiempo medio en segundos de REPETICIONES ejecuciones.
    """
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        solucion(serie, None)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.mean(tiempos)


def contar_operaciones(solucion: Solucion, serie: list[int]) -> int:
    """Ejecuta la solución una vez con contador y suma sus operaciones.

    Args:
        solucion: Función que resuelve la instancia.
        serie: Instancia a resolver.

    Returns:
        El total de operaciones elementales (sumas y comparaciones).
    """
    contador: Contador = {}
    solucion(serie, contador)
    return sum(contador.values())


def medir() -> list[Fila]:
    """Mide tiempo y operaciones de cada solución en tamaños crecientes.

    Dentro del experimento verifica que todas las soluciones que corren en un
    tamaño reportan el mismo exceso máximo.

    Returns:
        Una fila por (solución, tamaño) con tiempo, operaciones y exceso.
    """
    filas: list[Fila] = []
    for n in TAMANOS:
        serie = generar_serie(n, SEMILLA + n)
        excesos: set[int] = set()
        for nombre, solucion in SOLUCIONES.items():
            if n > TOPES[nombre]:
                continue
            tiempo = cronometrar(solucion, serie)
            operaciones = contar_operaciones(solucion, serie)
            suma, inicio, fin = solucion(serie, None)
            excesos.add(suma)
            filas.append({"solucion": nombre, "n": n, "tiempo_s": tiempo,
                          "operaciones": operaciones, "exceso": suma,
                          "inicio": inicio, "fin": fin})
            print(f"n={n:>6}  {nombre:<42} {tiempo:.6f} s  "
                  f"{operaciones:>12} ops")
        assert len(excesos) == 1, (n, excesos)  # todas coinciden
    return filas


def series(filas: list[Fila], nombre: str,
           campo: str) -> tuple[list[int], list[float]]:
    """Extrae los puntos (n, campo) de una solución.

    Args:
        filas: Resultados de medir().
        nombre: Nombre de la solución.
        campo: "tiempo_s" u "operaciones".

    Returns:
        Las listas de tamaños y valores, en orden creciente de n.
    """
    puntos = sorted((int(f["n"]), float(f[campo])) for f in filas
                    if f["solucion"] == nombre)
    return [p[0] for p in puntos], [p[1] for p in puntos]


def graficar(filas: list[Fila], campo: str, etiqueta_y: str, titulo: str,
             archivo: Path) -> None:
    """Dibuja una métrica frente a n, con todas las soluciones en un eje.

    Args:
        filas: Resultados de medir().
        campo: "tiempo_s" u "operaciones".
        etiqueta_y: Rótulo del eje y, con unidades.
        titulo: Título de la gráfica.
        archivo: Ruta del PNG de salida.
    """
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=130)
    for nombre, estilo in ESTILOS.items():
        xs, ys = series(filas, nombre, campo)
        ax.plot(xs, ys, color=estilo["color"], marker=estilo["marker"],
                linestyle=estilo["ls"], linewidth=2, markersize=6,
                label=nombre)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.axvline(N_REAL, color="#888888", linewidth=1, linestyle="--")
    ax.text(N_REAL * 0.92, 0.97, "volumen real\n(n = 33.000)",
            transform=ax.get_xaxis_transform(), va="top", ha="right",
            color="#555555", fontsize=8)
    ax.set_xlabel("n: número de lotes de un laboratorio (escala log)")
    ax.set_ylabel(etiqueta_y)
    ax.set_title(titulo)
    ax.grid(True, which="major", color="#e6e6e6", linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)


def buscar(filas: list[Fila], nombre: str, n: int, campo: str) -> float:
    """Devuelve el valor medido de una solución en un tamaño.

    Args:
        filas: Resultados de medir().
        nombre: Nombre de la solución.
        n: Tamaño.
        campo: "tiempo_s" u "operaciones".

    Returns:
        El valor medido.
    """
    for fila in filas:
        if fila["solucion"] == nombre and fila["n"] == n:
            return float(fila[campo])
    raise KeyError((nombre, n))


def tabla_duplicar(filas: list[Fila]) -> list[str]:
    """Calcula el factor de crecimiento al duplicar n para cada solución.

    Args:
        filas: Resultados de medir().

    Returns:
        Líneas de una tabla Markdown.
    """
    parejas = [
        (ACTUAL, 200, 400), (ACTUAL, 400, 800),
        (CUADRATICA, 1600, 3200), (CUADRATICA, 3200, 6400),
        (DYV, 1600, 3200), (DYV, 102400, 204800),
        (KADANE, 1600, 3200), (KADANE, 102400, 204800),
    ]
    lineas = ["| Solución | n → 2n | Factor tiempo | Factor operaciones "
              "| Factor esperado |", "|---|---|---|---|---|"]
    for nombre, a, b in parejas:
        ft = (buscar(filas, nombre, b, "tiempo_s")
              / buscar(filas, nombre, a, "tiempo_s"))
        fo = (buscar(filas, nombre, b, "operaciones")
              / buscar(filas, nombre, a, "operaciones"))
        fe = FORMAS[nombre](b) / FORMAS[nombre](a)
        lineas.append(f"| {nombre} | {a} → {b} | {ft:.2f} | {fo:.2f} "
                      f"| {fe:.2f} |")
    return lineas


def tiempo_real(filas: list[Fila], nombre: str) -> tuple[float, str]:
    """Estima el tiempo de una solución para un laboratorio con N_REAL lotes.

    Si N_REAL está medido, usa la medición; si no, ajusta la constante c de
    T(n) = c·f(n) con el mayor tamaño medido y la proyecta.

    Args:
        filas: Resultados de medir().
        nombre: Nombre de la solución.

    Returns:
        El tiempo en segundos y una nota sobre cómo se obtuvo.
    """
    try:
        return buscar(filas, nombre, N_REAL, "tiempo_s"), "medido"
    except KeyError:
        n_max = TOPES[nombre]
        c = buscar(filas, nombre, n_max, "tiempo_s") / FORMAS[nombre](n_max)
        return c * FORMAS[nombre](N_REAL), f"extrapolado desde n = {n_max}"


def formatear_tiempo(segundos: float) -> str:
    """Expresa un tiempo en la unidad más legible.

    Args:
        segundos: Tiempo en segundos.

    Returns:
        El tiempo con su unidad (ms, s, h o días).
    """
    if segundos < 1:
        return f"{segundos * 1e3:.2f} ms"
    if segundos < 3600:
        return f"{segundos:.2f} s"
    if segundos < 48 * 3600:
        return f"{segundos / 3600:.2f} h"
    return f"{segundos / 86400:.1f} días"


def extrapolar(filas: list[Fila]) -> list[str]:
    """Extrapola a 290 laboratorios × 33.000 lotes y estima la energía.

    Args:
        filas: Resultados de medir().

    Returns:
        Líneas Markdown con la tabla de extrapolación y energía.
    """
    lineas = [
        f"Volumen real: {LABORATORIOS} laboratorios × {N_REAL} lotes. "
        f"Supuesto: una ejecución diaria ({EJECUCIONES_ANO}/año). "
        f"Servidor de {POTENCIA_KW * 1000:.0f} W.",
        "",
        "| Solución | Un laboratorio | Cómo | 290 laboratorios "
        "| ¿Cabe en 4 h? | kWh por ejecución | kWh/año si fuera diaria |",
        "|---|---|---|---|---|---|---|",
    ]
    energia_ano: dict[str, float] = {}
    for nombre in SOLUCIONES:
        t_lab, como = tiempo_real(filas, nombre)
        t_total = t_lab * LABORATORIOS
        kwh = POTENCIA_KW * t_total / 3600
        energia_ano[nombre] = kwh * EJECUCIONES_ANO
        cabe = "Sí" if t_total / 3600 <= VENTANA_H else "No"
        lineas.append(f"| {nombre} | {formatear_tiempo(t_lab)} | {como} | "
                      f"{formatear_tiempo(t_total)} | {cabe} | {kwh:.3g} | "
                      f"{energia_ano[nombre]:.3g} |")
    ahorro = energia_ano[ACTUAL] - energia_ano[KADANE]
    lineas += ["", "Si una ejecución no cabe en un día, la cifra anual es "
               "teórica: esa solución no puede correr a diario.",
               f"Diferencia anual teórica regla actual − Kadane: "
               f"{ahorro:.4g} kWh."]
    return lineas


def guardar_csv(filas: list[Fila], archivo: Path) -> None:
    """Escribe una lista de filas en CSV.

    Args:
        filas: Filas con las mismas claves.
        archivo: Ruta del CSV.
    """
    with archivo.open("w", newline="", encoding="utf-8") as salida:
        escritor = csv.DictWriter(salida, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def main() -> None:
    """Corre los experimentos, guarda resultados y dibuja las gráficas."""
    DIR_GRAFICAS.mkdir(parents=True, exist_ok=True)
    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)
    filas = medir()
    guardar_csv(filas, DIR_RESULTADOS / "mediciones.csv")
    graficar(filas, "tiempo_s", "Tiempo medio por laboratorio (s, escala log)",
             "Operación 4: tiempo de ejecución frente a n",
             DIR_GRAFICAS / "tiempo_vs_n.png")
    graficar(filas, "operaciones",
             "Operaciones elementales (conteo, escala log)",
             "Operación 4: operaciones elementales frente a n",
             DIR_GRAFICAS / "operaciones_vs_n.png")
    resumen = ["# Resumen de mediciones — operación 4", "",
               f"Semilla {SEMILLA}, {REPETICIONES} repeticiones por tamaño "
               "(se reporta el promedio).", "", "## Factor al duplicar n", ""]
    resumen += tabla_duplicar(filas)
    resumen += ["", "## Extrapolación y energía", ""] + extrapolar(filas)
    texto = "\n".join(resumen) + "\n"
    (DIR_RESULTADOS / "resumen.md").write_text(texto, encoding="utf-8")
    print()
    print(texto)


if __name__ == "__main__":
    main()
