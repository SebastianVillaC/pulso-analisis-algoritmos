"""Experimentos, gráficas y extrapolación de la operación 3.

Ejecutar desde la raíz del repositorio (tarda unos minutos):

    python src/jornadas_unidades/medicion.py

Produce:
    graficas/jornadas_unidades/tiempo_vs_n.png
    graficas/jornadas_unidades/operaciones_vs_n.png
    graficas/jornadas_unidades/pacientes_por_estrategia.png
    resultados/jornadas_unidades/mediciones.csv
    resultados/jornadas_unidades/pacientes.csv
    resultados/jornadas_unidades/resumen.md
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

from datos import generar_solicitudes  # noqa: E402
from estrategia import seleccionar_jornadas, terminacion_temprana  # noqa: E402
from exhaustivo import seleccionar_exhaustivo  # noqa: E402
from modelo import Contador, Jornada, total_pacientes  # noqa: E402
from regla_actual import asignar_por_llegada  # noqa: E402

Solucion = Callable[[list[Jornada], Contador | None], list[Jornada]]

SEMILLA = 2026
REPETICIONES = 5
TAMANOS_EXHAUSTIVO = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
TAMANOS_GRANDES = [40, 120, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000,
                   64000, 128000]
TOPE_REGLA_ACTUAL = 16000  # Θ(n²): más allá tarda demasiado en Python
N_MAX_EXH = 24  # mayor tamaño donde corre la exhaustiva
INSTANCIAS_PACIENTES = 200
TAMANOS_PACIENTES = [40, 80, 120]

# Cifras del caso 2.
SUBREGIONES = 9
MESES_POR_ANO = 12
N_REAL = 120  # máximo de solicitudes por subregión y mes
POTENCIA_KW = 0.380
VENTANA_H = 4.0  # ventana nocturna 01:00-05:00, tomada como referencia
EDAD_UNIVERSO_ANOS = 13.8e9
SEGUNDOS_POR_ANO = 365.25 * 24 * 3600

RAIZ = Path(__file__).resolve().parents[2]
DIR_GRAFICAS = RAIZ / "graficas" / "jornadas_unidades"
DIR_RESULTADOS = RAIZ / "resultados" / "jornadas_unidades"

# Paleta categórica fija (slots 1-4), cada solución con su color y marcador.
ESTILOS = {
    "Programación dinámica": {"color": "#2a78d6", "marker": "o", "ls": "-"},
    "Exhaustiva": {"color": "#eb6834", "marker": "s", "ls": "-"},
    "Regla actual (llegada)": {"color": "#1baf7a", "marker": "^", "ls": "--"},
    "Voraz (terminación temprana)": {"color": "#eda100", "marker": "D",
                                     "ls": ":"},
}

SOLUCIONES: dict[str, Solucion] = {
    "Programación dinámica": seleccionar_jornadas,
    "Exhaustiva": seleccionar_exhaustivo,
    "Regla actual (llegada)": asignar_por_llegada,
    "Voraz (terminación temprana)": terminacion_temprana,
}


def cronometrar(solucion: Solucion, solicitudes: list[Jornada]) -> float:
    """Mide el tiempo medio de una solución, sin contar la generación de datos.

    Args:
        solucion: Función que resuelve la instancia.
        solicitudes: Instancia a resolver (la misma para todas las soluciones).

    Returns:
        El tiempo medio en segundos de REPETICIONES ejecuciones.
    """
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        solucion(solicitudes, None)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.mean(tiempos)


def contar_operaciones(solucion: Solucion, solicitudes: list[Jornada]) -> int:
    """Ejecuta la solución una vez con contador y suma sus operaciones.

    Args:
        solucion: Función que resuelve la instancia.
        solicitudes: Instancia a resolver.

    Returns:
        El total de operaciones elementales contadas.
    """
    contador: Contador = {}
    solucion(solicitudes, contador)
    return sum(contador.values())


def medir() -> list[dict[str, float | int | str]]:
    """Mide tiempo y operaciones de cada solución en tamaños crecientes.

    Dentro del experimento verifica que la programación dinámica y la
    exhaustiva obtienen el mismo número de pacientes donde ambas corren.

    Returns:
        Una fila por (solución, tamaño) con tiempo, operaciones y pacientes.
    """
    filas: list[dict[str, float | int | str]] = []
    tamanos = sorted(set(TAMANOS_EXHAUSTIVO + TAMANOS_GRANDES))
    for n in tamanos:
        solicitudes = generar_solicitudes(n, SEMILLA + n)
        valores: dict[str, int] = {}
        for nombre, solucion in SOLUCIONES.items():
            if nombre == "Exhaustiva" and n not in TAMANOS_EXHAUSTIVO:
                continue
            if nombre == "Regla actual (llegada)" and n > TOPE_REGLA_ACTUAL:
                continue
            tiempo = cronometrar(solucion, solicitudes)
            operaciones = contar_operaciones(solucion, solicitudes)
            valores[nombre] = total_pacientes(solucion(solicitudes, None))
            filas.append({"solucion": nombre, "n": n, "tiempo_s": tiempo,
                          "operaciones": operaciones,
                          "pacientes": valores[nombre]})
            print(f"n={n:>6}  {nombre:<30} {tiempo:.6f} s  "
                  f"{operaciones:>12} ops")
        if "Exhaustiva" in valores:
            assert valores["Exhaustiva"] == valores["Programación dinámica"], n
    return filas


def comparar_pacientes() -> list[dict[str, float | int | str]]:
    """Compara los pacientes atendidos por cada estrategia en tamaños reales.

    Returns:
        Una fila por (tamaño, solución) con el promedio de pacientes y de
        jornadas en INSTANCIAS_PACIENTES meses sintéticos.
    """
    filas: list[dict[str, float | int | str]] = []
    nombres = ["Programación dinámica", "Regla actual (llegada)",
               "Voraz (terminación temprana)"]
    for n in TAMANOS_PACIENTES:
        pacientes: dict[str, list[int]] = {nombre: [] for nombre in nombres}
        jornadas: dict[str, list[int]] = {nombre: [] for nombre in nombres}
        for k in range(INSTANCIAS_PACIENTES):
            solicitudes = generar_solicitudes(n, SEMILLA * 1000 + n * 7 + k)
            for nombre in nombres:
                elegidas = SOLUCIONES[nombre](solicitudes, None)
                pacientes[nombre].append(total_pacientes(elegidas))
                jornadas[nombre].append(len(elegidas))
        for nombre in nombres:
            filas.append({"n": n, "solucion": nombre,
                          "pacientes_prom": statistics.mean(pacientes[nombre]),
                          "jornadas_prom": statistics.mean(jornadas[nombre])})
    return filas


def series(filas: list[dict[str, float | int | str]], nombre: str,
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


def graficar(filas: list[dict[str, float | int | str]], campo: str,
             etiqueta_y: str, titulo: str, archivo: Path) -> None:
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
    ax.axvline(N_REAL, color="#888888", linewidth=1, linestyle="--")
    ax.text(N_REAL * 1.08, 0.97, "volumen real\n(n = 120)",
            transform=ax.get_xaxis_transform(), va="top",
            color="#555555", fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n: número de solicitudes de jornada (escala log)")
    ax.set_ylabel(etiqueta_y)
    ax.set_title(titulo)
    ax.grid(True, which="major", color="#e6e6e6", linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)


def graficar_pacientes(filas: list[dict[str, float | int | str]],
                       archivo: Path) -> None:
    """Dibuja barras agrupadas de pacientes atendidos por estrategia.

    Args:
        filas: Resultados de comparar_pacientes().
        archivo: Ruta del PNG de salida.
    """
    nombres = ["Programación dinámica", "Regla actual (llegada)",
               "Voraz (terminación temprana)"]
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=130)
    ancho = 0.26
    for i, nombre in enumerate(nombres):
        valores = [float(f["pacientes_prom"]) for f in filas
                   if f["solucion"] == nombre]
        posiciones = [k + (i - 1) * ancho
                      for k in range(len(TAMANOS_PACIENTES))]
        barras = ax.bar(posiciones, valores, width=ancho - 0.02,
                        color=ESTILOS[nombre]["color"], label=nombre)
        ax.bar_label(barras, fmt="%.0f", fontsize=8, color="#333333")
    ax.set_xticks(range(len(TAMANOS_PACIENTES)))
    ax.set_xticklabels([f"n = {n}" for n in TAMANOS_PACIENTES])
    ax.set_xlabel("Solicitudes de jornada en el mes de una subregión")
    ax.set_ylabel("Pacientes de alto riesgo atendidos (promedio por mes)")
    ax.set_title(f"Pacientes atendidos por estrategia "
                 f"({INSTANCIAS_PACIENTES} meses sintéticos por tamaño)")
    ax.grid(True, axis="y", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)


def buscar(filas: list[dict[str, float | int | str]], nombre: str, n: int,
           campo: str) -> float:
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


def tabla_duplicar(filas: list[dict[str, float | int | str]]) -> list[str]:
    """Calcula el factor de crecimiento al duplicar n para cada solución.

    Args:
        filas: Resultados de medir().

    Returns:
        Líneas de una tabla Markdown.
    """
    parejas = [
        ("Exhaustiva", 8, 16), ("Exhaustiva", 10, 20),
        ("Exhaustiva", 12, 24),
        ("Programación dinámica", 10, 20),
        ("Programación dinámica", 1000, 2000),
        ("Programación dinámica", 64000, 128000),
        ("Regla actual (llegada)", 10, 20),
        ("Regla actual (llegada)", 8000, 16000),
        ("Voraz (terminación temprana)", 64000, 128000),
    ]
    esperado = {
        "Exhaustiva": lambda a, b: (b * 2 ** b) / (a * 2 ** a),
        "Programación dinámica": lambda a, b: (b * math.log2(b))
        / (a * math.log2(a)),
        "Regla actual (llegada)": lambda a, b: (b / a) ** 2,
        "Voraz (terminación temprana)": lambda a, b: (b * math.log2(b))
        / (a * math.log2(a)),
    }
    lineas = ["| Solución | n → 2n | Factor tiempo | Factor operaciones "
              "| Factor esperado |", "|---|---|---|---|---|"]
    for nombre, a, b in parejas:
        ft = (buscar(filas, nombre, b, "tiempo_s")
              / buscar(filas, nombre, a, "tiempo_s"))
        fo = buscar(filas, nombre, b, "operaciones") / buscar(
            filas, nombre, a, "operaciones")
        fe = esperado[nombre](a, b)
        lineas.append(f"| {nombre} | {a} → {b} | {ft:.2f} | {fo:.2f} "
                      f"| {fe:.2f} |")
    return lineas


def extrapolar(filas: list[dict[str, float | int | str]]) -> list[str]:
    """Extrapola al volumen real, compara con la ventana y estima la energía.

    Para la PD y la regla actual, n = 120 está dentro de lo medido. Para la
    exhaustiva se ajusta la constante c de T(n) = c·n·2ⁿ con la medición más
    grande (n = 24) y se proyecta a n = 120 y a n = 40.

    Args:
        filas: Resultados de medir().

    Returns:
        Líneas Markdown con la tabla de extrapolación y energía.
    """
    ejecuciones_mes = SUBREGIONES
    ejecuciones_ano = SUBREGIONES * MESES_POR_ANO
    t20 = buscar(filas, "Exhaustiva", N_MAX_EXH, "tiempo_s")
    c_exh = t20 / (N_MAX_EXH * 2 ** N_MAX_EXH)

    def t_exhaustiva(n: int) -> float:
        return c_exh * n * 2 ** n

    tiempos = {
        "Programación dinámica": buscar(filas, "Programación dinámica",
                                        N_REAL, "tiempo_s"),
        "Regla actual (llegada)": buscar(filas, "Regla actual (llegada)",
                                         N_REAL, "tiempo_s"),
        "Exhaustiva": t_exhaustiva(N_REAL),
    }
    lineas = [
        f"Volumen real: {SUBREGIONES} subregiones × hasta {N_REAL} "
        "solicitudes "
        f"por mes = {ejecuciones_mes} ejecuciones/mes, {ejecuciones_ano}/año. "
        f"Servidor de {POTENCIA_KW * 1000:.0f} W.",
        "",
        "| Solución | Tiempo por subregión (n=120) | Tiempo por mes (×9) "
        "| ¿Cabe en 4 h? | Energía por mes (kWh) | Energía por año (kWh) |",
        "|---|---|---|---|---|---|",
    ]
    energia_ano: dict[str, float] = {}
    for nombre, t in tiempos.items():
        t_mes = t * ejecuciones_mes
        kwh_mes = POTENCIA_KW * t_mes / 3600
        kwh_ano = kwh_mes * MESES_POR_ANO
        energia_ano[nombre] = kwh_ano
        cabe = "Sí" if t_mes / 3600 <= VENTANA_H else "No"
        lineas.append(f"| {nombre} | {formatear_tiempo(t)} | "
                      f"{formatear_tiempo(t_mes)} | {cabe} | {kwh_mes:.3e} | "
                      f"{kwh_ano:.3e} |")
    anos_exh = t_exhaustiva(N_REAL) / SEGUNDOS_POR_ANO
    diferencia = (energia_ano["Regla actual (llegada)"]
                  - energia_ano["Programación dinámica"])
    lineas += [
        "",
        f"Constante ajustada exhaustiva: c = {c_exh:.3e} s por (n·2ⁿ), "
        f"con T({N_MAX_EXH}) = {t20:.3f} s.",
        f"Exhaustiva con n = 40 (mes más liviano): "
        f"{formatear_tiempo(t_exhaustiva(40))}.",
        f"Exhaustiva con n = 120: {anos_exh:.3e} "
        f"años = {anos_exh / EDAD_UNIVERSO_ANOS:.3e}"
        f" veces la edad del universo.",
        f"Diferencia anual regla actual − PD: {diferencia:.3e} kWh.",
    ]
    return lineas


def formatear_tiempo(segundos: float) -> str:
    """Expresa un tiempo en la unidad más legible.

    Args:
        segundos: Tiempo en segundos.

    Returns:
        El tiempo con su unidad (µs, ms, s, h o años).
    """
    if segundos < 1e-3:
        return f"{segundos * 1e6:.1f} µs"
    if segundos < 1:
        return f"{segundos * 1e3:.2f} ms"
    if segundos < 3600:
        return f"{segundos:.2f} s"
    if segundos < SEGUNDOS_POR_ANO:
        return f"{segundos / 3600:.2f} h"
    return f"{segundos / SEGUNDOS_POR_ANO:.3e} años"


def guardar_csv(
    filas: list[dict[str, float | int | str]], archivo: Path
) -> None:
    """Escribe una lista de filas en CSV.

    Args:
        filas: Filas con las mismas claves.
        archivo: Ruta del CSV.
    """
    with archivo.open("w", newline="", encoding="utf-8") as salida:
        escritor = csv.DictWriter(salida, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def tabla_pacientes(filas: list[dict[str, float | int | str]]) -> list[str]:
    """Resume la mejora en pacientes de la PD frente a las otras reglas.

    Args:
        filas: Resultados de comparar_pacientes().

    Returns:
        Líneas de una tabla Markdown.
    """
    lineas = ["| n | PD: pacientes (jornadas) | Regla actual: pacientes "
              "(jornadas) | Voraz: pacientes (jornadas) "
              "| Mejora PD vs actual |",
              "|---|---|---|---|---|"]
    for n in TAMANOS_PACIENTES:
        datos = {str(f["solucion"]): f for f in filas if f["n"] == n}
        pd_ = datos["Programación dinámica"]
        ac = datos["Regla actual (llegada)"]
        vz = datos["Voraz (terminación temprana)"]
        mejora = float(pd_["pacientes_prom"]) / float(ac["pacientes_prom"]) - 1
        lineas.append(
            f"| {n} | {float(pd_['pacientes_prom']):.1f} "
            f"({float(pd_['jornadas_prom']):.1f}) | "
            f"{float(ac['pacientes_prom']):.1f} "
            f"({float(ac['jornadas_prom']):.1f}) | "
            f"{float(vz['pacientes_prom']):.1f} "
            f"({float(vz['jornadas_prom']):.1f}) | {mejora:+.1%} |")
    return lineas


def main() -> None:
    """Corre los experimentos, guarda resultados y dibuja las gráficas."""
    DIR_GRAFICAS.mkdir(parents=True, exist_ok=True)
    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)

    filas = medir()
    guardar_csv(filas, DIR_RESULTADOS / "mediciones.csv")
    graficar(filas, "tiempo_s", "Tiempo medio por instancia (s, escala log)",
             "Operación 3: tiempo de ejecución frente a n",
             DIR_GRAFICAS / "tiempo_vs_n.png")
    graficar(filas, "operaciones",
             "Operaciones elementales (conteo, escala log)",
             "Operación 3: operaciones elementales frente a n",
             DIR_GRAFICAS / "operaciones_vs_n.png")

    pacientes = comparar_pacientes()
    guardar_csv(pacientes, DIR_RESULTADOS / "pacientes.csv")
    graficar_pacientes(pacientes,
                       DIR_GRAFICAS / "pacientes_por_estrategia.png")

    resumen = ["# Resumen de mediciones — operación 3", "",
               f"Semilla {SEMILLA}, {REPETICIONES} repeticiones por tamaño "
               "(se reporta el promedio).", "", "## Factor al duplicar n", ""]
    resumen += tabla_duplicar(filas)
    resumen += ["", "## Pacientes atendidos", ""] + tabla_pacientes(pacientes)
    resumen += ["", "## Extrapolación y energía", ""] + extrapolar(filas)
    texto = "\n".join(resumen) + "\n"
    (DIR_RESULTADOS / "resumen.md").write_text(texto, encoding="utf-8")
    print()
    print(texto)


if __name__ == "__main__":
    main()
