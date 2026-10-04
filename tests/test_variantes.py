"""Tests de las Variantes A1 (ponderada), B (combinada) y C (DAG)."""

import pytest

from core.combinado import (
    combinado_cobertura_obligatoria,
    combinado_exacto,
    combinado_heuristica,
    evaluar_combinada,
)
from core.dag import dag_exacto, dag_heuristica, preparar_dag, ruta_critica
from core.generadores import (
    generar_combinada,
    generar_dag,
    generar_mochila,
    generar_set_cover,
)
from core.instancias import InstanciaCombinada, InstanciaDAG, InstanciaMochila, InstanciaSetCover
from core.mochila import mochila_dp
from core.set_cover import (
    cobertura_exacta_ponderada,
    cobertura_voraz_ponderada,
    numero_armonico,
)

# ---------------------------------------------------------------- A1 ponderada


def _cubre(inst, indices):
    union = set()
    for j in indices:
        union |= inst.conjuntos[j]
    return len(union) == inst.r


def test_a1_el_costo_cambia_la_respuesta():
    # Un conjunto grande y caro vs. dos pequeños y baratos.
    inst = InstanciaSetCover(
        r=4,
        conjuntos=(frozenset({0, 1, 2, 3}), frozenset({0, 1}), frozenset({2, 3})),
        a=(10, 1, 1),
        w=(1, 1, 1, 1),
    )
    voraz = cobertura_voraz_ponderada(inst)
    assert sorted(voraz.indices) == [1, 2]
    assert voraz.costo == 2
    assert cobertura_exacta_ponderada(inst).costo == 2


def test_a1_infactible():
    inst = InstanciaSetCover(r=3, conjuntos=(frozenset({0}), frozenset({1})), a=(1, 1), w=(1, 1, 1))
    assert cobertura_voraz_ponderada(inst) is None
    assert cobertura_exacta_ponderada(inst) is None


@pytest.mark.parametrize("semilla", range(40))
def test_a1_voraz_respeta_cota_hd(semilla):
    n = 2 + semilla % 12  # n en [2, 13]
    r = 3 + semilla % 9
    inst = generar_set_cover(n, r, semilla=semilla, prob=0.2 + 0.05 * (semilla % 5), a_max=9)
    exacto = cobertura_exacta_ponderada(inst)
    voraz = cobertura_voraz_ponderada(inst)
    assert _cubre(inst, exacto.indices) and _cubre(inst, voraz.indices)
    d = max(len(s) for s in inst.conjuntos)
    assert exacto.costo <= voraz.costo <= numero_armonico(d) * exacto.costo + 1e-9


# ------------------------------------------------------------------- C: DAG

# Ejemplo de la Etapa 0: A=0, B=1, C=2, D=3. Sin acelerar: A-B-D = 10. Optimo = 7.
DAG_EJEMPLO = InstanciaDAG(
    t=(3, 5, 4, 2), c=(4, 2, 2, 3), d=(1, 3, 2, 1),
    aristas=((0, 1), (0, 2), (1, 3), (2, 3)), B=4,
)


def test_dag_ejemplo_ruta_inicial():
    r = ruta_critica(DAG_EJEMPLO, [0, 0, 0, 0])
    assert r.longitud == 10 and r.camino == (0, 1, 3)


def test_dag_ejemplo_acelerar_solo_b_no_basta():
    # Acelerar solo B: la ruta A-B-D baja a 7 pero A-C-D (9) pasa a ser la critica.
    r = ruta_critica(DAG_EJEMPLO, [0, 1, 0, 0])
    assert r.longitud == 9 and r.camino == (0, 2, 3)


def test_dag_ejemplo_exacto_es_7():
    sol = dag_exacto(DAG_EJEMPLO)
    assert sol.duracion == 7
    assert sol.aceleradas == (1, 2)
    assert sol.costo == 4
    assert sol.duracion_inicial == 10


def test_dag_ejemplo_heuristica_es_7():
    sol = dag_heuristica(DAG_EJEMPLO)
    assert sol.duracion == 7
    assert sol.aceleradas == (1, 2)
    assert sol.pasos == ((1, 9), (2, 7))  # B primero (L pasa a 9), luego C (L pasa a 7)


def _longitud_por_enumeracion(inst, x):
    """Referencia independiente: DFS que enumera todos los caminos."""
    suc = {i: [] for i in range(inst.n)}
    for u, v in inst.aristas:
        suc[u].append(v)
    tau = [inst.t[i] - inst.d[i] * x[i] for i in range(inst.n)]

    def dfs(u):
        return tau[u] + max((dfs(v) for v in suc[u]), default=0)

    return max((dfs(u) for u in range(inst.n)), default=0)


