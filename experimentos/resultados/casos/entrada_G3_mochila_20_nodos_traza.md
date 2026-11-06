# Traza del caso `entrada_G3_mochila_20_nodos`

## 0. Entrada

| parámetro | valor |
|---|---|
| etapas n | 20 |
| B (aceleración) | 72 |
| B conjunto (aceleración + auditoría) | 100 |
| categorías de riesgo r | 12 |
| interacciones N (variaciones de auditoría) | 35 |
| aristas del flujo m | 19 |
| flujo | cadena (serie) |
| Σ t_i (sin acelerar) | 501 |
| λ usado en la heurística | 10 |
| repeticiones medidas | 7 |

## 1. Resumen de resultados y tiempos

| algoritmo | tamaño | tiempo (mediana) | mín | máx | valor |
|---|---|---|---|---|---|
| mochila_dp | n=20, B=72 | 0.137 ms | 0.134 ms | 0.161 ms | 446 |
| dag_heuristica | n=20, m=19 | 0.082 ms | 0.078 ms | 0.119 ms | 446 |
| cobertura_voraz_ponderada | n=20, r=12 | 0.040 ms | 0.036 ms | 0.059 ms | 25 |
| cobertura_exacta_dp | n=20, r=12 | 5.240 ms | 5.207 ms | 6.710 ms | 24 |
| combinado_oblig_voraz | n=20, B=100 | 0.193 ms | 0.190 ms | 0.231 ms | 444 |
| combinado_oblig_exacta_dp | n=20, B=100 | 5.959 ms | 5.377 ms | 6.455 ms | 443 |
| combinado_heuristica_lambda | n=20, B=100 | 0.387 ms | 0.380 ms | 0.429 ms | 447 |

`valor` = duración (mochila, dag), Σa_j (cobertura) u objetivo (combinado).

## 2. Parte 1 — Mochila 0/1 (aceleración)

### DP exacta con B = 72

- Estados de la DP: (n+1)·(B+1) = 21·73 = **1533** celdas (1460 transiciones calculadas, O(n·B)).
- Celdas donde acelerar la etapa i mejora a no acelerarla: 386.
- Reducción máxima DP[n][B] = **55**.

Recorrido hacia atrás desde (i=n, b=B). Si DP[i][b] = DP[i-1][b] la etapa no hace falta; si no, se aceleró y el presupuesto baja en c_i:

| i | etapa | t_i | c_i | d_i | b | DP[i][b] | sin i = DP[i-1][b] | con i = DP[i-1][b-c_i]+d_i | decisión | b siguiente |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | E20 | 24 | 10 | 7 | 72 | 55 | 55 | 54 | no | 72 |
| 19 | E19 | 32 | 15 | 11 | 72 | 55 | 55 | 54 | no | 72 |
| 18 | E18 | 26 | 12 | 9 | 72 | 55 | 55 | 55 | no | 72 |
| 17 | E17 | 21 | 8 | 6 | 72 | 55 | 55 | 54 | no | 72 |
| 16 | E16 | 34 | 16 | 12 | 72 | 55 | 55 | 55 | no | 72 |
| 15 | E15 | 28 | 11 | 8 | 72 | 55 | 55 | 54 | no | 72 |
| 14 | E14 | 17 | 6 | 4 | 72 | 55 | 55 | 54 | no | 72 |
| 13 | E13 | 29 | 14 | 10 | 72 | 55 | 55 | 54 | no | 72 |
| 12 | E12 | 23 | 9 | 7 | 72 | 55 | 54 | 55 | ACELERA | 63 |
| 11 | E11 | 31 | 15 | 11 | 63 | 48 | 48 | 47 | no | 63 |
| 10 | E10 | 25 | 12 | 9 | 63 | 48 | 48 | 48 | no | 63 |
| 9 | E09 | 19 | 7 | 5 | 63 | 48 | 48 | 47 | no | 63 |
| 8 | E08 | 35 | 17 | 13 | 63 | 48 | 47 | 48 | ACELERA | 46 |
| 7 | E07 | 20 | 10 | 7 | 46 | 35 | 35 | 34 | no | 46 |
| 6 | E06 | 27 | 13 | 10 | 46 | 35 | 32 | 35 | ACELERA | 33 |
| 5 | E05 | 22 | 9 | 6 | 33 | 25 | 25 | 24 | no | 33 |
| 4 | E04 | 30 | 16 | 12 | 33 | 25 | 18 | 25 | ACELERA | 17 |
| 3 | E03 | 16 | 5 | 4 | 17 | 13 | 9 | 13 | ACELERA | 12 |
| 2 | E02 | 24 | 12 | 9 | 12 | 9 | 5 | 9 | ACELERA | 0 |
| 1 | E01 | 18 | 7 | 5 | 0 | 0 | 0 | — | no | 0 |

