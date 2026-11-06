# Traza del caso `entrada_G3_mochila_20_nodos`

## Parte 1 — Aceleración de la cadena (Mochila 0/1)

- Entrada: n = 20 etapas, presupuesto B = 72.
- **Etapas aceleradas: {E02, E03, E04, E06, E08, E12}** · costo 72 / 72
- Duración: 501 → **446** (reducción 55).
- Tiempo: **0.000095 s** (mediana de 7 repeticiones; mín 0.000092, máx 0.000103). T(n, B) = O(n·B), pseudo-polinomial; 1533 celdas.

- Verificación con fuerza bruta (2^n): reducción óptima 55 ✔ coincide

### Etapas y costos

| etapa | t | c | d | ¿acelerada? | t final |
|---|---|---|---|---|---|
| E01 | 18 | 7 | 5 | no | 18 |
| E02 | 24 | 12 | 9 | sí | 15 |
| E03 | 16 | 5 | 4 | sí | 12 |
| E04 | 30 | 16 | 12 | sí | 18 |
| E05 | 22 | 9 | 6 | no | 22 |
| E06 | 27 | 13 | 10 | sí | 17 |
| E07 | 20 | 10 | 7 | no | 20 |
| E08 | 35 | 17 | 13 | sí | 22 |
| E09 | 19 | 7 | 5 | no | 19 |
| E10 | 25 | 12 | 9 | no | 25 |
| E11 | 31 | 15 | 11 | no | 31 |
| E12 | 23 | 9 | 7 | sí | 16 |
| E13 | 29 | 14 | 10 | no | 29 |
| E14 | 17 | 6 | 4 | no | 17 |
| E15 | 28 | 11 | 8 | no | 28 |
| E16 | 34 | 16 | 12 | no | 34 |
| E17 | 21 | 8 | 6 | no | 21 |
| E18 | 26 | 12 | 9 | no | 26 |
| E19 | 32 | 15 | 11 | no | 32 |
| E20 | 24 | 10 | 7 | no | 24 |

### Estados de la DP: DP[i][b] = máxima reducción con las primeras i etapas y presupuesto b

(tabla de 21×73 guardada completa en el JSON, campo `traza.tabla_dp`)

### Reconstrucción (de DP[n][B] hacia atrás)

Se compara no acelerar la etapa i (DP[i−1][b]) con acelerarla (DP[i−1][b−c_i] + d_i, solo si c_i ≤ b) y se queda el mayor:

| etapa i | b | sin acelerar: DP[i−1][b] | acelerando: DP[i−1][b−c_i]+d_i | DP[i][b] | decisión | b siguiente |
|---|---|---|---|---|---|---|
| E20 | 72 | 55 | 54 | 55 | no acelerar | 72 |
| E19 | 72 | 55 | 54 | 55 | no acelerar | 72 |
| E18 | 72 | 55 | 55 | 55 | no acelerar | 72 |
| E17 | 72 | 55 | 54 | 55 | no acelerar | 72 |
| E16 | 72 | 55 | 55 | 55 | no acelerar | 72 |
| E15 | 72 | 55 | 54 | 55 | no acelerar | 72 |
| E14 | 72 | 55 | 54 | 55 | no acelerar | 72 |
| E13 | 72 | 55 | 54 | 55 | no acelerar | 72 |
| E12 | 72 | 54 | 55 | 55 | acelerar | 63 |
| E11 | 63 | 48 | 47 | 48 | no acelerar | 63 |
| E10 | 63 | 48 | 48 | 48 | no acelerar | 63 |
| E09 | 63 | 48 | 47 | 48 | no acelerar | 63 |
| E08 | 63 | 47 | 48 | 48 | acelerar | 46 |
| E07 | 46 | 35 | 34 | 35 | no acelerar | 46 |
| E06 | 46 | 32 | 35 | 35 | acelerar | 33 |
| E05 | 33 | 25 | 24 | 25 | no acelerar | 33 |
| E04 | 33 | 18 | 25 | 25 | acelerar | 17 |
| E03 | 17 | 9 | 13 | 13 | acelerar | 12 |
| E02 | 12 | 5 | 9 | 9 | acelerar | 0 |
| E01 | 0 | 0 | — | 0 | no acelerar | 0 |

