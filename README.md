# Plataforma Pulso: consolidación, priorización y agendamiento del tamizaje de diabetes

**Informe técnico — Proyecto final de Análisis de Algoritmos (2026-2)**

| | |
| --- | --- |
| **Caso asignado** | Caso 2 — Plataforma Pulso (Secretaría de Salud departamental) |
| **Integrantes** | Sebastian Villa Castillo · Jhon Eduardo Zabala Garzon · Brayan Alexis Arango Orrego · David Morales Vargas |
| **Operaciones trabajadas** | Op. 3 — Programación de las jornadas de las unidades móviles (Laboratorio 4) · Op. 4 — Vigilancia de la calidad de los laboratorios |

**Resumen.**
- **Op. 3 (jornadas):** la Secretaría asigna hoy por orden de llegada. Proponemos programación dinámica de intervalos ponderados, que maximiza los pacientes de alto riesgo atendidos. En meses sintéticos atiende un **36 % más de pacientes** que la regla actual, en menos de un milisegundo por mes.

---

## 1. Análisis del problema

### 1.1 Descripción del problema computacional

_Pendiente para la entrega del 23 de noviembre._

### 1.2 Entradas, salidas y restricciones

#### Operación 3 — Programación de las jornadas de las unidades móviles

| Elemento | Descripción |
| --- | --- |
| **Entrada** | Solicitudes del mes de una subregión, en orden de llegada. Cada una es una tupla `(inicio, fin, pacientes)`: inicio y fin en minutos desde el inicio del mes, con `fin > inicio` y el desplazamiento incluido; `pacientes` es el número de pacientes de alto riesgo pendientes en el municipio (entero ≥ 0) |
| **Tamaño** | n = 40 a 120 solicitudes por subregión y mes; 9 subregiones (9 instancias independientes por mes) |
| **Salida** | El subconjunto de solicitudes aceptadas, ordenado por hora de inicio, que **maximiza el total de pacientes de alto riesgo atendidos** |
| **Restricciones** | La programación de una unidad nunca tiene dos jornadas que se crucen. El resultado es el máximo, no una aproximación. Las solicitudes originales no se modifican |

**Por qué maximizar pacientes y no jornadas.** Según el caso, con la regla actual *"cada mes quedan sin atender municipios con muchos pacientes de alto riesgo"*. El objetivo del programa es valorar a la mayor cantidad de personas en riesgo, no hacer muchas jornadas. Un municipio con 60 pacientes pendientes no vale lo mismo que uno con 3.

La sección 4.1 muestra además que optimizar pacientes **no cuesta más** que optimizar jornadas: ambas estrategias son Θ(n log n).

Quién debe tomar esta decisión se discute en la sección 6.2.

#### Operación 4 — Vigilancia de la calidad de los laboratorios

_Pendiente para la entrega del 23 de noviembre._

#### Operaciones 1 y 2 (solo para la línea base)

_Pendiente para la entrega del 23 de noviembre._

### 1.3 Operaciones críticas del proceso

_Pendiente para la entrega del 23 de noviembre._

### 1.4 Costo energético del proceso actual (línea base)

_Pendiente para la entrega del 23 de noviembre._

### 1.5 Supuestos

**Generales** (permitidos por el enunciado):
- Datos válidos.
- Todo cabe en memoria.
- Un solo hilo de ejecución.
- Sin interfaz ni base de datos.
- Datos sintéticos de tamaño creciente con semilla fija, y extrapolación al volumen real.

**Operación 3:**
1. Dos jornadas que **se tocan en un extremo** (una termina justo cuando la otra empieza) **no se cruzan**, porque la hora de fin ya incluye el desplazamiento. La regla vive en un único lugar, [`modelo.se_cruzan`](src/jornadas_unidades/modelo.py), y en el `<=` de la búsqueda binaria.
2. **Regla actual:** se recorren las solicitudes en el orden de la lista (orden de llegada) y se acepta cada una que no se cruce con ninguna ya aceptada. Nunca se revoca una aceptación.
3. Cada subregión se programa por separado, con una unidad por subregión.
4. Una solicitud con 0 pacientes es válida. Si hay varios óptimos con el mismo valor, cualquiera es correcto.
5. Datos sintéticos ([`datos.py`](src/jornadas_unidades/datos.py)):
   - Unas 4 solicitudes por día, la densidad del mes más cargado (120 en 30 días).
   - Inicio entre las 06:00 y las 16:00 y duración de 2 a 10 h, en pasos de 30 min.
   - De 1 a 80 pacientes por solicitud.

