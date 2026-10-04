"""Variante B: aceleración y auditoría con presupuesto conjunto.

Tamaño de la entrada: n (etapas), N (interacciones), r (categorías) y B.
Se elige (x, C) con  Σ c_i·x_i + Σ_{j∈C} a_j ≤ B  minimizando
    (Σ t_i − Σ d_i·x_i) + λ · Σ_{k no cubierta} w_k.

Tres algoritmos:
- ``combinado_cobertura_obligatoria``: caso λ grande (se cubre todo).
- ``combinado_heuristica``: λ general.
- ``combinado_exacto``: referencia para los tests (2^N coberturas × una DP).

Los comentarios "# O(.)" coinciden con docs/03_eficiencia_exactos.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.instancias import InstanciaCombinada, InstanciaMochila
from core.mochila import construir_tabla_dp, mochila_dp
from core.set_cover import cobertura_exacta_ponderada, cobertura_voraz_ponderada


@dataclass(frozen=True)
class SolucionCombinada:
    """Etapas aceleradas, interacciones auditadas y desglose del objetivo."""

    etapas: tuple[int, ...]
    interacciones: tuple[int, ...]
    costo: int
    duracion: int
    penalizacion: int
    objetivo: int


def _cadena_con_presupuesto(inst: InstanciaCombinada, presupuesto: int) -> InstanciaMochila:
    ch = inst.cadena
    return InstanciaMochila(t=ch.t, c=ch.c, d=ch.d, B=presupuesto)


def evaluar_combinada(
    inst: InstanciaCombinada, etapas: tuple[int, ...], interacciones: tuple[int, ...]
) -> SolucionCombinada:
    """Calcula costo conjunto, duración, penalización y objetivo de (x, C). O(n + N·r)."""
    ch, cob = inst.cadena, inst.cobertura
    costo = 0
    reduccion = 0
    for i in etapas:  # ≤ n iteraciones
        costo += ch.c[i]
        reduccion += ch.d[i]
    cubierta = [False] * cob.r  # O(r)
    for j in interacciones:  # ≤ N iteraciones
        costo += cob.a[j]
        for k in cob.conjuntos[j]:  # ≤ r iteraciones
            cubierta[k] = True
    sin_cubrir = 0
    for k in range(cob.r):  # r iteraciones
        if not cubierta[k]:
            sin_cubrir += cob.w[k]
    duracion = sum(ch.t) - reduccion
    penalizacion = inst.lam * sin_cubrir
    return SolucionCombinada(
        etapas=tuple(sorted(etapas)),
        interacciones=tuple(sorted(interacciones)),
        costo=costo,
        duracion=duracion,
        penalizacion=penalizacion,
        objetivo=duracion + penalizacion,
    )


def combinado_cobertura_obligatoria(
    inst: InstanciaCombinada, exacta: bool = True
) -> SolucionCombinada | None:
    """Caso λ grande: cobertura de costo mínimo C* y luego Mochila con B − a(C*).

    Es óptimo cuando ``exacta=True`` porque el óptimo de la Mochila nunca
    empeora al aumentar el presupuesto: gastar lo mínimo en cubrir deja el
    máximo para acelerar. Con ``exacta=False`` se usa el voraz ponderado (A1) y
    es una heurística. Devuelve None si no hay cobertura o a(C*) > B.

    T = T_cobertura + O(n·B):
      exacta  -> O(2^N · N · r) + O(n·B);   voraz -> O(N·r²) + O(n·B).
    """
    if exacta:
        cob = cobertura_exacta_ponderada(inst.cobertura)  # O(2^N·N·r)
    else:
        cob = cobertura_voraz_ponderada(inst.cobertura)  # O(N·r²)
    if cob is None or cob.costo > inst.B:  # O(1)
        return None
    resto = inst.B - cob.costo  # O(1)
    sol = mochila_dp(_cadena_con_presupuesto(inst, resto))  # O(n·resto) ≤ O(n·B)
    return evaluar_combinada(inst, sol.etapas, cob.indices)  # O(n + N·r)


def combinado_heuristica(inst: InstanciaCombinada) -> SolucionCombinada:
    """Heurística para λ general: cobertura voraz por beneficio/costo + una sola DP.

    1. Construir UNA vez la tabla DP de la cadena con presupuesto B: la fila
       DP[n][b] da la máxima reducción con presupuesto ≤ b. O(n·B).
    2. Hacer crecer la cobertura con el voraz "mayor λ·w(nuevas)/a_j" mientras
       el costo quepa en B y haya beneficio. Tras cada elección (cada prefijo
       C_0 ⊂ C_1 ⊂ …) el objetivo se evalúa en O(1):
           Σt − DP[n][B − a(C_p)] + λ·w(sin cubrir).
    3. Quedarse con el mejor prefijo (incluye el vacío) y reconstruir la
       Mochila con el presupuesto restante.

    T(n, N, r, B) = O(n·B + N·r·min(N, r)) ⊆ O(n·B + N·r²): hay ≤ min(N, r) rondas
    y cada ronda recorre N conjuntos en O(r). Nunca es peor que "no auditar nada".
    """
    ch, cob = inst.cadena, inst.cobertura
    n, N, r, B, lam = ch.n, cob.n, cob.r, inst.B, inst.lam  # O(1)
    ultima_fila = construir_tabla_dp(_cadena_con_presupuesto(inst, B))[n]  # O(n·B)
    suma_t = sum(ch.t)  # O(n)
    cubierta = [False] * r  # O(r)
    sin_cubrir = sum(cob.w)  # O(r)
    costo_cob = 0  # O(1)
    elegidos: list[int] = []
    mejor_obj = suma_t - ultima_fila[B] + lam * sin_cubrir  # prefijo vacío, O(1)
    mejor_p = 0  # O(1)
    while lam > 0:  # ≤ min(N, r) rondas: cada una cubre ≥ 1 categoría nueva
        mejor_j = -1
        mejor_peso = 0
        for j in range(N):  # N iteraciones
            if cob.a[j] > B - costo_cob:  # no cabe en el presupuesto
                continue
            peso_nuevo = 0
            for k in cob.conjuntos[j]:  # ≤ r iteraciones
                if not cubierta[k]:
                    peso_nuevo += cob.w[k]
            # razón w_j/a_j > w_m/a_m  ⇔  w_j·a_m > w_m·a_j  (λ es común, se cancela)
            if peso_nuevo > 0 and (
                mejor_j == -1 or peso_nuevo * cob.a[mejor_j] > mejor_peso * cob.a[j]
            ):
                mejor_j = j
                mejor_peso = peso_nuevo
        # elegir el mejor conjunto de la ronda: N · O(r)
        if mejor_j == -1:
            break
        for k in cob.conjuntos[mejor_j]:  # O(r)
            cubierta[k] = True
        sin_cubrir -= mejor_peso  # O(1)
        costo_cob += cob.a[mejor_j]  # O(1)
        elegidos.append(mejor_j)  # O(1)
        obj = suma_t - ultima_fila[B - costo_cob] + lam * sin_cubrir  # O(1)
        if obj < mejor_obj:
            mejor_obj = obj
            mejor_p = len(elegidos)
    # Total del barrido: O(min(N, r) · N · r)
    interacciones = tuple(elegidos[:mejor_p])
    costo_final = sum(cob.a[j] for j in interacciones)  # O(N)
    sol = mochila_dp(_cadena_con_presupuesto(inst, B - costo_final))  # O(n·B)
    return evaluar_combinada(inst, sol.etapas, interacciones)


def combinado_exacto(inst: InstanciaCombinada) -> SolucionCombinada:
    """Exacto (referencia): para cada C ⊆ [N] con a(C) ≤ B, la mejor Mochila es DP[n][B − a(C)].

    La tabla DP se construye una sola vez: O(n·B). Después, 2^N coberturas
    × O(N·r) cada una. T = O(n·B + 2^N · N · r).
    """
    ch, cob = inst.cadena, inst.cobertura
    n, N, r, B, lam = ch.n, cob.n, cob.r, inst.B, inst.lam  # O(1)
    ultima_fila = construir_tabla_dp(_cadena_con_presupuesto(inst, B))[n]  # O(n·B)
    suma_t = sum(ch.t)
    suma_w = sum(cob.w)
    mejor_obj = -1
    mejor_c: tuple[int, ...] = ()
    for mascara in range(1 << N):  # 2^N iteraciones
        costo = 0
        cubierta = [False] * r  # O(r)
        peso_cubierto = 0
        for j in range(N):  # N iteraciones
            if (mascara >> j) & 1:
                costo += cob.a[j]
                for k in cob.conjuntos[j]:  # ≤ r iteraciones
                    if not cubierta[k]:
                        cubierta[k] = True
                        peso_cubierto += cob.w[k]
        # una máscara: O(N·r)
        if costo <= B:
            obj = suma_t - ultima_fila[B - costo] + lam * (suma_w - peso_cubierto)
            if mejor_obj == -1 or obj < mejor_obj:
                mejor_obj = obj
                mejor_c = tuple(j for j in range(N) if (mascara >> j) & 1)
    costo_cob = sum(cob.a[j] for j in mejor_c)
    sol = mochila_dp(_cadena_con_presupuesto(inst, B - costo_cob))  # O(n·B)
    return evaluar_combinada(inst, sol.etapas, mejor_c)
