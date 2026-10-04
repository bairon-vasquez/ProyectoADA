"""Experimento Parte 2 y Variante A1: Set Cover. Escribe resultados/set_cover.csv.

- cobertura_voraz / voraz_ponderada, barrido n : r fijo, n creciente   (T = O(n·r²))
- cobertura_voraz / voraz_ponderada, barrido r : n fijo, r creciente
- cobertura_exacta (Parte 2)       , barrido n : r fijo, n creciente   (exponencial en n)
- cobertura_exacta_ponderada       , barrido n : (2^n·n·r)

``valor_solucion`` = tamaño (o costo) de la cobertura. ``extra``:
- voraz y voraz ponderado: rondas × Σ|S_j| = nº EXACTO de iteraciones del ciclo interno
  dominante (modelo fino del tiempo, a contrastar con la cota de peor caso n·r²);
- exactos: Σ|S_j| (tamaño de la entrada).

Uso:  python -m experimentos.correr_set_cover [--rapido]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from core.generadores import generar_set_cover
from core.set_cover import (
    cobertura_exacta,
    cobertura_exacta_ponderada,
    cobertura_voraz,
    cobertura_voraz_ponderada,
)
from experimentos.medir import RESULTADOS, escribir_csv, medir_caso

SEMILLA = 2026

COMPLETO = {
    "voraz_n": [100, 200, 400, 800, 1600, 3200], "voraz_r_fijo": 100,
    "voraz_r": [50, 100, 200, 400, 800, 1600], "voraz_n_fijo": 400,
    "exacto_n": [12, 14, 16, 18, 20, 22], "exacto_r": 24, "exacto_prob": 0.10,
    "expond_n": [8, 10, 12, 14, 16], "expond_r": 20,
    "reps": 7, "reps_exacto": 3,
}
RAPIDO = {
    "voraz_n": [10, 20, 40, 80, 160], "voraz_r_fijo": 20,
    "voraz_r": [10, 20, 40, 80, 160], "voraz_n_fijo": 30,
    "exacto_n": [6, 8, 10, 12, 14], "exacto_r": 10, "exacto_prob": 0.2,
    "expond_n": [4, 6, 8, 10, 12], "expond_r": 10,
    "reps": 2, "reps_exacto": 2,
}


def _entrada(inst) -> int:
    return sum(len(s) for s in inst.conjuntos)


def _trabajo_voraz(inst):
    """Función que, dado el resultado del voraz, devuelve rondas × Σ|S_j|."""
    total = _entrada(inst)
    return lambda sol: len(sol.indices) * total


def main(rapido: bool = False, carpeta: Path = RESULTADOS) -> Path:
    cfg = RAPIDO if rapido else COMPLETO
    filas: list[dict] = []
    tam = lambda sol: sol.tamano  # noqa: E731
    costo = lambda sol: sol.costo  # noqa: E731

    # Voraz y voraz ponderado: mismo tamaño de instancia (a_max=9 para A1).
    for barrido, valores in (("n", cfg["voraz_n"]), ("r", cfg["voraz_r"])):
        for v in valores:
            n, r = (v, cfg["voraz_r_fijo"]) if barrido == "n" else (cfg["voraz_n_fijo"], v)
            inst = generar_set_cover(n, r, semilla=SEMILLA + n + r)
            instp = generar_set_cover(n, r, semilla=SEMILLA + n + r, a_max=9)
            filas += medir_caso("cobertura_voraz", barrido, n, "r", r,
                                lambda i=inst: cobertura_voraz(i), tam,
                                extra=_trabajo_voraz(inst), repeticiones=cfg["reps"])
            filas += medir_caso("cobertura_voraz_ponderada", barrido, n, "r", r,
                                lambda i=instp: cobertura_voraz_ponderada(i), costo,
                                extra=_trabajo_voraz(instp), repeticiones=cfg["reps"])

    for n in cfg["exacto_n"]:
        inst = generar_set_cover(n, cfg["exacto_r"], semilla=SEMILLA + n, prob=cfg["exacto_prob"])
        filas += medir_caso("cobertura_exacta", "n", n, "r", cfg["exacto_r"],
                            lambda i=inst: cobertura_exacta(i), tam,
                            extra=_entrada(inst), repeticiones=cfg["reps_exacto"])
    for n in cfg["expond_n"]:
        inst = generar_set_cover(n, cfg["expond_r"], semilla=SEMILLA + n, a_max=9)
        filas += medir_caso("cobertura_exacta_ponderada", "n", n, "r", cfg["expond_r"],
                            lambda i=inst: cobertura_exacta_ponderada(i), costo,
                            extra=_entrada(inst), repeticiones=cfg["reps_exacto"])

    ruta = carpeta / "set_cover.csv"
    escribir_csv(ruta, filas)
    return ruta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="tamaños pequeños (prueba de humo)")
    print(main(ap.parse_args().rapido))