**Operación 4:** _Pendiente para la entrega del 23 de noviembre._

**Línea base:** _Pendiente para la entrega del 23 de noviembre._

---

## 2. Diseño de la solución

### 2.1 Estructuras de datos

_Pendiente para la entrega del 23 de noviembre._

### 2.2 Operación 3 — Estrategias

| Estrategia | Familia | Objetivo | Archivo |
|---|---|---|---|
| **Intervalos ponderados (recomendada)** | Programación dinámica | Máximo de pacientes | [`estrategia.py`](src/jornadas_unidades/estrategia.py) |
| Exhaustiva | Fuerza bruta (verificador exacto) | Máximo de pacientes | [`exhaustivo.py`](src/jornadas_unidades/exhaustivo.py) |
| Orden de llegada (actual) | Voraz ingenua | Ninguno explícito | [`regla_actual.py`](src/jornadas_unidades/regla_actual.py) |
| Terminación más temprana | Voraz | Máximo de **jornadas** | [`estrategia.py`](src/jornadas_unidades/estrategia.py) (`terminacion_temprana`) |

#### Por qué el problema admite programación dinámica

Se ordenan las solicitudes por hora de fin y se numeran 1..n. Para la última jornada j solo hay dos opciones:
- **No aceptarla.** Entonces la mejor programación es la mejor entre las jornadas 1..j−1.
- **Aceptarla.** Entonces se ganan sus v_j pacientes, pero solo se le pueden sumar jornadas que terminen antes de que j empiece. Como la lista está ordenada por fin, esas jornadas son exactamente las 1..p(j), y lo mejor que se puede sumar es la mejor programación de ese prefijo.

Hay **subestructura óptima**: en ambos casos, la solución óptima del problema contiene una solución óptima de un prefijo más pequeño. Si contuviera una programación peor de ese prefijo, se podría reemplazar por la óptima y mejorar el total, lo que es una contradicción.

Hay **subproblemas traslapados**: los mismos prefijos se consultan muchas veces.
- En el ejemplo de abajo, M[3] lo usan tanto la jornada 5 como la 6, y cada M[j−1] se consulta en el paso j.
- Una recursión sin tabla resolvería los mismos prefijos una y otra vez, con costo exponencial.
- Con la tabla, cada prefijo se resuelve **una vez**.

**¿Por qué no basta un voraz?** La propiedad de elección voraz ("aceptar primero la que termina antes") garantiza el máximo de **jornadas**, porque deja la unidad libre lo antes posible. Pero no garantiza el máximo de **pacientes**: una jornada larga con muchos pacientes puede valer más que tres cortas con pocos (contraejemplo en la sección 5.1). Una elección hecha sin mirar los pesos puede necesitar reconsiderarse, y eso es justo lo que la PD hace al comparar las dos opciones.

#### Recurrencia

```
M[0] = 0                                       (caso base: sin jornadas, 0 pacientes)
M[j] = max( M[j−1] ,  v_j + M[p(j)] )          para j = 1..n
```

| Término | Significado |
|---|---|
| `M[j]` | Máximo de pacientes atendibles usando solo las jornadas 1..j (ordenadas por fin) |
| `M[j−1]` | Opción (a): no aceptar la jornada j |
| `v_j` | Pacientes de alto riesgo de la jornada j |
| `p(j)` | Cuántas jornadas anteriores terminan a más tardar cuando j empieza (búsqueda binaria sobre los fines) |
| `v_j + M[p(j)]` | Opción (b): aceptar j y sumarle lo mejor de las compatibles con ella |

