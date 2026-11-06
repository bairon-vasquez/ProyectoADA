# Traza del caso `caso_01_etapa0`

Ejemplo de la Etapa 0: óptimo de la Parte 1 = {2, 3} (duración 23 → 18); óptimo de la Parte 2 = {1, 4}.

## Parte 1 — Aceleración de la cadena (Mochila 0/1)

- Entrada: n = 4 etapas, presupuesto B = 6.
- **Etapas aceleradas: {2, 3}** · costo 6 / 6
- Duración: 23 → **18** (reducción 5).
- Tiempo: **0.000005 s** (mediana de 7 repeticiones; mín 0.000004, máx 0.000014). T(n, B) = O(n·B), pseudo-polinomial; 35 celdas.

- Verificación con fuerza bruta (2^n): reducción óptima 5 ✔ coincide

### Etapas y costos

| etapa | t | c | d | ¿acelerada? | t final |
|---|---|---|---|---|---|
| 1 | 5 | 3 | 2 | no | 5 |
| 2 | 8 | 4 | 4 | sí | 4 |
| 3 | 6 | 2 | 1 | sí | 5 |
| 4 | 4 | 3 | 2 | no | 4 |

### Estados de la DP: DP[i][b] = máxima reducción con las primeras i etapas y presupuesto b

| i \ b | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 | 2 | 2 | 2 | 2 |
| 2 | 0 | 0 | 0 | 2 | 4 | 4 | 4 |
| 3 | 0 | 0 | 1 | 2 | 4 | 4 | 5 |
| 4 | 0 | 0 | 1 | 2 | 4 | 4 | 5 |

### Reconstrucción (de DP[n][B] hacia atrás)

Se compara no acelerar la etapa i (DP[i−1][b]) con acelerarla (DP[i−1][b−c_i] + d_i, solo si c_i ≤ b) y se queda el mayor:

| etapa i | b | sin acelerar: DP[i−1][b] | acelerando: DP[i−1][b−c_i]+d_i | DP[i][b] | decisión | b siguiente |
|---|---|---|---|---|---|---|
| 4 | 6 | 5 | 4 | 5 | no acelerar | 6 |
| 3 | 6 | 4 | 5 | 5 | acelerar | 4 |
| 2 | 4 | 2 | 4 | 4 | acelerar | 0 |
| 1 | 0 | 0 | — | 0 | no acelerar | 0 |

## Parte 2 — Cobertura de auditoría (Parte 2)

- Entrada: 5 interacciones, 5 categorías (d = 3).
- Tiempo: **0.000003 s** (mediana de 7 repeticiones). T(n, r) = O(n·r²).
- **Interacciones auditadas: {1, 4}** (orden de elección: ['1', '4']) · cantidad 2 · costo total 2.
- Cobertura: 5/5 categorías (completa).
- Cota: G ≤ H_d · óptimo (Johnson 1974; Chvátal 1979) · H_d = 1.833 · H_r = 2.283.
- Verificación con exacto por fuerza bruta: óptimo = 2 ({1, 4}); razón voraz/óptimo = 1.000; cumple la cota H_d.

### Elecciones del voraz

| paso | interacción | categorías nuevas | #nuevas | costo a | costo acumulado | cubiertas | pendientes |
|---|---|---|---|---|---|---|---|
| 1 | 1 | {1, 2, 3} | 3 | 1 | 1 | 3 | 2 |
| 2 | 4 | {4, 5} | 2 | 1 | 2 | 5 | 0 |
