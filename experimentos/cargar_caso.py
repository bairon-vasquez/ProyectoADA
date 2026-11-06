"""Lector de los casos de prueba de la profesora (JSON) -> instancias de ``core``.

Es I/O, por eso vive en ``experimentos/`` y no en ``core/``.

Correspondencia JSON -> modelo (índices 0-based; los ids "E01", "R01" se conservan
en las etiquetas para poder leer la traza):

    duracion_normal              -> t_i
    costo_aceleracion            -> c_i
    reduccion_tiempo_si_acelera  -> d_i
    presupuesto_aceleracion_B    -> B de la Mochila (Parte 1) y de la Variante C
    presupuesto_conjunto_...     -> B de la Variante B (aceleración + auditoría)
    flujo                        -> aristas (u, v) del DAG; si es una cadena, es la Mochila
    categorias_riesgo.importancia-> w_k
    variaciones_auditoria        -> UNA interacción j por cada variación (a_j = costo,
                                    S_j = riesgos_cubiertos). "E01-parcial" y "E01-completa"
                                    son dos interacciones distintas de la misma etapa.

Decisión de modelado: elegir a la vez "parcial" y "completa" de una etapa nunca conviene
cuando parcial ⊆ completa (se paga de más sin cubrir nada nuevo), así que tratar cada
variación como interacción independiente da el mismo óptimo que "una variación por etapa".
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from core.instancias import InstanciaDAG, InstanciaMochila, InstanciaSetCover


@dataclass(frozen=True)
class CasoProfesora:
    """Un caso de prueba ya traducido, con las etiquetas originales para la traza."""

    nombre: str
    ids_etapas: tuple[str, ...]
    ids_riesgos: tuple[str, ...]
    nombres_riesgos: tuple[str, ...]
    etiquetas_interacciones: tuple[str, ...]  # "E01-parcial", ...
    mochila: InstanciaMochila  # B = presupuesto_aceleracion_B
    cobertura: InstanciaSetCover
    dag: InstanciaDAG  # mismas etapas, aristas = flujo, B = presupuesto_aceleracion_B
    B_conjunto: int
    es_cadena: bool  # True si el flujo es una sola ruta E1 -> E2 -> ... -> En


def _es_cadena(n: int, aristas: tuple[tuple[int, int], ...]) -> bool:
    """True si las aristas son exactamente (0,1), (1,2), ..., (n-2, n-1) en algún orden. O(m)."""
    return set(aristas) == {(i, i + 1) for i in range(n - 1)} and len(aristas) == n - 1


def cargar_caso(ruta: Path) -> CasoProfesora:
    """Lee un JSON de la profesora y valida su consistencia básica. Lanza ValueError si falla."""
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    p = datos["parametros"]
    etapas = datos["etapas"]
    riesgos = datos["categorias_riesgo"]

    ids_etapas = tuple(e["id"] for e in etapas)
    ids_riesgos = tuple(r["id"] for r in riesgos)
    indice_etapa = {x: i for i, x in enumerate(ids_etapas)}
    indice_riesgo = {x: k for k, x in enumerate(ids_riesgos)}
    if len(indice_etapa) != len(ids_etapas) or len(indice_riesgo) != len(ids_riesgos):
        raise ValueError("ids de etapas o riesgos repetidos")
    if p.get("numero_etapas", len(etapas)) != len(etapas):
        raise ValueError("numero_etapas no coincide con la lista de etapas")
    if p.get("numero_categorias_riesgo", len(riesgos)) != len(riesgos):
        raise ValueError("numero_categorias_riesgo no coincide con categorias_riesgo")

    t = tuple(int(e["duracion_normal"]) for e in etapas)
    c = tuple(int(e["costo_aceleracion"]) for e in etapas)
    d = tuple(int(e["reduccion_tiempo_si_acelera"]) for e in etapas)
    B = int(p["presupuesto_aceleracion_B"])

    aristas = tuple(
        (indice_etapa[a["origen"]], indice_etapa[a["destino"]]) for a in datos["flujo"]
    )

    conjuntos: list[frozenset[int]] = []
    costos: list[int] = []
    etiquetas: list[str] = []
    for e in etapas:
        for v in e.get("variaciones_auditoria", []):
            conjuntos.append(frozenset(indice_riesgo[x] for x in v["riesgos_cubiertos"]))
            costos.append(int(v["costo"]))
            etiquetas.append(f'{e["id"]}-{v["id"]}')
    w = tuple(int(r["importancia"]) for r in riesgos)
    cobertura = InstanciaSetCover(
        r=len(riesgos), conjuntos=tuple(conjuntos), a=tuple(costos), w=w
    )

    return CasoProfesora(
        nombre=Path(ruta).stem,
        ids_etapas=ids_etapas,
        ids_riesgos=ids_riesgos,
        nombres_riesgos=tuple(r["categoria"] for r in riesgos),
        etiquetas_interacciones=tuple(etiquetas),
        mochila=InstanciaMochila(t=t, c=c, d=d, B=B),
        cobertura=cobertura,
        dag=InstanciaDAG(t=t, c=c, d=d, aristas=aristas, B=B),
        B_conjunto=int(p["presupuesto_conjunto_aceleracion_y_auditoria"]),
        es_cadena=_es_cadena(len(etapas), aristas),
    )