- **Orden de llenado:** de izquierda a derecha, j = 1..n. Es válido porque M[j] solo depende de M[j−1] y de M[p(j)], con p(j) < j.
- **Respuesta:** M[n].
- **Reconstrucción:** se recorre desde j = n hacia atrás.
  - Si v_j + M[p(j)] > M[j−1], la jornada j entró y se salta a p(j).
  - Si no, se pasa a j−1.

**Pseudocódigo:**

```
SELECCIONAR-JORNADAS(S)
1  O ← S ordenada por fin                      ▷ Θ(n log n)
2  F ← fines de O
3  para j ← 1..n: p[j] ← #{ i < j : F[i] ≤ O[j].inicio }   ▷ búsqueda binaria, Θ(log n)
4  M[0] ← 0
5  para j ← 1..n: M[j] ← max(M[j−1], O[j].v + M[p[j]])     ▷ Θ(n)
6  j ← n ; R ← ∅
7  mientras j > 0:
8      si O[j].v + M[p[j]] > M[j−1]: R ← R ∪ {O[j]} ; j ← p[j]
9      si no: j ← j − 1
10 devolver R ordenada por inicio
```

#### Ejemplo resuelto a mano (6 solicitudes, horas de un mismo día)

| Llegada | Municipio | Horario | Pacientes |
|---|---|---|---|
| 1 | M1 | 07–12 | 4 |
| 2 | M2 | 06–09 | 10 |
| 3 | M3 | 09–13 | 8 |
| 4 | M4 | 12–16 | 5 |
| 5 | M5 | 13–17 | 12 |
| 6 | M6 | 15–18 | 3 |

**Paso 1, ordenar por fin:** M2 (fin 9), M1 (12), M3 (13), M4 (16), M5 (17), M6 (18).

**Pasos 2 y 3, calcular p(j) y llenar M:**

| j | Jornada | Inicio | Fines anteriores ≤ inicio | p(j) | (a) M[j−1] | (b) v_j + M[p(j)] | M[j] | Gana |
|---|---|---|---|---|---|---|---|---|
| 0 | — | — | — | — | — | — | 0 | caso base |
| 1 | M2 (6–9) | 6 | ninguno | 0 | 0 | 10 + 0 = 10 | **10** | aceptar |
| 2 | M1 (7–12) | 7 | ninguno (9 > 7) | 0 | 10 | 4 + 0 = 4 | **10** | no aceptar |
| 3 | M3 (9–13) | 9 | M2 (9) | 1 | 10 | 8 + 10 = 18 | **18** | aceptar |
| 4 | M4 (12–16) | 12 | M2 (9), M1 (12) | 2 | 18 | 5 + 10 = 15 | **18** | no aceptar |
| 5 | M5 (13–17) | 13 | M2, M1, M3 (13) | 3 | 18 | 12 + 18 = 30 | **30** | aceptar |
| 6 | M6 (15–18) | 15 | M2, M1, M3 (M4 = 16 > 15) | 3 | 30 | 3 + 18 = 21 | **30** | no aceptar |

**Paso 4, reconstruir:**
- j = 6: 21 no supera 30, así que M6 no entra y se pasa a j = 5.
- j = 5: 30 supera 18, así que **M5 entra** y se salta a p(5) = 3.
- j = 3: 18 supera 10, así que **M3 entra** y se salta a p(3) = 1.
- j = 1: 10 supera 0, así que **M2 entra** y se salta a 0.

**Resultado:** M2 (06–09) + M3 (09–13) + M5 (13–17) = **30 pacientes**.
- Las tres jornadas solo se tocan en los extremos, así que no se cruzan.
- [`pruebas.py`](src/jornadas_unidades/pruebas.py) verifica exactamente este resultado.

**Cómo reduce el consumo energético.**
- Frente a la única forma de garantizar el óptimo sin PD, que es la búsqueda exhaustiva con Θ(n·2ⁿ), la PD pasa de un tiempo literalmente inalcanzable a microsegundos (sección 4.1).
- Frente a la regla actual también es más rápida, porque es Θ(n log n) frente a Θ(n²).
- Y permite automatizar un trabajo que hoy se hace a mano en hojas de cálculo.

