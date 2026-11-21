# Resumen de mediciones — operación 4

Semilla 2026, 5 repeticiones por tamaño (se reporta el promedio).

## Factor al duplicar n

| Solución | n → 2n | Factor tiempo | Factor operaciones | Factor esperado |
|---|---|---|---|---|
| Regla actual Θ(n³) | 200 → 400 | 9.09 | 7.88 | 8.00 |
| Regla actual Θ(n³) | 400 → 800 | 8.81 | 7.94 | 8.00 |
| Todos los tramos con suma acumulada Θ(n²) | 1600 → 3200 | 3.99 | 4.00 | 4.00 |
| Todos los tramos con suma acumulada Θ(n²) | 3200 → 6400 | 3.96 | 4.00 | 4.00 |
| Dividir y vencer Θ(n log n) | 1600 → 3200 | 2.13 | 2.17 | 2.19 |
| Dividir y vencer Θ(n log n) | 102400 → 204800 | 2.09 | 2.11 | 2.12 |
| Kadane Θ(n) | 1600 → 3200 | 1.92 | 2.00 | 2.00 |
| Kadane Θ(n) | 102400 → 204800 | 2.01 | 2.00 | 2.00 |

## Extrapolación y energía

Volumen real: 290 laboratorios × 33000 lotes. Supuesto: una ejecución diaria (365/año). Servidor de 380 W.

| Solución | Un laboratorio | Cómo | 290 laboratorios | ¿Cabe en 4 h? | kWh por ejecución | kWh/año si fuera diaria |
|---|---|---|---|---|---|---|
| Regla actual Θ(n³) | 24.04 h | extrapolado desde n = 800 | 290.5 días | No | 2.65e+03 | 9.67e+05 |
| Todos los tramos con suma acumulada Θ(n²) | 21.76 s | extrapolado desde n = 6400 | 1.75 h | Sí | 0.666 | 243 |
| Dividir y vencer Θ(n log n) | 28.74 ms | medido | 8.34 s | Sí | 0.00088 | 0.321 |
| Kadane Θ(n) | 1.70 ms | medido | 492.67 ms | Sí | 5.2e-05 | 0.019 |

Si una ejecución no cabe en un día, la cifra anual es teórica: esa solución no puede correr a diario.
Diferencia anual teórica regla actual − Kadane: 9.67e+05 kWh.
