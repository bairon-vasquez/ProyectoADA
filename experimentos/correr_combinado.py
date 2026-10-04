"""Experimento Variante B: combinado. Escribe resultados/combinado.csv.

- combinado_heuristica, barrido n: B, N, r fijos       (T = O(n·B + N·r·min(N,r)))
- combinado_heuristica, barrido B: n, N, r fijos
- combinado_exacto,     barrido N: n, B, r fijos       (T = O(n·B + 2^N·N·r))

``parametro``/``valor_parametro`` es B en los barridos de la heurística y N en el del
exacto. ``valor_solucion`` = valor del objetivo.

Uso:  python -m experimentos.correr_combinado [--rapido]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from core.combinado import combinado_exacto, combinado_heuristica
from core.generadores import generar_combinada
from core.instancias import InstanciaCombinada
from experimentos.medir import RESULTADOS, escribir_csv, medir_caso

SEMILLA = 2026

COMPLETO = {
    "n": [100, 200, 400, 800, 1600], "B_fijo": 1000, "N": 60, "r": 40,
    "B": [250, 500, 1000, 2000, 4000], "n_fijo": 400,
    "N_exacto": [6, 8, 10, 12, 14], "n_exacto": 20, "B_exacto": 100, "r_exacto": 12,
    "lam": 3, "reps": 7, "reps_exacto": 5,
}
RAPIDO = {
    "n": [10, 20, 40, 80, 160], "B_fijo": 50, "N": 10, "r": 8,
    "B": [25, 50, 100, 200, 400], "n_fijo": 20,
    "N_exacto": [4, 6, 8, 10, 12], "n_exacto": 8, "B_exacto": 30, "r_exacto": 6,
    "lam": 3, "reps": 2, "reps_exacto": 2,
}


def _con(base: InstanciaCombinada, B: int, lam: int) -> InstanciaCombinada:
    return InstanciaCombinada(cadena=base.cadena, cobertura=base.cobertura, B=B, lam=lam)


def main(rapido: bool = False, carpeta: Path = RESULTADOS) -> Path:
    cfg = RAPIDO if rapido else COMPLETO
    filas: list[dict] = []
    obj = lambda sol: sol.objetivo  # noqa: E731

    for n in cfg["n"]:
        inst = _con(generar_combinada(n, cfg["N"], cfg["r"], semilla=SEMILLA + n),
                    cfg["B_fijo"], cfg["lam"])
        filas += medir_caso("combinado_heuristica", "n", n, "B", inst.B,
                            lambda i=inst: combinado_heuristica(i), obj, repeticiones=cfg["reps"])
    for B in cfg["B"]:
        inst = _con(generar_combinada(cfg["n_fijo"], cfg["N"], cfg["r"], semilla=SEMILLA + B),
                    B, cfg["lam"])
        filas += medir_caso("combinado_heuristica", "B", inst.cadena.n, "B", B,
                            lambda i=inst: combinado_heuristica(i), obj, repeticiones=cfg["reps"])
    for N in cfg["N_exacto"]:
        inst = _con(generar_combinada(cfg["n_exacto"], N, cfg["r_exacto"], semilla=SEMILLA + N),
                    cfg["B_exacto"], cfg["lam"])
        filas += medir_caso("combinado_exacto", "N", inst.cadena.n, "N", N,
                            lambda i=inst: combinado_exacto(i), obj,
                            repeticiones=cfg["reps_exacto"])

    destino = carpeta / "combinado.csv"
    escribir_csv(destino, filas)
    return destino


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="tamaños pequeños (prueba de humo)")
    print(main(ap.parse_args().rapido))
