"""Ejecuta todos los experimentos en orden.  Uso:  python -m experimentos.correr_todo [--rapido]"""

from __future__ import annotations

import argparse
import time

from experimentos import (
    correr_combinado,
    correr_dag,
    correr_mochila,
    correr_razones,
    correr_set_cover,
)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="tamaños pequeños (prueba de humo)")
    rapido = ap.parse_args().rapido
    for modulo in (correr_mochila, correr_set_cover, correr_dag, correr_combinado, correr_razones):
        t0 = time.perf_counter()
        salida = modulo.main(rapido)
        print(f"{modulo.__name__}: {salida}  ({time.perf_counter() - t0:.1f} s)")
