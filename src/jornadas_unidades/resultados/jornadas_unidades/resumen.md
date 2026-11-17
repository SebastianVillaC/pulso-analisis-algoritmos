# Resumen de mediciones — operación 3

Semilla 2026, 5 repeticiones por tamaño (se reporta el promedio).

## Factor al duplicar n

| Solución | n → 2n | Factor tiempo | Factor operaciones | Factor esperado |
|---|---|---|---|---|
| Exhaustiva | 8 → 16 | 259.24 | 277.16 | 512.00 |
| Exhaustiva | 10 → 20 | 1115.01 | 1124.77 | 2048.00 |
| Exhaustiva | 12 → 24 | 5319.57 | 4639.50 | 8192.00 |
| Programación dinámica | 10 → 20 | 2.42 | 2.53 | 2.60 |
| Programación dinámica | 1000 → 2000 | 1.98 | 2.21 | 2.20 |
| Programación dinámica | 64000 → 128000 | 2.18 | 2.13 | 2.13 |
| Regla actual (llegada) | 10 → 20 | 3.77 | 4.20 | 4.00 |
| Regla actual (llegada) | 8000 → 16000 | 3.99 | 3.97 | 4.00 |
| Voraz (terminación temprana) | 64000 → 128000 | 2.54 | 2.00 | 2.13 |

## Pacientes atendidos

| n | PD: pacientes (jornadas) | Regla actual: pacientes (jornadas) | Voraz: pacientes (jornadas) | Mejora PD vs actual |
|---|---|---|---|---|
| 40 | 840.6 (15.8) | 616.4 (14.8) | 679.4 (16.4) | +36.4% |
| 80 | 1660.2 (31.9) | 1217.6 (30.2) | 1329.7 (33.1) | +36.4% |
| 120 | 2484.7 (47.6) | 1824.2 (45.0) | 1986.9 (49.1) | +36.2% |

## Extrapolación y energía

Volumen real: 9 subregiones × hasta 120 solicitudes por mes = 9 ejecuciones/mes, 108/año. Servidor de 380 W.

| Solución | Tiempo por subregión (n=120) | Tiempo por mes (×9) | ¿Cabe en 4 h? | Energía por mes (kWh) | Energía por año (kWh) |
|---|---|---|---|---|---|
| Programación dinámica | 53.9 µs | 484.8 µs | Sí | 5.117e-08 | 6.141e-07 |
| Regla actual (llegada) | 105.0 µs | 945.1 µs | Sí | 9.976e-08 | 1.197e-06 |
| Exhaustiva | 5.232e+22 años | 4.708e+23 años | No | 1.568e+27 | 1.882e+28 |

Constante ajustada exhaustiva: c = 1.035e-08 s por (n·2ⁿ), con T(24) = 4.168 s.
Exhaustiva con n = 40 (mes más liviano): 126.45 h.
Exhaustiva con n = 120: 5.232e+22 años = 3.791e+12 veces la edad del universo.
Diferencia anual regla actual − PD: 5.830e-07 kWh.
