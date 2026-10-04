"""Experimento de calidad (no de tiempo): razón heurística / óptimo.

Escribe en resultados/:
- razon_set_cover.csv    : voraz y voraz ponderado vs. exacto en instancias aleatorias pequeñas
- razon_set_cover_adv.csv: familia adversarial (el voraz se aleja del óptimo ~ log r)
- razon_dag.csv          : heurística vs. exacto en DAG pequeños
- razon_combinado.csv    : heurística vs. exacto en la Variante B

Uso:  python -m experimentos.correr_razones [--rapido]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from core.combinado import combinado_exacto, combinado_heuristica
from core.dag import dag_exacto, dag_heuristica
from core.generadores import (
    generar_combinada,
    generar_dag,
    generar_set_cover,
    generar_set_cover_adversarial,
)
from core.instancias import InstanciaCombinada
from core.set_cover import (
    cobertura_exacta,
    cobertura_exacta_ponderada,
    cobertura_voraz,
    cobertura_voraz_ponderada,
    numero_armonico,
)
from experimentos.medir import RESULTADOS, escribir_csv

SEMILLA = 7000


def _razon(heur: float, opt: float) -> float:
    return 1.0 if opt == 0 else heur / opt


def main(rapido: bool = False, carpeta: Path = RESULTADOS) -> list[Path]:
    semillas = 8 if rapido else 40
    rs = [4, 6, 8] if rapido else [4, 6, 8, 10, 12, 14, 16]
    ks = range(1, 6) if rapido else range(1, 11)

    # --- Set Cover aleatorio (n ≤ 15 para que el exacto sea viable)
    cols = ["variante", "semilla", "n", "r", "d", "heuristica", "optimo", "razon", "H_r", "H_d"]
    filas = []
    for r in rs:
        for s in range(semillas):
            n = 8 + s % 5
            inst = generar_set_cover(n, r, semilla=SEMILLA + 100 * r + s, prob=0.15 + 0.05 * (s % 4))
            d = max(len(c) for c in inst.conjuntos)
            v, e = cobertura_voraz(inst), cobertura_exacta(inst)
            filas.append(dict(variante="voraz", semilla=s, n=n, r=r, d=d, heuristica=v.tamano,
                              optimo=e.tamano, razon=_razon(v.tamano, e.tamano),
                              H_r=numero_armonico(r), H_d=numero_armonico(d)))
            instp = generar_set_cover(n, r, semilla=SEMILLA + 100 * r + s, prob=0.15 + 0.05 * (s % 4), a_max=9)
            dp = max(len(c) for c in instp.conjuntos)
            vp, ep = cobertura_voraz_ponderada(instp), cobertura_exacta_ponderada(instp)
            filas.append(dict(variante="voraz_ponderado", semilla=s, n=n, r=r, d=dp, heuristica=vp.costo,
                              optimo=ep.costo, razon=_razon(vp.costo, ep.costo),
                              H_r=numero_armonico(r), H_d=numero_armonico(dp)))
    rutas = [carpeta / "razon_set_cover.csv"]
    escribir_csv(rutas[0], filas, cols)

    # --- Familia adversarial (óptimo conocido = 2, verificado con el exacto)
    filas = []
    for k in ks:
        inst = generar_set_cover_adversarial(k)
        v, e = cobertura_voraz(inst), cobertura_exacta(inst)
        d = max(len(c) for c in inst.conjuntos)
        filas.append(dict(variante="adversarial", semilla=0, n=inst.n, r=inst.r, d=d,
                          heuristica=v.tamano, optimo=e.tamano, razon=_razon(v.tamano, e.tamano),
                          H_r=numero_armonico(inst.r), H_d=numero_armonico(d)))
    rutas.append(carpeta / "razon_set_cover_adv.csv")
    escribir_csv(rutas[1], filas, cols)

    # --- DAG: heurística vs. exacto
    cols_dag = ["semilla", "n", "m", "B", "duracion_inicial", "heuristica", "optimo", "razon"]
    filas = []
    for n in ([5, 7] if rapido else [5, 6, 7, 8, 9, 10, 11, 12]):
        for s in range(semillas):
            inst = generar_dag(n, min(n * (n - 1) // 2, 2 * n), semilla=SEMILLA + 100 * n + s,
                               fraccion_presupuesto=0.2 + 0.1 * (s % 4))
            h, e = dag_heuristica(inst), dag_exacto(inst)
            filas.append(dict(semilla=s, n=n, m=inst.m, B=inst.B, duracion_inicial=e.duracion_inicial,
                              heuristica=h.duracion, optimo=e.duracion, razon=_razon(h.duracion, e.duracion)))
    rutas.append(carpeta / "razon_dag.csv")
    escribir_csv(rutas[2], filas, cols_dag)

    # --- Variante B: heurística vs. exacto, varios λ
    cols_b = ["semilla", "n", "N", "r", "lam", "B", "heuristica", "optimo", "razon"]
    filas = []
    for lam in (1, 3, 10, 30):
        for s in range(semillas):
            base = generar_combinada(8, 8 + s % 4, 6, semilla=SEMILLA + s, fraccion_presupuesto=0.3 + 0.1 * (s % 4))
            inst = InstanciaCombinada(cadena=base.cadena, cobertura=base.cobertura, B=base.B, lam=lam)
            h, e = combinado_heuristica(inst), combinado_exacto(inst)
            filas.append(dict(semilla=s, n=8, N=inst.cobertura.n, r=6, lam=lam, B=inst.B,
                              heuristica=h.objetivo, optimo=e.objetivo, razon=_razon(h.objetivo, e.objetivo)))
    rutas.append(carpeta / "razon_combinado.csv")
    escribir_csv(rutas[3], filas, cols_b)
    return rutas


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="menos instancias (prueba de humo)")
    for ruta in main(ap.parse_args().rapido):
        print(ruta)
