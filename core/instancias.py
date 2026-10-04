"""Dataclasses de cada tipo de instancia del Proyecto Ruta.

Convenciones (ver Etapa 0):
- Todos los valores numéricos son enteros no negativos.
- Los índices de etapas, interacciones y categorías son 0-based en el código
  (en los documentos se usan 1-based; el código resta 1).
- Los conjuntos S_j se guardan como ``frozenset[int]`` de categorías en [0, r).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstanciaMochila:
    """Parte 1: cadena de n etapas en serie con presupuesto B.

    La etapa i dura ``t[i]``, acelerarla cuesta ``c[i]`` y reduce ``d[i]``
    (0 <= d[i] <= t[i]). Tamaño de la entrada: n y B.
    """

    t: tuple[int, ...]
    c: tuple[int, ...]
    d: tuple[int, ...]
    B: int

    @property
    def n(self) -> int:
        return len(self.t)

    def __post_init__(self) -> None:
        if not (len(self.t) == len(self.c) == len(self.d)):
            raise ValueError("t, c y d deben tener la misma longitud")
        if self.B < 0:
            raise ValueError("B debe ser >= 0")
        for ti, ci, di in zip(self.t, self.c, self.d):
            if ti < 0 or ci < 1 or not (0 <= di <= ti):
                raise ValueError("se exige t>=0, c>=1 y 0<=d<=t")


@dataclass(frozen=True)
class InstanciaSetCover:
    """Parte 2 (y Variante A1 si ``a`` no es todo unos): cobertura de U = {0..r-1}.

    ``conjuntos[j]`` es S_j. ``a[j]`` es el costo de auditar la interacción j
    (a_j >= 1); en la Parte 2 todos valen 1. ``w[k]`` es el peso de la
    categoría k (solo se usa en la Variante B).
    """

    r: int
    conjuntos: tuple[frozenset[int], ...]
    a: tuple[int, ...]
    w: tuple[int, ...]

    @property
    def n(self) -> int:
        return len(self.conjuntos)

    def es_factible(self) -> bool:
        """True si la unión de todos los S_j es U (O(sum |S_j|))."""
        cubiertas: set[int] = set()
        for s in self.conjuntos:
            cubiertas |= s
        return len(cubiertas) == self.r

    def __post_init__(self) -> None:
        if len(self.a) != len(self.conjuntos):
            raise ValueError("a debe tener un costo por conjunto")
        if len(self.w) != self.r:
            raise ValueError("w debe tener un peso por categoría")
        if any(x < 1 for x in self.a) or any(x < 1 for x in self.w):
            raise ValueError("costos y pesos deben ser >= 1")
        for s in self.conjuntos:
            if any(not (0 <= k < self.r) for k in s):
                raise ValueError("categoría fuera de U")


@dataclass(frozen=True)
class InstanciaDAG:
    """Variante C: DAG de n etapas con m dependencias y presupuesto B.

    Los nodos 0..n-1 ya vienen en un orden topológico válido de generación,
    pero los algoritmos NO deben suponerlo: calculan su propio orden. La
    fuente y el sumidero ficticios (duración 0) los añade el algoritmo.
    ``aristas`` contiene pares (u, v): v no empieza hasta que termine u.
    """

    t: tuple[int, ...]
    c: tuple[int, ...]
    d: tuple[int, ...]
    aristas: tuple[tuple[int, int], ...]
    B: int

    @property
    def n(self) -> int:
        return len(self.t)

    @property
    def m(self) -> int:
        return len(self.aristas)

    def __post_init__(self) -> None:
        if not (len(self.t) == len(self.c) == len(self.d)):
            raise ValueError("t, c y d deben tener la misma longitud")
        if self.B < 0:
            raise ValueError("B debe ser >= 0")
        for u, v in self.aristas:
            if not (0 <= u < self.n and 0 <= v < self.n) or u == v:
                raise ValueError("arista inválida")


@dataclass(frozen=True)
class InstanciaCombinada:
    """Variante B: Mochila (etapas) + Set Cover (interacciones) con un solo B.

    Aquí ``cadena.B`` no se usa: el presupuesto conjunto es ``B``.
    ``lam`` es el factor de penalización λ por peso de riesgo sin cubrir.
    Tamaño de la entrada: n = cadena.n, N = cobertura.n, r y B.
    """

    cadena: InstanciaMochila
    cobertura: InstanciaSetCover
    B: int
    lam: int

    def __post_init__(self) -> None:
        if self.B < 0 or self.lam < 0:
            raise ValueError("B y lam deben ser >= 0")