### 2.3 Operación 4 — Estrategias

_Pendiente para la entrega del 23 de noviembre._

---

## 3. Implementación

**Tecnologías.**
- Python 3.10 o superior.
- Los algoritmos usan solo la biblioteca estándar y están escritos a mano. Las operaciones 3 y 4 no usan bibliotecas de optimización.
- `matplotlib` se usa solo para las gráficas.
- El código cumple PEP 8, revisado con `pycodestyle`, y tiene type hints y docstrings estilo Google en cada función.

**Estructura del repositorio.**

```
src/
├── jornadas_unidades/        # Op. 3 (Laboratorio 4)
│   ├── modelo.py             # Jornada, se_cruzan, contador
│   ├── estrategia.py         # PD de intervalos ponderados, hay_cruce, voraz de contraste
│   ├── exhaustivo.py         # 2ⁿ subconjuntos
│   ├── regla_actual.py       # orden de llegada
│   ├── datos.py · pruebas.py · medicion.py
graficas/<operacion>/*.png    resultados/<operacion>/{mediciones.csv, resumen.md}
```

**Código de la operación 3:** [`estrategia.py`](src/jornadas_unidades/estrategia.py) · [`exhaustivo.py`](src/jornadas_unidades/exhaustivo.py) · [`regla_actual.py`](src/jornadas_unidades/regla_actual.py) · [`pruebas.py`](src/jornadas_unidades/pruebas.py) · [`modelo.py`](src/jornadas_unidades/modelo.py)

**Decisiones de implementación relevantes.**
1. **La regla de cruce vive en un solo lugar.**
   - `se_cruzan(a, b) = a.inicio < b.fin and b.inicio < a.fin` (tocarse no es cruce), junto con el `<=` de `contar_compatibles`.
   - La estrategia, la exhaustiva, la regla actual y `hay_cruce` usan la misma convención.
   - Comprobamos que si se cambia `<=` por `<` en la búsqueda binaria, las pruebas fallan.
2. **La búsqueda binaria está escrita a mano** (`contar_compatibles`), con el rango limitado a las jornadas anteriores a j.
3. **La salida se devuelve ordenada por inicio**, como exige el esqueleto, aunque la PD trabaja ordenada por fin.
4. **La entrada nunca se modifica.** Se usa `sorted` (copia), no `.sort()`, y las tuplas son inmutables. Las pruebas comparan la entrada con una copia después de cada llamada.
5. **El conteo de operaciones es opcional.** Cada función recibe `contador=None`. El cronómetro corre sin contador, y el conteo se hace en una ejecución aparte, para que contar no infle el tiempo.
6. **Exhaustiva de la op. 3.** Ordena por inicio y abandona un subconjunto en cuanto encuentra un cruce. Así se mantiene exacta y es más rápida en promedio; en el peor caso sigue siendo Θ(n·2ⁿ).

---

## 4. Evaluación del desempeño

### 4.0 Método experimental (común a todas las operaciones)

- **Datos:** sintéticos, generados con `random.Random(semilla)`, con semilla 2026 + n. En cada tamaño, **todas las soluciones resuelven la misma instancia**.
- **Tiempo:** `time.perf_counter()` alrededor de la llamada, sin incluir la generación de datos. Se promedian **5 repeticiones**.
- **Operaciones elementales:** se cuentan con un contador propio, en una ejecución aparte.
  - Op. 3, PD: comparaciones de la búsqueda binaria y celdas de M.
  - Op. 3, exhaustiva: subconjuntos y comparaciones.
  - Op. 3, regla actual: comparaciones contra las jornadas aceptadas.
- **Verificación dentro del experimento:** en cada tamaño, todas las soluciones que corren deben coincidir en el valor óptimo (`assert`).
- **Gráficas:** escala log-log, porque en ella una curva de la forma n^k se ve como una recta de pendiente k y una exponencial se ve casi vertical.
- Los tiempos absolutos dependen del equipo en que se mide (un portátil con macOS y Python 3.14). La forma de las curvas y los factores al duplicar n no dependen de él.

