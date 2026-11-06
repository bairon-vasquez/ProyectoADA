"""Tests del lector de casos y del ejecutor por caso (resultado, tiempo y traza)."""

import csv
import json

import pytest

from core.mochila import mochila_dp
from core.set_cover import cobertura_voraz
from experimentos import generar_casos
from experimentos.casos import CasoInvalido, cargar_caso, listar_casos, parsear_caso
from experimentos.correr_casos import COLUMNAS_RESUMEN, main, resolver_caso

ETAPA0 = {
    "id": "e0",
    "parte1": {"t": [5, 8, 6, 4], "c": [3, 4, 2, 3], "d": [2, 4, 1, 2], "B": 6},
    "parte2": {"r": 5, "conjuntos": [[1, 2, 3], [2, 4], [3, 4], [4, 5], [1, 5]]},
}


# ------------------------------------------------------------------------------ lector

def test_parseo_pasa_a_base_cero():
    caso = parsear_caso(ETAPA0)
    assert caso.mochila.t == (5, 8, 6, 4) and caso.mochila.B == 6
    assert caso.cobertura.conjuntos[0] == frozenset({0, 1, 2})  # categorías 1,2,3 -> 0,1,2
    assert not caso.ponderado and caso.cobertura.a == (1,) * 5


def test_costos_activan_la_variante_a1():
    d = json.loads(json.dumps(ETAPA0))
    d["parte2"]["costos"] = [3, 1, 1, 2, 5]
    caso = parsear_caso(d)
    assert caso.ponderado and caso.cobertura.a == (3, 1, 1, 2, 5)


@pytest.mark.parametrize("mutar, texto", [
    (lambda d: d["parte1"].update(B=-1), "parte1.B"),
    (lambda d: d["parte1"].update(d=[2, 4, 1]), "misma longitud"),
    (lambda d: d["parte1"].update(d=[9, 4, 1, 2]), "no puede superar"),
    (lambda d: d["parte1"].update(c=[0, 4, 2, 3]), "parte1.c[1]"),
    (lambda d: d["parte1"].pop("B"), "sin el campo 'B'"),
    (lambda d: d["parte2"].update(conjuntos=[[1, 9]]), "fuera de 1..5"),
    (lambda d: d["parte2"].update(costos=[1, 2]), "parte2.costos"),
    (lambda d: d["parte2"].update(r=0), "parte2.r"),
    (lambda d: d["parte1"].update(t="hola"), "se esperaba una lista"),
    (lambda d: d["parte1"].update(B=2.5), "se esperaba un entero"),
])
def test_validacion_con_mensaje_claro(mutar, texto):
    d = json.loads(json.dumps(ETAPA0))
    mutar(d)
    with pytest.raises(CasoInvalido, match=texto.replace("[", r"\[").replace("]", r"\]")):
        parsear_caso(d)


def test_caso_sin_partes_y_json_malo(tmp_path):
    with pytest.raises(CasoInvalido, match="parte1' o 'parte2"):
        parsear_caso({"id": "vacio"})
    malo = tmp_path / "malo.json"
    malo.write_text("{no es json", encoding="utf-8")
    with pytest.raises(CasoInvalido, match="JSON mal formado"):
        cargar_caso(malo)
    with pytest.raises(CasoInvalido):
        listar_casos(tmp_path / "no_existe")


def test_un_caso_con_una_sola_parte():
    solo1 = parsear_caso({"parte1": ETAPA0["parte1"]})
    res = resolver_caso(solo1, repeticiones=2)
    assert "parte1" in res and "parte2" not in res


# ---------------------------------------------------------------------------- ejecutor

def test_resultado_del_ejemplo_de_la_etapa0():
    res = resolver_caso(parsear_caso(ETAPA0), repeticiones=3)
    r1, r2 = res["parte1"]["resultado"], res["parte2"]["resultado"]
    assert r1["etapas_aceleradas"] == [2, 3]  # base 1
    assert (r1["duracion_inicial"], r1["duracion_final"], r1["costo_usado"]) == (23, 18, 6)
    assert r2["interacciones_auditadas"] == [1, 4] and r2["cobertura_completa"]
    assert res["parte1"]["verificacion"]["coincide"]
    assert res["parte2"]["verificacion"]["optimo"] == 2


