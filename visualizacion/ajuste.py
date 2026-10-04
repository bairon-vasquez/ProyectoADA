"""Análisis de los CSV de tiempos: medianas, ajuste por mínimos cuadrados y pendientes.

Capa 3: solo LEE los CSV de ``experimentos/resultados`` y calcula; nunca mide ni ejecuta
los algoritmos. Cada serie es un par (algoritmo, barrido) y tiene uno o varios modelos
teóricos f(fila) con T ≈ c·f. El tiempo se compara contra f escalado por la constante c
que minimiza el error cuadrático:  c = Σ t_i·f_i / Σ f_i².
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from experimentos import correr_combinado
from experimentos.medir import RESULTADOS

Fila = pd.Series  # una fila de medianas: n, valor_parametro, valor_solucion, extra, tiempo_s


@dataclass(frozen=True)
class Modelo:
    """Un modelo teórico de tiempo T ≈ c·f(fila)."""

    nombre: str  # etiqueta corta de la curva
    formula: str  # fórmula legible (en el título / tabla)
    f: Callable[[Fila], float]
    exponente: float | None = None  # pendiente log-log esperada (None si no aplica)


@dataclass(frozen=True)
class Serie:
    """Una serie experimental: qué se varía y con qué modelos se contrasta."""

    archivo: str
    algoritmo: str
    barrido: str  # columna de tamaño que varía: n, B, r, m, N
    titulo: str
    modelos: tuple[Modelo, ...]  # el primero es el teórico (cota deducida en docs/03)
    exponencial: bool = False  # True -> semilog y factor de crecimiento en vez de pendiente
    factor_esperado: float | None = None  # factor teórico por +1 en x (series exponenciales)
    intercepto: bool = False  # ajusta c·f + c0 (hay un término constante en el barrido)


@dataclass
class Ajuste:
    """Resultado del ajuste de una serie contra un modelo."""

    serie: Serie
    modelo: Modelo
    x: np.ndarray
    t: np.ndarray  # mediana por tamaño
    t_min: np.ndarray
    t_max: np.ndarray
    f: np.ndarray
    c: float
    c0: float
    prediccion: np.ndarray
    r2: float
    err_rel_medio: float  # media de |t − pred| / t
    razon: np.ndarray  # t / (c·f + c0): ≈ 1 si el modelo es correcto
    detalle: dict = field(default_factory=dict)


# ----------------------------------------------------------------- modelos teóricos

def _n_por_B(r: Fila) -> float:
    return r["n"] * (r["valor_parametro"] + 1)


def _suma_n_m(r: Fila) -> float:
    return r["n"] + r["valor_parametro"]


def _cota_voraz(r: Fila) -> float:
    return r["n"] * r["valor_parametro"] ** 2  # n·r²


def _fino(r: Fila) -> float:
    return r["extra"]  # rondas × Σ|S_j|  /  evaluaciones × (n+m)


def _dag_cota(r: Fila) -> float:
    return r["n"] * (r["n"] + r["valor_parametro"])  # n·(n+m)


def _exacto_sc(r: Fila) -> float:
    """Σ_{k=0}^{k*} C(n,k)·k·r con k* = valor_solucion y r = valor_parametro."""
    n, kstar, rr = int(r["n"]), int(r["valor_solucion"]), r["valor_parametro"]
    return sum(math.comb(n, k) * max(k, 1) * rr for k in range(kstar + 1))


_CFG_B = correr_combinado.COMPLETO  # N, r fijos de la heurística de B


def _comb_heur(r: Fila) -> float:
    # n·B (DP) es el término que crece; la parte de cobertura es constante en los barridos
    # y la absorbe el intercepto.
    return r["n"] * (r["valor_parametro"] + 1)


def _comb_exacto(r: Fila) -> float:
    # 2^N·N·r domina; el término constante n·B (tabla DP) lo absorbe el intercepto c0.
    N = r["valor_parametro"]
    return 2**N * N * _CFG_B["r_exacto"]


MOD_FINO_VORAZ = Modelo("modelo fino", "rondas·Σ|S_j|", _fino, None)
MOD_FINO_DAG = Modelo("modelo fino", "(pasos+2)·(n+m)", _fino, None)


def _series() -> list[Serie]:
    S: list[Serie] = []
    # Mochila
    S.append(Serie("mochila", "mochila_dp", "n", "Mochila DP, B fijo",
                   (Modelo("n·B", "n·B", _n_por_B, 1.0),)))
    S.append(Serie("mochila", "mochila_dp", "B", "Mochila DP, n fijo",
                   (Modelo("n·B", "n·B", _n_por_B, 1.0),)))
    S.append(Serie("mochila", "mochila_fuerza_bruta", "n", "Mochila fuerza bruta",
                   (Modelo("n·2^n", "n·2^n", lambda r: r["n"] * 2 ** r["n"]),),
                   exponencial=True, factor_esperado=2.0))
    # Set Cover
    for alg, nom in (("cobertura_voraz", "Set Cover voraz"),
                     ("cobertura_voraz_ponderada", "Set Cover voraz ponderado (A1)")):
        S.append(Serie("set_cover", alg, "n", f"{nom}, r fijo",
                       (Modelo("cota n·r²", "n·r²", _cota_voraz, 1.0), MOD_FINO_VORAZ)))
        S.append(Serie("set_cover", alg, "r", f"{nom}, n fijo",
                       (Modelo("cota n·r²", "n·r²", _cota_voraz, 2.0), MOD_FINO_VORAZ)))
    S.append(Serie("set_cover", "cobertura_exacta", "n", "Set Cover exacto (por tamaño creciente)",
                   (Modelo("ΣC(n,k)·k·r", "Σ_{k≤k*} C(n,k)·k·r", _exacto_sc),),
                   exponencial=True))
    S.append(Serie("set_cover", "cobertura_exacta_ponderada", "n", "Set Cover exacto ponderado (A1)",
                   (Modelo("2^n·n·r", "2^n·n·r", lambda r: 2 ** r["n"] * r["n"] * r["valor_parametro"]),),
                   exponencial=True, factor_esperado=2.0))
    # DAG
    S.append(Serie("dag", "ruta_critica", "n", "Ruta crítica, m fijo",
                   (Modelo("n+m", "n+m", _suma_n_m, 1.0),)))
    S.append(Serie("dag", "ruta_critica", "m", "Ruta crítica, n fijo",
                   (Modelo("n+m", "n+m", _suma_n_m, 1.0),)))
    S.append(Serie("dag", "dag_heuristica", "n", "Heurística DAG, m fijo",
                   (Modelo("cota n·(n+m)", "n·(n+m)", _dag_cota, 2.0), MOD_FINO_DAG)))
    S.append(Serie("dag", "dag_heuristica", "m", "Heurística DAG, n fijo",
                   (Modelo("cota n·(n+m)", "n·(n+m)", _dag_cota, 1.0), MOD_FINO_DAG)))
    S.append(Serie("dag", "dag_exacto", "n", "DAG exacto",
                   (Modelo("2^n·(n+m)", "2^n·(n+m)", lambda r: 2 ** r["n"] * (r["n"] + r["valor_parametro"])),),
                   exponencial=True, factor_esperado=2.0))
    # Combinado
    S.append(Serie("combinado", "combinado_heuristica", "n", "Combinado heurística, B fijo",
                   (Modelo("n·B + cte", "n·B (+ cobertura constante)", _comb_heur, 1.0),), intercepto=True))
    S.append(Serie("combinado", "combinado_heuristica", "B", "Combinado heurística, n fijo",
                   (Modelo("n·B + cte", "n·B (+ cobertura constante)", _comb_heur, 1.0),), intercepto=True))
    S.append(Serie("combinado", "combinado_exacto", "N", "Combinado exacto",
                   (Modelo("2^N·N·r + cte", "2^N·N·r (+ n·B constante)", _comb_exacto),),
                   exponencial=True, factor_esperado=2.0, intercepto=True))
    return S


SERIES: list[Serie] = _series()


# ---------------------------------------------------------------------- lectura

def cargar(archivo: str, carpeta: Path = RESULTADOS) -> pd.DataFrame:
    return pd.read_csv(carpeta / f"{archivo}.csv")


def medianas(df: pd.DataFrame, serie: Serie) -> pd.DataFrame:
    """Una fila por tamaño: mediana (y mín./máx.) del tiempo; columnas de tamaño y de contexto."""
    d = df[(df["algoritmo"] == serie.algoritmo) & (df["barrido"] == serie.barrido)]
    clave = {"n": "n", "B": "valor_parametro", "r": "valor_parametro",
             "m": "valor_parametro", "N": "valor_parametro"}[serie.barrido]
    g = d.groupby(clave, sort=True)
    out = g.agg(
        tiempo_s=("tiempo_s", "median"), t_min=("tiempo_s", "min"), t_max=("tiempo_s", "max"),
        n=("n", "first"), valor_parametro=("valor_parametro", "first"),
        valor_solucion=("valor_solucion", "first"), extra=("extra", "first"),
    ).reset_index(drop=True)
    out["x"] = out[clave] if clave in out else out["n"]
    return out


# ------------------------------------------------------------------------ ajuste

def ajustar(med: pd.DataFrame, serie: Serie, modelo: Modelo) -> Ajuste:
    """Ajuste por mínimos cuadrados de T ≈ c·f (o c·f + c0 si ``serie.intercepto``)."""
    x = med["x"].to_numpy(dtype=float)
    t = med["tiempo_s"].to_numpy(dtype=float)
    f = np.array([modelo.f(r) for _, r in med.iterrows()], dtype=float)
    if serie.intercepto:
        A = np.column_stack([f, np.ones_like(f)])
        (c, c0), *_ = np.linalg.lstsq(A, t, rcond=None)
    else:
        c, c0 = float(np.dot(t, f) / np.dot(f, f)), 0.0
    pred = c * f + c0
    sst = float(np.sum((t - t.mean()) ** 2))
    r2 = 1.0 - float(np.sum((t - pred) ** 2)) / sst if sst > 0 else 1.0
    return Ajuste(
        serie=serie, modelo=modelo, x=x, t=t,
        t_min=med["t_min"].to_numpy(dtype=float), t_max=med["t_max"].to_numpy(dtype=float),
        f=f, c=float(c), c0=float(c0), prediccion=pred, r2=r2,
        err_rel_medio=float(np.mean(np.abs(t - pred) / t)), razon=t / pred,
    )


def pendiente_loglog(x: np.ndarray, t: np.ndarray) -> float:
    """Pendiente de la recta log t = a + p·log x (regresión lineal en escala log-log)."""
    p, _ = np.polyfit(np.log(x), np.log(t), 1)
    return float(p)


def factor_por_paso(x: np.ndarray, t: np.ndarray) -> float:
    """Factor de crecimiento del tiempo por cada +1 en x: e^b con log t = a + b·x."""
    b, _ = np.polyfit(x, np.log(t), 1)
    return float(math.exp(b))


def resumen(carpeta: Path = RESULTADOS) -> pd.DataFrame:
    """Tabla de ajustes de todas las series (una fila por serie y modelo)."""
    cache: dict[str, pd.DataFrame] = {}
    filas = []
    for s in SERIES:
        df = cache.setdefault(s.archivo, cargar(s.archivo, carpeta))
        med = medianas(df, s)
        for m in s.modelos:
            a = ajustar(med, s, m)
            fila = {
                "serie": s.titulo, "algoritmo": s.algoritmo, "barrido": s.barrido,
                "modelo": m.formula, "tamanos": len(med),
                "c_ajustada_s": a.c, "R2": a.r2, "err_rel_medio": a.err_rel_medio,
                "razon_min": float(a.razon.min()), "razon_max": float(a.razon.max()),
            }
            if s.exponencial:
                t_neto = np.clip(a.t - a.c0, 1e-12, None)  # sin la parte constante, si la hay
                fila["factor_medido_+1"] = factor_por_paso(a.x, t_neto)
                fila["factor_modelo_+1"] = factor_por_paso(a.x, a.f)
            else:
                fila["pendiente_medida"] = pendiente_loglog(a.x, a.t)
                fila["pendiente_modelo"] = pendiente_loglog(a.x, a.f)
                fila["exponente_asintotico"] = m.exponente
            filas.append(fila)
    return pd.DataFrame(filas)


def ajuste_conjunto_ruta(carpeta: Path = RESULTADOS) -> dict:
    """Ajuste t ≈ a·n + b·m con los dos barridos de ``ruta_critica`` a la vez.

    O(n+m) significa lineal en n y en m, pero el costo por nodo (a) y por arista (b) no tiene
    por qué ser el mismo; una sola constante c·(n+m) no lo representa. Devuelve a, b, R²,
    error relativo medio y los vectores para graficar medido vs. predicho.
    """
    df = cargar("dag", carpeta)
    puntos = []
    for barrido in ("n", "m"):
        serie = next(s for s in SERIES if s.algoritmo == "ruta_critica" and s.barrido == barrido)
        med = medianas(df, serie)
        puntos.append(med[["n", "valor_parametro", "tiempo_s"]].rename(columns={"valor_parametro": "m"}))
    d = pd.concat(puntos, ignore_index=True)
    A = d[["n", "m"]].to_numpy(dtype=float)
    t = d["tiempo_s"].to_numpy(dtype=float)
    (a, b), *_ = np.linalg.lstsq(A, t, rcond=None)
    pred = A @ np.array([a, b])
    r2 = 1.0 - float(np.sum((t - pred) ** 2)) / float(np.sum((t - t.mean()) ** 2))
    return {
        "a_por_nodo_s": float(a), "b_por_arista_s": float(b), "R2": r2,
        "err_rel_medio": float(np.mean(np.abs(t - pred) / t)),
        "n": d["n"].to_numpy(), "m": d["m"].to_numpy(), "t": t, "pred": pred,
    }
