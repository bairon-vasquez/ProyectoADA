# Traza del caso `caso_03_mediano`

Tamaño mediano generado con semilla 303 (verificable contra la fuerza bruta).

## Parte 1 — Aceleración de la cadena (Mochila 0/1)

- Entrada: n = 14 etapas, presupuesto B = 30.
- **Etapas aceleradas: {3, 6, 7, 8, 10, 11, 14}** · costo 28 / 30
- Duración: 92 → **62** (reducción 30).
- Tiempo: **0.000034 s** (mediana de 7 repeticiones; mín 0.000032, máx 0.000056). T(n, B) = O(n·B), pseudo-polinomial; 465 celdas.

- Verificación con fuerza bruta (2^n): reducción óptima 30 ✔ coincide

### Etapas y costos

| etapa | t | c | d | ¿acelerada? | t final |
|---|---|---|---|---|---|
| 1 | 1 | 2 | 0 | no | 1 |
| 2 | 4 | 5 | 1 | no | 4 |
| 3 | 12 | 9 | 5 | sí | 7 |
| 4 | 4 | 9 | 1 | no | 4 |
| 5 | 2 | 1 | 0 | no | 2 |
| 6 | 10 | 2 | 3 | sí | 7 |
| 7 | 10 | 7 | 9 | sí | 1 |
| 8 | 5 | 3 | 2 | sí | 3 |
| 9 | 10 | 8 | 1 | no | 10 |
| 10 | 9 | 5 | 3 | sí | 6 |
| 11 | 7 | 1 | 4 | sí | 3 |
| 12 | 3 | 7 | 1 | no | 3 |
| 13 | 7 | 5 | 0 | no | 7 |
| 14 | 8 | 1 | 4 | sí | 4 |

### Estados de la DP: DP[i][b] = máxima reducción con las primeras i etapas y presupuesto b

(tabla de 15×31 guardada completa en el JSON, campo `traza.tabla_dp`)

### Reconstrucción (de DP[n][B] hacia atrás)

| etapa i | b | DP[i][b] | DP[i−1][b] | decisión | b siguiente |
|---|---|---|---|---|---|
| 14 | 30 | 30 | 26 | acelerar | 29 |
| 13 | 29 | 26 | 26 | no acelerar | 29 |
| 12 | 29 | 26 | 26 | no acelerar | 29 |
| 11 | 29 | 26 | 22 | acelerar | 28 |
| 10 | 28 | 22 | 20 | acelerar | 23 |
| 9 | 23 | 19 | 19 | no acelerar | 23 |
| 8 | 23 | 19 | 18 | acelerar | 20 |
| 7 | 20 | 17 | 9 | acelerar | 13 |
| 6 | 13 | 8 | 5 | acelerar | 11 |
| 5 | 11 | 5 | 5 | no acelerar | 11 |
| 4 | 11 | 5 | 5 | no acelerar | 11 |
| 3 | 11 | 5 | 1 | acelerar | 2 |
| 2 | 2 | 0 | 0 | no acelerar | 2 |
| 1 | 2 | 0 | 0 | no acelerar | 2 |

## Parte 2 — Cobertura de auditoría (Parte 2)

- Entrada: 14 interacciones, 12 categorías (d = 6).
- Tiempo: **0.000009 s** (mediana de 7 repeticiones). T(n, r) = O(n·r²).
- **Interacciones auditadas: {1, 6, 7, 9, 11}** (orden de elección: ['6', '7', '1', '9', '11']) · cantidad 5 · costo total 5.
- Cobertura: 12/12 categorías (completa).
- Cota: G ≤ H_d · óptimo (Johnson 1974; Chvátal 1979) · H_d = 2.450 · H_r = 3.103.
- Verificación con exacto por fuerza bruta: óptimo = 5 ({1, 6, 7, 9, 11}); razón voraz/óptimo = 1.000; cumple la cota H_d.

### Elecciones del voraz

| paso | interacción | categorías nuevas | #nuevas | costo a | costo acumulado | cubiertas | pendientes |
|---|---|---|---|---|---|---|---|
| 1 | 6 | {2, 3, 5, 7, 8, 11} | 6 | 1 | 1 | 6 | 6 |
| 2 | 7 | {4, 9, 12} | 3 | 1 | 2 | 9 | 3 |
| 3 | 1 | {1} | 1 | 1 | 3 | 10 | 2 |
| 4 | 9 | {6} | 1 | 1 | 4 | 11 | 1 |
| 5 | 11 | {10} | 1 | 1 | 5 | 12 | 0 |
