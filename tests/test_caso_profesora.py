"""Tests del lector de casos JSON, de la cobertura exacta por DP de máscaras y del runner."""

from __future__ import annotations

import random
from pathlib import Path

from core.combinado import combinado_cobertura_obligatoria, combinado_cobertura_obligatoria_dp
from core.generadores import generar_combinada, generar_set_cover
from core.mochila import mochila_dp, mochila_fuerza_bruta
from core.set_cover import cobertura_exacta_dp, cobertura_exacta_ponderada
from experimentos.cargar_caso import cargar_caso
from experimentos.correr_caso import main

CASO = Path(__file__).parent.parent / "casos" / "entrada_G3_mochila_20_nodos.json"


def test_cobertura_dp_igual_a_enumeracion() -> None:
    """El DP de máscaras da el mismo costo mínimo que la enumeración 2^N."""
    for semilla in range(30):
        rng = random.Random(semilla)
        inst = generar_set_cover(n=rng.randint(3, 11), r=rng.randint(2, 7), semilla=semilla, a_max=5)
        a = cobertura_exacta_dp(inst)
        b = cobertura_exacta_ponderada(inst)
        assert a is not None and b is not None
        assert a.costo == b.costo
        cubiertas = set().union(*(inst.conjuntos[j] for j in a.indices))
        assert len(cubiertas) == inst.r
        assert sum(inst.a[j] for j in a.indices) == a.costo


def test_combinado_oblig_dp_igual_a_enumeracion() -> None:
    for semilla in range(15):
        inst = generar_combinada(n=6, N=7, r=5, semilla=semilla)
        x, y = combinado_cobertura_obligatoria_dp(inst), combinado_cobertura_obligatoria(inst)
        assert (x is None) == (y is None)
        if x is not None and y is not None:
            assert x.objetivo == y.objetivo


def test_carga_del_caso_20_nodos() -> None:
    caso = cargar_caso(CASO)
    assert caso.mochila.n == 20 and caso.mochila.B == 72 and caso.B_conjunto == 100
    assert caso.cobertura.r == 12 and caso.cobertura.n == 35 and caso.cobertura.es_factible()
    assert caso.es_cadena and caso.dag.m == 19
    assert caso.etiquetas_interacciones[0] == "E01-parcial"


def test_mochila_del_caso_20_nodos() -> None:
    """Valor esperado verificado con fuerza bruta (2^20): duración 446, etapas E02..E12."""
    caso = cargar_caso(CASO)
    sol = mochila_dp(caso.mochila)
    assert sol.duracion == 446 and sol.costo == 72
    assert [caso.ids_etapas[i] for i in sol.etapas] == ["E02", "E03", "E04", "E06", "E08", "E12"]
    assert cobertura_exacta_dp(caso.cobertura).costo == 24  # type: ignore[union-attr]


def test_mochila_dp_caso_recortado_vs_fuerza_bruta() -> None:
    """Primeras 12 etapas del caso: la DP coincide con fuerza bruta."""
    from core.instancias import InstanciaMochila

    m = cargar_caso(CASO).mochila
    pe = InstanciaMochila(t=m.t[:12], c=m.c[:12], d=m.d[:12], B=m.B)
    assert mochila_dp(pe).duracion == mochila_fuerza_bruta(pe).duracion


def test_runner_escribe_evidencia(tmp_path: Path) -> None:
    (ruta,) = main([str(CASO), "--repeticiones", "2", "--salida", str(tmp_path)])
    texto = ruta.read_text(encoding="utf-8")
    assert "ACELERA" in texto and "446" in texto and "SIN CUBRIR" not in texto
    assert (tmp_path / "entrada_G3_mochila_20_nodos_dp.csv").exists()
    assert (tmp_path / "entrada_G3_mochila_20_nodos_tiempos.csv").exists()
