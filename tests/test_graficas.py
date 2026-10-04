"""Prueba de humo de la capa de visualización: lee CSV (modo rápido) y genera los PNG."""

import numpy as np
import pandas as pd

from experimentos import correr_combinado, correr_dag, correr_mochila, correr_razones, correr_set_cover
from visualizacion import ajuste as aj
from visualizacion import graficas


def test_ajuste_por_minimos_cuadrados_recupera_la_constante():
    # Datos exactos t = 6·f: c = 6, R² = 1 y cociente = 1.
    f = np.array([1.0, 2.0, 4.0, 8.0])
    med = pd.DataFrame({"x": f, "n": f, "valor_parametro": 1, "tiempo_s": 6 * f,
                        "t_min": 0, "t_max": 0, "valor_solucion": 0, "extra": 0})
    a = aj.ajustar(med, aj.SERIES[0], aj.Modelo("lineal", "x", lambda r: r["x"]))
    assert abs(a.c - 6.0) < 1e-12 and abs(a.r2 - 1.0) < 1e-12 and np.allclose(a.razon, 1.0)
    assert abs(aj.pendiente_loglog(f, f**2) - 2.0) < 1e-9
    assert abs(aj.factor_por_paso(np.arange(5.0), 2.0 ** np.arange(5.0)) - 2.0) < 1e-9


def test_graficas_modo_rapido(tmp_path):
    datos, figs = tmp_path / "datos", tmp_path / "figs"
    for m in (correr_mochila, correr_set_cover, correr_dag, correr_combinado, correr_razones):
        m.main(rapido=True, carpeta=datos)
    rutas = graficas.main(carpeta=datos, salida=figs)
    pngs = [r for r in rutas if r.suffix == ".png"]
    assert len(pngs) == len(aj.SERIES) + 4
    assert all(r.exists() for r in rutas)
    assert all(r.stat().st_size > 2000 for r in pngs)
    assert (figs / "tabla_ajustes.csv").exists()