@pytest.mark.parametrize("semilla", range(30))
def test_ruta_critica_contra_enumeracion_de_caminos(semilla):
    n = 2 + semilla % 9
    m = min(n * (n - 1) // 2, n + semilla % 7)
    inst = generar_dag(n, m, semilla=semilla)
    x = [(semilla >> i) & 1 for i in range(n)]
    rc = ruta_critica(inst, x)
    assert rc.longitud == _longitud_por_enumeracion(inst, x)
    # el camino devuelto es realmente una ruta con esa longitud
    aristas = set(inst.aristas)
    assert all((u, v) in aristas for u, v in zip(rc.camino, rc.camino[1:]))
    assert sum(inst.t[i] - inst.d[i] * x[i] for i in rc.camino) == rc.longitud


def test_orden_topologico_valido_y_ciclo():
    inst = generar_dag(10, 20, semilla=3)
    orden = preparar_dag(inst.n, inst.aristas).orden
    pos = {v: k for k, v in enumerate(orden)}
    assert sorted(orden) == list(range(10))
    assert all(pos[u] < pos[v] for u, v in inst.aristas)
    with pytest.raises(ValueError):
        preparar_dag(2, ((0, 1), (1, 0)))


def test_orden_topologico_sin_suponer_indices_ordenados():
    # arista 2->0: el orden de indices NO es topologico.
    assert preparar_dag(3, ((2, 0), (0, 1))).orden == (2, 0, 1)


@pytest.mark.parametrize("semilla", range(30))
def test_dag_cadena_equivale_a_mochila(semilla):
    n = 1 + semilla % 10
    mochila = generar_mochila(n, semilla=semilla)
    cadena = InstanciaDAG(
        t=mochila.t, c=mochila.c, d=mochila.d,
        aristas=tuple((i, i + 1) for i in range(n - 1)), B=mochila.B,
    )
    assert dag_exacto(cadena).duracion == mochila_dp(mochila).duracion


@pytest.mark.parametrize("semilla", range(30))
def test_dag_heuristica_factible_y_no_mejor_que_exacto(semilla):
    n = 3 + semilla % 9  # n en [3, 11]
    m = min(n * (n - 1) // 2, n + semilla % 8)
    inst = generar_dag(n, m, semilla=semilla, fraccion_presupuesto=0.2 + 0.1 * (semilla % 4))
    exacto = dag_exacto(inst)
    heur = dag_heuristica(inst)
    assert heur.costo <= inst.B and exacto.costo <= inst.B
    assert exacto.duracion <= heur.duracion <= heur.duracion_inicial
    assert exacto.duracion <= exacto.duracion_inicial


# --------------------------------------------------------------- B: combinado

# 2 etapas, 3 interacciones. Cubrir todo cuesta 3 (S_0 + S_1); sobran B-3 = 2 para acelerar.
COMB = InstanciaCombinada(
    cadena=InstanciaMochila(t=(6, 6), c=(2, 5), d=(4, 5), B=0),
    cobertura=InstanciaSetCover(
        r=3,
        conjuntos=(frozenset({0, 1}), frozenset({2}), frozenset({0, 1, 2})),
        a=(1, 2, 7),
        w=(2, 2, 2),
    ),
    B=5,
    lam=100,
)


def test_b_obligatoria_ejemplo():
    sol = combinado_cobertura_obligatoria(COMB)
    assert sol.interacciones == (0, 1)
    assert sol.etapas == (0,)  # con 2 de presupuesto solo cabe la etapa 0
    assert sol.costo == 5
    assert sol.duracion == 12 - 4
    assert sol.penalizacion == 0
    assert sol.objetivo == 8


def test_b_obligatoria_infactible_si_cobertura_no_cabe():
    inst = InstanciaCombinada(cadena=COMB.cadena, cobertura=COMB.cobertura, B=2, lam=100)
    assert combinado_cobertura_obligatoria(inst) is None


@pytest.mark.parametrize("semilla", range(25))
def test_b_obligatoria_exacta_coincide_con_exacto_con_lambda_grande(semilla):
    n, N, r = 2 + semilla % 8, 2 + semilla % 8, 3 + semilla % 6
    inst = generar_combinada(n, N, r, semilla=semilla, fraccion_presupuesto=0.5 + 0.1 * (semilla % 5))
    oblig = combinado_cobertura_obligatoria(inst, exacta=True)
    if oblig is None:
        return  # la cobertura minima no cabe en B
    ref = combinado_exacto(inst)
    assert oblig.costo <= inst.B
    assert oblig.penalizacion == 0
    # lam > suma de t: con cobertura posible, el optimo la cubre toda y coincide con la separacion.
    assert oblig.objetivo == ref.objetivo


@pytest.mark.parametrize("semilla", range(30))
def test_b_heuristica_factible_y_acotada(semilla):
    n, N, r = 2 + semilla % 8, 2 + semilla % 9, 3 + semilla % 6
    lam = [0, 1, 2, 5, 20, 1000][semilla % 6]
    base = generar_combinada(n, N, r, semilla=semilla, fraccion_presupuesto=0.3 + 0.1 * (semilla % 5))
    inst = InstanciaCombinada(cadena=base.cadena, cobertura=base.cobertura, B=base.B, lam=lam)
    heur = combinado_heuristica(inst)
    ref = combinado_exacto(inst)
    solo_mochila = mochila_dp(InstanciaMochila(inst.cadena.t, inst.cadena.c, inst.cadena.d, inst.B))
    sin_auditar = evaluar_combinada(inst, solo_mochila.etapas, ())
    assert heur.costo <= inst.B and ref.costo <= inst.B
    assert ref.objetivo <= heur.objetivo <= sin_auditar.objetivo


def test_b_sin_interacciones_utiles_se_reduce_a_mochila():
    ch = generar_mochila(6, semilla=2)
    cob = InstanciaSetCover(r=1, conjuntos=(frozenset({0}),), a=(10**6,), w=(1,))
    inst = InstanciaCombinada(cadena=ch, cobertura=cob, B=ch.B, lam=3)
    assert combinado_heuristica(inst).duracion == mochila_dp(ch).duracion
    assert combinado_exacto(inst).duracion == mochila_dp(ch).duracion
