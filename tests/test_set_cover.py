"""Tests de la Parte 2: voraz y exacto de Set Cover."""

import pytest

from core.generadores import generar_set_cover
from core.instancias import InstanciaSetCover
from core.set_cover import cobertura_exacta, cobertura_voraz, numero_armonico


def _inst(r: int, conjuntos: list[set[int]]) -> InstanciaSetCover:
    return InstanciaSetCover(
        r=r,
        conjuntos=tuple(frozenset(s) for s in conjuntos),
        a=(1,) * len(conjuntos),
        w=(1,) * r,
    )


# Ejemplo de la Etapa 0 (0-based): óptimo {0, 3}, el voraz también.
EJEMPLO = _inst(5, [{0, 1, 2}, {1, 3}, {2, 3}, {3, 4}, {0, 4}])

# Trampa clásica: óptimo = {X, Y} (2); el voraz toma primero Z (4 nuevas) y termina con 3.
TRAMPA = _inst(6, [{0, 1, 3, 4}, {0, 1, 2}, {3, 4, 5}])


def _cubre(inst: InstanciaSetCover, indices) -> bool:
    union: set[int] = set()
    for j in indices:
        union |= inst.conjuntos[j]
    return len(union) == inst.r


def _optimo_por_mascaras(inst: InstanciaSetCover) -> int:
    """Referencia independiente: enumera todas las máscaras y toma la menor que cubre."""
    mejor = inst.n + 1
    for mascara in range(1 << inst.n):
        idx = [j for j in range(inst.n) if (mascara >> j) & 1]
        if len(idx) < mejor and _cubre(inst, idx):
            mejor = len(idx)
    return mejor


def test_ejemplo_etapa0():
    assert sorted(cobertura_exacta(EJEMPLO).indices) == [0, 3]
    voraz = cobertura_voraz(EJEMPLO)
    assert voraz.indices == (0, 3)
    assert voraz.pasos[0] == (0, (0, 1, 2))  # primero S_1 con 3 categorías nuevas
    assert voraz.pasos[1] == (3, (3, 4))


def test_trampa_voraz_no_es_optimo_pero_respeta_cota():
    assert cobertura_exacta(TRAMPA).tamano == 2
    voraz = cobertura_voraz(TRAMPA)
    assert voraz.tamano == 3
    assert voraz.tamano <= numero_armonico(TRAMPA.r) * 2


def test_infactible_devuelve_none():
    inst = _inst(3, [{0}, {1}])  # la categoría 2 nunca se cubre
    assert cobertura_voraz(inst) is None
    assert cobertura_exacta(inst) is None


def test_universo_vacio():
    inst = _inst(0, [])
    assert cobertura_exacta(inst).indices == ()
    assert cobertura_voraz(inst).indices == ()


def test_numero_armonico():
    assert numero_armonico(0) == 0
    assert numero_armonico(1) == 1
    assert numero_armonico(4) == pytest.approx(1 + 1 / 2 + 1 / 3 + 1 / 4)


@pytest.mark.parametrize("semilla", range(40))
def test_exacto_voraz_y_cota_en_aleatorias(semilla):
    n = 2 + semilla % 14  # n ∈ [2, 15]
    r = 3 + semilla % 10  # r ∈ [3, 12]
    inst = generar_set_cover(n, r, semilla=semilla, prob=0.15 + 0.05 * (semilla % 5))
    assert inst.es_factible()

    exacto = cobertura_exacta(inst)
    voraz = cobertura_voraz(inst)

    # El exacto cubre y es mínimo (comparado con una enumeración independiente).
    assert _cubre(inst, exacto.indices)
    if n <= 12:
        assert exacto.tamano == _optimo_por_mascaras(inst)

    # El voraz cubre, nunca mejora al óptimo y respeta |voraz| ≤ H_r · óptimo.
    assert _cubre(inst, voraz.indices)
    assert exacto.tamano <= voraz.tamano <= numero_armonico(r) * exacto.tamano

    # Cada paso del voraz cubre ≥ 1 categoría nueva y las nuevas suman r.
    assert all(len(nuevas) >= 1 for _, nuevas in voraz.pasos)
    assert sum(len(nuevas) for _, nuevas in voraz.pasos) == r