def test_la_traza_es_consistente_con_el_resultado():
    caso = parsear_caso(ETAPA0)
    res = resolver_caso(caso, repeticiones=2)
    t1 = res["parte1"]["traza"]
    aceleradas = [q["etapa"] for q in t1["reconstruccion"] if q["decision"] == "acelerar"]
    assert sorted(aceleradas) == res["parte1"]["resultado"]["etapas_aceleradas"]
    assert t1["tabla_dp"][4][6] == res["parte1"]["resultado"]["reduccion"]  # DP[n][B] = reducción
    assert sum(e["c"] for e in t1["etapas"] if e["acelerada"]) == res["parte1"]["resultado"]["costo_usado"]
    pasos = res["parte2"]["traza"]["pasos"]
    assert [p["interaccion"] for p in pasos] == res["parte2"]["resultado"]["orden_de_eleccion"]
    assert pasos[-1]["categorias_pendientes"] == 0
    assert pasos[-1]["costo_acumulado"] == res["parte2"]["resultado"]["costo_total"]


def test_el_ejecutor_no_cambia_el_resultado_de_core():
    caso = parsear_caso(ETAPA0)
    res = resolver_caso(caso, repeticiones=2)
    sol = mochila_dp(caso.mochila)
    assert res["parte1"]["resultado"]["etapas_aceleradas"] == [i + 1 for i in sol.etapas]
    assert res["parte2"]["resultado"]["cantidad"] == cobertura_voraz(caso.cobertura).tamano


def test_tiempo_positivo_y_repeticiones():
    res = resolver_caso(parsear_caso(ETAPA0), repeticiones=5)
    for parte in ("parte1", "parte2"):
        assert res[parte]["tiempo_s"] > 0 and res[parte]["repeticiones"] == 5
        assert res[parte]["tiempo_min_s"] <= res[parte]["tiempo_s"] <= res[parte]["tiempo_max_s"]


def test_a1_traza_con_razon_y_cota():
    d = json.loads(json.dumps(ETAPA0))
    d["parte2"] = {"r": 4, "conjuntos": [[1, 2, 3, 4], [1, 2], [3, 4]], "costos": [10, 1, 1]}
    res = resolver_caso(parsear_caso(d), repeticiones=2)["parte2"]
    assert res["entrada"]["variante"] == "A1 (costos)"
    assert res["resultado"]["costo_total"] == 2 and res["verificacion"]["optimo"] == 2
    assert res["traza"]["pasos"][0]["razon_a_sobre_nuevas"] == 0.5
    assert res["verificacion"]["cumple_cota_Hd"]


def test_instancia_infactible_se_reporta_sin_romper():
    d = {"parte2": {"r": 3, "conjuntos": [[1], [2]]}}
    res = resolver_caso(parsear_caso(d), repeticiones=2)["parte2"]
    assert res["factible"] is False and "sin solución" in res["resultado"]["mensaje"]


def test_tabla_grande_se_omite_pero_queda_la_reconstruccion():
    d = {"parte1": {"t": [3] * 100, "c": [2] * 100, "d": [1] * 100, "B": 400}}
    p1 = resolver_caso(parsear_caso(d), repeticiones=2)["parte1"]
    assert "tabla_dp" not in p1["traza"] and "tabla_dp_omitida" in p1["traza"]
    assert len(p1["traza"]["reconstruccion"]) == 100
    assert "omitida" in p1["verificacion"]  # n = 100 > 16: sin fuerza bruta


# ---------------------------------------------------------------- archivos de salida

def test_casos_de_ejemplo_y_salidas(tmp_path):
    casos, salida = tmp_path / "casos", tmp_path / "salida"
    generar_casos.main(casos)
    assert len(list(casos.glob("*.json"))) == 5
    resultados = main(casos, salida, repeticiones=2)
    assert len(resultados) == 5
    for r in resultados:
        assert (salida / f"{r['id']}.json").exists() and (salida / f"{r['id']}_traza.md").exists()
        json.loads((salida / f"{r['id']}.json").read_text(encoding="utf-8"))  # JSON válido
    with open(salida / "resumen_casos.csv", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    assert list(filas[0].keys()) == COLUMNAS_RESUMEN and len(filas) == 5
    assert all(f["verif_parte1"] in ("ok", "omitida") for f in filas)  # nunca "FALLA"
    md = (salida / "caso_01_etapa0_traza.md").read_text(encoding="utf-8")
    assert "Etapas aceleradas: {2, 3}" in md and "Elecciones del voraz" in md


def test_los_casos_del_repositorio_son_validos_y_reproducibles(tmp_path):
    """Los JSON versionados en casos/ coinciden con lo que genera el generador (semilla fija)."""
    generar_casos.main(tmp_path)
    for archivo in sorted(tmp_path.glob("*.json")):
        versionado = generar_casos.CASOS / archivo.name
        assert versionado.exists(), archivo.name
        assert json.loads(versionado.read_text(encoding="utf-8")) == json.loads(archivo.read_text(encoding="utf-8"))
