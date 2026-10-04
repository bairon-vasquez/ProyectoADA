"""Prueba de humo de la app Streamlit: ejecuta el script y recorre las ramas de la interfaz."""

import pytest
from streamlit.testing.v1 import AppTest

from visualizacion import ajuste as aj

APP = "visualizacion/app.py"


def _limpio(at: AppTest) -> None:
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error, [e.value for e in at.error]


@pytest.fixture(scope="module")
def at() -> AppTest:
    app = AppTest.from_file(APP, default_timeout=180).run()
    _limpio(app)
    return app


def test_valores_del_ejemplo_de_la_etapa0(at):
    m = {x.label: x.value for x in at.metric}
    assert m["Duración sin acelerar"] == "23" and m["Duración óptima"] == "18"
    assert m["Etapas aceleradas"] == "{2, 3}"
    assert m["Ruta crítica sin acelerar"] == "10" and m["Heurística"] == "7"
    assert m["Óptimo (exacto)"] == "7"


def test_mochila_generada(at):
    at.radio(key="mo_f").set_value("Generada").run()
    _limpio(at)
    at.slider(key="mo_B2").set_value(0).run()  # presupuesto cero: nada que acelerar
    _limpio(at)


@pytest.mark.parametrize("opcion", [
    "Ejemplo de la Etapa 0", "Trampa del voraz (óptimo 2, voraz 3)",
    "A1: un conjunto grande y caro vs. dos baratos",
    "Familia adversarial (el voraz se aleja del óptimo)", "Aleatoria",
])
def test_set_cover_todas_las_instancias(at, opcion):
    at.selectbox(key="sc_f").set_value(opcion).run()
    _limpio(at)
    if opcion == "Aleatoria":
        at.checkbox(key="sc_a1").set_value(True).run()
        _limpio(at)


def test_dag_generado_y_exacto(at):
    at.radio(key="dag_f").set_value("Generada").run()
    _limpio(at)
    at.radio(key="dag_modo").set_value("Exacto (fuerza bruta)").run()
    _limpio(at)


def test_combinado_con_lambda_manual(at):
    at.checkbox(key="co_g").set_value(False).run()
    _limpio(at)
    at.slider(key="co_l").set_value(3).run()
    _limpio(at)


def test_experimentos_todas_las_vistas(at):
    for vista in ("Calidad de la aproximación", "Resumen de ajustes", "Series de tiempo"):
        at.radio(key="ex_v").set_value(vista).run()
        _limpio(at)
    for idx in range(len(aj.SERIES)):
        at.selectbox(key="ex_s").set_value(idx).run()
        _limpio(at)
