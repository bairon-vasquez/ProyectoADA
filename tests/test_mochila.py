"""Tests de la Parte 1: DP contra fuerza bruta en instancias pequeñas aleatorias."""

import pytest

from core.generadores import generar_mochila
from core.instancias import InstanciaMochila
from core.mochila import (
    construir_tabla_dp,
    mochila_dp,
    mochila_fuerza_bruta,
)

# Ejemplo de la Etapa 0: óptimo S = {2, 3} (1-based) -> {1, 2} (0-based).
EJEMPLO = InstanciaMochila(t=(5, 8, 6, 4), c=(3, 4, 2, 3), d=(2, 4, 1, 2), B=6)


def test_ejemplo_etapa0_dp():
    sol = mochila_dp(EJEMPLO)
    assert sol.etapas == (1, 2)
    assert sol.costo == 6
    assert sol.reduccion == 5
    assert sol.duracion == 18


def test_ejemplo_etapa0_fuerza_bruta():
    assert mochila_fuerza_bruta(EJEMPLO).duracion == 18


@pytest.mark.parametrize("semilla", range(40))
def test_dp_igual_a_fuerza_bruta(semilla):
    n = 1 + semilla % 15  # n ∈ [1, 15]
    inst = generar_mochila(n, semilla=semilla, fraccion_presupuesto=0.2 + 0.1 * (semilla % 6))
    dp = mochila_dp(inst)
    fb = mochila_fuerza_bruta(inst)
    assert dp.reduccion == fb.reduccion
    assert dp.duracion == fb.duracion
    # La solución reconstruida debe ser factible y realmente alcanzar ese valor.
    assert dp.costo <= inst.B
    assert sum(inst.d[i] for i in dp.etapas) == dp.reduccion
    assert sum(inst.c[i] for i in dp.etapas) == dp.costo


def test_presupuesto_cero():
    inst = InstanciaMochila(t=(4, 5), c=(1, 2), d=(2, 3), B=0)
    assert mochila_dp(inst).etapas == ()
    assert mochila_dp(inst).duracion == 9


def test_etapa_mas_cara_que_presupuesto_se_ignora():
    inst = InstanciaMochila(t=(10, 3), c=(50, 1), d=(9, 1), B=5)
    assert mochila_dp(inst).etapas == (1,)


def test_tabla_monotona_y_dimensiones():
    tabla = construir_tabla_dp(EJEMPLO)
    assert len(tabla) == EJEMPLO.n + 1
    assert all(len(fila) == EJEMPLO.B + 1 for fila in tabla)
    assert all(v == 0 for v in tabla[0])
    for fila in tabla:  # más presupuesto nunca reduce menos
        assert all(fila[b] <= fila[b + 1] for b in range(len(fila) - 1))
    assert tabla[EJEMPLO.n][EJEMPLO.B] == 5


def test_sin_etapas():
    inst = InstanciaMochila(t=(), c=(), d=(), B=3)
    assert mochila_dp(inst).duracion == 0
    assert mochila_fuerza_bruta(inst).etapas == ()
