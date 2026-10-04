"""Experimento Variante C: DAG. Escribe resultados/dag.csv.

- ruta_critica (incluye orden topológico), barrido n: m fijo   (T = O(n+m))
- ruta_critica,                             barrido m: n fijo
- dag_heuristica, barrido n y barrido m                       (T = O(n·(n+m)))
- dag_exacto,     barrido n                                   (T = O(2^n·(n+m)))

``valor_solucion`` = duración (ruta crítica) resultante. ``extra`` (solo dag_heuristica) =
(evaluaciones de la ruta crítica) × (n + m): nº de pasos del modelo fino del tiempo.

Uso:  python -m experimentos.correr_dag [--rapido]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from core.dag import dag_exacto, dag_heuristica, ruta_critica
from core.generadores import generar_dag
from experimentos.medir import RESULTADOS, escribir_csv, medir_caso

SEMILLA = 2026

COMPLETO = {
    "ruta_n": [250, 500, 1000, 2000, 4000, 8000], "ruta_m_fijo": 4000,
    "ruta_m": [1000, 2000, 4000, 8000, 16000, 32000], "ruta_n_fijo": 2000,
    "heur_n": [100, 200, 400, 800, 1600], "heur_m_fijo": 1600,
    "heur_m": [400, 800, 1600, 3200, 6400], "heur_n_fijo": 300,
    "exacto_n": [8, 10, 12, 14, 16], "reps": 7, "reps_exacto": 5,
}
RAPIDO = {
    "ruta_n": [20, 40, 80, 160, 320], "ruta_m_fijo": 150,
    "ruta_m": [50, 100, 200, 400, 800], "ruta_n_fijo": 100,
    "heur_n": [10, 20, 40, 80, 160], "heur_m_fijo": 40,
    "heur_m": [30, 60, 120, 240, 480], "heur_n_fijo": 40,
    "exacto_n": [4, 6, 8, 10, 12], "reps": 2, "reps_exacto": 2,
}


def _trabajo(inst):
    """(evaluaciones de ruta_critica) × (n+m); hay len(pasos) + 2 evaluaciones (inicial, una por paso, final)."""
    return lambda sol: (len(sol.pasos) + 2) * (inst.n + inst.m)


def main(rapido: bool = False, carpeta: Path = RESULTADOS) -> Path:
    cfg = RAPIDO if rapido else COMPLETO
    filas: list[dict] = []
    dur = lambda sol: sol.duracion  # noqa: E731
    ruta = lambda rc: rc.longitud  # noqa: E731

    for n in cfg["ruta_n"]:
        inst = generar_dag(n, cfg["ruta_m_fijo"], semilla=SEMILLA + n)
        x = [0] * n
        filas += medir_caso("ruta_critica", "n", n, "m", inst.m,
                            lambda i=inst, x=x: ruta_critica(i, x), ruta, repeticiones=cfg["reps"])
    for m in cfg["ruta_m"]:
        inst = generar_dag(cfg["ruta_n_fijo"], m, semilla=SEMILLA + m)
        x = [0] * inst.n
        filas += medir_caso("ruta_critica", "m", inst.n, "m", m,
                            lambda i=inst, x=x: ruta_critica(i, x), ruta, repeticiones=cfg["reps"])

    for n in cfg["heur_n"]:
        inst = generar_dag(n, cfg["heur_m_fijo"], semilla=SEMILLA + n)
        filas += medir_caso("dag_heuristica", "n", n, "m", inst.m,
                            lambda i=inst: dag_heuristica(i), dur,
                            extra=_trabajo(inst), repeticiones=cfg["reps"])
    for m in cfg["heur_m"]:
        inst = generar_dag(cfg["heur_n_fijo"], m, semilla=SEMILLA + m)
        filas += medir_caso("dag_heuristica", "m", inst.n, "m", m,
                            lambda i=inst: dag_heuristica(i), dur,
                            extra=_trabajo(inst), repeticiones=cfg["reps"])

    for n in cfg["exacto_n"]:
        inst = generar_dag(n, min(2 * n, n * (n - 1) // 2), semilla=SEMILLA + n)
        filas += medir_caso("dag_exacto", "n", n, "m", inst.m,
                            lambda i=inst: dag_exacto(i), dur, repeticiones=cfg["reps_exacto"])

    destino = carpeta / "dag.csv"
    escribir_csv(destino, filas)
    return destino


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="tamaños pequeños (prueba de humo)")
    print(main(ap.parse_args().rapido))
