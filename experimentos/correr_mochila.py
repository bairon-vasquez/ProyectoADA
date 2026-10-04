"""Experimento Parte 1: Mochila. Escribe resultados/mochila.csv.

- mochila_dp, barrido n   : B fijo, n creciente         (T = Θ(n·B), lineal en n)
- mochila_dp, barrido B   : n fijo, B creciente         (T = Θ(n·B), lineal en B)
- mochila_fuerza_bruta    : n creciente                 (T = Θ(n·2^n))

Uso:  python -m experimentos.correr_mochila [--rapido]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from core.generadores import generar_mochila
from core.mochila import mochila_dp, mochila_fuerza_bruta
from experimentos.medir import RESULTADOS, escribir_csv, medir_caso

SEMILLA = 2026

COMPLETO = {
    "dp_n": [100, 200, 400, 800, 1600, 3200], "dp_B_fijo": 1000,
    "dp_B": [250, 500, 1000, 2000, 4000, 8000], "dp_n_fijo": 500,
    "fb_n": [8, 10, 12, 14, 16, 18], "reps": 7, "reps_fb": 5,
}
RAPIDO = {
    "dp_n": [10, 20, 40, 80, 160], "dp_B_fijo": 50,
    "dp_B": [25, 50, 100, 200, 400], "dp_n_fijo": 30,
    "fb_n": [4, 6, 8, 10, 12], "reps": 2, "reps_fb": 2,
}


def main(rapido: bool = False, carpeta: Path = RESULTADOS) -> Path:
    cfg = RAPIDO if rapido else COMPLETO
    filas: list[dict] = []
    valor = lambda sol: sol.duracion  # noqa: E731

    for n in cfg["dp_n"]:
        inst = generar_mochila(n, B=cfg["dp_B_fijo"], semilla=SEMILLA + n)
        filas += medir_caso("mochila_dp", "n", n, "B", inst.B,
                            lambda i=inst: mochila_dp(i), valor, repeticiones=cfg["reps"])
    for B in cfg["dp_B"]:
        inst = generar_mochila(cfg["dp_n_fijo"], B=B, semilla=SEMILLA + B)
        filas += medir_caso("mochila_dp", "B", inst.n, "B", B,
                            lambda i=inst: mochila_dp(i), valor, repeticiones=cfg["reps"])
    for n in cfg["fb_n"]:
        inst = generar_mochila(n, semilla=SEMILLA + n)
        filas += medir_caso("mochila_fuerza_bruta", "n", n, "B", inst.B,
                            lambda i=inst: mochila_fuerza_bruta(i), valor,
                            repeticiones=cfg["reps_fb"])

    ruta = carpeta / "mochila.csv"
    escribir_csv(ruta, filas)
    return ruta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="tamaños pequeños (prueba de humo)")
    print(main(ap.parse_args().rapido))
