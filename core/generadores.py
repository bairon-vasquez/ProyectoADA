"""Generadores sintéticos de instancias, reproducibles mediante semilla.

Cada generador crea su propio ``random.Random(semilla)``, así que la misma
semilla y los mismos parámetros dan siempre la misma instancia, sin tocar el
estado global de ``random``.
"""

from __future__ import annotations

import random

from core.instancias import (
    InstanciaCombinada,
    InstanciaDAG,
    InstanciaMochila,
    InstanciaSetCover,
)


def generar_mochila(
    n: int,
    B: int | None = None,
    semilla: int = 0,
    t_max: int = 20,
    c_max: int = 10,
    fraccion_presupuesto: float = 0.5,
) -> InstanciaMochila:
    """Genera una cadena de ``n`` etapas.

    t_i ~ U[1, t_max], c_i ~ U[1, c_max], d_i ~ U[0, t_i].
    Si ``B`` es None se fija en ``fraccion_presupuesto * sum(c)`` (tamaño
    "interesante": ni se acelera todo ni nada). Si se da ``B``, se usa tal cual,
    lo que permite variar B con n fijo en los experimentos.
    """
    rng = random.Random(semilla)
    t = tuple(rng.randint(1, t_max) for _ in range(n))
    c = tuple(rng.randint(1, c_max) for _ in range(n))
    d = tuple(rng.randint(0, ti) for ti in t)
    if B is None:
        B = int(fraccion_presupuesto * sum(c))
    return InstanciaMochila(t=t, c=c, d=d, B=B)


def generar_set_cover(
    n: int,
    r: int,
    semilla: int = 0,
    prob: float = 0.3,
    a_max: int = 1,
    w_max: int = 5,
) -> InstanciaSetCover:
    """Genera ``n`` subconjuntos de U = {0..r-1}, GARANTIZANDO factibilidad.

    Cada categoría k entra en cada S_j con probabilidad ``prob``. Después se
    repara: toda categoría que quedó sin cubrir se añade a un S_j al azar, de
    modo que la unión de todos los S_j es U (requiere n >= 1). Además se evita
    que algún S_j quede vacío añadiéndole una categoría al azar.

    ``a_max = 1`` produce la Parte 2 (costos todos 1); ``a_max > 1`` produce la
    Variante A1 con a_j ~ U[1, a_max]. Los pesos w_k ~ U[1, w_max].
    """
    if n < 1 or r < 1:
        raise ValueError("n y r deben ser >= 1")
    rng = random.Random(semilla)
    conjuntos: list[set[int]] = [
        {k for k in range(r) if rng.random() < prob} for _ in range(n)
    ]
    # Reparación de factibilidad: cada categoría debe estar en algún S_j.
    cubiertas: set[int] = set()
    for s in conjuntos:
        cubiertas |= s
    for k in range(r):
        if k not in cubiertas:
            conjuntos[rng.randrange(n)].add(k)
    # Sin conjuntos vacíos (un S_j vacío nunca sirve y ensucia las estadísticas).
    for s in conjuntos:
        if not s:
            s.add(rng.randrange(r))
    a = tuple(rng.randint(1, a_max) for _ in range(n))
    w = tuple(rng.randint(1, w_max) for _ in range(r))
    return InstanciaSetCover(
        r=r, conjuntos=tuple(frozenset(s) for s in conjuntos), a=a, w=w
    )


def generar_dag(
    n: int,
    m: int | None = None,
    B: int | None = None,
    semilla: int = 0,
    t_max: int = 20,
    c_max: int = 10,
    fraccion_presupuesto: float = 0.3,
) -> InstanciaDAG:
    """Genera un DAG de ``n`` nodos y exactamente ``m`` aristas.

    Las aristas se eligen entre los pares (u, v) con u < v (esto garantiza que
    es acíclico) y se numeran sin barajar los nodos, pero los algoritmos no
    deben depender de ello. Máximo posible: n(n-1)/2 aristas. Si ``m`` es None
    se usa 2n (o el máximo si es menor). Los tiempos/costos se generan como en
    la Mochila. Si ``B`` es None se fija en ``fraccion_presupuesto * sum(c)``.
    """
    max_m = n * (n - 1) // 2
    if m is None:
        m = min(2 * n, max_m)
    if not (0 <= m <= max_m):
        raise ValueError(f"m debe estar en [0, {max_m}] para n={n}")
    rng = random.Random(semilla)
    t = tuple(rng.randint(1, t_max) for _ in range(n))
    c = tuple(rng.randint(1, c_max) for _ in range(n))
    d = tuple(rng.randint(0, ti) for ti in t)
    pares = [(u, v) for u in range(n) for v in range(u + 1, n)]
    aristas = tuple(sorted(rng.sample(pares, m)))
    if B is None:
        B = int(fraccion_presupuesto * sum(c))
    return InstanciaDAG(t=t, c=c, d=d, aristas=aristas, B=B)


def generar_combinada(
    n: int,
    N: int,
    r: int,
    semilla: int = 0,
    fraccion_presupuesto: float = 0.6,
    lam: int | None = None,
    a_max: int = 5,
) -> InstanciaCombinada:
    """Genera una instancia de la Variante B.

    El presupuesto conjunto es ``fraccion_presupuesto * (sum(c) + sum(a))``.
    Si ``lam`` es None se usa un λ "grande" (> sum t_i), lo que activa el caso
    de cobertura obligatoria.
    """
    cadena = generar_mochila(n, semilla=semilla)
    cobertura = generar_set_cover(N, r, semilla=semilla + 1, a_max=a_max)
    B = int(fraccion_presupuesto * (sum(cadena.c) + sum(cobertura.a)))
    if lam is None:
        lam = sum(cadena.t) + 1
    return InstanciaCombinada(cadena=cadena, cobertura=cobertura, B=B, lam=lam)


def generar_set_cover_adversarial(k: int) -> InstanciaSetCover:
    """Familia clásica donde el voraz queda lejos del óptimo (r = 2^(k+1) − 2, n = k + 2).

    El universo se parte en bloques B_1..B_k con |B_i| = 2^i. Hay dos conjuntos
    "fila" R_1 y R_2 que toman cada uno la mitad de cada bloque (|R| = 2^k − 1),
    y k conjuntos "bloque" T_i = B_i. El óptimo es {R_1, R_2} (tamaño 2), pero el
    voraz elige T_k (2^k > 2^k − 1 elementos), luego T_{k−1}, …, y termina con k
    conjuntos. Razón voraz/óptimo = k/2 ≈ log₂(r)/2, que crece con r.

    Los conjuntos T_i van primero (índices 0..k−1, de mayor a menor tamaño no
    importa: los tamaños son estrictamente distintos) y R_1, R_2 al final.
    """
    if k < 1:
        raise ValueError("k debe ser >= 1")
    bloques: list[list[int]] = []
    siguiente = 0
    for i in range(1, k + 1):
        bloques.append(list(range(siguiente, siguiente + 2**i)))
        siguiente += 2**i
    r = siguiente
    fila1: set[int] = set()
    fila2: set[int] = set()
    for b in bloques:
        mitad = len(b) // 2
        fila1 |= set(b[:mitad])
        fila2 |= set(b[mitad:])
    conjuntos = tuple(frozenset(b) for b in bloques) + (frozenset(fila1), frozenset(fila2))
    return InstanciaSetCover(r=r, conjuntos=conjuntos, a=(1,) * len(conjuntos), w=(1,) * r)
