"""Genera los casos de ejemplo del repositorio en ``casos/`` (JSON, índices base 1).

Son NUESTROS casos de ejemplo, reproducibles (semilla fija). Cuando se reciban los casos de la
profesora basta con copiarlos a ``casos/`` si usan este formato, o adaptar ``experimentos/casos.py``.

Uso:  python -m experimentos.generar_casos
"""

from __future__ import annotations

import json
from pathlib import Path

from core.generadores import generar_mochila, generar_set_cover
from core.instancias import InstanciaMochila, InstanciaSetCover
from experimentos.correr_casos import CASOS


def _p1(inst: InstanciaMochila) -> dict:
    return {"t": list(inst.t), "c": list(inst.c), "d": list(inst.d), "B": inst.B}


def _p2(inst: InstanciaSetCover, con_costos: bool = False) -> dict:
    d = {"r": inst.r, "conjuntos": [sorted(k + 1 for k in s) for s in inst.conjuntos]}
    if con_costos:
        d["costos"] = list(inst.a)
    return d


def _casos() -> list[dict]:
    etapa0_p1 = InstanciaMochila(t=(5, 8, 6, 4), c=(3, 4, 2, 3), d=(2, 4, 1, 2), B=6)
    etapa0_p2 = {"r": 5, "conjuntos": [[1, 2, 3], [2, 4], [3, 4], [4, 5], [1, 5]]}
    trampa = {"r": 6, "conjuntos": [[1, 2, 4, 5], [1, 2, 3], [4, 5, 6]]}
    return [
        {"id": "caso_01_etapa0",
         "descripcion": "Ejemplo de la Etapa 0: óptimo de la Parte 1 = {2, 3} (duración 23 → 18); "
                        "óptimo de la Parte 2 = {1, 4}.",
         "parte1": _p1(etapa0_p1), "parte2": etapa0_p2},
        {"id": "caso_02_trampa_voraz",
         "descripcion": "Parte 2 con la trampa clásica: el voraz elige primero el conjunto más grande y "
                        "usa 3 interacciones, el óptimo usa 2. Parte 1 de tamaño pequeño.",
         "parte1": _p1(generar_mochila(8, B=20, semilla=11, t_max=12, c_max=8)), "parte2": trampa},
        {"id": "caso_03_mediano",
         "descripcion": "Tamaño mediano generado con semilla 303 (verificable contra la fuerza bruta).",
         "parte1": _p1(generar_mochila(14, B=30, semilla=303, t_max=15, c_max=9)),
         "parte2": _p2(generar_set_cover(14, 12, semilla=303, prob=0.25))},
        {"id": "caso_04_costos_A1",
         "descripcion": "Variante A1: la auditoría tiene costo a_j por interacción (minimizar el costo total).",
         "parte1": _p1(generar_mochila(16, B=60, semilla=404, t_max=15, c_max=9)),
         "parte2": _p2(generar_set_cover(12, 10, semilla=404, prob=0.3, a_max=9), con_costos=True)},
        {"id": "caso_05_grande",
         "descripcion": "Tamaño grande (n = 300, B = 1500; 200 interacciones, 80 categorías): "
                        "muestra tiempos; sin verificación exacta.",
         "parte1": _p1(generar_mochila(300, B=1500, semilla=505, t_max=20, c_max=10)),
         "parte2": _p2(generar_set_cover(200, 80, semilla=505, prob=0.1))},
    ]


def main(destino: Path = CASOS) -> list[Path]:
    destino.mkdir(parents=True, exist_ok=True)
    rutas = []
    for caso in _casos():
        ruta = destino / f"{caso['id']}.json"
        ruta.write_text(json.dumps(caso, ensure_ascii=False) + "\n", encoding="utf-8")
        rutas.append(ruta)
    return rutas


if __name__ == "__main__":
    for r in main():
        print(r)
