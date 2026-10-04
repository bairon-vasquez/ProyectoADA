"""Utilidades de medición. ÚNICO lugar del proyecto donde se miden tiempos.

Protocolo: una llamada de calentamiento (no se registra), luego ``repeticiones``
llamadas medidas con ``time.perf_counter`` y con el recolector de basura
apagado durante la medición. La instancia se genera ANTES de medir: el tiempo
registrado es solo el del algoritmo.
"""

from __future__ import annotations

import csv
import gc
import statistics
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

RESULTADOS = Path(__file__).parent / "resultados"

# algoritmo      : nombre del algoritmo medido
# barrido        : qué parámetro se varía en ese experimento ("n", "B", "r", "m", "N")
# n              : tamaño n de la instancia
# parametro      : nombre del segundo parámetro de tamaño ("B", "r", "m", "N"; "-" si no hay)
# valor_parametro: valor de ese segundo parámetro
# repeticion     : 1..R
# tiempo_s       : segundos de UNA ejecución
# valor_solucion : valor objetivo de la solución (duración, nº de interacciones, etc.)
# extra          : dato auxiliar numérico que depende del algoritmo (ver cada correr_*.py);
#                  0 si no aplica
COLUMNAS = [
    "algoritmo", "barrido", "n", "parametro", "valor_parametro",
    "repeticion", "tiempo_s", "valor_solucion", "extra",
]


def medir(
    funcion: Callable[[], Any], repeticiones: int = 7, calentamiento: int = 1
) -> tuple[list[float], Any]:
    """Ejecuta ``funcion`` y devuelve (tiempos en segundos, resultado de la última llamada)."""
    resultado = None
    for _ in range(calentamiento):
        resultado = funcion()
    tiempos: list[float] = []
    gc.collect()
    gc.disable()
    try:
        for _ in range(repeticiones):
            inicio = time.perf_counter()
            resultado = funcion()
            tiempos.append(time.perf_counter() - inicio)
    finally:
        gc.enable()
    return tiempos, resultado


def mediana(tiempos: list[float]) -> float:
    return statistics.median(tiempos)


def medir_caso(
    algoritmo: str,
    barrido: str,
    n: int,
    parametro: str,
    valor_parametro: int,
    funcion: Callable[[], Any],
    valor: Callable[[Any], float],
    extra: float | Callable[[Any], float] = 0,
    repeticiones: int = 7,
) -> list[dict[str, Any]]:
    """Mide ``funcion`` y devuelve una fila por repetición, lista para el CSV."""
    tiempos, resultado = medir(funcion, repeticiones)
    v = valor(resultado)
    e = extra(resultado) if callable(extra) else extra
    return [
        {
            "algoritmo": algoritmo, "barrido": barrido, "n": n,
            "parametro": parametro, "valor_parametro": valor_parametro,
            "repeticion": k + 1, "tiempo_s": f"{t:.9f}", "valor_solucion": v, "extra": e,
        }
        for k, t in enumerate(tiempos)
    ]


def escribir_csv(ruta: Path, filas: list[dict[str, Any]], columnas: list[str] = COLUMNAS) -> None:
    """Escribe (sobrescribe) un CSV con las columnas dadas."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