### 4.1 Operación 3

#### Complejidad temporal y espacial

| Solución | Tiempo | Espacio | Justificación |
|---|---|---|---|
| **PD intervalos ponderados** | **Θ(n log n)** | Θ(n) | Ordenar Θ(n log n), más n búsquedas binarias Θ(log n), más llenar M y reconstruir Θ(n). Guarda la lista ordenada, p y M |
| Exhaustiva | Θ(n·2ⁿ) | Θ(n) | 2ⁿ subconjuntos, cada uno revisado en hasta n pasos. Solo guarda el mejor |
| Regla actual (llegada) | Θ(n·a) ⊆ Θ(n²) | Θ(n) | Cada solicitud se compara con las *a* ya aceptadas, y *a* crece proporcionalmente con n |
| Voraz por jornadas | Θ(n log n) | Θ(n) | Ordenar más un recorrido |

**Contraste.**
- La PD y el voraz tienen la misma complejidad: optimizar **pacientes** en lugar de **jornadas** no cuesta más.
- La exhaustiva es exponencial: cada solicitud adicional duplica el trabajo.
- La regla actual, además de dar peores resultados, es asintóticamente más lenta que la PD.

#### Verificación (las estrategias cumplen las restricciones del negocio)

[`pruebas.py`](src/jornadas_unidades/pruebas.py) se ejecuta sin errores. Comprueba:
- **Casos límite:**
  - entrada vacía;
  - una sola solicitud;
  - ninguna se cruza (en cadena, tocándose: se aceptan todas);
  - todas se cruzan (queda la de más pacientes);
  - jornadas que se tocan (no es cruce) frente a jornadas solapadas un minuto (sí es cruce);
  - pacientes en cero.
- El **ejemplo a mano**: M2 + M3 + M5 = 30.
- El **contraejemplo de la regla actual**: 9 frente a 30.
- El **contraejemplo del voraz**: 9 frente a 50. Con pesos iguales, el voraz sí es óptimo.
- **200 instancias aleatorias** (semilla 2026, hasta 12 solicitudes). En todas:
  - la PD y la exhaustiva obtienen el mismo número de pacientes;
  - **ninguna programación tiene dos jornadas que se crucen**;
  - lo reconstruido suma el óptimo;
  - la entrada no se modifica;
  - la regla actual nunca supera a la PD.

En la medición, la PD y la exhaustiva coinciden en todos los tamaños de 4 a 24.

#### Resultados

Medición: [`datos.py`](src/jornadas_unidades/datos.py) y [`medicion.py`](src/jornadas_unidades/medicion.py). Datos: [`mediciones.csv`](resultados/jornadas_unidades/mediciones.csv) y [`resumen.md`](resultados/jornadas_unidades/resumen.md).
- Exhaustiva: n = 4, 6, …, 24.
- PD y voraz: además 40, 120, 250, 500 y de 1.000 a 128.000, duplicando.
- Regla actual: hasta 16.000.

![Op. 3: tiempo frente a n](graficas/jornadas_unidades/tiempo_vs_n.png)

![Op. 3: operaciones frente a n](graficas/jornadas_unidades/operaciones_vs_n.png)

| n | PD | Exhaustiva | Regla actual | Voraz |
|---|---|---|---|---|
| 10 | 3,3 µs · 32 ops | 183 µs · 3.232 ops | 1,0 µs · 15 ops | 0,9 µs · 10 ops |
| 20 | 7,9 µs · 81 ops | 0,204 s · 3.635.272 ops | 3,8 µs · 63 ops | 2,5 µs · 20 ops |
| 24 | 9,4 µs · 102 ops | **4,17 s** · 65.147.904 ops | 8,3 µs · 91 ops | 4,1 µs · 24 ops |
| 120 (real) | **54 µs** · 758 ops | — | 105 µs · 2.557 ops | 12,5 µs · 120 ops |
| 16.000 | 14,1 ms | — | 1,50 s | 3,3 ms |
| 128.000 | 143 ms | — | — | 38 ms |

