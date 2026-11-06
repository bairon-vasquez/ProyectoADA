# Traza del caso `caso_04_costos_A1`

Variante A1: la auditoría tiene costo a_j por interacción (minimizar el costo total).

## Parte 1 — Aceleración de la cadena (Mochila 0/1)

- Entrada: n = 16 etapas, presupuesto B = 60.
- **Etapas aceleradas: {2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16}** · costo 59 / 60
- Duración: 108 → **67** (reducción 41).
- Tiempo: **0.000076 s** (mediana de 7 repeticiones; mín 0.000075, máx 0.000084). T(n, B) = O(n·B), pseudo-polinomial; 1037 celdas.

- Verificación con fuerza bruta (2^n): reducción óptima 41 ✔ coincide

### Etapas y costos

| etapa | t | c | d | ¿acelerada? | t final |
|---|---|---|---|---|---|
| 1 | 2 | 8 | 1 | no | 2 |
| 2 | 15 | 2 | 6 | sí | 9 |
| 3 | 7 | 9 | 1 | no | 7 |
| 4 | 15 | 1 | 1 | sí | 14 |
| 5 | 1 | 3 | 1 | sí | 0 |
| 6 | 9 | 3 | 1 | sí | 8 |
| 7 | 2 | 4 | 1 | sí | 1 |
| 8 | 11 | 3 | 7 | sí | 4 |
| 9 | 10 | 9 | 6 | sí | 4 |
| 10 | 2 | 3 | 2 | sí | 0 |
| 11 | 6 | 5 | 1 | sí | 5 |
| 12 | 3 | 7 | 3 | sí | 0 |
| 13 | 7 | 5 | 1 | sí | 6 |
| 14 | 2 | 9 | 2 | sí | 0 |
| 15 | 1 | 1 | 0 | no | 1 |
| 16 | 15 | 5 | 9 | sí | 6 |

### Estados de la DP: DP[i][b] = máxima reducción con las primeras i etapas y presupuesto b

(tabla de 17×61 guardada completa en el JSON, campo `traza.tabla_dp`)

### Reconstrucción (de DP[n][B] hacia atrás)

Se compara no acelerar la etapa i (DP[i−1][b]) con acelerarla (DP[i−1][b−c_i] + d_i, solo si c_i ≤ b) y se queda el mayor:

| etapa i | b | sin acelerar: DP[i−1][b] | acelerando: DP[i−1][b−c_i]+d_i | DP[i][b] | decisión | b siguiente |
|---|---|---|---|---|---|---|
| 16 | 60 | 32 | 41 | 41 | acelerar | 55 |
| 15 | 55 | 32 | 32 | 32 | no acelerar | 55 |
| 14 | 55 | 31 | 32 | 32 | acelerar | 46 |
| 13 | 46 | 29 | 30 | 30 | acelerar | 41 |
| 12 | 41 | 27 | 29 | 29 | acelerar | 34 |
| 11 | 34 | 25 | 26 | 26 | acelerar | 29 |
| 10 | 29 | 23 | 25 | 25 | acelerar | 26 |
| 9 | 26 | 18 | 23 | 23 | acelerar | 17 |
| 8 | 17 | 10 | 17 | 17 | acelerar | 14 |
| 7 | 14 | 9 | 10 | 10 | acelerar | 10 |
| 6 | 10 | 8 | 9 | 9 | acelerar | 7 |
| 5 | 7 | 7 | 8 | 8 | acelerar | 4 |
| 4 | 4 | 6 | 7 | 7 | acelerar | 3 |
| 3 | 3 | 6 | — | 6 | no acelerar | 3 |
| 2 | 3 | 0 | 6 | 6 | acelerar | 1 |
| 1 | 1 | 0 | — | 0 | no acelerar | 1 |

## Parte 2 — Cobertura de auditoría (A1 (costos))

- Entrada: 12 interacciones, 10 categorías (d = 7).
- Tiempo: **0.000010 s** (mediana de 7 repeticiones). T(n, r) = O(n·r²).
- **Interacciones auditadas: {1, 3, 5, 12}** (orden de elección: ['1', '3', '12', '5']) · cantidad 4 · costo total 10.
- Cobertura: 10/10 categorías (completa).
- Cota: G ≤ H_d · óptimo (Chvátal, 1979) · H_d = 2.593 · H_r = 2.929.
- Verificación con exacto por fuerza bruta: óptimo = 9 ({3, 5, 12}); razón voraz/óptimo = 1.111; cumple la cota H_d.

### Elecciones del voraz

| paso | interacción | categorías nuevas | #nuevas | costo a | a/nuevas | costo acumulado | cubiertas | pendientes |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | {1, 3, 4, 8} | 4 | 1 | 0.250 | 1 | 4 | 6 |
| 2 | 3 | {2, 6, 7} | 3 | 2 | 0.667 | 3 | 7 | 3 |
| 3 | 12 | {10} | 1 | 1 | 1.000 | 4 | 8 | 2 |
| 4 | 5 | {5, 9} | 2 | 6 | 3.000 | 10 | 10 | 0 |
