"""Ejecutor de casos: resultado, tiempo y traza POR CASO (Parte 1, Parte 2 y Variante A1).

Para cada caso JSON (formato en ``experimentos/casos.py``) escribe en la carpeta de salida:
  <id>.json        resultado + tiempo + traza (máquina-legible)
  <id>_traza.md    la misma traza en texto legible
y al final ``resumen_casos.csv`` con una fila por caso.

La lógica de los algoritmos NO se edita ni se envuelve: se llama a ``core`` tal cual y solo se mide
el tiempo (mediana de R repeticiones tras 1 calentamiento) y se registran las decisiones.

Uso:
    python -m experimentos.correr_casos                       # todos los casos de casos/
    python -m experimentos.correr_casos casos/caso_01_etapa0.json
    python -m experimentos.correr_casos casos/ --repeticiones 11 --salida mi_salida/
Los índices de la salida están en BASE 1 (igual que la entrada).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path
from typing import Any

from core.combinado import combinado_cobertura_obligatoria_mascaras, evaluar_combinada
from core.instancias import InstanciaCombinada, InstanciaMochila, InstanciaSetCover
from core.mochila import construir_tabla_dp, mochila_dp, mochila_fuerza_bruta, reconstruir_etapas
from core.set_cover import (
    cobertura_exacta,
    cobertura_exacta_mascaras,
    cobertura_exacta_ponderada,
    cobertura_voraz,
    cobertura_voraz_ponderada,
    numero_armonico,
)
from experimentos.casos import Caso, CasoInvalido, cargar_caso, listar_casos
from experimentos.medir import RESULTADOS, medir

RAIZ = Path(__file__).resolve().parent.parent
CASOS = RAIZ / "casos"
SALIDA = RESULTADOS / "casos"

MAX_CELDAS_TABLA = 5000  # la tabla DP completa se guarda en el JSON solo si cabe
MAX_N_FUERZA_BRUTA = 20  # verificación contra la fuerza bruta (2^n; n = 20 tarda ≈ 1 s)
MAX_N_EXACTO_SC = 16  # verificación contra el exacto de Set Cover (2^N / subconjuntos)
MAX_R_MASCARAS = 20  # el exacto por máscaras cuesta O(N·2^r): con r ≤ 20 son ≤ ~10^6 pasos por opción


def _tiempos(tiempos: list[float]) -> dict[str, Any]:
    return {"tiempo_s": statistics.median(tiempos), "tiempo_min_s": min(tiempos),
            "tiempo_max_s": max(tiempos), "repeticiones": len(tiempos)}


# ------------------------------------------------------------------------------ Parte 1

def _reconstruccion(inst: InstanciaMochila, tabla: list[list[int]]) -> list[dict[str, Any]]:
    """Decisión de cada etapa al recorrer la tabla desde DP[n][B] (mismo criterio que ``core``)."""
    b = inst.B
    pasos = []
    for i in range(inst.n, 0, -1):
        con, sin = tabla[i][b], tabla[i - 1][b]
        acelerar = con != sin
        pasos.append({"etapa": i, "presupuesto_b": b, "dp_i_b": con, "dp_i_1_b": sin,
                      "decision": "acelerar" if acelerar else "no acelerar",
                      "presupuesto_siguiente": b - inst.c[i - 1] if acelerar else b})
        if acelerar:
            b -= inst.c[i - 1]
    return pasos


def resolver_parte1(inst: InstanciaMochila, repeticiones: int) -> dict[str, Any]:
    tiempos, sol = medir(lambda: mochila_dp(inst), repeticiones)  # DP completa + reconstrucción
    tabla = construir_tabla_dp(inst)  # solo para la traza (no se mide)
    recon = _reconstruccion(inst, tabla)
    elegidas = [p["etapa"] for p in recon if p["decision"] == "acelerar"][::-1]
    assert tuple(e - 1 for e in elegidas) == sol.etapas == reconstruir_etapas(inst, tabla)
    suma_t = sum(inst.t)
    etapas = [{"etapa": i + 1, "t": inst.t[i], "c": inst.c[i], "d": inst.d[i],
               "acelerada": i in sol.etapas, "t_final": inst.t[i] - (inst.d[i] if i in sol.etapas else 0)}
              for i in range(inst.n)]
    res: dict[str, Any] = {
        "entrada": {"n": inst.n, "B": inst.B},
        "resultado": {"etapas_aceleradas": [i + 1 for i in sol.etapas], "costo_usado": sol.costo,
                      "presupuesto": inst.B, "reduccion": sol.reduccion,
                      "duracion_inicial": suma_t, "duracion_final": sol.duracion},
        "complejidad": "T(n, B) = O(n·B), pseudo-polinomial",
        "celdas_dp": (inst.n + 1) * (inst.B + 1),
        **_tiempos(tiempos),
        "traza": {"etapas": etapas, "reconstruccion": recon},
    }
    if (inst.n + 1) * (inst.B + 1) <= MAX_CELDAS_TABLA:
        res["traza"]["tabla_dp"] = tabla
    else:
        res["traza"]["tabla_dp_omitida"] = (
            f"la tabla tiene {(inst.n + 1) * (inst.B + 1)} celdas (> {MAX_CELDAS_TABLA}); "
            "se conserva la reconstrucción completa")
    if inst.n <= MAX_N_FUERZA_BRUTA:
        fb = mochila_fuerza_bruta(inst)
        res["verificacion"] = {"metodo": "fuerza bruta (2^n)", "reduccion_optima": fb.reduccion,
                               "coincide": fb.reduccion == sol.reduccion}
    else:
        res["verificacion"] = {"metodo": "fuerza bruta", "omitida": f"n = {inst.n} > {MAX_N_FUERZA_BRUTA}"}
    return res


# ------------------------------------------------------------------------------ Parte 2

def _reparar_un_por_grupo(inst: InstanciaSetCover, indices: tuple[int, ...],
                          grupos: tuple[int, ...]) -> tuple[tuple[int, ...], dict[int, list[int]], bool]:
    """Impone "a lo sumo una variación por etapa" sobre la elección del voraz.

    Si el voraz eligió dos variaciones de la misma etapa y una de ellas cubre la unión de todas las
    elegidas de esa etapa, se queda solo con la más barata de esas (la cobertura no cambia y el costo
    no sube). Devuelve (índices, {grupo: opciones repetidas}, ¿quedó cumpliendo la regla?).
    """
    por_grupo: dict[int, list[int]] = {}
    for j in indices:  # ≤ min(N, r) elecciones
        por_grupo.setdefault(grupos[j], []).append(j)
    repetidos = {g: js for g, js in por_grupo.items() if len(js) > 1}
    reparados: list[int] = []
    cumple = True
    for js in por_grupo.values():
        if len(js) == 1:
            reparados += js
            continue
        union = frozenset().union(*(inst.conjuntos[j] for j in js))
        abarcan = [j for j in js if inst.conjuntos[j] == union]
        if abarcan:
            reparados.append(min(abarcan, key=lambda j: inst.a[j]))
        else:  # ninguna variación sola cubre lo que cubrían juntas: no es reparable sin cambiar la cobertura
            reparados += js
            cumple = False
    return tuple(sorted(reparados)), repetidos, cumple


def resolver_parte2(inst: InstanciaSetCover, ponderado: bool, repeticiones: int,
                    grupos: tuple[int, ...] = ()) -> dict[str, Any]:
    voraz_fn = cobertura_voraz_ponderada if ponderado else cobertura_voraz
    exacto_fn = cobertura_exacta_ponderada if ponderado else cobertura_exacta
    tiempos, sol = medir(lambda: voraz_fn(inst), repeticiones)
    d = max(len(s) for s in inst.conjuntos)
    base: dict[str, Any] = {
        "entrada": {"interacciones": inst.n, "categorias": inst.r, "variante": "A1 (costos)" if ponderado else "Parte 2",
                    "d": d},
        "complejidad": "T(n, r) = O(n·r²)",
        "cota": "G ≤ H_d · óptimo" + (" (Chvátal, 1979)" if ponderado else " (Johnson 1974; Chvátal 1979)"),
        "H_d": numero_armonico(d), "H_r": numero_armonico(inst.r),
        **_tiempos(tiempos),
    }
    if sol is None:
        return {**base, "factible": False,
                "resultado": {"mensaje": "sin solución: alguna categoría no la cubre ninguna interacción"}}
    pasos, cubiertas = [], set()
    costo_acum = 0
    for k, (j, nuevas) in enumerate(sol.pasos, start=1):
        cubiertas |= set(nuevas)
        costo_acum += inst.a[j]
        paso = {"paso": k, "interaccion": j + 1, "categorias_nuevas": [c + 1 for c in nuevas],
                "n_nuevas": len(nuevas), "costo_a": inst.a[j], "costo_acumulado": costo_acum,
                "categorias_cubiertas": len(cubiertas), "categorias_pendientes": inst.r - len(cubiertas)}
        if ponderado:
            paso["razon_a_sobre_nuevas"] = inst.a[j] / len(nuevas)
        pasos.append(paso)
    res = {**base, "factible": True,
           "resultado": {"interacciones_auditadas": sorted(j + 1 for j in sol.indices),
                         "orden_de_eleccion": [j + 1 for j in sol.indices],
                         "cantidad": sol.tamano, "costo_total": sol.costo,
                         "categorias_cubiertas": len(cubiertas), "categorias_totales": inst.r,
                         "cobertura_completa": len(cubiertas) == inst.r},
           "traza": {"pasos": pasos}}
    medida = sol.costo if ponderado else sol.tamano
    if grupos:  # una variación por etapa: el costo comparable es el de la elección ya reparada
        rep, repetidos, cumple = _reparar_un_por_grupo(inst, sol.indices, grupos)
        costo_rep = sum(inst.a[j] for j in rep)
        res["resultado"]["una_variacion_por_etapa"] = {
            "cumple": cumple, "etapas_repetidas": sorted(g + 1 for g in repetidos),
            "interacciones_reparadas": [j + 1 for j in rep] if repetidos else [], "costo_reparado": costo_rep}
        medida = costo_rep
    if grupos and inst.r <= MAX_R_MASCARAS:  # exacto que respeta "una por etapa": O(N·2^r)
        ex = cobertura_exacta_mascaras(inst, grupos)
        metodo = f"exacto por DP sobre máscaras de categorías, O(N·2^r) con r = {inst.r}"
    elif not grupos and inst.n <= MAX_N_EXACTO_SC:
        ex = exacto_fn(inst)
        metodo = "exacto por fuerza bruta"
    else:
        ex, metodo = None, ""
    if ex is not None:
        opt = ex.costo if ponderado else ex.tamano
        res["verificacion"] = {"metodo": metodo, "optimo": opt,
                               "optimo_interacciones": sorted(j + 1 for j in ex.indices),
                               "razon_voraz_sobre_optimo": medida / opt,
                               "cumple_cota_Hd": medida <= numero_armonico(d) * opt + 1e-9}
    else:
        motivo = (f"N = {inst.n} > {MAX_N_EXACTO_SC}" if not grupos else f"r = {inst.r} > {MAX_R_MASCARAS}")
        res["verificacion"] = {"metodo": "exacto", "omitida": motivo}
    return res


# --------------------------------------------------------------------------- Variante B

def resolver_variante_b(caso: Caso, p2: dict[str, Any], repeticiones: int) -> dict[str, Any]:
    """Presupuesto conjunto: la auditoría cubre todo y lo que sobra acelera (cobertura obligatoria).

    Exacta: a* (mínimo costo de cubrir) y luego la DP con B − a*. Con el voraz: costo a_g ≤ H_d·a* y la DP
    con B − a_g; la diferencia de duración es lo que se pierde por el exceso de auditoría.
    """
    cob, ch, presupuesto = caso.cobertura, caso.mochila, caso.presupuesto_conjunto
    grupos = caso.grupo_interaccion or None
    inst = InstanciaCombinada(cadena=ch, cobertura=cob, B=presupuesto, lam=1)
    out: dict[str, Any] = {"presupuesto_conjunto": presupuesto,
                           "complejidad": "T = T_cobertura + O(n·B); exacto por máscaras O(N·2^r), voraz O(N·r²)"}

    def describir(sol, extra: dict[str, Any]) -> dict[str, Any]:
        audit = sum(cob.a[j] for j in sol.interacciones)
        return {"interacciones_auditadas": [j + 1 for j in sol.interacciones], "costo_auditoria": audit,
                "presupuesto_para_acelerar": presupuesto - audit,
                "etapas_aceleradas": [i + 1 for i in sol.etapas],
                "costo_total": sol.costo, "duracion_final": sol.duracion,
                "reduccion": sum(ch.t) - sol.duracion, **extra}

    exacta = None
    if cob.r <= MAX_R_MASCARAS:
        tiempos, exacta = medir(lambda: combinado_cobertura_obligatoria_mascaras(inst, grupos), repeticiones)
        out["exacta"] = describir(exacta, _tiempos(tiempos)) if exacta else {"mensaje": "infactible: a* > B"}
    else:
        out["exacta"] = {"omitida": f"r = {cob.r} > {MAX_R_MASCARAS}"}
    if not p2.get("factible"):
        return out
    r2 = p2["resultado"]
    elegidas = tuple(j - 1 for j in (r2.get("una_variacion_por_etapa", {}).get("interacciones_reparadas")
                                     or r2["orden_de_eleccion"]))
    audit_g = sum(cob.a[j] for j in elegidas)
    if audit_g > presupuesto:
        out["voraz"] = {"mensaje": f"la cobertura voraz cuesta {audit_g} > B conjunto {presupuesto}"}
        return out
    cadena = InstanciaMochila(t=ch.t, c=ch.c, d=ch.d, B=presupuesto - audit_g)
    tiempos, mochila = medir(lambda: mochila_dp(cadena), repeticiones)
    voraz = evaluar_combinada(inst, mochila.etapas, elegidas)
    out["voraz"] = describir(voraz, {"tiempo_mochila_s": statistics.median(tiempos),
                                     "nota": "el tiempo del voraz de cobertura está en parte2"})
    if exacta is not None:
        out["comparacion"] = {
            "a_estrella": sum(cob.a[j] for j in exacta.interacciones), "a_voraz": audit_g,
            "razon_a_voraz_sobre_a_estrella": audit_g / sum(cob.a[j] for j in exacta.interacciones),
            "duracion_exacta": exacta.duracion, "duracion_voraz": voraz.duracion,
            "tiempo_perdido_por_exceso_de_auditoria": voraz.duracion - exacta.duracion}
    return out


# ----------------------------------------------------------------------------- por caso

def resolver_caso(caso: Caso, repeticiones: int = 7) -> dict[str, Any]:
    out: dict[str, Any] = {"id": caso.id, "descripcion": caso.descripcion}
    if caso.mochila is not None:
        out["parte1"] = resolver_parte1(caso.mochila, repeticiones)
    if caso.cobertura is not None:
        out["parte2"] = resolver_parte2(caso.cobertura, caso.ponderado, repeticiones, caso.grupo_interaccion)
    if caso.presupuesto_conjunto is not None and caso.mochila is not None and caso.cobertura is not None:
        out["variante_b"] = resolver_variante_b(caso, out["parte2"], repeticiones)
    if caso.nombres_etapas or caso.nombres_interacciones:  # ids originales del archivo (E01, "E03 parcial", R01)
        out["nombres"] = {"etapas": list(caso.nombres_etapas), "interacciones": list(caso.nombres_interacciones),
                          "categorias": list(caso.nombres_categorias)}
        _anotar_nombres(out)
    return out


def _nom(res: dict[str, Any], clave: str, i: int) -> str:
    """Nombre original del elemento i (base 1) o el propio número si el caso no trae nombres."""
    nombres = res.get("nombres", {}).get(clave) or []
    return nombres[i - 1] if nombres else str(i)


def _anotar_nombres(res: dict[str, Any]) -> None:
    """Agrega listas con los ids originales junto a las de índices (los índices se conservan)."""
    if "parte1" in res:
        r = res["parte1"]["resultado"]
        r["etapas_aceleradas_nombres"] = [_nom(res, "etapas", i) for i in r["etapas_aceleradas"]]
    if "parte2" in res and res["parte2"]["factible"]:
        r = res["parte2"]["resultado"]
        r["interacciones_auditadas_nombres"] = [_nom(res, "interacciones", j) for j in r["interacciones_auditadas"]]
        v = res["parte2"]["verificacion"]
        if "optimo_interacciones" in v:
            v["optimo_interacciones_nombres"] = [_nom(res, "interacciones", j) for j in v["optimo_interacciones"]]
    for clave in ("exacta", "voraz"):
        s = res.get("variante_b", {}).get(clave, {})
        if "etapas_aceleradas" in s:
            s["etapas_aceleradas_nombres"] = [_nom(res, "etapas", i) for i in s["etapas_aceleradas"]]
            s["interacciones_auditadas_nombres"] = [_nom(res, "interacciones", j) for j in s["interacciones_auditadas"]]


def _lista_n(res: dict[str, Any], clave: str, xs) -> str:
    return _lista(_nom(res, clave, x) for x in xs) if xs else "∅"


def _lista(xs) -> str:
    return "{" + ", ".join(str(x) for x in xs) + "}" if xs else "∅"


def traza_markdown(res: dict[str, Any]) -> str:
    L = [f"# Traza del caso `{res['id']}`", ""]
    if res["descripcion"]:
        L += [res["descripcion"], ""]
    p1 = res.get("parte1")
    if p1:
        r = p1["resultado"]
        L += ["## Parte 1 — Aceleración de la cadena (Mochila 0/1)", "",
              f"- Entrada: n = {p1['entrada']['n']} etapas, presupuesto B = {p1['entrada']['B']}.",
              f"- **Etapas aceleradas: {_lista_n(res, 'etapas', r['etapas_aceleradas'])}** · costo {r['costo_usado']} / {r['presupuesto']}",
              f"- Duración: {r['duracion_inicial']} → **{r['duracion_final']}** (reducción {r['reduccion']}).",
              f"- Tiempo: **{p1['tiempo_s']:.6f} s** (mediana de {p1['repeticiones']} repeticiones; "
              f"mín {p1['tiempo_min_s']:.6f}, máx {p1['tiempo_max_s']:.6f}). {p1['complejidad']}; "
              f"{p1['celdas_dp']} celdas.", ""]
        v = p1["verificacion"]
        L += [("- Verificación con " + v["metodo"] + ": " +
               ("reducción óptima " + str(v["reduccion_optima"]) + (" ✔ coincide" if v["coincide"] else " ✘ NO coincide"))
               if "coincide" in v else f"- Verificación omitida ({v['omitida']})."), "",
              "### Etapas y costos", "", "| etapa | t | c | d | ¿acelerada? | t final |", "|---|---|---|---|---|---|"]
        L += [f"| {_nom(res, 'etapas', e['etapa'])} | {e['t']} | {e['c']} | {e['d']} | {'sí' if e['acelerada'] else 'no'} | {e['t_final']} |"
              for e in p1["traza"]["etapas"]]
        tabla = p1["traza"].get("tabla_dp")
        L += ["", "### Estados de la DP: DP[i][b] = máxima reducción con las primeras i etapas y presupuesto b", ""]
        if tabla is not None and len(tabla[0]) <= 26:
            cab = "| i \\ b | " + " | ".join(str(b) for b in range(len(tabla[0]))) + " |"
            L += [cab, "|" + "---|" * (len(tabla[0]) + 1)]
            L += [f"| {i} | " + " | ".join(str(v) for v in fila) + " |" for i, fila in enumerate(tabla)]
        elif tabla is not None:
            L.append(f"(tabla de {len(tabla)}×{len(tabla[0])} guardada completa en el JSON, campo `traza.tabla_dp`)")
        else:
            L.append("(tabla omitida por tamaño: " + p1["traza"]["tabla_dp_omitida"] + ")")
        L += ["", "### Reconstrucción (de DP[n][B] hacia atrás)", "",
              "| etapa i | b | DP[i][b] | DP[i−1][b] | decisión | b siguiente |", "|---|---|---|---|---|---|"]
        pasos = p1["traza"]["reconstruccion"]
        mostrar = pasos if len(pasos) <= 60 else pasos[:30]
        L += [f"| {_nom(res, 'etapas', q['etapa'])} | {q['presupuesto_b']} | {q['dp_i_b']} | {q['dp_i_1_b']} | {q['decision']} | "
              f"{q['presupuesto_siguiente']} |" for q in mostrar]
        if len(pasos) > len(mostrar):
            L.append(f"\n(se muestran 30 de {len(pasos)} pasos; el resto está en el JSON)")
        L.append("")
    p2 = res.get("parte2")
    if p2:
        e = p2["entrada"]
        L += [f"## Parte 2 — Cobertura de auditoría ({e['variante']})", "",
              f"- Entrada: {e['interacciones']} interacciones, {e['categorias']} categorías (d = {e['d']}).",
              f"- Tiempo: **{p2['tiempo_s']:.6f} s** (mediana de {p2['repeticiones']} repeticiones). {p2['complejidad']}."]
        if not p2["factible"]:
            L += ["", "**" + p2["resultado"]["mensaje"] + "**", ""]
        else:
            r = p2["resultado"]
            L += [f"- **Interacciones auditadas: {_lista_n(res, 'interacciones', r['interacciones_auditadas'])}** "
                  f"(orden de elección: {[_nom(res, 'interacciones', j) for j in r['orden_de_eleccion']]}) · "
                  f"cantidad {r['cantidad']} · costo total {r['costo_total']}.",
                  f"- Cobertura: {r['categorias_cubiertas']}/{r['categorias_totales']} categorías "
                  f"({'completa' if r['cobertura_completa'] else 'INCOMPLETA'}).",
                  f"- Cota: {p2['cota']} · H_d = {p2['H_d']:.3f} · H_r = {p2['H_r']:.3f}."]
            u = r.get("una_variacion_por_etapa")
            if u:
                if not u["etapas_repetidas"]:
                    regla = "cumplida."
                else:
                    regla = (f"el voraz repitió las etapas {_lista_n(res, 'etapas', u['etapas_repetidas'])}; "
                             f"se repara a {_lista_n(res, 'interacciones', u['interacciones_reparadas'])} "
                             f"(costo {u['costo_reparado']})" + ("." if u["cumple"] else ", pero NO es reparable."))
                L.append("- Regla «a lo sumo una variación por etapa»: " + regla)
            v = p2["verificacion"]
            if "optimo" in v:
                L.append(f"- Verificación con {v['metodo']}: óptimo = {v['optimo']} "
                         f"({_lista_n(res, 'interacciones', v['optimo_interacciones'])}); "
                         f"razón voraz/óptimo = {v['razon_voraz_sobre_optimo']:.3f}; "
                         f"{'cumple' if v['cumple_cota_Hd'] else 'NO cumple'} la cota H_d.")
            else:
                L.append(f"- Verificación omitida ({v['omitida']}).")
            pond = "razon_a_sobre_nuevas" in p2["traza"]["pasos"][0] if p2["traza"]["pasos"] else False
            L += ["", "### Elecciones del voraz", "",
                  "| paso | interacción | categorías nuevas | #nuevas | costo a | " + ("a/nuevas | " if pond else "") +
                  "costo acumulado | cubiertas | pendientes |",
                  "|---|---|---|---|---|" + ("---|" if pond else "") + "---|---|---|"]
            for q in p2["traza"]["pasos"]:
                fila = (f"| {q['paso']} | {_nom(res, 'interacciones', q['interaccion'])} | "
                        f"{_lista_n(res, 'categorias', q['categorias_nuevas'])} | {q['n_nuevas']} | "
                        f"{q['costo_a']} | " + (f"{q['razon_a_sobre_nuevas']:.3f} | " if pond else "") +
                        f"{q['costo_acumulado']} | {q['categorias_cubiertas']} | {q['categorias_pendientes']} |")
                L.append(fila)
            L.append("")
    vb = res.get("variante_b")
    if vb:
        L += ["## Variante B — presupuesto conjunto (la auditoría cubre todo; el resto acelera)", "",
              f"- Presupuesto conjunto: {vb['presupuesto_conjunto']}. {vb['complejidad']}.", ""]
        for clave, titulo in (("exacta", "Exacta (a* por máscaras + DP con B − a*)"),
                              ("voraz", "Con la cobertura voraz (a_g + DP con B − a_g)")):
            s = vb.get(clave, {})
            if "duracion_final" not in s:
                L.append(f"- {titulo}: {s.get('mensaje') or s.get('omitida', 'sin resultado')}.")
                continue
            L += [f"- **{titulo}**: auditoría {_lista_n(res, 'interacciones', s['interacciones_auditadas'])} "
                  f"(costo {s['costo_auditoria']}), quedan {s['presupuesto_para_acelerar']} para acelerar "
                  f"{_lista_n(res, 'etapas', s['etapas_aceleradas'])}; costo total {s['costo_total']}; "
                  f"duración final **{s['duracion_final']}** (reducción {s['reduccion']})."]
        cmp_ = vb.get("comparacion")
        if cmp_:
            L += ["", f"- Costo de auditoría: voraz {cmp_['a_voraz']} vs a* = {cmp_['a_estrella']} "
                      f"(razón {cmp_['razon_a_voraz_sobre_a_estrella']:.3f}). Duración: voraz {cmp_['duracion_voraz']} vs exacta "
                      f"{cmp_['duracion_exacta']} → se pierden **{cmp_['tiempo_perdido_por_exceso_de_auditoria']}** unidades "
                      "de tiempo por el exceso de auditoría.", ""]
    return "\n".join(L)


COLUMNAS_RESUMEN = [
    "caso", "n_etapas", "B", "duracion_inicial", "duracion_final", "reduccion", "costo_usado",
    "etapas_aceleradas", "tiempo_parte1_s", "verif_parte1", "interacciones", "categorias", "variante",
    "tamano_cobertura", "costo_cobertura", "optimo", "razon_voraz_optimo", "tiempo_parte2_s",
    "B_conjunto", "duracion_b_exacta", "duracion_b_voraz",
]


def fila_resumen(res: dict[str, Any]) -> dict[str, Any]:
    f: dict[str, Any] = {c: "" for c in COLUMNAS_RESUMEN}
    f["caso"] = res["id"]
    if "parte1" in res:
        p = res["parte1"]
        r = p["resultado"]
        f.update(n_etapas=p["entrada"]["n"], B=p["entrada"]["B"], duracion_inicial=r["duracion_inicial"],
                 duracion_final=r["duracion_final"], reduccion=r["reduccion"], costo_usado=r["costo_usado"],
                 etapas_aceleradas=(" ".join(_nom(res, "etapas", i) for i in r["etapas_aceleradas"])
                                    if len(r["etapas_aceleradas"]) <= 30
                                    else f"{len(r['etapas_aceleradas'])} etapas (ver JSON)"),
                 tiempo_parte1_s=f"{p['tiempo_s']:.9f}",
                 verif_parte1="ok" if p["verificacion"].get("coincide") else ("omitida" if "omitida" in p["verificacion"] else "FALLA"))
    if "parte2" in res:
        p = res["parte2"]
        f.update(interacciones=p["entrada"]["interacciones"], categorias=p["entrada"]["categorias"],
                 variante=p["entrada"]["variante"], tiempo_parte2_s=f"{p['tiempo_s']:.9f}")
        if p["factible"]:
            r, v = p["resultado"], p["verificacion"]
            f.update(tamano_cobertura=r["cantidad"], costo_cobertura=r["costo_total"],
                     optimo=v.get("optimo", ""),
                     razon_voraz_optimo=f"{v['razon_voraz_sobre_optimo']:.4f}" if "optimo" in v else "")
        else:
            f["tamano_cobertura"] = "sin solución"
    if "variante_b" in res:
        vb = res["variante_b"]
        f.update(B_conjunto=vb["presupuesto_conjunto"], duracion_b_exacta=vb.get("exacta", {}).get("duracion_final", ""),
                 duracion_b_voraz=vb.get("voraz", {}).get("duracion_final", ""))
    return f


def main(casos: Path = CASOS, salida: Path = SALIDA, repeticiones: int = 7) -> list[dict[str, Any]]:
    salida.mkdir(parents=True, exist_ok=True)
    resultados = []
    for archivo in listar_casos(casos):
        caso = cargar_caso(archivo)
        res = resolver_caso(caso, repeticiones)
        (salida / f"{caso.id}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        (salida / f"{caso.id}_traza.md").write_text(traza_markdown(res), encoding="utf-8")
        resultados.append(res)
    with open(salida / "resumen_casos.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS_RESUMEN)
        w.writeheader()
        w.writerows(fila_resumen(r) for r in resultados)
    return resultados


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Ejecuta casos y escribe resultado, tiempo y traza por caso.")
    ap.add_argument("casos", nargs="?", default=str(CASOS), help="archivo .json o carpeta (por defecto casos/)")
    ap.add_argument("--salida", default=str(SALIDA), help="carpeta de salida")
    ap.add_argument("--repeticiones", type=int, default=7, help="repeticiones por medición (mediana)")
    a = ap.parse_args()
    try:
        out = main(Path(a.casos), Path(a.salida), a.repeticiones)
    except CasoInvalido as e:
        raise SystemExit(f"Caso inválido: {e}")
    for r in out:
        t1 = f"{r['parte1']['tiempo_s']:.6f} s" if "parte1" in r else "-"
        t2 = f"{r['parte2']['tiempo_s']:.6f} s" if "parte2" in r else "-"
        print(f"{r['id']:<28} parte1: {t1:>12}   parte2: {t2:>12}")
    print(f"\nSalida en {a.salida}")
