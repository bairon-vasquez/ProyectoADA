"""Parte 1: aceleración de la cadena bajo presupuesto (Mochila 0/1).

Tamaño de la entrada: n (etapas) y B (presupuesto).
Maximizar la reducción total Σ d_i·x_i  ⇔  minimizar Σ t_i − Σ d_i·x_i,
con la restricción Σ c_i·x_i ≤ B.

Los comentarios "# O(.)" cuentan operaciones y coinciden con la deducción de
T(n, B) en docs/03_eficiencia_exactos.md. Se usan ciclos explícitos (sin numpy).
"""

from __future__ import annotations

from dataclasses import dataclass

from core.instancias import InstanciaMochila


@dataclass(frozen=True)
class SolucionMochila:
    """Resultado: etapas aceleradas (0-based, ordenadas), reducción, costo y duración."""

    etapas: tuple[int, ...]
    reduccion: int
    costo: int
    duracion: int


def _evaluar(inst: InstanciaMochila, etapas: tuple[int, ...]) -> SolucionMochila:
    """Calcula costo, reducción y duración de un subconjunto de etapas. O(|etapas|)."""
    costo = 0
    reduccion = 0
    for i in etapas:  # |etapas| ≤ n iteraciones, cada una O(1)
        costo += inst.c[i]
        reduccion += inst.d[i]
    duracion = sum(inst.t) - reduccion
    return SolucionMochila(etapas, reduccion, costo, duracion)


def mochila_fuerza_bruta(inst: InstanciaMochila) -> SolucionMochila:
    """Exacto por enumeración de los 2^n subconjuntos. T(n) = O(2^n · n).

    Cada máscara ``mascara`` ∈ [0, 2^n) codifica x: x_i = 1 si el bit i está
    encendido. Se descartan los subconjuntos con costo > B.
    """
    n = inst.n  # O(1)
    mejor_red = -1  # O(1)
    mejor_etapas: tuple[int, ...] = ()
    for mascara in range(1 << n):  # 2^n iteraciones
        costo = 0
        reduccion = 0
        for i in range(n):  # n iteraciones por máscara -> O(n)
            if (mascara >> i) & 1:  # O(1)
                costo += inst.c[i]  # O(1)
                reduccion += inst.d[i]  # O(1)
        if costo <= inst.B and reduccion > mejor_red:  # O(1)
            mejor_red = reduccion
            mejor_etapas = tuple(i for i in range(n) if (mascara >> i) & 1)  # O(n), solo al mejorar
    # Total: 2^n · (n·O(1) + O(1)) = O(2^n · n)  (la máscara 0 siempre es factible)
    return _evaluar(inst, mejor_etapas)


def construir_tabla_dp(inst: InstanciaMochila) -> list[list[int]]:
    """Llena DP[i][b] = máxima reducción usando solo las primeras i etapas con presupuesto b.

    Recurrencia (i = 1..n, b = 0..B):
        DP[i][b] = DP[i-1][b]                                   si c_i > b
        DP[i][b] = max(DP[i-1][b], DP[i-1][b-c_i] + d_i)        si c_i ≤ b
    Caso base: DP[0][b] = 0. Devuelve la tabla completa de (n+1) × (B+1).
    T(n, B) = O(n·B) tiempo y O(n·B) espacio.
    """
    n, B = inst.n, inst.B  # O(1)
    tabla = [[0] * (B + 1) for _ in range(n + 1)]  # (n+1)(B+1) asignaciones -> O(n·B)
    for i in range(1, n + 1):  # n iteraciones
        ci = inst.c[i - 1]  # O(1)
        di = inst.d[i - 1]  # O(1)
        for b in range(B + 1):  # B+1 iteraciones por cada i
            sin_i = tabla[i - 1][b]  # O(1)
            if ci <= b:  # O(1)
                con_i = tabla[i - 1][b - ci] + di  # O(1)
                tabla[i][b] = con_i if con_i > sin_i else sin_i  # O(1)
            else:
                tabla[i][b] = sin_i  # O(1)
    # Total llenado: n · (B+1) · O(1) = O(n·B)
    return tabla


def reconstruir_etapas(inst: InstanciaMochila, tabla: list[list[int]]) -> tuple[int, ...]:
    """Recupera las etapas elegidas recorriendo la tabla desde (n, B) hacia atrás. O(n).

    Si DP[i][b] == DP[i-1][b], la etapa i no hizo falta; si no, se eligió
    (entonces DP[i][b] = DP[i-1][b-c_i] + d_i) y el presupuesto baja en c_i.
    """
    b = inst.B  # O(1)
    elegidas: list[int] = []
    for i in range(inst.n, 0, -1):  # n iteraciones
        if tabla[i][b] != tabla[i - 1][b]:  # O(1)
            elegidas.append(i - 1)  # O(1) amortizado
            b -= inst.c[i - 1]  # O(1)
    elegidas.reverse()  # O(n)
    return tuple(elegidas)  # Total: O(n)


def mochila_dp(inst: InstanciaMochila) -> SolucionMochila:
    """Exacto por programación dinámica con reconstrucción. T(n, B) = O(n·B)."""
    tabla = construir_tabla_dp(inst)  # O(n·B)
    etapas = reconstruir_etapas(inst, tabla)  # O(n)
    return _evaluar(inst, etapas)  # O(n)  ->  total O(n·B + n) = O(n·B)