**Cuánto mejora el resultado.** Se promediaron 200 meses sintéticos por tamaño ([`pacientes.csv`](resultados/jornadas_unidades/pacientes.csv)):

![Op. 3: pacientes atendidos por estrategia](graficas/jornadas_unidades/pacientes_por_estrategia.png)

| n (solicitudes/mes) | PD: pacientes (jornadas) | Regla actual | Voraz por jornadas | Mejora PD frente a la actual |
|---|---|---|---|---|
| 40 | 840,6 (15,8) | 616,4 (14,8) | 679,4 (16,4) | **+36,4 %** |
| 80 | 1.660,2 (31,9) | 1.217,6 (30,2) | 1.329,7 (33,1) | **+36,4 %** |
| 120 | 2.484,7 (47,6) | 1.824,2 (45,0) | 1.986,9 (49,1) | **+36,2 %** |

- El voraz hace **más jornadas** que la PD (49,1 frente a 47,6), pero atiende **500 pacientes menos**. Es la evidencia empírica de que los dos criterios son problemas distintos.
- En el mes más cargado, la PD atiende en promedio **≈ 660 pacientes de alto riesgo más por subregión**, unos 5.900 más al mes en las 9 subregiones. Es una estimación con datos sintéticos.

#### Lo medido frente a lo esperado

| Solución | n → 2n | Factor tiempo | Factor operaciones | Esperado por la complejidad |
|---|---|---|---|---|
| Exhaustiva | 8 → 16 | 259 | 277 | (16·2¹⁶)/(8·2⁸) = 512 |
| Exhaustiva | 10 → 20 | 1.115 | 1.125 | 2.048 |
| Exhaustiva | 12 → 24 | 5.320 | 4.640 | 8.192 |
| PD | 10 → 20 | 2,42 | 2,53 | (20 log 20)/(10 log 10) = 2,60 |
| PD | 1.000 → 2.000 | 1,98 | 2,21 | 2,20 |
| PD | 64.000 → 128.000 | 2,18 | 2,13 | 2,13 |
| Regla actual | 8.000 → 16.000 | 3,99 | 3,97 | 4,00 |
| Voraz | 64.000 → 128.000 | 2,54 | 2,00 | 2,13 |

- **PD:** al duplicar n, las operaciones crecen ×2,13 a ×2,21 y el tiempo ×2,0 a ×2,4, lo esperado para n log n (≈ ×2,1 a ×2,2). **Coincide.** Las pequeñas diferencias en tiempo son ruido del sistema y efectos de caché y del intérprete cuando se miden micro y milisegundos; el conteo de operaciones, que no tiene ruido, coincide casi exacto.
- **Regla actual:** ×3,99 en tiempo y ×3,97 en operaciones, con ×4 esperado. **Comportamiento cuadrático confirmado.** No solo da peores resultados, también cuesta más que la PD: a n = 16.000 es 100 veces más lenta.
- **Exhaustiva:** el factor exponencial **sí aparece**. Al sumar 10 solicitudes el trabajo se multiplica por más de 1.000 (≈ 2¹⁰), y al sumar 12, por más de 4.600. La curva es casi vertical en la gráfica.
  - Sale **por debajo** del peor caso n·2ⁿ porque la implementación abandona cada subconjunto en el primer cruce.
  - Con solicitudes que se cruzan a menudo, en promedio revisa pocos elementos por subconjunto. El factor n del peor caso solo aparecería si casi ningún subconjunto tuviera cruces.
  - Por eso lo medido se parece más a c·2ⁿ multiplicado por un factor que crece lentamente. Usar n·2ⁿ para extrapolar es, por lo tanto, una cota conservadora en la dirección correcta: hace más largo el tiempo de la exhaustiva y no favorece a la PD.

#### Escala real, ventana operativa y energía