- Etapas aceleradas: **E02, E03, E04, E06, E08, E12** (6 de 20).
- Costo de aceleración: **72** de B = 72 (sobran 0).
- Duración: Σt = 501 → Σt − Σd = 501 − 55 = **446**.

| etapa | t_i | c_i | d_i | t_i − d_i |
|---|---|---|---|---|
| E02 | 24 | 12 | 9 | 15 |
| E03 | 16 | 5 | 4 | 12 |
| E04 | 30 | 16 | 12 | 18 |
| E06 | 27 | 13 | 10 | 17 |
| E08 | 35 | 17 | 13 | 22 |
| E12 | 23 | 9 | 7 | 16 |
| **Total** | 155 | 72 | 55 | — |

## 3. Parte 2 — Cobertura de auditoría (interacciones = variaciones)

### Voraz ponderado (A1): menor a_j / nuevas

| paso | interacción elegida | a_j | categorías nuevas | a_j / nuevas | costo acumulado |
|---|---|---|---|---|---|
| 1 | E01-parcial | 3 | R01, R02 | 3/2 = 1.50 | 3 |
| 2 | E12-completa | 7 | R03, R07, R09, R12 | 7/4 = 1.75 | 10 |
| 3 | E13-completa | 6 | R05, R06, R11 | 6/3 = 2.00 | 16 |
| 4 | E11-completa | 6 | R04, R10 | 6/2 = 3.00 | 22 |
| 5 | E18-parcial | 3 | R08 | 3/1 = 3.00 | 25 |

- Interacciones elegidas (5): **E01-parcial, E12-completa, E13-completa, E11-completa, E18-parcial**.
- Costo de auditoría Σa_j = **25**.

| riesgo | categoría | importancia w_k | cubierto por |
|---|---|---|---|
| R01 | sesgo | 4 | E01-parcial, E11-completa, E18-parcial |
| R02 | privacidad | 5 | E01-parcial |
| R03 | formato | 2 | E12-completa |
| R04 | seguridad | 5 | E11-completa |
| R05 | trazabilidad | 3 | E13-completa |
| R06 | equidad | 4 | E13-completa |
| R07 | coherencia | 2 | E12-completa |
| R08 | robustez | 3 | E18-parcial |
| R09 | disponibilidad | 3 | E12-completa |
| R10 | cumplimiento | 5 | E11-completa |
| R11 | integridad | 4 | E13-completa |
| R12 | transparencia | 2 | E12-completa |

Cota teórica (Chvátal): costo(voraz) ≤ H_d · óptimo con d = 4, H_4 = 2.083.

### Exacto por DP sobre máscaras de categorías

- Interacciones elegidas (4): **E07-completa, E17-completa, E18-completa, E19-parcial**.
- Costo de auditoría Σa_j = **24**.

| riesgo | categoría | importancia w_k | cubierto por |
|---|---|---|---|
| R01 | sesgo | 4 | E07-completa, E18-completa |
| R02 | privacidad | 5 | E17-completa |
| R03 | formato | 2 | E19-parcial |
| R04 | seguridad | 5 | E19-parcial |
| R05 | trazabilidad | 3 | E07-completa |
| R06 | equidad | 4 | E17-completa |
| R07 | coherencia | 2 | E17-completa |
| R08 | robustez | 3 | E18-completa |
| R09 | disponibilidad | 3 | E07-completa |
| R10 | cumplimiento | 5 | E17-completa |
| R11 | integridad | 4 | E18-completa |
| R12 | transparencia | 2 | E18-completa |

Razón voraz / óptimo = 25/24 = **1.042**.

## 4. Variante C — flujo como DAG (heurística)

- Ruta crítica inicial: E01 → E02 → E03 → E04 → E05 → E06 → E07 → E08 → E09 → E10 → E11 → E12 → E13 → E14 → E15 → E16 → E17 → E18 → E19 → E20 (duración 501).

| paso | etapa acelerada | ruta crítica tras acelerar |
|---|---|---|
| 1 | E03 | 497 |
| 2 | E12 | 490 |
| 3 | E06 | 480 |
| 4 | E08 | 467 |
| 5 | E02 | 458 |
| 6 | E04 | 446 |

- Etapas aceleradas: **E02, E03, E04, E06, E08, E12**, costo 72 de B = 72.
- Duración final: **446**.
- El flujo es una cadena, así que su duración óptima es la de la Mochila (446). La heurística voraz obtuvo 446 (coincide).

## 5. Variante B — presupuesto conjunto

### Cobertura obligatoria (λ grande): cobertura de costo mínimo + Mochila con lo que sobra

- Etapas aceleradas: **E03, E04, E06, E08, E12, E16** (costo de aceleración 76).
- Interacciones auditadas: **E07-completa, E17-completa, E18-completa, E19-parcial** (costo de auditoría 24).
- Costo conjunto: 76 + 24 = **100** de B = 100 (sobran 0).
- Categorías cubiertas: 12 de 12; sin cubrir: ninguna.
- Duración 443 + penalización 0 = objetivo **443**.

