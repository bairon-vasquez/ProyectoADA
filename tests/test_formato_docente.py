"""Tests del exacto por máscaras (núcleo) y del lector/ejecutor del formato del docente (G3)."""

import copy
import json
from itertools import combinations
from pathlib import Path

import pytest

from core.combinado import combinado_cobertura_obligatoria, combinado_cobertura_obligatoria_mascaras
from core.generadores import generar_combinada, generar_set_cover
from core.instancias import InstanciaSetCover
from core.set_cover import cobertura_exacta_mascaras, cobertura_exacta_ponderada, cobertura_voraz_ponderada
from experimentos.casos import CasoInvalido, cargar_caso, parsear_caso
from experimentos.correr_casos import COLUMNAS_RESUMEN, main, resolver_caso, traza_markdown
from experimentos.medir import COLUMNAS

ARCHIVO = Path(__file__).resolve().parent.parent / "casos" / "entrada_G3_mochila_20_nodos.json"


# ------------------------------------------------- exacto por máscaras vs fuerza bruta (núcleo)

@pytest.mark.parametrize("semilla", range(25))
def test_mascaras_coincide_con_fuerza_bruta_ponderada(semilla):
    inst = generar_set_cover(n=4 + semilla % 9, r=3 + semilla % 6, semilla=semilla, a_max=6)
    mascaras = cobertura_exacta_mascaras(inst)
    bruta = cobertura_exacta_ponderada(inst)
    assert mascaras is not None and bruta is not None
    assert mascaras.costo == bruta.costo
    union = frozenset().union(*(inst.conjuntos[j] for j in mascaras.indices))
    assert union == frozenset(range(inst.r))
    assert sum(inst.a[j] for j in mascaras.indices) == mascaras.costo


def _fuerza_bruta_un_por_grupo(inst, grupos):
    mejor = None
    universo = frozenset(range(inst.r))
    for k in range(inst.n + 1):
        for sel in combinations(range(inst.n), k):
            gs = [grupos[j] for j in sel]
            if len(set(gs)) != len(gs):
                continue
            if frozenset().union(*(inst.conjuntos[j] for j in sel)) == universo:
                c = sum(inst.a[j] for j in sel)
                mejor = c if mejor is None else min(mejor, c)
    return mejor