- **Volumen real:** n = 120 solicitudes por subregión (el peor mes), 9 subregiones al mes, **108 ejecuciones al año**.
- **Ventana:** el caso no fija una para esta operación, porque hoy se hace a mano. Tomamos como referencia la **ventana nocturna de 4 h (01:00–05:00)** del mismo servidor: si la programación mensual cabe ahí, puede correr la misma noche de cierre de mes sin desplazar a las ops. 1 y 2.
- **Extrapolación:** n = 120 está dentro del rango medido para la PD y la regla actual, así que no hace falta extrapolar esas dos.
  - Para la exhaustiva se justificó la forma de la curva antes de extrapolar, en vez de usar una regla de tres: T(n) = c·n·2ⁿ.
  - Con T(24) = 4,17 s se obtiene c = 4,17 / (24·2²⁴) ≈ 1,04 × 10⁻⁸ s.

| Solución | Por subregión (n = 120) | Por mes (× 9) | ¿Cabe en 4 h? | kWh/mes | kWh/año |
|---|---|---|---|---|---|
| **PD** | 54 µs | 0,48 ms | **Sí** | 5,1 × 10⁻⁸ | 6,1 × 10⁻⁷ |
| Regla actual | 105 µs | 0,95 ms | Sí | 1,0 × 10⁻⁷ | 1,2 × 10⁻⁶ |
| Exhaustiva | **5,2 × 10²² años** | — | **Nunca termina** | — | — |

- La exhaustiva **no terminaría nunca en la práctica**.
  - Con n = 40, el mes más liviano, ya tarda ≈ 126 h, así que ni ese mes cabe en la ventana.
  - Con n = 120 tardaría unas 3,8 × 10¹² veces la edad del universo.
  - Su consumo teórico (≈ 1,9 × 10²⁸ kWh al año) carece de sentido físico: simplemente no es una opción. Por eso existe hoy una regla simplificada.
- **Diferencia de energía entre la regla actual y la PD:** ≈ 0,38 kW × (0,95 − 0,48) ms × 12 meses ≈ **6 × 10⁻⁷ kWh al año**, despreciable. Son estimaciones; el cálculo es kWh = kW × h.
- En esta operación el beneficio **no es energético sino de resultado**: +36 % de pacientes de alto riesgo valorados con el mismo cómputo. El ahorro de recursos real está en dos lugares:
  1. Hace viable un óptimo exacto que con fuerza bruta sería imposible.
  2. Reemplaza el trabajo manual con hojas de cálculo.

### 4.2 Operación 4

_Pendiente para la entrega del 23 de noviembre._

### 4.3 Línea base (ops. 1 y 2) y alternativa de referencia

_Pendiente para la entrega del 23 de noviembre._

---

## 5. Análisis comparativo

### 5.1 Operación 3

**Contraejemplo de la regla actual (orden de llegada).** Con las 6 solicitudes del ejemplo a mano:

| Paso | Solicitud | Decisión de la regla actual |
|---|---|---|
| 1 | M1 (07–12, 4) | Aceptada (no hay ninguna antes) |
| 2 | M2 (06–09, 10) | Rechazada: se cruza con M1 |
| 3 | M3 (09–13, 8) | Rechazada: se cruza con M1 |
| 4 | M4 (12–16, 5) | Aceptada: solo toca a M1 |
| 5 | M5 (13–17, 12) | Rechazada: se cruza con M4 |
| 6 | M6 (15–18, 3) | Rechazada: se cruza con M4 |

| | Jornadas | Pacientes |
|---|---|---|
| Regla actual | M1, M4 | **9** |
| Óptimo (PD) | M2, M3, M5 | **30** |
| **Diferencia** | | **21 pacientes de alto riesgo sin valorar (−70 %)** |

La regla falla porque la primera solicitud que llega bloquea a las que se cruzan con ella, sin mirar cuántos pacientes tienen ni cuánto tiempo ocupa. El orden de llegada no tiene relación con la necesidad.

**Condición contraria: cuándo bastaría un voraz.** Si todas las solicitudes tuvieran **el mismo número de pacientes**, o si la Secretaría decidiera maximizar el **número de jornadas**, el voraz de terminación más temprana sería óptimo, porque la propiedad de elección voraz se cumple cuando todas las jornadas valen lo mismo. Sería además más simple.

