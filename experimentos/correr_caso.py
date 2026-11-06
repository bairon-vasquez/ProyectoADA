"""Ejecuta la solución base sobre los casos de la profesora (JSON) y deja la evidencia.

Uso:
    python -m experimentos.correr_caso casos/entrada_G3_mochila_20_nodos.json
    python -m experimentos.correr_caso casos/            # todos los .json de la carpeta
    python -m experimentos.correr_caso CASO.json --lam 10 --repeticiones 7 --verificar

Por cada caso escribe en ``experimentos/resultados/casos/``:
    <caso>_traza.md      resultados + traza legible (DP, etapas aceleradas, costos, cobertura)
    <caso>_dp.csv        la tabla DP completa, DP[i][b] (i = 0..n, b = 0..B)
    <caso>_tiempos.csv   tiempo de cada algoritmo, una fila por repetición (formato COLUMNAS)
y repite el resumen por consola.

Los tiempos se miden con ``medir.py`` (único lugar que mide). Los algoritmos son los de
``core``; este módulo solo traduce el JSON, mide y presenta.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from core.combinado import (
    SolucionCombinada,
    combinado_cobertura_obligatoria,
    combinado_cobertura_obligatoria_dp,
    combinado_heuristica,
)
from core.dag import dag_heuristica
from core.instancias import InstanciaCombinada, InstanciaMochila
from core.mochila import construir_tabla_dp, mochila_dp, mochila_fuerza_bruta, reconstruir_etapas
from core.set_cover import (
    SolucionCobertura,
    cobertura_exacta_dp,
    cobertura_voraz_ponderada,
    numero_armonico,
)
from experimentos.cargar_caso import CasoProfesora, cargar_caso
from experimentos.medir import RESULTADOS, escribir_csv, mediana, medir_caso

CARPETA_CASOS = RESULTADOS / "casos"


# ---------------------------------------------------------------- utilidades de texto
def _tabla_md(encabezados: list[str], filas: list[list[object]]) -> list[str]:
    """Tabla Markdown (también legible como texto plano)."""
    out = ["| " + " | ".join(encabezados) + " |", "|" + "|".join("---" for _ in encabezados) + "|"]
    for f in filas:
        out.append("| " + " | ".join(str(x) for x in f) + " |")
    return out


def _ids(caso: CasoProfesora, idx: tuple[int, ...]) -> str:
    return ", ".join(caso.ids_etapas[i] for i in idx) if idx else "(ninguna)"


def _fmt_t(segundos: float) -> str:
    return f"{segundos * 1000:.3f} ms" if segundos < 1 else f"{segundos:.3f} s"


# ---------------------------------------------------------------- traza de la Mochila
def traza_mochila(caso: CasoProfesora, inst: InstanciaMochila, titulo: str) -> list[str]:
    """Reconstruye la decisión de la DP paso a paso: de DP[n][B] hacia DP[0][·]."""
    n, B = inst.n, inst.B
    tabla = construir_tabla_dp(inst)
    elegidas = reconstruir_etapas(inst, tabla)
    celdas = (n + 1) * (B + 1)
    tomas = sum(
        1 for i in range(1, n + 1) for b in range(B + 1) if tabla[i][b] > tabla[i - 1][b]
    )
    L = [f"### {titulo}", ""]
    L.append(
        f"- Estados de la DP: (n+1)·(B+1) = {n + 1}·{B + 1} = **{celdas}** celdas "
        f"({n * (B + 1)} transiciones calculadas, O(n·B))."
    )
    L.append(f"- Celdas donde acelerar la etapa i mejora a no acelerarla: {tomas}.")
    L.append(f"- Reducción máxima DP[n][B] = **{tabla[n][B]}**.")
    L.append("")
    L.append(
        "Recorrido hacia atrás desde (i=n, b=B). Si DP[i][b] = DP[i-1][b] la etapa no "
        "hace falta; si no, se aceleró y el presupuesto baja en c_i:"
    )
    L.append("")
    filas: list[list[object]] = []
    b = B
    for i in range(n, 0, -1):
        ci, di = inst.c[i - 1], inst.d[i - 1]
        con = tabla[i - 1][b - ci] + di if ci <= b else "—"
        sin = tabla[i - 1][b]
        acelera = tabla[i][b] != sin
        filas.append([
            i, caso.ids_etapas[i - 1], inst.t[i - 1], ci, di, b, tabla[i][b], sin, con,
            "ACELERA" if acelera else "no", b - ci if acelera else b,
        ])
        if acelera:
            b -= ci
    L += _tabla_md(
        ["i", "etapa", "t_i", "c_i", "d_i", "b", "DP[i][b]", "sin i = DP[i-1][b]",
         "con i = DP[i-1][b-c_i]+d_i", "decisión", "b siguiente"],
        filas,
    )
    L.append("")
    sol = mochila_dp(inst)
    L.append(f"- Etapas aceleradas: **{_ids(caso, sol.etapas)}** ({len(sol.etapas)} de {n}).")
    L.append(f"- Costo de aceleración: **{sol.costo}** de B = {B} (sobran {B - sol.costo}).")
    L.append(
        f"- Duración: Σt = {sum(inst.t)} → Σt − Σd = {sum(inst.t)} − {sol.reduccion} "
        f"= **{sol.duracion}**."
    )
    L.append("")
    L += _tabla_md(
        ["etapa", "t_i", "c_i", "d_i", "t_i − d_i"],
        [[caso.ids_etapas[i], inst.t[i], inst.c[i], inst.d[i], inst.t[i] - inst.d[i]]
         for i in sol.etapas]
        + [["**Total**", sum(inst.t[i] for i in sol.etapas), sol.costo, sol.reduccion, "—"]],
    )
    L.append("")
    return L


def escribir_tabla_dp(ruta: Path, inst: InstanciaMochila) -> None:
    """Vuelca DP[i][b] completa (filas i = 0..n, columnas b = 0..B)."""
    tabla = construir_tabla_dp(inst)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["i\\b"] + list(range(inst.B + 1)))
        for i, fila in enumerate(tabla):
            w.writerow([i] + fila)


# ---------------------------------------------------------------- traza de la cobertura
def traza_cobertura(
    caso: CasoProfesora, sol: SolucionCobertura | None, titulo: str, pasos: bool
) -> list[str]:
    cob = caso.cobertura
    L = [f"### {titulo}", ""]
    if sol is None:
        return L + ["- No hay cobertura factible.", ""]
    if pasos and sol.pasos:
        filas: list[list[object]] = []
        acumulado = 0
        for k, (j, nuevas) in enumerate(sol.pasos, 1):
            acumulado += cob.a[j]
            filas.append([
                k, caso.etiquetas_interacciones[j], cob.a[j],
                ", ".join(caso.ids_riesgos[x] for x in nuevas),
                f"{cob.a[j]}/{len(nuevas)} = {cob.a[j] / len(nuevas):.2f}", acumulado,
            ])
        L += _tabla_md(
            ["paso", "interacción elegida", "a_j", "categorías nuevas", "a_j / nuevas",
             "costo acumulado"],
            filas,
        )
        L.append("")
    L.append(
        f"- Interacciones elegidas ({sol.tamano}): "
        f"**{', '.join(caso.etiquetas_interacciones[j] for j in sol.indices)}**."
    )
    L.append(f"- Costo de auditoría Σa_j = **{sol.costo}**.")
    L.append("")
    filas2: list[list[object]] = []
    for k in range(cob.r):
        quienes = [caso.etiquetas_interacciones[j] for j in sol.indices if k in cob.conjuntos[j]]
        filas2.append([
            caso.ids_riesgos[k], caso.nombres_riesgos[k], cob.w[k],
            ", ".join(quienes) if quienes else "**SIN CUBRIR**",
        ])
    L += _tabla_md(["riesgo", "categoría", "importancia w_k", "cubierto por"], filas2)
    L.append("")
    return L


def _describe_combinada(
    caso: CasoProfesora, s: SolucionCombinada | None, B: int, titulo: str
) -> list[str]:
    L = [f"### {titulo}", ""]
    if s is None:
        return L + ["- Sin solución: el costo mínimo de cubrir todo supera el presupuesto.", ""]
    cob = caso.cobertura
    cubiertas = {k for j in s.interacciones for k in cob.conjuntos[j]}
    sin = [caso.ids_riesgos[k] for k in range(cob.r) if k not in cubiertas]
    ch = caso.mochila
    costo_acel = sum(ch.c[i] for i in s.etapas)
    costo_aud = sum(cob.a[j] for j in s.interacciones)
    L.append(f"- Etapas aceleradas: **{_ids(caso, s.etapas)}** (costo de aceleración {costo_acel}).")
    L.append(
        f"- Interacciones auditadas: **{', '.join(caso.etiquetas_interacciones[j] for j in s.interacciones) or '(ninguna)'}** "
        f"(costo de auditoría {costo_aud})."
    )
    L.append(f"- Costo conjunto: {costo_acel} + {costo_aud} = **{s.costo}** de B = {B} (sobran {B - s.costo}).")
    L.append(f"- Categorías cubiertas: {len(cubiertas)} de {cob.r}; sin cubrir: {', '.join(sin) or 'ninguna'}.")
    L.append(f"- Duración {s.duracion} + penalización {s.penalizacion} = objetivo **{s.objetivo}**.")
    L.append("")
    return L


# ---------------------------------------------------------------- ejecución de un caso
def correr_caso(
    caso: CasoProfesora, lam: int, repeticiones: int, verificar: bool, carpeta: Path
) -> Path:
    mo, cob = caso.mochila, caso.cobertura
    n, B = mo.n, mo.B
    filas_csv: list[dict[str, object]] = []
    resumen_t: list[list[object]] = []

    def medir_alg(nombre: str, fn, valor, parametro: str, vp: int, extra=0):  # type: ignore[no-untyped-def]
        filas = medir_caso(nombre, "caso", n, parametro, vp, fn, valor, extra, repeticiones)
        filas_csv.extend(filas)
        ts = [float(f["tiempo_s"]) for f in filas]
        resumen_t.append([nombre, f"n={n}, {parametro}={vp}", _fmt_t(mediana(ts)),
                          _fmt_t(min(ts)), _fmt_t(max(ts)), filas[0]["valor_solucion"]])
        return fn()

    inst_comb = InstanciaCombinada(
        cadena=mo, cobertura=cob, B=caso.B_conjunto, lam=lam
    )

    # --- medición (cada algoritmo se ejecuta repeticiones+1 veces; ver medir.medir)
    sol_m = medir_alg("mochila_dp", lambda: mochila_dp(mo), lambda s: s.duracion, "B", B,
                      extra=lambda s: n * (B + 1))
    sol_dag = medir_alg("dag_heuristica", lambda: dag_heuristica(caso.dag),
                        lambda s: s.duracion, "m", caso.dag.m,
                        extra=lambda s: len(s.pasos))
    sol_v = medir_alg("cobertura_voraz_ponderada", lambda: cobertura_voraz_ponderada(cob),
                      lambda s: s.costo if s else -1, "r", cob.r,
                      extra=lambda s: len(s.pasos) if s else 0)
    sol_e = medir_alg("cobertura_exacta_dp", lambda: cobertura_exacta_dp(cob),
                      lambda s: s.costo if s else -1, "r", cob.r,
                      extra=lambda s: cob.n * (1 << cob.r))
    sol_ov = medir_alg("combinado_oblig_voraz",
                       lambda: combinado_cobertura_obligatoria(inst_comb, exacta=False),
                       lambda s: s.objetivo if s else -1, "B", caso.B_conjunto)
    sol_oe = medir_alg("combinado_oblig_exacta_dp",
                       lambda: combinado_cobertura_obligatoria_dp(inst_comb),
                       lambda s: s.objetivo if s else -1, "B", caso.B_conjunto)
    sol_h = medir_alg("combinado_heuristica_lambda",
                      lambda: combinado_heuristica(inst_comb),
                      lambda s: s.objetivo, "B", caso.B_conjunto)

    # --- informe
    L: list[str] = [f"# Traza del caso `{caso.nombre}`", ""]
    L += ["## 0. Entrada", ""]
    L += _tabla_md(["parámetro", "valor"], [
        ["etapas n", n],
        ["B (aceleración)", B],
        ["B conjunto (aceleración + auditoría)", caso.B_conjunto],
        ["categorías de riesgo r", cob.r],
        ["interacciones N (variaciones de auditoría)", cob.n],
        ["aristas del flujo m", caso.dag.m],
        ["flujo", "cadena (serie)" if caso.es_cadena else "DAG con paralelismo"],
        ["Σ t_i (sin acelerar)", sum(mo.t)],
        ["λ usado en la heurística", lam],
        ["repeticiones medidas", repeticiones],
    ])
    L.append("")

    L += ["## 1. Resumen de resultados y tiempos", ""]
    L += _tabla_md(["algoritmo", "tamaño", "tiempo (mediana)", "mín", "máx", "valor"], resumen_t)
    L += ["", "`valor` = duración (mochila, dag), Σa_j (cobertura) u objetivo (combinado).", ""]

    L += ["## 2. Parte 1 — Mochila 0/1 (aceleración)", ""]
    L += traza_mochila(caso, mo, f"DP exacta con B = {B}")

    L += ["## 3. Parte 2 — Cobertura de auditoría (interacciones = variaciones)", ""]
    L += traza_cobertura(caso, sol_v, "Voraz ponderado (A1): menor a_j / nuevas", True)
    if sol_v is not None:
        d = max(len(s) for s in cob.conjuntos)
        L.append(
            f"Cota teórica (Chvátal): costo(voraz) ≤ H_d · óptimo con d = {d}, "
            f"H_{d} = {numero_armonico(d):.3f}."
        )
        L.append("")
    L += traza_cobertura(caso, sol_e, "Exacto por DP sobre máscaras de categorías", False)
    if sol_v is not None and sol_e is not None:
        razon = sol_v.costo / sol_e.costo
        L.append(f"Razón voraz / óptimo = {sol_v.costo}/{sol_e.costo} = **{razon:.3f}**.")
        L.append("")

    L += ["## 4. Variante C — flujo como DAG (heurística)", ""]
    L.append(f"- Ruta crítica inicial: {' → '.join(caso.ids_etapas[i] for i in sol_dag.camino_inicial)} "
             f"(duración {sol_dag.duracion_inicial}).")
    if sol_dag.pasos:
        L += ["", *_tabla_md(
            ["paso", "etapa acelerada", "ruta crítica tras acelerar"],
            [[k, caso.ids_etapas[e], Lc] for k, (e, Lc) in enumerate(sol_dag.pasos, 1)],
        )]
    L.append("")
    L.append(f"- Etapas aceleradas: **{_ids(caso, sol_dag.aceleradas)}**, costo {sol_dag.costo} de B = {B}.")
    L.append(f"- Duración final: **{sol_dag.duracion}**.")
    if caso.es_cadena:
        L.append(
            f"- El flujo es una cadena, así que su duración óptima es la de la Mochila "
            f"({sol_m.duracion}). La heurística voraz obtuvo {sol_dag.duracion}"
            f"{' (coincide)' if sol_dag.duracion == sol_m.duracion else ' (no es óptima: la DP sí lo es)'}."
        )
    L.append("")

    L += ["## 5. Variante B — presupuesto conjunto", ""]
    L += _describe_combinada(
        caso, sol_oe, caso.B_conjunto,
        "Cobertura obligatoria (λ grande): cobertura de costo mínimo + Mochila con lo que sobra",
    )
    if sol_oe is not None:
        costo_cob = sum(cob.a[j] for j in sol_oe.interacciones)
        L += ["Mochila con el presupuesto restante:", ""]
        resto = InstanciaMochila(t=mo.t, c=mo.c, d=mo.d, B=caso.B_conjunto - costo_cob)
        L += traza_mochila(caso, resto, f"DP con B' = {caso.B_conjunto} − {costo_cob} = {resto.B}")
    L += _describe_combinada(
        caso, sol_ov, caso.B_conjunto, "Cobertura obligatoria con voraz ponderado (heurística)"
    )
    L += _describe_combinada(
        caso, sol_h, caso.B_conjunto, f"Heurística para λ general (λ = {lam})"
    )

    if verificar:
        L += ["## 6. Verificación", ""]
        if n <= 22:
            bf = mochila_fuerza_bruta(mo)
            ok = bf.duracion == sol_m.duracion
            L.append(f"- Mochila: fuerza bruta (2^{n}) = {bf.duracion}, DP = {sol_m.duracion} → "
                     f"**{'OK' if ok else 'DIFIERE'}**.")
        else:
            L.append(f"- Mochila: n = {n} es demasiado grande para fuerza bruta.")
        L.append("")

    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_md = carpeta / f"{caso.nombre}_traza.md"
    ruta_md.write_text("\n".join(L) + "\n", encoding="utf-8")
    escribir_tabla_dp(carpeta / f"{caso.nombre}_dp.csv", mo)
    escribir_csv(carpeta / f"{caso.nombre}_tiempos.csv", filas_csv)  # type: ignore[arg-type]
    print("\n".join(L))
    print(f"\n[escrito] {ruta_md}\n[escrito] {carpeta / (caso.nombre + '_dp.csv')}\n"
          f"[escrito] {carpeta / (caso.nombre + '_tiempos.csv')}")
    return ruta_md


def main(argv: list[str] | None = None) -> list[Path]:
    ap = argparse.ArgumentParser(description="Ejecuta casos JSON de la profesora.")
    ap.add_argument("rutas", nargs="+", type=Path, help="archivos .json o carpetas con .json")
    ap.add_argument("--lam", type=int, default=10, help="λ de la heurística de la Variante B")
    ap.add_argument("--repeticiones", type=int, default=7)
    ap.add_argument("--verificar", action="store_true", help="comparar la DP con fuerza bruta")
    ap.add_argument("--salida", type=Path, default=CARPETA_CASOS)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # la consola de Windows (cp1252) no tiene Σ, λ, →
        sys.stdout.reconfigure(encoding="utf-8")
    archivos: list[Path] = []
    for ruta in args.rutas:
        archivos += sorted(ruta.glob("*.json")) if ruta.is_dir() else [ruta]
    salidas = []
    for archivo in archivos:
        caso = cargar_caso(archivo)
        salidas.append(correr_caso(caso, args.lam, args.repeticiones, args.verificar, args.salida))
    return salidas


if __name__ == "__main__":
    main()
