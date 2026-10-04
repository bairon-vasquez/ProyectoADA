"""Parte 2: cobertura mínima de auditoría (Set Cover, versión sin pesos).

Tamaño de la entrada: n (interacciones) y r (categorías), U = {0..r-1}.
Los comentarios "# O(.)" cuentan operaciones y coinciden con la deducción de
T(n, r) en docs/03_eficiencia_exactos.md. Ciclos explícitos, sin numpy.

Variante A1 (costos a_j): ``cobertura_voraz_ponderada`` y
``cobertura_exacta_ponderada`` al final del módulo.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from core.instancias import InstanciaSetCover


@dataclass(frozen=True)
class SolucionCobertura:
    """Interacciones elegidas (0-based) y, para el voraz, la traza de pasos.

    ``pasos[k] = (j, nuevas)``: en el paso k se eligió S_j, que cubrió por
    primera vez las categorías ``nuevas``. Vacío en el exacto.
    """

    indices: tuple[int, ...]
    costo: int
    pasos: tuple[tuple[int, tuple[int, ...]], ...] = ()

    @property
    def tamano(self) -> int:
        return len(self.indices)


def numero_armonico(k: int) -> float:
    """H_k = 1 + 1/2 + … + 1/k. O(k). H_0 = 0."""
    h = 0.0
    for i in range(1, k + 1):  # k iteraciones
        h += 1.0 / i  # O(1)
    return h


def cobertura_voraz(inst: InstanciaSetCover) -> SolucionCobertura | None:
    """Voraz: repetir "tomar la interacción que cubre más categorías aún no cubiertas".

    Devuelve None si la instancia no es factible. Desempate: menor índice.
    T(n, r) = O(n·r²):  ≤ r iteraciones del while × n conjuntos × O(r) por conteo.
    Garantía: |voraz| ≤ H_d · |óptimo|, d = max|S_j| ≤ r (docs/04).
    """
    r = inst.r  # O(1)
    n = inst.n  # O(1)
    cubierta = [False] * r  # O(r)
    n_cubiertas = 0  # O(1)
    elegidos: list[int] = []
    pasos: list[tuple[int, tuple[int, ...]]] = []
    while n_cubiertas < r:  # ≤ r iteraciones: cada una cubre ≥ 1 categoría nueva
        mejor_j = -1  # O(1)
        mejor_nuevas = 0  # O(1)
        for j in range(n):  # n iteraciones
            nuevas = 0  # O(1)
            for k in inst.conjuntos[j]:  # |S_j| ≤ r iteraciones
                if not cubierta[k]:  # O(1)
                    nuevas += 1  # O(1)
            # conteo de S_j: O(r)
            if nuevas > mejor_nuevas:  # O(1)
                mejor_nuevas = nuevas
                mejor_j = j
        # búsqueda del mejor conjunto en esta ronda: n · O(r) = O(n·r)
        if mejor_j == -1:  # ninguna categoría nueva alcanzable -> infactible
            return None
        nuevas_cat: list[int] = []
        for k in inst.conjuntos[mejor_j]:  # ≤ r iteraciones -> O(r)
            if not cubierta[k]:
                cubierta[k] = True
                nuevas_cat.append(k)
        n_cubiertas += mejor_nuevas  # O(1)
        elegidos.append(mejor_j)  # O(1)
        pasos.append((mejor_j, tuple(sorted(nuevas_cat))))  # O(r log r) ≤ O(r²), no domina
        # costo por ronda: O(n·r) + O(r) = O(n·r)
    # Total: r rondas × O(n·r) = O(n·r²)
    return SolucionCobertura(
        indices=tuple(elegidos),
        costo=sum(inst.a[j] for j in elegidos),
        pasos=tuple(pasos),
    )


def cobertura_exacta(inst: InstanciaSetCover) -> SolucionCobertura | None:
    """Exacto por fuerza bruta: probar todos los subconjuntos de tamaño k = 0, 1, 2, …

    El primer k para el que algún subconjunto cubre U es el óptimo k*. Devuelve
    None si la unión de todos los S_j no es U.
    T(n, r) = O(Σ_{k≤k*} C(n,k) · k·r) ⊆ O(2^n · n · r).
    """
    r = inst.r  # O(1)
    n = inst.n  # O(1)
    todo: set[int] = set()
    for s in inst.conjuntos:  # n iteraciones
        todo |= s  # O(|S_j|) ≤ O(r)
    if len(todo) < r:  # factibilidad: O(n·r) en total
        return None
    for k in range(n + 1):  # k = 0..n (se detiene en k* ≤ min(n, r))
        for subconjunto in combinations(range(n), k):  # C(n,k) subconjuntos de tamaño k
            cubiertas: set[int] = set()
            for j in subconjunto:  # k iteraciones
                cubiertas |= inst.conjuntos[j]  # O(r)
            # verificar un subconjunto: O(k·r)
            if len(cubiertas) == r:  # O(1)
                return SolucionCobertura(
                    indices=subconjunto,
                    costo=sum(inst.a[j] for j in subconjunto),
                )
    return None  # inalcanzable si la instancia es factible


def cobertura_voraz_ponderada(inst: InstanciaSetCover) -> SolucionCobertura | None:
    """Variante A1: voraz por menor costo por categoría nueva, a_j / (nuevas de S_j).

    Devuelve None si la instancia es infactible. Las razones se comparan sin
    división (productos cruzados enteros): a_j/nuevas_j < a_m/nuevas_m
    ⇔ a_j·nuevas_m < a_m·nuevas_j. Desempate: menor índice.
    T(n, r) = O(n·r²), igual que el voraz sin pesos.
    Garantía (Chvátal, 1979): costo(voraz) ≤ H_d · costo(óptimo), d = max|S_j|.
    """
    r = inst.r  # O(1)
    n = inst.n  # O(1)
    cubierta = [False] * r  # O(r)
    n_cubiertas = 0  # O(1)
    elegidos: list[int] = []
    pasos: list[tuple[int, tuple[int, ...]]] = []
    while n_cubiertas < r:  # ≤ r iteraciones: cada una cubre ≥ 1 categoría nueva
        mejor_j = -1  # O(1)
        mejor_nuevas = 0  # O(1)
        for j in range(n):  # n iteraciones
            nuevas = 0  # O(1)
            for k in inst.conjuntos[j]:  # |S_j| ≤ r iteraciones
                if not cubierta[k]:  # O(1)
                    nuevas += 1  # O(1)
            # conteo de S_j: O(r)
            if nuevas > 0:  # O(1)
                if mejor_j == -1 or inst.a[j] * mejor_nuevas < inst.a[mejor_j] * nuevas:  # O(1)
                    mejor_j = j
                    mejor_nuevas = nuevas
        # búsqueda del mejor conjunto en esta ronda: n · O(r) = O(n·r)
        if mejor_j == -1:  # ninguna categoría nueva alcanzable -> infactible
            return None
        nuevas_cat: list[int] = []
        for k in inst.conjuntos[mejor_j]:  # ≤ r iteraciones -> O(r)
            if not cubierta[k]:
                cubierta[k] = True
                nuevas_cat.append(k)
        n_cubiertas += mejor_nuevas  # O(1)
        elegidos.append(mejor_j)  # O(1)
        pasos.append((mejor_j, tuple(sorted(nuevas_cat))))
        # costo por ronda: O(n·r)
    # Total: r rondas × O(n·r) = O(n·r²)
    return SolucionCobertura(
        indices=tuple(elegidos),
        costo=sum(inst.a[j] for j in elegidos),
        pasos=tuple(pasos),
    )


def cobertura_exacta_ponderada(inst: InstanciaSetCover) -> SolucionCobertura | None:
    """Variante A1, exacto: enumera los 2^n subconjuntos y toma el de menor Σ a_j que cubre U.

    Devuelve None si la instancia es infactible. T(n, r) = O(2^n · n · r):
    por máscara, O(r) para inicializar y O(Σ_{j∈máscara} |S_j|) ≤ O(n·r) para cubrir.
    """
    r = inst.r  # O(1)
    n = inst.n  # O(1)
    mejor_costo = -1  # O(1)
    mejor: tuple[int, ...] = ()
    for mascara in range(1 << n):  # 2^n iteraciones
        costo = 0  # O(1)
        cubierta = [False] * r  # O(r)
        n_cubiertas = 0  # O(1)
        for j in range(n):  # n iteraciones
            if (mascara >> j) & 1:  # O(1)
                costo += inst.a[j]  # O(1)
                for k in inst.conjuntos[j]:  # |S_j| ≤ r iteraciones
                    if not cubierta[k]:  # O(1)
                        cubierta[k] = True
                        n_cubiertas += 1
        # una máscara: O(r + n·r) = O(n·r)
        if n_cubiertas == r and (mejor_costo == -1 or costo < mejor_costo):  # O(1)
            mejor_costo = costo
            mejor = tuple(j for j in range(n) if (mascara >> j) & 1)  # O(n)
    # Total: 2^n · O(n·r)
    if mejor_costo == -1:
        return None
    return SolucionCobertura(indices=mejor, costo=mejor_costo)
