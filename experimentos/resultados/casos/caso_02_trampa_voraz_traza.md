# Traza del caso `caso_02_trampa_voraz`

Parte 2 con la trampa clásica: el voraz elige primero el conjunto más grande y usa 3 interacciones, el óptimo usa 2. Parte 1 de tamaño pequeño.

## Parte 1 — Aceleración de la cadena (Mochila 0/1)

- Entrada: n = 8 etapas, presupuesto B = 20.
- **Etapas aceleradas: {1, 2, 3, 5}** · costo 18 / 20
- Duración: 59 → **36** (reducción 23).
- Tiempo: **0.000018 s** (mediana de 7 repeticiones; mín 0.000017, máx 0.000023). T(n, B) = O(n·B), pseudo-polinomial; 189 celdas.

- Verificación con fuerza bruta (2^n): reducción óptima 23 ✔ coincide

### Etapas y costos

| etapa | t | c | d | ¿acelerada? | t final |
|---|---|---|---|---|---|
| 1 | 8 | 8 | 6 | sí | 2 |
| 2 | 9 | 3 | 7 | sí | 2 |
| 3 | 8 | 2 | 2 | sí | 6 |
| 4 | 8 | 8 | 0 | no | 8 |
| 5 | 9 | 5 | 8 | sí | 1 |
| 6 | 10 | 3 | 1 | no | 10 |
| 7 | 4 | 2 | 0 | no | 4 |
| 8 | 3 | 1 | 0 | no | 3 |

### Estados de la DP: DP[i][b] = máxima reducción con las primeras i etapas y presupuesto b

| i \ b | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| 2 | 0 | 0 | 0 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 |
| 3 | 0 | 0 | 2 | 7 | 7 | 9 | 9 | 9 | 9 | 9 | 9 | 13 | 13 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |
| 4 | 0 | 0 | 2 | 7 | 7 | 9 | 9 | 9 | 9 | 9 | 9 | 13 | 13 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |
| 5 | 0 | 0 | 2 | 7 | 7 | 9 | 9 | 10 | 15 | 15 | 17 | 17 | 17 | 17 | 17 | 17 | 21 | 21 | 23 | 23 | 23 |
| 6 | 0 | 0 | 2 | 7 | 7 | 9 | 9 | 10 | 15 | 15 | 17 | 17 | 17 | 18 | 18 | 18 | 21 | 21 | 23 | 23 | 23 |
| 7 | 0 | 0 | 2 | 7 | 7 | 9 | 9 | 10 | 15 | 15 | 17 | 17 | 17 | 18 | 18 | 18 | 21 | 21 | 23 | 23 | 23 |
| 8 | 0 | 0 | 2 | 7 | 7 | 9 | 9 | 10 | 15 | 15 | 17 | 17 | 17 | 18 | 18 | 18 | 21 | 21 | 23 | 23 | 23 |

### Reconstrucción (de DP[n][B] hacia atrás)

Se compara no acelerar la etapa i (DP[i−1][b]) con acelerarla (DP[i−1][b−c_i] + d_i, solo si c_i ≤ b) y se queda el mayor:

| etapa i | b | sin acelerar: DP[i−1][b] | acelerando: DP[i−1][b−c_i]+d_i | DP[i][b] | decisión | b siguiente |
|---|---|---|---|---|---|---|
| 8 | 20 | 23 | 23 | 23 | no acelerar | 20 |
| 7 | 20 | 23 | 23 | 23 | no acelerar | 20 |
| 6 | 20 | 23 | 22 | 23 | no acelerar | 20 |
| 5 | 20 | 15 | 23 | 23 | acelerar | 15 |
| 4 | 15 | 15 | 9 | 15 | no acelerar | 15 |
| 3 | 15 | 13 | 15 | 15 | acelerar | 13 |
| 2 | 13 | 6 | 13 | 13 | acelerar | 10 |
| 1 | 10 | 0 | 6 | 6 | acelerar | 2 |

## Parte 2 — Cobertura de auditoría (Parte 2)

- Entrada: 3 interacciones, 6 categorías (d = 4).
- Tiempo: **0.000003 s** (mediana de 7 repeticiones). T(n, r) = O(n·r²).
- **Interacciones auditadas: {1, 2, 3}** (orden de elección: ['1', '2', '3']) · cantidad 3 · costo total 3.
- Cobertura: 6/6 categorías (completa).
- Cota: G ≤ H_d · óptimo (Johnson 1974; Chvátal 1979) · H_d = 2.083 · H_r = 2.450.
- Verificación con exacto por fuerza bruta: óptimo = 2 ({2, 3}); razón voraz/óptimo = 1.500; cumple la cota H_d.

### Elecciones del voraz

| paso | interacción | categorías nuevas | #nuevas | costo a | costo acumulado | cubiertas | pendientes |
|---|---|---|---|---|---|---|---|
| 1 | 1 | {1, 2, 4, 5} | 4 | 1 | 1 | 4 | 2 |
| 2 | 2 | {3} | 1 | 1 | 2 | 5 | 1 |
| 3 | 3 | {6} | 1 | 1 | 3 | 6 | 0 |
