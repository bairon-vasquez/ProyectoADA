"""Dibujos para la app: tabla DP, cobertura paso a paso y DAG con ruta crítica.

Capa 3: solo dibuja resultados que ya calcularon los algoritmos de ``core``; no mide nada.
Cada función devuelve una figura de matplotlib. Misma paleta que ``graficas.py``.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

from core.dag import preparar_dag  # noqa: E402
from core.instancias import InstanciaDAG, InstanciaMochila, InstanciaSetCover  # noqa: E402
from visualizacion.graficas import (  # noqa: E402
    AQUA, AZUL, EJE, NARANJA, REJILLA, SUPERFICIE, TINTA, TINTA_2, TINTA_3, _estilo,
)

RAMPA_AZUL = LinearSegmentedColormap.from_list(
    "azul", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])


# ------------------------------------------------------------------------------ Mochila

def camino_reconstruccion(inst: InstanciaMochila, tabla: list[list[int]]) -> list[tuple[int, int, bool]]:
    """Celdas (i, b) visitadas al reconstruir, con ``True`` si la etapa i se tomó.

    Misma lógica que ``core.mochila.reconstruir_etapas``, pero conservando el recorrido.
    """
    b = inst.B
    camino = []
    for i in range(inst.n, 0, -1):
        tomada = tabla[i][b] != tabla[i - 1][b]
        camino.append((i, b, tomada))
        if tomada:
            b -= inst.c[i - 1]
    camino.append((0, b, False))
    return camino


def fig_tabla_dp(inst: InstanciaMochila, tabla: list[list[int]], nombres: list[str] | None = None):
    """Mapa de calor de DP[i][b]: más oscuro = más reducción; el camino de reconstrucción se resalta."""
    _estilo()
    n, B = inst.n, inst.B
    datos = np.array(tabla, dtype=float)
    camino = camino_reconstruccion(inst, tabla)
    ancho = min(15.0, 0.5 * (B + 1) + 3.2)
    fig, ax = plt.subplots(figsize=(ancho, 0.55 * (n + 1) + 1.8), constrained_layout=True)
    ax.imshow(datos, cmap=RAMPA_AZUL, aspect="auto", vmin=0, vmax=max(1.0, datos.max()))
    ax.grid(False)
    if B <= 30:
        for i in range(n + 1):
            for b in range(B + 1):
                v = tabla[i][b]
                ax.text(b, i, str(v), ha="center", va="center", fontsize=8.5,
                        color="white" if v > 0.5 * datos.max() else TINTA)
    for (i, b, tomada) in camino:  # anillo naranja en las celdas del recorrido
        ax.add_patch(Rectangle((b - 0.5, i - 0.5), 1, 1, fill=False, ec=NARANJA,
                               lw=3.0 if tomada else 1.6, zorder=5))
    etiquetas = ["0 · sin etapas"] + [
        (f"{i + 1}" if nombres is None else f"{i + 1} · {nombres[i]}") + f"  (c={inst.c[i]}, d={inst.d[i]})"
        for i in range(n)]
    ax.set_yticks(range(n + 1)); ax.set_yticklabels(etiquetas, fontsize=8.5)
    ax.set_xticks(range(0, B + 1, max(1, (B + 1) // 20)))
    ax.set_xlabel("presupuesto b"); ax.set_ylabel("etapas consideradas (primeras i)")
    ax.set_title("DP[i][b] = máxima reducción de tiempo", loc="left", fontsize=10.5)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.legend(handles=[Line2D([0], [0], color=NARANJA, lw=3, label="recorrido de la reconstrucción"
                               " (trazo grueso = etapa elegida)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False)
    return fig


# --------------------------------------------------------------------------- Set Cover

def fig_cobertura(inst: InstanciaSetCover, indices: tuple[int, ...], paso: int, titulo: str):
    """Matriz interacciones × categorías tras ``paso`` elecciones de ``indices``.

    Azul fuerte = celda de un conjunto ya elegido; azul claro = categoría aún sin cubrir
    que pertenece al conjunto; gris = categoría ya cubierta por otro conjunto elegido.
    """
    _estilo()
    n, r = inst.n, inst.r
    elegidos = list(indices[:paso])
    cubierta = [False] * r
    for j in elegidos:
        for k in inst.conjuntos[j]:
            cubierta[k] = True
    ponderado = any(a != 1 for a in inst.a)
    fig, ax = plt.subplots(figsize=(min(13.0, 0.42 * r + 3.4), 0.42 * n + 1.9), constrained_layout=True)
    ax.set_xlim(-0.5, r - 0.5); ax.set_ylim(n - 0.5, -1.4)
    ax.grid(False)
    for j in range(n):
        for k in range(r):
            if k in inst.conjuntos[j]:
                if j in elegidos:
                    color = AZUL
                elif cubierta[k]:
                    color = EJE
                else:
                    color = "#cde2fb"
                ax.add_patch(Rectangle((k - 0.46, j - 0.44), 0.92, 0.88, fc=color, ec="none"))
            else:
                ax.add_patch(Rectangle((k - 0.46, j - 0.44), 0.92, 0.88, fc=SUPERFICIE, ec=REJILLA, lw=0.6))
    for k in range(r):  # fila de encabezado: ● cubierta, ○ sin cubrir
        ax.text(k, -1.0, "●" if cubierta[k] else "○", ha="center", va="center", fontsize=11,
                color=AQUA if cubierta[k] else TINTA_3)
    ax.set_xticks(range(r)); ax.set_xticklabels([str(k + 1) for k in range(r)], fontsize=8.5)
    etiquetas = []
    for j in range(n):
        base = f"S{j + 1}" + (f"  (a={inst.a[j]})" if ponderado else "")
        etiquetas.append(("★ " if j in elegidos else "   ") + base)
    ax.set_yticks(range(n)); ax.set_yticklabels(etiquetas, fontsize=9)
    for lab, j in zip(ax.get_yticklabels(), range(n)):
        lab.set_fontweight("bold" if j in elegidos else "normal")
        lab.set_color(TINTA if j in elegidos else TINTA_2)
    ax.set_xlabel("categoría de riesgo (● cubierta · ○ sin cubrir)")
    n_cub = sum(cubierta)
    ax.set_title(f"{titulo} — {len(elegidos)} elegidos, {n_cub}/{r} categorías cubiertas",
                 loc="left", fontsize=10.5)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.legend(handles=[Patch(fc=AZUL, label="conjunto elegido"),
                       Patch(fc="#cde2fb", label="categoría aún sin cubrir"),
                       Patch(fc=EJE, label="ya cubierta por otro conjunto")],
              loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False, fontsize=8.5)
    return fig


# -------------------------------------------------------------------------------- DAG

def capas_dag(inst: InstanciaDAG) -> list[int]:
    """Capa de cada nodo = longitud (en aristas) del camino más largo que llega a él. O(n+m)."""
    prep = preparar_dag(inst.n, inst.aristas)
    capa = [0] * inst.n
    for u in prep.orden:
        for v in prep.sucesores[u]:
            capa[v] = max(capa[v], capa[u] + 1)
    return capa


def posiciones_dag(inst: InstanciaDAG) -> dict[int, tuple[float, float]]:
    capa = capas_dag(inst)
    por_capa: dict[int, list[int]] = {}
    for v, c in enumerate(capa):
        por_capa.setdefault(c, []).append(v)
    pos = {}
    for c, nodos in por_capa.items():
        for k, v in enumerate(nodos):
            pos[v] = (float(c), (len(nodos) - 1) / 2.0 - k)
    return pos


def fig_dag(
    inst: InstanciaDAG,
    x: list[int] | tuple[int, ...],
    camino: tuple[int, ...],
    longitud: int,
    titulo: str,
    nombres: list[str] | None = None,
):
    """Grafo con la ruta crítica (naranja) y las etapas aceleradas (relleno turquesa).

    Cada nodo muestra su nombre y la duración efectiva τ = t − d·x.
    """
    _estilo()
    n = inst.n
    nombres = nombres or [str(i + 1) for i in range(n)]
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(inst.aristas)
    pos = posiciones_dag(inst)
    en_ruta = set(camino)
    aristas_ruta = set(zip(camino, camino[1:]))
    capas = max(c for c, _ in pos.values()) + 1 if pos else 1
    alto = max((abs(y) for _, y in pos.values()), default=0) * 2 + 1
    fig, ax = plt.subplots(figsize=(max(6.0, 2.1 * capas + 1.5), max(3.2, 1.1 * alto + 1.6)),
                           constrained_layout=True)
    ax.set_axis_off()
    nx.draw_networkx_edges(
        G, pos, ax=ax, edgelist=[e for e in G.edges if e not in aristas_ruta],
        edge_color=EJE, width=1.4, arrows=True, arrowsize=14, node_size=1900,
        connectionstyle="arc3,rad=0.0")
    nx.draw_networkx_edges(
        G, pos, ax=ax, edgelist=[e for e in G.edges if e in aristas_ruta],
        edge_color=NARANJA, width=3.4, arrows=True, arrowsize=18, node_size=1900)
    colores = [("#a8e6cf" if x[v] else SUPERFICIE) for v in range(n)]
    bordes = [(NARANJA if v in en_ruta else AZUL) for v in range(n)]
    anchos = [3.2 if v in en_ruta else 1.6 for v in range(n)]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1900, node_color=colores,
                           edgecolors=bordes, linewidths=anchos)
    for v in range(n):
        px, py = pos[v]
        tau = inst.t[v] - inst.d[v] * x[v]
        ax.text(px, py + 0.06, nombres[v], ha="center", va="center", fontsize=12,
                fontweight="bold", color=TINTA, zorder=10)
        ax.text(px, py - 0.2, f"τ={tau}" + (f" (t={inst.t[v]})" if x[v] else ""), ha="center",
                va="center", fontsize=8, color=TINTA_2, zorder=10)
    ax.set_title(f"{titulo} — duración de la ruta crítica L = {longitud}", loc="left",
                 fontsize=11, fontweight="bold")
    ax.margins(0.18)
    ax.legend(handles=[Line2D([0], [0], color=NARANJA, lw=3.4, label="ruta crítica"),
                       Patch(fc="#a8e6cf", ec=AZUL, label="etapa acelerada"),
                       Patch(fc=SUPERFICIE, ec=AZUL, label="etapa sin acelerar")],
              loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, frameon=False, fontsize=8.5)
    return fig
