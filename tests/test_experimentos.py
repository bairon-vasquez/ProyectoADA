"""Pruebas de humo de la capa de experimentos y de la familia adversarial."""

import csv

from core.generadores import generar_set_cover_adversarial
from core.set_cover import cobertura_exacta, cobertura_voraz, numero_armonico
from experimentos import correr_combinado, correr_dag, correr_mochila, correr_razones, correr_set_cover
from experimentos.medir import COLUMNAS, mediana, medir


def test_medir_devuelve_tiempos_positivos_y_resultado():
    tiempos, res = medir(lambda: sum(range(1000)), repeticiones=4)
    assert len(tiempos) == 4 and all(t > 0 for t in tiempos)
    assert res == sum(range(1000))
    assert mediana([3.0, 1.0, 2.0]) == 2.0


def _leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_modo_rapido_genera_csv_con_columnas_y_al_menos_5_tamanos(tmp_path):
    for modulo, archivo in (
        (correr_mochila, "mochila.csv"),
        (correr_set_cover, "set_cover.csv"),
        (correr_dag, "dag.csv"),
        (correr_combinado, "combinado.csv"),
    ):
        ruta = modulo.main(rapido=True, carpeta=tmp_path)
        assert ruta.name == archivo
        filas = _leer(ruta)
        assert list(filas[0].keys()) == COLUMNAS
        # al menos 5 tamaños distintos por (algoritmo, barrido)
        grupos: dict[tuple, set] = {}
        for f in filas:
            clave = (f["algoritmo"], f["barrido"])
            grupos.setdefault(clave, set()).add((f["n"], f["valor_parametro"]))
            assert float(f["tiempo_s"]) >= 0
        assert all(len(v) >= 5 for v in grupos.values()), grupos


def test_razones_modo_rapido(tmp_path):
    rutas = correr_razones.main(rapido=True, carpeta=tmp_path)
    assert len(rutas) == 4
    for fila in _leer(rutas[0]):  # voraz / óptimo respeta la cota
        assert 1.0 <= float(fila["razon"]) <= float(fila["H_d"]) + 1e-9
    for ruta in rutas[2:]:  # heurística nunca mejor que el exacto
        assert all(float(f["razon"]) >= 1.0 - 1e-9 for f in _leer(ruta))


def test_familia_adversarial():
    for k in range(2, 9):
        inst = generar_set_cover_adversarial(k)
        assert inst.r == 2 ** (k + 1) - 2 and inst.n == k + 2
        assert inst.es_factible()
        assert cobertura_exacta(inst).tamano == 2
        voraz = cobertura_voraz(inst)
        assert voraz.tamano == k
        assert voraz.tamano <= numero_armonico(inst.r) * 2