@pytest.mark.parametrize("semilla", range(25))
def test_mascaras_respeta_una_opcion_por_grupo(semilla):
    inst = generar_set_cover(n=4 + semilla % 8, r=3 + semilla % 5, semilla=100 + semilla, a_max=6)
    grupos = tuple(j // 2 for j in range(inst.n))  # pares de opciones del mismo grupo
    sol = cobertura_exacta_mascaras(inst, grupos)
    esperado = _fuerza_bruta_un_por_grupo(inst, grupos)
    assert (sol.costo if sol else None) == esperado
    if sol:
        assert len({grupos[j] for j in sol.indices}) == len(sol.indices)  # a lo sumo una por grupo


def test_mascaras_infactible_devuelve_none():
    inst = InstanciaSetCover(r=3, conjuntos=(frozenset({0}), frozenset({1})), a=(1, 1), w=(1, 1, 1))
    assert cobertura_exacta_mascaras(inst) is None


# --------------------------------------------------------------- lector del formato del docente

@pytest.fixture(scope="module")
def datos():
    return json.loads(ARCHIVO.read_text(encoding="utf-8"))


def test_el_archivo_del_docente_se_convierte_a_las_instancias(datos):
    caso = parsear_caso(datos, "entrada_G3")
    m, cob = caso.mochila, caso.cobertura
    assert (m.n, m.B) == (20, 72) and m.t[0] == 18 and m.c[0] == 7 and m.d[0] == 5
    assert caso.presupuesto_conjunto == 100 and caso.ponderado
    assert cob.r == 12 and cob.n == 35  # 35 variaciones de auditoría en total
    assert cob.w[0] == 4 and cob.w[1] == 5  # importancia de R01 y R02
    assert caso.nombres_etapas[:2] == ("E01", "E02") and caso.nombres_interacciones[0] == "E01 parcial"
    # E01 parcial = {R01, R02} -> categorías 0 y 1; cuesta 3
    assert cob.conjuntos[0] == frozenset({0, 1}) and cob.a[0] == 3
    assert caso.grupo_interaccion[0] == 0 and caso.grupo_interaccion[2] == 1  # E01 tiene 2 variaciones


def test_resultado_del_caso_del_docente():
    res = resolver_caso(cargar_caso(ARCHIVO), repeticiones=2)
    p1, p2, vb = res["parte1"], res["parte2"], res["variante_b"]
    assert p1["resultado"]["etapas_aceleradas_nombres"] == ["E02", "E03", "E04", "E06", "E08", "E12"]
    assert (p1["resultado"]["reduccion"], p1["resultado"]["duracion_final"]) == (55, 446)
    assert p1["verificacion"]["coincide"]  # n = 20 <= 20: contrastada con la fuerza bruta
    assert p2["resultado"]["cobertura_completa"] and p2["resultado"]["costo_total"] == 25
    assert p2["resultado"]["una_variacion_por_etapa"]["cumple"]
    assert p2["verificacion"]["optimo"] == 24 and p2["verificacion"]["cumple_cota_Hd"]
    assert vb["exacta"]["costo_auditoria"] == 24 and vb["voraz"]["costo_auditoria"] == 25
    assert vb["exacta"]["duracion_final"] <= vb["voraz"]["duracion_final"]  # el exacto nunca pierde
    assert vb["comparacion"]["tiempo_perdido_por_exceso_de_auditoria"] >= 0
    assert vb["exacta"]["costo_total"] <= 100 and vb["voraz"]["costo_total"] <= 100


def test_salida_con_ids_originales(tmp_path):
    res = main(ARCHIVO, tmp_path, repeticiones=2)[0]
    md = (tmp_path / f"{res['id']}_traza.md").read_text(encoding="utf-8")
    assert "E02" in md and "R01" in md and "E01 parcial" in md and "Variante B" in md
    assert md == traza_markdown(res)
    fila = (tmp_path / "resumen_casos.csv").read_text(encoding="utf-8").splitlines()
    assert fila[0].split(",") == COLUMNAS_RESUMEN
    assert "E02 E03 E04 E06 E08 E12" in fila[1]


@pytest.mark.parametrize("mutar, texto", [
    (lambda d: d["etapas"][0].update(id="E02"), "etapa repetida"),
    (lambda d: d["parametros"].update(numero_etapas=19), "numero_etapas"),
    (lambda d: d["parametros"].update(numero_categorias_riesgo=11), "numero_categorias_riesgo"),
    (lambda d: d["etapas"][0].update(reduccion_tiempo_si_acelera=99), "no puede superar"),
    (lambda d: d["etapas"][0].update(costo_aceleracion=0), "costo_aceleracion"),
    (lambda d: d["etapas"][0]["variaciones_auditoria"][0].update(riesgos_cubiertos=["R99"]), "riesgo inexistente"),
    (lambda d: d["etapas"][0]["variaciones_auditoria"][0].update(costo=0), "costo"),
    (lambda d: d["etapas"][0]["variaciones_auditoria"][0].update(id="completa"), "variación repetida"),
    (lambda d: d["flujo"].append({"origen": "E20", "destino": "E01"}), "ciclo"),
    (lambda d: d["flujo"].append({"origen": "E01", "destino": "E02"}), "arista repetida"),
    (lambda d: d["flujo"].append({"origen": "E03", "destino": "E03"}), "sí misma"),
    (lambda d: d["flujo"].__setitem__(0, {"origen": "E01", "destino": "E99"}), "etapa inexistente"),
    (lambda d: d["parametros"].pop("presupuesto_aceleracion_B"), "presupuesto_aceleracion_B"),
])
def test_validacion_del_formato_del_docente(datos, mutar, texto):
    d = copy.deepcopy(datos)
    mutar(d)
    with pytest.raises(CasoInvalido, match=texto):
        parsear_caso(d, "x")


def test_flujo_en_cadena_corre_la_variante_c_y_coincide_con_la_mochila():
    res = resolver_caso(cargar_caso(ARCHIVO), repeticiones=2)
    vc = res["variante_c"]
    assert vc["entrada"]["es_cadena"]
    assert vc["entrada"]["m"] == 19
    assert vc["resultado"]["duracion_inicial"] == 501
    assert vc["resultado"]["duracion_final"] == res["parte1"]["resultado"]["duracion_final"] == 446
    assert vc["verificacion"]["coincide"]


DIAMANTE = {  # E1 → {E2, E3} → E4: dos rutas paralelas, el flujo NO es una cadena
    "parametros": {"presupuesto_aceleracion_B": 6},
    "flujo": [{"origen": "E1", "destino": "E2"}, {"origen": "E1", "destino": "E3"},
              {"origen": "E2", "destino": "E4"}, {"origen": "E3", "destino": "E4"}],
    "categorias_riesgo": [{"id": "R1", "importancia": 1}],
    "etapas": [
        {"id": "E1", "duracion_normal": 2, "costo_aceleracion": 1, "reduccion_tiempo_si_acelera": 1,
         "variaciones_auditoria": [{"id": "completa", "costo": 2, "riesgos_cubiertos": ["R1"]}]},
        {"id": "E2", "duracion_normal": 5, "costo_aceleracion": 3, "reduccion_tiempo_si_acelera": 3},
        {"id": "E3", "duracion_normal": 4, "costo_aceleracion": 3, "reduccion_tiempo_si_acelera": 3},
        {"id": "E4", "duracion_normal": 2, "costo_aceleracion": 1, "reduccion_tiempo_si_acelera": 1},
    ],
}


def test_flujo_con_ramas_omite_la_mochila_y_resuelve_la_variante_c(tmp_path):
    caso = parsear_caso(DIAMANTE, "diamante")
    assert not caso.es_cadena
    res = resolver_caso(caso, repeticiones=2)
    assert "omitida" in res["parte1"]
    assert "variante_b" not in res  # la Variante B parte de la Mochila (cadena)
    vc = res["variante_c"]
    assert vc["resultado"]["duracion_inicial"] == 9  # E1(2) + E2(5) + E4(2)
    assert vc["verificacion"]["metodo"].startswith("exacto")
    assert vc["resultado"]["duracion_final"] >= vc["verificacion"]["duracion_optima"]
    assert "Omitida" in traza_markdown(res)
    caso_json = tmp_path / "diamante.json"
    caso_json.write_text(json.dumps(DIAMANTE), encoding="utf-8")
    main(caso_json, tmp_path / "salida", repeticiones=2)  # no debe fallar con la Parte 1 omitida
    assert (tmp_path / "salida" / "diamante_tiempos.csv").exists()


def test_salida_incluye_tabla_dp_y_tiempos_por_repeticion(tmp_path):
    main(ARCHIVO, tmp_path, repeticiones=3)
    dp = (tmp_path / "entrada_G3_mochila_20_nodos_dp.csv").read_text(encoding="utf-8").splitlines()
    assert len(dp) == 1 + 21  # encabezado + una fila por i = 0..20
    assert len(dp[1].split(",")) == 73 + 1  # i y las columnas b = 0..72
    tiempos = (tmp_path / "entrada_G3_mochila_20_nodos_tiempos.csv").read_text(encoding="utf-8").splitlines()
    assert tiempos[0].split(",") == COLUMNAS
    assert len(tiempos) == 1 + 3 * 4  # 3 repeticiones × (Mochila, voraz, DAG, Variante B exacta)


def test_reconstruccion_muestra_las_dos_opciones_de_la_recurrencia():
    p1 = resolver_caso(cargar_caso(ARCHIVO), repeticiones=2)["parte1"]
    for q in p1["traza"]["reconstruccion"]:
        mejor = max(q["dp_i_1_b"], q["dp_acelerando_i"] if q["dp_acelerando_i"] is not None else -1)
        assert q["dp_i_b"] == mejor
        assert (q["decision"] == "acelerar") == (q["dp_i_b"] != q["dp_i_1_b"])


@pytest.mark.parametrize("semilla", range(15))
def test_variante_b_por_mascaras_coincide_con_la_enumeracion(semilla):
    inst = generar_combinada(n=6, N=7, r=5, semilla=semilla)
    por_mascaras = combinado_cobertura_obligatoria_mascaras(inst)
    por_enumeracion = combinado_cobertura_obligatoria(inst)
    assert (por_mascaras is None) == (por_enumeracion is None)
    if por_mascaras is not None and por_enumeracion is not None:
        assert por_mascaras.objetivo == por_enumeracion.objetivo


def test_sin_variante_b_si_no_hay_presupuesto_conjunto(datos):
    d = copy.deepcopy(datos)
    del d["parametros"]["presupuesto_conjunto_aceleracion_y_auditoria"]
    res = resolver_caso(parsear_caso(d, "x"), repeticiones=2)
    assert "variante_b" not in res and "parte1" in res and "parte2" in res


def test_voraz_que_repite_etapa_se_repara():
    """Si el voraz elige 'parcial' y 'completa' de la misma etapa, se queda con la que cubre la unión."""
    d = {
        "parametros": {"presupuesto_aceleracion_B": 5},
        "categorias_riesgo": [{"id": "R1", "importancia": 1}, {"id": "R2", "importancia": 1},
                              {"id": "R3", "importancia": 1}],
        "etapas": [
            {"id": "E1", "duracion_normal": 5, "costo_aceleracion": 1, "reduccion_tiempo_si_acelera": 1,
             "variaciones_auditoria": [
                 {"id": "parcial", "costo": 1, "riesgos_cubiertos": ["R1"]},
                 {"id": "completa", "costo": 3, "riesgos_cubiertos": ["R1", "R2", "R3"]}]},
        ],
    }
    caso = parsear_caso(d, "rep")
    sol = cobertura_voraz_ponderada(caso.cobertura)
    assert sol is not None and sol.tamano == 2  # el voraz ignora la regla de grupos: elige las dos variaciones
    assert sol.costo == 4
    res = resolver_caso(caso, repeticiones=2)["parte2"]["resultado"]
    u = res["una_variacion_por_etapa"]
    assert u["etapas_repetidas"] == [1]
    assert u["cumple"]
    assert u["costo_reparado"] == 3  # se queda solo con E1 completa
    assert u["interacciones_reparadas"] == [2]