## Parte 2 — Cobertura de auditoría (A1 (costos))

- Entrada: 35 interacciones, 12 categorías (d = 4).
- Tiempo: **0.000028 s** (mediana de 7 repeticiones). T(n, r) = O(n·r²).
- **Interacciones auditadas: {E01 parcial, E11 completa, E12 completa, E13 completa, E18 parcial}** (orden de elección: ['E01 parcial', 'E12 completa', 'E13 completa', 'E11 completa', 'E18 parcial']) · cantidad 5 · costo total 25.
- Cobertura: 12/12 categorías (completa).
- Cota: G ≤ H_d · óptimo (Chvátal, 1979) · H_d = 2.083 · H_r = 3.103.
- Regla «a lo sumo una variación por etapa»: cumplida.
- Verificación con exacto por DP sobre máscaras de categorías, O(N·2^r) con r = 12: óptimo = 24 ({E07 completa, E17 completa, E18 completa, E19 parcial}); razón voraz/óptimo = 1.042; cumple la cota H_d.

### Elecciones del voraz

| paso | interacción | categorías nuevas | #nuevas | costo a | a/nuevas | costo acumulado | cubiertas | pendientes |
|---|---|---|---|---|---|---|---|---|
| 1 | E01 parcial | {R01, R02} | 2 | 3 | 1.500 | 3 | 2 | 10 |
| 2 | E12 completa | {R03, R07, R09, R12} | 4 | 7 | 1.750 | 10 | 6 | 6 |
| 3 | E13 completa | {R05, R06, R11} | 3 | 6 | 2.000 | 16 | 9 | 3 |
| 4 | E11 completa | {R04, R10} | 2 | 6 | 3.000 | 22 | 11 | 1 |
| 5 | E18 parcial | {R08} | 1 | 3 | 3.000 | 25 | 12 | 0 |

## Variante C — flujo como DAG (heurística de la ruta crítica)

- Entrada: n = 20 etapas, m = 19 precedencias, B = 72 (cadena en serie). T(n, m) = O(n·(n+m)); sin garantía de optimalidad (docs/04).
- Tiempo: **0.000066 s** (mediana de 7 repeticiones).
- Ruta crítica inicial: E01 → E02 → E03 → E04 → E05 → E06 → E07 → E08 → E09 → E10 → E11 → E12 → E13 → E14 → E15 → E16 → E17 → E18 → E19 → E20 (duración 501).
- **Etapas aceleradas: {E02, E03, E04, E06, E08, E12}** · costo 72 / 72 · duración final **446**.

| paso | etapa acelerada | ruta crítica tras acelerarla |
|---|---|---|
| 1 | E03 | 497 |
| 2 | E12 | 490 |
| 3 | E06 | 480 |
| 4 | E08 | 467 |
| 5 | E02 | 458 |
| 6 | E04 | 446 |

- Verificación con Mochila (óptimo en una cadena): duración óptima 446 (✔ la heurística coincide).

## Variante B — presupuesto conjunto (la auditoría cubre todo; el resto acelera)

- Presupuesto conjunto: 100. T = T_cobertura + O(n·B); exacto por máscaras O(N·2^r), voraz O(N·r²).

- **Exacta (a* por máscaras + DP con B − a*)**: auditoría {E07 completa, E17 completa, E18 completa, E19 parcial} (costo 24), quedan 76 para acelerar {E03, E04, E06, E08, E12, E16}; costo total 100; duración final **443** (reducción 58).
- **Con la cobertura voraz (a_g + DP con B − a_g)**: auditoría {E01 parcial, E11 completa, E12 completa, E13 completa, E18 parcial} (costo 25), quedan 75 para acelerar {E02, E03, E04, E06, E08, E10}; costo total 100; duración final **444** (reducción 57).

- Costo de auditoría: voraz 25 vs a* = 24 (razón 1.042). Duración: voraz 444 vs exacta 443 → se pierden **1** unidades de tiempo por el exceso de auditoría.
