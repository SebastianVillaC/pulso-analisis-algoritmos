# Plataforma Pulso: consolidación, priorización y agendamiento del tamizaje de diabetes

**Informe técnico — Proyecto final de Análisis de Algoritmos (2026-2)**

| | |
|---|---|
| **Caso asignado** | Caso 2 — Plataforma Pulso (Secretaría de Salud departamental) |
| **Integrantes** | Sebastian Villa Castillo · Jhon Eduardo Zabala Garzon · Brayan Alexis Arango Orrego · David Morales Vargas |
| **Operaciones trabajadas** | Op. 3 — Programación de las jornadas de las unidades móviles (Laboratorio 4) · Op. 4 — Vigilancia de la calidad de los laboratorios |
| **Uso de IA** | Redacción apoyada por un asistente de IA, con autorización del docente. El equipo revisó el texto, las cifras y las fuentes |

---

## 1. Análisis del problema

### 1.1 Descripción del problema computacional

_Pendiente para la entrega del 23 de noviembre._

### 1.2 Entradas, salidas y restricciones

#### Operación 3 — Programación de las jornadas de las unidades móviles

| Elemento | Descripción |
|---|---|
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

**Cómo reduce el consumo energético.**
- Frente a la única forma de garantizar el óptimo sin PD, que es la búsqueda exhaustiva con Θ(n·2ⁿ), la PD pasa de un tiempo literalmente inalcanzable a microsegundos (sección 4.1).
- Frente a la regla actual también es más rápida, porque es Θ(n log n) frente a Θ(n²).
- Y permite automatizar un trabajo que hoy se hace a mano en hojas de cálculo.

### 2.3 Operación 4 — Estrategias

_Pendiente para la entrega del 23 de noviembre._

---

## 3. Implementación

_Pendiente._

---

## 4. Evaluación del desempeño

### 4.0 Método experimental (común a todas las operaciones)

_Pendiente._

### 4.1 Operación 3

#### Complejidad temporal y espacial

_Pendiente._

#### Verificación (las estrategias cumplen las restricciones del negocio)

_Pendiente._

#### Resultados

_Pendiente._

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

### 5.2 Operación 4 y comparación global

_Pendiente para la entrega del 23 de noviembre._

---

## 6. Implicaciones éticas, sociales y ambientales

### 6.1 Consumo energético

_Pendiente._

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

_Pendiente._