Mochila con el presupuesto restante:

### DP con B' = 100 − 24 = 76

- Estados de la DP: (n+1)·(B+1) = 21·77 = **1617** celdas (1540 transiciones calculadas, O(n·B)).
- Celdas donde acelerar la etapa i mejora a no acelerarla: 422.
- Reducción máxima DP[n][B] = **58**.

Recorrido hacia atrás desde (i=n, b=B). Si DP[i][b] = DP[i-1][b] la etapa no hace falta; si no, se aceleró y el presupuesto baja en c_i:

| i | etapa | t_i | c_i | d_i | b | DP[i][b] | sin i = DP[i-1][b] | con i = DP[i-1][b-c_i]+d_i | decisión | b siguiente |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | E20 | 24 | 10 | 7 | 76 | 58 | 58 | 57 | no | 76 |
| 19 | E19 | 32 | 15 | 11 | 76 | 58 | 58 | 57 | no | 76 |
| 18 | E18 | 26 | 12 | 9 | 76 | 58 | 58 | 58 | no | 76 |
| 17 | E17 | 21 | 8 | 6 | 76 | 58 | 58 | 58 | no | 76 |
| 16 | E16 | 34 | 16 | 12 | 76 | 58 | 57 | 58 | ACELERA | 60 |
| 15 | E15 | 28 | 11 | 8 | 60 | 46 | 46 | 45 | no | 60 |
| 14 | E14 | 17 | 6 | 4 | 60 | 46 | 46 | 45 | no | 60 |
| 13 | E13 | 29 | 14 | 10 | 60 | 46 | 46 | 45 | no | 60 |
| 12 | E12 | 23 | 9 | 7 | 60 | 46 | 45 | 46 | ACELERA | 51 |
| 11 | E11 | 31 | 15 | 11 | 51 | 39 | 39 | 38 | no | 51 |
| 10 | E10 | 25 | 12 | 9 | 51 | 39 | 39 | 38 | no | 51 |
| 9 | E09 | 19 | 7 | 5 | 51 | 39 | 39 | 38 | no | 51 |
| 8 | E08 | 35 | 17 | 13 | 51 | 39 | 38 | 39 | ACELERA | 34 |
| 7 | E07 | 20 | 10 | 7 | 34 | 26 | 26 | 25 | no | 34 |
| 6 | E06 | 27 | 13 | 10 | 34 | 26 | 25 | 26 | ACELERA | 21 |
| 5 | E05 | 22 | 9 | 6 | 21 | 16 | 16 | 15 | no | 21 |
| 4 | E04 | 30 | 16 | 12 | 21 | 16 | 14 | 16 | ACELERA | 5 |
| 3 | E03 | 16 | 5 | 4 | 5 | 4 | 0 | 4 | ACELERA | 0 |
| 2 | E02 | 24 | 12 | 9 | 0 | 0 | 0 | — | no | 0 |
| 1 | E01 | 18 | 7 | 5 | 0 | 0 | 0 | — | no | 0 |

- Etapas aceleradas: **E03, E04, E06, E08, E12, E16** (6 de 20).
- Costo de aceleración: **76** de B = 76 (sobran 0).
- Duración: Σt = 501 → Σt − Σd = 501 − 58 = **443**.

| etapa | t_i | c_i | d_i | t_i − d_i |
|---|---|---|---|---|
| E03 | 16 | 5 | 4 | 12 |
| E04 | 30 | 16 | 12 | 18 |
| E06 | 27 | 13 | 10 | 17 |
| E08 | 35 | 17 | 13 | 22 |
| E12 | 23 | 9 | 7 | 16 |
| E16 | 34 | 16 | 12 | 22 |
| **Total** | 165 | 76 | 58 | — |

### Cobertura obligatoria con voraz ponderado (heurística)

- Etapas aceleradas: **E02, E03, E04, E06, E08, E10** (costo de aceleración 75).
- Interacciones auditadas: **E01-parcial, E11-completa, E12-completa, E13-completa, E18-parcial** (costo de auditoría 25).
- Costo conjunto: 75 + 25 = **100** de B = 100 (sobran 0).
- Categorías cubiertas: 12 de 12; sin cubrir: ninguna.
- Duración 444 + penalización 0 = objetivo **444**.

### Heurística para λ general (λ = 10)

- Etapas aceleradas: **E02, E03, E04, E08, E10, E12** (costo de aceleración 71).
- Interacciones auditadas: **E01-parcial, E04-completa, E05-completa, E12-completa, E13-completa** (costo de auditoría 29).
- Costo conjunto: 71 + 29 = **100** de B = 100 (sobran 0).
- Categorías cubiertas: 12 de 12; sin cubrir: ninguna.
- Duración 447 + penalización 0 = objetivo **447**.

## 6. Verificación

- Mochila: fuerza bruta (2^20) = 446, DP = 446 → **OK**.