Con pesos distintos falla. Ejemplo: X (06–12, 50), Y (06–08, 3), Z (08–10, 3) y W (10–12, 3).
- El voraz elige Y, Z y W: **3 jornadas y 9 pacientes**.
- La PD elige X: **1 jornada y 50 pacientes**.

Ambos casos se verifican en las pruebas.

**Ventajas y limitaciones.**

| Estrategia | Ventajas | Limitaciones |
|---|---|---|
| **PD intervalos ponderados** | Óptima en pacientes; Θ(n log n); determinista y auditable; los pesos pueden ser cualquier prioridad (no solo pacientes) | Hay que decidir y declarar el criterio; puede dejar fuera repetidamente a municipios pequeños |
| Exhaustiva | Exacta, sin supuestos; sirve de verificador | Exponencial: inviable con más de ~30 solicitudes |
| Regla actual | Simple, "justa" en el sentido de quién pide primero | 36 % menos pacientes; Θ(n²); premia la rapidez para pedir, no la necesidad |
| Voraz por jornadas | Óptima en número de jornadas; la más rápida | Ignora los pacientes: −20 % frente a la PD |

**Recomendación para la op. 3.** Adoptar la **programación dinámica de intervalos ponderados**.
- **Ganancia:** +36 % de pacientes de alto riesgo valorados con las mismas unidades móviles, con un resultado exacto y reproducible en menos de un milisegundo por mes.
- **Riesgos y límites que la Secretaría debe conocer:**
  - Optimizar pacientes puede dejar siempre fuera a municipios pequeños. La sección 6.2 propone una mitigación.
  - El resultado depende de que "pacientes pendientes" esté bien reportado: un municipio que exagere su cifra desplaza a otros.
  - El modelo supone una unidad por subregión. Si una subregión tuviera dos o más unidades, el problema pasaría a ser de programación en varias máquinas y la recurrencia tendría que cambiar.
  - Si el volumen creciera, el costo sigue siendo Θ(n log n): incluso 100 veces más solicitudes se resolverían en menos de un segundo.

### 5.2 Operación 4 y comparación global

_Pendiente para la entrega del 23 de noviembre._

---

## 6. Implicaciones éticas, sociales y ambientales

### 6.1 Consumo energético

**Operación 3** (ver la sección 4.1): con 108 ejecuciones al año en el servidor de 0,38 kW, la regla actual consume ≈ 1,2 × 10⁻⁶ kWh/año y la PD ≈ 6,1 × 10⁻⁷ kWh/año. La diferencia proyectada a un año (≈ 6 × 10⁻⁷ kWh) es despreciable: en esta operación el beneficio no es energético sino de resultado (+36 % de pacientes de alto riesgo atendidos con el mismo cómputo). La alternativa exacta por fuerza bruta no terminaría nunca.

_Consumo del proceso completo: pendiente para la entrega del 23 de noviembre._

### 6.2 Preguntas de impacto del caso

_Pendiente para la entrega del 23 de noviembre._

### 6.3 Consecuencias sobre las personas: errores y retrasos

_Pendiente para la entrega del 23 de noviembre._

### 6.4 Marco normativo y buenas prácticas

_Pendiente para la entrega del 23 de noviembre._

### 6.5 Sostenibilidad de la decisión: escenario de crecimiento

_Pendiente para la entrega del 23 de noviembre._

---

## 7. Conclusiones

_Pendiente para la entrega del 23 de noviembre._

---

## 8. Reproducción

Requisitos: Python 3.10 o superior.

```bash
# 1. Crear y activar el entorno virtual
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Pruebas (cada una imprime "OK: ...")
python src/jornadas_unidades/pruebas.py

# 3. Datos sintéticos, mediciones y gráficas
python src/jornadas_unidades/medicion.py          # op. 3, ~1 min
```

- Cada `medicion.py` genera sus datos sintéticos con semilla fija (2026 + n), mediante el `datos.py` de su carpeta.
- Escribe sus gráficas en `graficas/<operacion>/` y sus tablas en `resultados/<operacion>/` (`mediciones.csv` y `resumen.md`).
- Los tiempos absolutos dependen del equipo; la forma de las curvas, los factores al duplicar n y los conteos de operaciones no.
