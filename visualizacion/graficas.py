"""Gráficas matplotlib -> PNG en figuras/. Capa 3: solo LEE los CSV, nunca mide.

Una figura de tres paneles por serie experimental:
  A. tiempo medido (mediana, con rango mín.–máx.) vs. curva teórica escalada c·T(n);
  B. cociente medido / (c·T): debe ser ≈ 1 (constante) si el T(n) deducido es correcto;
  C. escala log-log con la pendiente estimada (series polinomiales) o semilog con el
     factor de crecimiento por +1 (series exponenciales).
Más: razón voraz/óptimo vs. H_r, razón de las heurísticas, resumen de pendientes y la tabla
de ajustes. Paleta validada con scripts/validate_palette.js (slots 1-3, todos los pares).

Uso:  python -m visualizacion.graficas
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo PNG
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from core.set_cover import numero_armonico  # noqa: E402  (solo H_k, función matemática)
from experimentos.medir import RESULTADOS  # noqa: E402
from visualizacion import ajuste as aj  # noqa: E402

FIGURAS = Path(__file__).resolve().parent.parent / "figuras"

# --- tokens de color (paleta de referencia, modo claro) -------------------------------
SUPERFICIE = "#fcfcfb"
TINTA, TINTA_2, TINTA_3 = "#0b0b0b", "#52514e", "#898781"
REJILLA, EJE = "#e1e0d9", "#c3c2b7"
AZUL, NARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"  # slots 1-3 (validados all-pairs)
COLORES_MODELO = [NARANJA, AQUA]
MARCAS_MODELO = ["", "s"]  # el 2.º modelo lleva marcador propio (codificación secundaria)

XLABEL = {
    "n": "n (tamaño de la instancia)", "B": "B (presupuesto)", "r": "r (categorías)",
    "m": "m (aristas)", "N": "N (interacciones)",
}


def _estilo() -> None:
    plt.rcParams.update({
        "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
        "font.family": "DejaVu Sans", "font.size": 9.5,
        "text.color": TINTA, "axes.labelcolor": TINTA_2, "axes.titlecolor": TINTA,
        "xtick.color": TINTA_3, "ytick.color": TINTA_3,
        "axes.edgecolor": EJE, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True, "grid.color": REJILLA, "grid.linewidth": 0.8,
        "grid.linestyle": "-", "axes.grid.axis": "y",
        "legend.frameon": False, "legend.fontsize": 8.5,
        "lines.linewidth": 1.6, "lines.markersize": 6.5,
    })


def _unidad(tmax: float) -> tuple[float, str]:
    """Factor y etiqueta de unidad para que los números del eje sean legibles."""
    if tmax >= 1:
        return 1.0, "s"
    if tmax >= 1e-3:
        return 1e3, "ms"
    return 1e6, "µs"


def _fmt_x(ax, x: np.ndarray) -> None:
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", " ")))


def _punto(ax, x, y, color, marca="o", **kw):
    """Marca con anillo de superficie de 2 px para separarla de las líneas que cruzan."""
    ax.plot(x, y, linestyle="none", marker=marca, color=color, markeredgecolor=SUPERFICIE,
            markeredgewidth=1.4, zorder=4, **kw)


# ----------------------------------------------------------------- figura por serie

def figura_serie(serie: aj.Serie, df: pd.DataFrame, destino: Path) -> aj.Ajuste:
    med = aj.medianas(df, serie)
    ajustes = [aj.ajustar(med, serie, m) for m in serie.modelos]
    base = ajustes[0]
    k, unidad = _unidad(float(base.t.max()))
    xl = XLABEL[serie.barrido]

    fig, axs = plt.subplots(1, 3, figsize=(15.5, 4.6), constrained_layout=True)
    fig.suptitle(serie.titulo, fontsize=12.5, fontweight="bold", x=0.01, ha="left", color=TINTA)

    # ---- A: tiempo medido vs teoría escalada
    ax = axs[0]
    ax.vlines(base.x, base.t_min * k, base.t_max * k, color=AZUL, lw=1.0, alpha=0.55, zorder=2)
    ax.plot(base.x, base.t * k, color=AZUL, lw=1.6, zorder=3)
    _punto(ax, base.x, base.t * k, AZUL, label="tiempo medido (mediana)")
    for a, col, mk in zip(ajustes, COLORES_MODELO, MARCAS_MODELO):
        ax.plot(a.x, a.prediccion * k, color=col, lw=1.6, zorder=3, marker=mk,
                markerfacecolor="none" if mk else None, markersize=7,
                label=f"{a.modelo.nombre}  (c = {a.c:.2e} s)")
    if serie.exponencial:
        ax.set_yscale("log")
    ax.set_title("A. Tiempo medido vs. teoría escalada", loc="left", fontsize=10.5)
    ax.set_xlabel(xl)
    ax.set_ylabel(f"Tiempo ({unidad})")
    _fmt_x(ax, base.x)
    ax.legend(loc="best")
    if serie.archivo == "set_cover" and serie.algoritmo == "cobertura_exacta":
        ax.text(0.99, 0.02, "el exacto se detiene en el óptimo k*", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=8, color=TINTA_3)

    # ---- B: cociente medido / (c·T)
    ax = axs[1]
    ax.axhline(1.0, color=TINTA_3, lw=1.0, zorder=1)
    todos = np.concatenate([a.razon for a in ajustes])
    for a, col, mk in zip(ajustes, COLORES_MODELO, ["o", "s"]):
        ax.plot(a.x, a.razon, color=col, lw=1.6, zorder=3)
        _punto(ax, a.x, a.razon, col, marca=mk, label=a.modelo.nombre)
    ax.set_yscale("log")
    lo, hi = min(0.5, todos.min() / 1.15), max(2.0, todos.max() * 1.15)
    ax.set_ylim(lo, hi)
    ticks = [t for t in (0.1, 0.25, 0.5, 1, 2, 4, 8, 16, 32) if lo <= t <= hi]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{t:g}" for t in ticks])
    ax.minorticks_off()
    ax.set_title("B. Cociente medido / (c·T): debe ser ≈ 1", loc="left", fontsize=10.5)
    ax.set_xlabel(xl)
    ax.set_ylabel("medido / (c·T)   (escala log)")
    _fmt_x(ax, base.x)
    ax.legend(loc="upper left")
    resumen = "   ".join(
        f"{a.modelo.nombre}: R²={a.r2:.4f}, rango [{a.razon.min():.2f}, {a.razon.max():.2f}]"
        for a in ajustes)
    ax.text(0.0, -0.27, resumen, transform=ax.transAxes, fontsize=8, color=TINTA_2, va="top")

    # ---- C: log-log (polinomial) o semilog (exponencial)
    ax = axs[2]
    ax.vlines(base.x, base.t_min * k, base.t_max * k, color=AZUL, lw=1.0, alpha=0.55, zorder=2)
    ax.plot(base.x, base.t * k, color=AZUL, lw=1.6, zorder=3)
    _punto(ax, base.x, base.t * k, AZUL, label="tiempo medido (mediana)")
    for a, col, mk in zip(ajustes, COLORES_MODELO, MARCAS_MODELO):
        ax.plot(a.x, a.prediccion * k, color=col, lw=1.6, zorder=3, marker=mk,
                markerfacecolor="none" if mk else None, markersize=7, label=a.modelo.nombre)
    ax.set_yscale("log")
    if serie.exponencial:
        t_neto = np.clip(base.t - base.c0, 1e-12, None)
        fm, fth = aj.factor_por_paso(base.x, t_neto), aj.factor_por_paso(base.x, base.f)
        ax.set_title("C. Escala semilog (eje y logarítmico)", loc="left", fontsize=10.5)
        txt = f"factor de crecimiento por +1 en {serie.barrido}:\n  medido ×{fm:.2f}   modelo ×{fth:.2f}"
        _fmt_x(ax, base.x)
    else:
        ax.set_xscale("log")
        pm, pth = aj.pendiente_loglog(base.x, base.t), aj.pendiente_loglog(base.x, base.f)
        ax.set_title("C. Escala log-log", loc="left", fontsize=10.5)
        txt = f"pendiente medida = {pm:.2f}\npendiente del modelo en este rango = {pth:.2f}"
        asin = serie.modelos[0].exponente
        if asin is not None:
            txt += f"\nexponente asintótico = {asin:g}"
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", " ")))
        ax.minorticks_off()
        ax.set_xticks(base.x)
        ax.tick_params(axis="x", labelrotation=45)
    ax.grid(True, axis="y")
    ax.set_xlabel(xl)
    ax.set_ylabel(f"Tiempo ({unidad})")
    ax.text(0.02, 0.97, txt, transform=ax.transAxes, va="top", fontsize=8.8, color=TINTA_2)
    ax.legend(loc="lower right")

    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return base


# --------------------------------------------------------- ruta crítica: ajuste a·n+b·m

def figura_ruta_conjunta(destino: Path) -> dict:
    j = aj.ajuste_conjunto_ruta()
    k, unidad = _unidad(float(j["t"].max()))
    fig, ax = plt.subplots(figsize=(5.8, 4.8), constrained_layout=True)
    lim = [min(j["t"].min(), j["pred"].min()) * k * 0.8, max(j["t"].max(), j["pred"].max()) * k * 1.25]
    ax.plot(lim, lim, color=TINTA_3, lw=1.0, zorder=1, label="predicción = medido")
    _punto(ax, j["pred"] * k, j["t"] * k, AZUL, label="12 puntos (ambos barridos)")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.grid(True, axis="both")
    ax.set_xlabel(f"Predicho a·n + b·m ({unidad})"); ax.set_ylabel(f"Medido ({unidad})")
    ax.set_title("Ruta crítica: t ≈ a·n + b·m", loc="left", fontsize=11, fontweight="bold")
    ax.text(0.03, 0.97,
            f"a (por nodo) = {j['a_por_nodo_s'] * 1e9:.0f} ns\nb (por arista) = {j['b_por_arista_s'] * 1e9:.0f} ns\n"
            f"R² = {j['R2']:.4f}   error rel. medio = {j['err_rel_medio'] * 100:.1f} %",
            transform=ax.transAxes, va="top", fontsize=8.8, color=TINTA_2)
    ax.legend(loc="lower right")
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return j


# --------------------------------------------------------------- calidad de aproximación

def figura_razon_set_cover(carpeta: Path, destino: Path) -> pd.DataFrame:
    alea = pd.read_csv(carpeta / "razon_set_cover.csv")
    adv = pd.read_csv(carpeta / "razon_set_cover_adv.csv")
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.6), constrained_layout=True)
    fig.suptitle("Set Cover: razón voraz / óptimo frente a la cota H_r", fontsize=12.5,
                 fontweight="bold", x=0.01, ha="left")

    ax = axs[0]
    rs = np.array(sorted(alea["r"].unique()))
    ax.plot(rs, [numero_armonico(int(r)) for r in rs], color=TINTA_2, lw=1.6, zorder=2, label="cota H_r")
    rng = np.random.default_rng(1)
    for variante, col, mk, off in (("voraz", AZUL, "o", -0.25), ("voraz_ponderado", NARANJA, "s", 0.25)):
        d = alea[alea["variante"] == variante]
        _punto(ax, d["r"] + off + rng.uniform(-0.12, 0.12, len(d)), d["razon"], col, marca=mk,
               markersize=4.5, alpha=0.55, label=None)
        mx = d.groupby("r")["razon"].max()
        ax.plot(mx.index + off, mx.values, color=col, lw=1.6, zorder=3, marker=mk, markersize=7,
                markerfacecolor="none", label=f"máximo — {variante.replace('_', ' ')}")
    ax.set_ylim(0.9, max(numero_armonico(int(rs.max())), alea["razon"].max()) * 1.08)
    ax.set_title("Instancias aleatorias (n ≤ 15, 40 por r): puntos = instancias, línea = máximo", loc="left", fontsize=10.5)
    ax.set_xlabel("r (categorías)"); ax.set_ylabel("tamaño o costo del voraz / óptimo")
    ax.set_xticks(rs); ax.legend(loc="upper left")

    ax = axs[1]
    ax.plot(adv["r"], [numero_armonico(int(r)) for r in adv["r"]], color=TINTA_2, lw=1.6, zorder=2,
            label="cota H_r")
    ax.plot(adv["r"], adv["razon"], color=AZUL, lw=1.6, zorder=3)
    _punto(ax, adv["r"], adv["razon"], AZUL, label="voraz / óptimo (familia adversarial)")
    ax.set_xscale("log", base=2)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", " ")))
    ax.set_xticks([14, 62, 254, 1022]); ax.minorticks_off()
    ax.set_ylim(0.9, adv["razon"].max() * 1.8)
    ax.set_title("Familia adversarial: óptimo = 2, voraz = k, r = 2^(k+1) − 2", loc="left", fontsize=10.5)
    ax.set_xlabel("r (categorías, escala log)"); ax.set_ylabel("voraz / óptimo")
    ax.legend(loc="upper left")
    ax.text(0.99, 0.04, f"razón máxima {adv['razon'].max():.1f} con r = {int(adv['r'].iloc[-1])}",
            transform=ax.transAxes, ha="right", fontsize=8.8, color=TINTA_2)
    fig.savefig(destino, dpi=150)
    plt.close(fig)

    filas = []
    for (variante,), d in alea.groupby(["variante"]):
        filas.append({"experimento": f"set_cover_{variante}", "instancias": len(d),
                      "razon_media": d["razon"].mean(), "razon_max": d["razon"].max(),
                      "pct_optimo": 100 * (d["razon"] == 1).mean(),
                      "viola_cota_Hd": int((d["razon"] > d["H_d"] + 1e-9).sum())})
    filas.append({"experimento": "set_cover_adversarial", "instancias": len(adv),
                  "razon_media": adv["razon"].mean(), "razon_max": adv["razon"].max(),
                  "pct_optimo": 100 * (adv["razon"] == 1).mean(),
                  "viola_cota_Hd": int((adv["razon"] > adv["H_d"] + 1e-9).sum())})
    return pd.DataFrame(filas)


def figura_razon_heuristicas(carpeta: Path, destino: Path) -> pd.DataFrame:
    dag = pd.read_csv(carpeta / "razon_dag.csv")
    comb = pd.read_csv(carpeta / "razon_combinado.csv")
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.4), constrained_layout=True)
    fig.suptitle("Heurísticas: razón heurística / óptimo (1 = óptima)", fontsize=12.5,
                 fontweight="bold", x=0.01, ha="left")
    rng = np.random.default_rng(2)
    for ax, d, clave, titulo, xl in (
        (axs[0], dag, "n", "Variante C — heurística DAG vs. exacto (40 por n)", "n (etapas)"),
        (axs[1], comb, "lam", "Variante B — heurística vs. exacto (40 por λ)", "λ (penalización)"),
    ):
        xs = np.array(sorted(d[clave].unique()))
        pos = {v: i for i, v in enumerate(xs)}
        px = d[clave].map(pos) + rng.uniform(-0.22, 0.22, len(d))
        ax.axhline(1.0, color=TINTA_3, lw=1.0, zorder=1)
        _punto(ax, px, d["razon"], AZUL, markersize=4.5, alpha=0.5)
        medio = d.groupby(clave)["razon"].mean()
        ax.plot([pos[v] for v in medio.index], medio.values, color=AZUL, lw=1.6, zorder=3,
                marker="D", markersize=7, markerfacecolor=SUPERFICIE, label="media")
        ax.set_xticks(range(len(xs))); ax.set_xticklabels([str(v) for v in xs])
        ax.set_ylim(0.97, max(1.1, d["razon"].max() * 1.04))
        ax.set_title(titulo, loc="left", fontsize=10.5)
        ax.set_xlabel(xl); ax.set_ylabel("heurística / óptimo")
        ax.legend(loc="upper left")
        ax.text(0.99, 0.97, f"óptima en {100 * (d['razon'] == 1).mean():.0f} % de las instancias\n"
                f"peor razón {d['razon'].max():.2f}", transform=ax.transAxes, ha="right", va="top",
                fontsize=8.8, color=TINTA_2)
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    filas = []
    for nombre, d in (("dag_heuristica", dag), ("combinado_heuristica", comb)):
        filas.append({"experimento": nombre, "instancias": len(d), "razon_media": d["razon"].mean(),
                      "razon_max": d["razon"].max(), "pct_optimo": 100 * (d["razon"] == 1).mean(),
                      "viola_cota_Hd": 0})
    return pd.DataFrame(filas)


# ------------------------------------------------------------------ resumen de pendientes

def figura_resumen(tabla: pd.DataFrame, destino: Path) -> None:
    pol = tabla[tabla["pendiente_medida"].notna()].reset_index(drop=True)
    exp = tabla[tabla["factor_medido_+1"].notna()].reset_index(drop=True)
    fig, axs = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1.5, 1]},
                            constrained_layout=True)
    fig.suptitle("Resumen: crecimiento medido vs. el que predice el modelo (en el mismo rango)",
                 fontsize=12.5, fontweight="bold", x=0.01, ha="left")
    for ax, d, med, mod, xl, tit in (
        (axs[0], pol, "pendiente_medida", "pendiente_modelo", "pendiente log-log",
         "Series polinomiales"),
        (axs[1], exp, "factor_medido_+1", "factor_modelo_+1", "factor de crecimiento por +1 en x",
         "Series exponenciales"),
    ):
        y = np.arange(len(d))[::-1]
        etiquetas = [f"{r.serie} — {r.modelo}" for r in d.itertuples()]
        ax.hlines(y, d[med], d[mod], color=EJE, lw=2.0, zorder=1)
        _punto(ax, d[mod], y, NARANJA, marca="s", label="modelo teórico (en el rango)")
        _punto(ax, d[med], y, AZUL, label="medido")
        ax.set_yticks(y); ax.set_yticklabels(etiquetas, fontsize=8, color=TINTA_2)
        ax.grid(True, axis="x"); ax.grid(False, axis="y")
        ax.set_xlabel(xl); ax.set_title(tit, loc="left", fontsize=10.5)
        ax.set_ylim(-0.7, len(d) - 0.3)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=2)
    fig.savefig(destino, dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------ principal

def nombre_archivo(serie: aj.Serie) -> str:
    return f"{serie.archivo}__{serie.algoritmo}__{serie.barrido}.png"


def main(carpeta: Path = RESULTADOS, salida: Path = FIGURAS) -> list[Path]:
    _estilo()
    salida.mkdir(parents=True, exist_ok=True)
    cache: dict[str, pd.DataFrame] = {}
    rutas: list[Path] = []
    for s in aj.SERIES:
        df = cache.setdefault(s.archivo, aj.cargar(s.archivo, carpeta))
        ruta = salida / nombre_archivo(s)
        figura_serie(s, df, ruta)
        rutas.append(ruta)
    ruta = salida / "dag__ruta_critica__conjunto.png"
    figura_ruta_conjunta(ruta); rutas.append(ruta)

    t_sc = figura_razon_set_cover(carpeta, salida / "razon_set_cover.png")
    t_h = figura_razon_heuristicas(carpeta, salida / "razon_heuristicas.png")
    rutas += [salida / "razon_set_cover.png", salida / "razon_heuristicas.png"]

    tabla = aj.resumen(carpeta)
    figura_resumen(tabla, salida / "resumen_pendientes.png")
    rutas.append(salida / "resumen_pendientes.png")

    tabla.round(6).to_csv(salida / "tabla_ajustes.csv", index=False, encoding="utf-8")
    pd.concat([t_sc, t_h]).round(4).to_csv(salida / "tabla_razones.csv", index=False, encoding="utf-8")
    rutas += [salida / "tabla_ajustes.csv", salida / "tabla_razones.csv"]
    return rutas


if __name__ == "__main__":
    for r in main():
        print(r)
