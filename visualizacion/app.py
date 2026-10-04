"""App Streamlit para la sustentación del Proyecto Ruta.

Capa 3: presentación. Llama a ``core`` solo para MOSTRAR resultados de los algoritmos y
LEE los CSV de ``experimentos/resultados``; nunca mide tiempos (eso es de ``experimentos/``).

Uso:  streamlit run visualizacion/app.py
"""

from __future__ import annotations

import sys
import tempfile
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:  # `streamlit run` solo agrega visualizacion/ al path
    sys.path.insert(0, str(RAIZ))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from core.combinado import (  # noqa: E402
    combinado_cobertura_obligatoria, combinado_exacto, combinado_heuristica,
)
from core.dag import dag_exacto, dag_heuristica, ruta_critica  # noqa: E402
from core.generadores import (  # noqa: E402
    generar_combinada, generar_dag, generar_mochila, generar_set_cover,
    generar_set_cover_adversarial,
)
from core.instancias import (  # noqa: E402
    InstanciaCombinada, InstanciaDAG, InstanciaMochila, InstanciaSetCover,
)
from core.mochila import construir_tabla_dp, mochila_dp, mochila_fuerza_bruta  # noqa: E402
from core.set_cover import (  # noqa: E402
    cobertura_exacta, cobertura_exacta_ponderada, cobertura_voraz, cobertura_voraz_ponderada,
    numero_armonico,
)
from experimentos.medir import RESULTADOS  # noqa: E402
from visualizacion import ajuste as aj  # noqa: E402
from visualizacion import dibujos, graficas  # noqa: E402
from visualizacion.graficas import AZUL, EJE, NARANJA, SUPERFICIE, TINTA_2  # noqa: E402

st.set_page_config(page_title="Proyecto Ruta · ADA 2026-2", page_icon="📈", layout="wide")

CSS = """
<style>
.block-container {padding-top: 2.2rem; max-width: 1280px;}
h1 {font-weight: 700; letter-spacing: -0.01em;}
div[data-testid="stMetric"] {background: #f1f0ec; border-radius: 10px; padding: 10px 14px;}
button[data-baseweb="tab"] {font-size: 1.0rem; font-weight: 600;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def mostrar(fig) -> None:
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def _set(lista: list[int]) -> str:
    return "{" + ", ".join(str(k + 1) for k in lista) + "}" if lista else "∅"


# =========================================================================== Mochila

EJEMPLO_MOCHILA = InstanciaMochila(t=(5, 8, 6, 4), c=(3, 4, 2, 3), d=(2, 4, 1, 2), B=6)


def tab_mochila() -> None:
    st.subheader("Parte 1 · Aceleración de la cadena bajo presupuesto (Mochila 0/1)")
    st.caption("Elegir qué etapas acelerar sin pasar de B para minimizar la duración total. "
               "DP[i][b] = máx(DP[i−1][b], DP[i−1][b−cᵢ] + dᵢ) · T(n, B) = Θ(n·B), pseudo-polinomial.")
    izq, der = st.columns([1, 2.2])
    with izq:
        fuente = st.radio("Instancia", ["Ejemplo de la Etapa 0", "Generada"], horizontal=True, key="mo_f")
        if fuente == "Ejemplo de la Etapa 0":
            B = st.slider("Presupuesto B", 0, 20, 6, key="mo_B1")
            inst = replace(EJEMPLO_MOCHILA, B=B)
        else:
            n = st.slider("n (etapas)", 3, 10, 6, key="mo_n")
            semilla = st.number_input("Semilla", 0, 9999, 7, key="mo_s")
            B = st.slider("Presupuesto B", 0, 40, 14, key="mo_B2")
            inst = generar_mochila(n, B=B, semilla=int(semilla), t_max=12, c_max=8)
        tabla = construir_tabla_dp(inst)
        sol = mochila_dp(inst)
        df = pd.DataFrame({
            "etapa": range(1, inst.n + 1), "t (duración)": inst.t, "c (costo)": inst.c,
            "d (reducción)": inst.d, "d/c": [round(d / c, 2) for d, c in zip(inst.d, inst.c)],
            "¿acelerar?": ["✔" if i in sol.etapas else "" for i in range(inst.n)],
        })
        st.dataframe(df, hide_index=True, use_container_width=True)
    with der:
        a, b, c, d = st.columns(4)
        a.metric("Duración sin acelerar", sum(inst.t))
        b.metric("Duración óptima", sol.duracion, delta=-sol.reduccion, delta_color="inverse")
        c.metric("Costo usado", f"{sol.costo} / {inst.B}")
        d.metric("Etapas aceleradas", _set(list(sol.etapas)))
        mostrar(dibujos.fig_tabla_dp(inst, tabla))
    with st.expander("Cómo se reconstruyen las etapas elegidas (recorrido desde DP[n][B])", expanded=True):
        b_act = inst.B
        for i in range(inst.n, 0, -1):
            sin, con = tabla[i - 1][b_act], tabla[i][b_act]
            if con != sin:
                st.markdown(f"- **Etapa {i}**: DP[{i}][{b_act}] = {con} ≠ DP[{i - 1}][{b_act}] = {sin} → "
                            f"**se acelera**; el presupuesto baja a {b_act} − {inst.c[i - 1]} = {b_act - inst.c[i - 1]}.")
                b_act -= inst.c[i - 1]
            else:
                st.markdown(f"- Etapa {i}: DP[{i}][{b_act}] = DP[{i - 1}][{b_act}] = {sin} → no hizo falta.")
    if inst.n <= 12:
        fb = mochila_fuerza_bruta(inst)
        if fb.reduccion == sol.reduccion:
            st.success(f"Verificación: la fuerza bruta (2^{inst.n} subconjuntos) obtiene la misma "
                       f"reducción óptima, {fb.reduccion}.")
        else:
            st.error("La DP y la fuerza bruta NO coinciden.")
    with st.expander("¿Por qué es pseudo-polinomial?"):
        st.markdown("La tabla tiene (n+1)·(B+1) celdas, y cada una cuesta O(1). Pero **B ocupa solo log B bits** "
                    "en la entrada: pasar de B a 2B añade un bit y duplica el tiempo. Es polinomial en el "
                    "*valor* de B, no en su tamaño.")


# ========================================================================== Set Cover

def _sc(r: int, conjuntos: list[set[int]], a: tuple[int, ...] | None = None) -> InstanciaSetCover:
    return InstanciaSetCover(r=r, conjuntos=tuple(frozenset(s) for s in conjuntos),
                             a=a or (1,) * len(conjuntos), w=(1,) * r)


FIJOS_SC = {
    "Ejemplo de la Etapa 0": _sc(5, [{0, 1, 2}, {1, 3}, {2, 3}, {3, 4}, {0, 4}]),
    "Trampa del voraz (óptimo 2, voraz 3)": _sc(6, [{0, 1, 3, 4}, {0, 1, 2}, {3, 4, 5}]),
    "A1: un conjunto grande y caro vs. dos baratos": _sc(4, [{0, 1, 2, 3}, {0, 1}, {2, 3}], a=(10, 1, 1)),
}


def tab_set_cover() -> None:
    st.subheader("Parte 2 y Variante A1 · Cobertura de auditoría (Set Cover)")
    st.caption("El voraz elige en cada paso la interacción que cubre más categorías nuevas "
               "(o la de menor a/nuevas en A1). T(n, r) = O(n·r²) · garantía: |voraz| ≤ H_d · óptimo.")
    opciones = list(FIJOS_SC) + ["Familia adversarial (el voraz se aleja del óptimo)", "Aleatoria"]
    izq, der = st.columns([1, 2.4])
    with izq:
        eleccion = st.selectbox("Instancia", opciones, key="sc_f")
        if eleccion in FIJOS_SC:
            inst = FIJOS_SC[eleccion]
        elif eleccion.startswith("Familia"):
            k = st.slider("k (r = 2^(k+1) − 2)", 2, 4, 3, key="sc_k")
            inst = generar_set_cover_adversarial(k)
            st.caption(f"r = {inst.r} categorías, {inst.n} conjuntos. Óptimo = 2 (las dos filas R₁, R₂).")
        else:
            n = st.slider("n (interacciones)", 4, 12, 8, key="sc_n")
            r = st.slider("r (categorías)", 4, 14, 10, key="sc_r")
            semilla = st.number_input("Semilla", 0, 9999, 3, key="sc_s")
            costos = st.checkbox("Con costos a_j (Variante A1)", key="sc_a1")
            inst = generar_set_cover(n, r, semilla=int(semilla), prob=0.3, a_max=9 if costos else 1)
    ponderado = any(a != 1 for a in inst.a)
    voraz = cobertura_voraz_ponderada(inst) if ponderado else cobertura_voraz(inst)
    opt = cobertura_exacta_ponderada(inst) if ponderado else cobertura_exacta(inst)
    if voraz is None or opt is None:
        st.error("La instancia no es factible (alguna categoría no la cubre ninguna interacción).")
        return
    medida = (lambda s: s.costo) if ponderado else (lambda s: s.tamano)
    d = max(len(s) for s in inst.conjuntos)
    with der:
        a, b, c, e = st.columns(4)
        etiqueta = "costo" if ponderado else "interacciones"
        a.metric(f"Voraz ({etiqueta})", medida(voraz))
        b.metric(f"Óptimo ({etiqueta})", medida(opt))
        c.metric("Razón voraz / óptimo", f"{medida(voraz) / medida(opt):.2f}")
        e.metric(f"Cota H_d (d={d})", f"{numero_armonico(d):.2f}")
        paso = st.slider("Paso del voraz", 0, len(voraz.pasos), len(voraz.pasos), key="sc_paso")
    col1, col2 = st.columns(2)
    with col1:
        mostrar(dibujos.fig_cobertura(inst, voraz.indices, paso, "Voraz"))
    with col2:
        mostrar(dibujos.fig_cobertura(inst, opt.indices, len(opt.indices), "Óptimo (fuerza bruta)"))
    with st.expander("Detalle de los pasos del voraz", expanded=True):
        cubiertas: set[int] = set()
        for k, (j, nuevas) in enumerate(voraz.pasos, start=1):
            razon = f" · a/nuevas = {inst.a[j]}/{len(nuevas)} = {inst.a[j] / len(nuevas):.2f}" if ponderado else ""
            cubiertas |= set(nuevas)
            st.markdown(f"**Paso {k}.** Elige **S{j + 1}**, que cubre {len(nuevas)} categoría(s) nueva(s) "
                        f"{_set(list(nuevas))}{razon}. Cubiertas: {len(cubiertas)}/{inst.r}.")
        st.markdown(f"Voraz: {_set(list(voraz.indices))} · Óptimo: {_set(list(opt.indices))}")


# ================================================================================ DAG

def _ejemplo_dag() -> InstanciaDAG:
    return InstanciaDAG(t=(3, 5, 4, 2), c=(4, 2, 2, 3), d=(1, 3, 2, 1),
                        aristas=((0, 1), (0, 2), (1, 3), (2, 3)), B=4)


def tab_dag() -> None:
    st.subheader("Variante C · Etapas en paralelo (DAG) y ruta crítica")
    st.caption("La duración es la ruta más larga (DP en orden topológico, O(n+m)). Acelerar una etapa "
               "solo ayuda si está en la ruta crítica, y al hacerlo la ruta crítica puede cambiar.")
    izq, der = st.columns([1, 3])
    with izq:
        fuente = st.radio("Instancia", ["Ejemplo de la Etapa 0 (A→B, A→C, B→D, C→D)", "Generada"], key="dag_f")
        if fuente.startswith("Ejemplo"):
            B = st.slider("Presupuesto B", 0, 11, 4, key="dag_B1")
            inst = replace(_ejemplo_dag(), B=B)
            nombres = ["A", "B", "C", "D"]
        else:
            n = st.slider("n (etapas)", 4, 11, 7, key="dag_n")
            m = st.slider("m (dependencias)", n - 1, min(3 * n, n * (n - 1) // 2), min(2 * n, n * (n - 1) // 2), key="dag_m")
            semilla = st.number_input("Semilla", 0, 9999, 5, key="dag_s")
            B = st.slider("Presupuesto B", 0, 40, 12, key="dag_B2")
            inst = generar_dag(n, m, B=B, semilla=int(semilla), t_max=12, c_max=8)
            nombres = [chr(ord("A") + i) for i in range(n)]
        modo = st.radio("Algoritmo", ["Heurística (paso a paso)", "Exacto (fuerza bruta)"], key="dag_modo")
        df = pd.DataFrame({"etapa": nombres, "t": inst.t, "c": inst.c, "d": inst.d})
        st.dataframe(df, hide_index=True, use_container_width=True)
    heur = dag_heuristica(inst)
    ex = dag_exacto(inst) if inst.n <= 12 else None
    with der:
        a, b, c, d = st.columns(4)
        a.metric("Ruta crítica sin acelerar", heur.duracion_inicial)
        b.metric("Heurística", heur.duracion, delta=heur.duracion - heur.duracion_inicial, delta_color="inverse")
        c.metric("Óptimo (exacto)", ex.duracion if ex else "n > 12", delta=(ex.duracion - ex.duracion_inicial) if ex else None,
                 delta_color="inverse")
        d.metric("Costo usado (heurística)", f"{heur.costo} / {inst.B}")
        if modo.startswith("Heur"):
            paso = st.slider("Paso de la heurística", 0, len(heur.pasos), len(heur.pasos), key="dag_paso")
            x = [0] * inst.n
            for etapa, _ in heur.pasos[:paso]:
                x[etapa] = 1
            titulo_despues = f"Después de {paso} aceleración(es)"
        else:
            sol = ex
            if sol is None:
                st.info("El exacto se limita a n ≤ 12 (2ⁿ subconjuntos).")
                sol = heur
            x = [1 if i in sol.aceleradas else 0 for i in range(inst.n)]
            titulo_despues = "Solución exacta"
        antes = ruta_critica(inst, [0] * inst.n)
        despues = ruta_critica(inst, x)
        col1, col2 = st.columns(2)
        with col1:
            mostrar(dibujos.fig_dag(inst, [0] * inst.n, antes.camino, antes.longitud, "Antes", nombres))
        with col2:
            mostrar(dibujos.fig_dag(inst, x, despues.camino, despues.longitud, titulo_despues, nombres))
        st.caption("Si varias rutas empatan en la duración máxima, se dibuja solo una de ellas.")
        ganancia = antes.longitud - despues.longitud
        suma_d = sum(inst.d[i] for i in range(inst.n) if x[i])
        st.info(f"**Ganancia real:** {antes.longitud} → {despues.longitud} = {ganancia}. "
                f"La suma de las reducciones d de las etapas aceleradas es {suma_d}"
                + (" (iguales: toda aceleración estaba en una ruta crítica única)." if ganancia == suma_d
                   else f": **no se suma**, porque otra ruta paralela pasa a ser la crítica. Por eso no basta la Mochila."))
    if heur.pasos:
        with st.expander("Pasos de la heurística"):
            filas = [{"paso": k, "etapa acelerada": nombres[e], "ruta crítica L": L}
                     for k, (e, L) in enumerate(heur.pasos, start=1)]
            st.dataframe(pd.DataFrame(filas), hide_index=True)


# ============================================================================ Combinado

def tab_combinado() -> None:
    st.subheader("Variante B · Aceleración + auditoría con presupuesto conjunto")
    st.caption("Σcᵢxᵢ + Σa_j ≤ B · minimizar (Σtᵢ − Σdᵢxᵢ) + λ · (peso de las categorías sin cubrir). "
               "Con λ grande se separa en cobertura de costo mínimo + Mochila con el presupuesto restante.")
    izq, der = st.columns([1, 2.4])
    with izq:
        n = st.slider("n (etapas)", 3, 9, 5, key="co_n")
        N = st.slider("N (interacciones)", 3, 10, 6, key="co_N")
        r = st.slider("r (categorías)", 3, 8, 6, key="co_r")
        semilla = st.number_input("Semilla", 0, 9999, 4, key="co_s")
        base = generar_combinada(n, N, r, semilla=int(semilla))
        total = sum(base.cadena.c) + sum(base.cobertura.a)
        B = st.slider("Presupuesto conjunto B", 0, total, int(0.6 * total), key="co_B")
        suma_t = sum(base.cadena.t)
        grande = st.checkbox(f"λ grande (Σt + 1 = {suma_t + 1}): cobertura obligatoria", value=True, key="co_g")
        lam = suma_t + 1 if grande else st.slider("λ (penalización por peso sin cubrir)", 0, 2 * suma_t, 5, key="co_l")
        inst = InstanciaCombinada(cadena=base.cadena, cobertura=base.cobertura, B=B, lam=lam)
        st.caption(f"Σt = {suma_t} · pesos de categoría w = {list(inst.cobertura.w)}")
        st.dataframe(pd.DataFrame({"etapa": range(1, n + 1), "t": inst.cadena.t, "c": inst.cadena.c,
                                   "d": inst.cadena.d}), hide_index=True, use_container_width=True)
        st.dataframe(pd.DataFrame({"interacción": range(1, N + 1), "a": inst.cobertura.a,
                                   "categorías": [_set(sorted(s)) for s in inst.cobertura.conjuntos]}),
                     hide_index=True, use_container_width=True)
    resultados = {"Heurística (λ general)": combinado_heuristica(inst)}
    oblig = combinado_cobertura_obligatoria(inst, exacta=True)
    if oblig is not None:
        resultados["Cobertura obligatoria + Mochila"] = oblig
    if N <= 10:
        resultados["Exacto (referencia)"] = combinado_exacto(inst)
    with der:
        if oblig is None:
            st.warning("No se puede cubrir todo dentro de B: la cobertura obligatoria no tiene solución.")
        filas = [{
            "método": nombre, "etapas": _set(list(s.etapas)), "interacciones": _set(list(s.interacciones)),
            "costo / B": f"{s.costo} / {B}", "duración": s.duracion, "penalización": s.penalizacion,
            "objetivo": s.objetivo,
        } for nombre, s in resultados.items()]
        st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
        graficas._estilo()
        fig, ax = plt.subplots(figsize=(8.6, 0.8 * len(resultados) + 1.3), constrained_layout=True)
        nombres = list(resultados)[::-1]
        dur = [resultados[k].duracion for k in nombres]
        pen = [resultados[k].penalizacion for k in nombres]
        ax.barh(nombres, dur, color=AZUL, edgecolor=SUPERFICIE, linewidth=2, height=0.55, label="duración de la cadena")
        ax.barh(nombres, pen, left=dur, color=NARANJA, edgecolor=SUPERFICIE, linewidth=2, height=0.55,
                label="λ · peso sin cubrir")
        for y, (dd, pp) in enumerate(zip(dur, pen)):
            ax.text(dd + pp + 0.01 * max(1, max(dur)), y, f"{dd + pp}", va="center", fontsize=9, color=TINTA_2)
        ax.set_xlabel("objetivo (menor es mejor)"); ax.grid(True, axis="x"); ax.grid(False, axis="y")
        ax.legend(loc="lower right")
        ax.set_title("Desglose del objetivo", loc="left", fontsize=10.5)
        mostrar(fig)
        if "Exacto (referencia)" in resultados:
            ex, he = resultados["Exacto (referencia)"], resultados["Heurística (λ general)"]
            if he.objetivo == ex.objetivo:
                st.success(f"La heurística alcanza el óptimo ({ex.objetivo}).")
            else:
                st.info(f"La heurística obtiene {he.objetivo} frente al óptimo {ex.objetivo} "
                        f"(razón {he.objetivo / max(ex.objetivo, 1):.2f}). No tiene garantía de aproximación.")


# ========================================================================== Experimentos

def _mtime(archivo: str) -> float:
    ruta = RESULTADOS / f"{archivo}.csv"
    return ruta.stat().st_mtime if ruta.exists() else 0.0


@st.cache_data(show_spinner=False)
def _png_serie(idx: int, mtime: float) -> bytes:
    serie = aj.SERIES[idx]
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "f.png"
        graficas.figura_serie(serie, aj.cargar(serie.archivo), destino)
        return destino.read_bytes()


@st.cache_data(show_spinner=False)
def _png_razones(cual: str, mtime: float):
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "f.png"
        graficas._estilo()
        tabla = (graficas.figura_razon_set_cover if cual == "sc" else graficas.figura_razon_heuristicas)(
            RESULTADOS, destino)
        return destino.read_bytes(), tabla


@st.cache_data(show_spinner=False)
def _png_resumen(mtime: float):
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "f.png"
        tabla = aj.resumen()
        graficas._estilo()
        graficas.figura_resumen(tabla, destino)
        return destino.read_bytes(), tabla


def tab_experimentos() -> None:
    st.subheader("Experimentos · tiempo medido vs. T(n) teórico")
    st.caption("Las gráficas se dibujan en vivo a partir de los CSV de `experimentos/resultados/`. "
               "Esta app no mide tiempos: eso se hace solo en `experimentos/`.")
    faltan = [a for a in ("mochila", "set_cover", "dag", "combinado", "razon_set_cover") if not (RESULTADOS / f"{a}.csv").exists()]
    if faltan:
        st.warning("Faltan CSV: " + ", ".join(faltan) + ". Ejecuta `python -m experimentos.correr_todo`.")
        return
    vista = st.radio("Vista", ["Series de tiempo", "Calidad de la aproximación", "Resumen de ajustes"], horizontal=True, key="ex_v")
    if vista == "Series de tiempo":
        etiquetas = [f"{s.titulo}  ·  {s.algoritmo} (varía {s.barrido})" for s in aj.SERIES]
        idx = st.selectbox("Serie", range(len(etiquetas)), format_func=lambda i: etiquetas[i], key="ex_s")
        serie = aj.SERIES[idx]
        st.image(_png_serie(idx, _mtime(serie.archivo)), use_container_width=True)
        st.markdown("**A**: tiempo medido (mediana, con rango mín–máx) vs. la curva teórica con la constante c "
                    "ajustada por mínimos cuadrados. **B**: medido / (c·T), debe valer ≈ 1. "
                    "**C**: escala log-log (pendiente) o semilog (factor por +1 en las exponenciales).")
        med = aj.medianas(aj.cargar(serie.archivo), serie)
        ajustes = [aj.ajustar(med, serie, m) for m in serie.modelos]
        filas = [{"modelo": a.modelo.formula, "c (s)": f"{a.c:.3e}", "R²": round(a.r2, 4),
                  "cociente mín": round(float(a.razon.min()), 2), "cociente máx": round(float(a.razon.max()), 2)}
                 for a in ajustes]
        st.dataframe(pd.DataFrame(filas), hide_index=True)
        with st.expander("Tabla de medianas (vista de datos)"):
            st.dataframe(med[["x", "n", "valor_parametro", "tiempo_s", "t_min", "t_max", "valor_solucion", "extra"]]
                         .rename(columns={"x": f"tamaño ({serie.barrido})", "n": "n (instancia)",
                                          "valor_parametro": "parámetro"}), hide_index=True)
    elif vista == "Calidad de la aproximación":
        st.markdown("Razón heurística / óptimo calculada con el exacto en instancias pequeñas.")
        png, tabla = _png_razones("sc", _mtime("razon_set_cover"))
        st.image(png, use_container_width=True)
        png2, tabla2 = _png_razones("h", _mtime("razon_dag"))
        st.image(png2, use_container_width=True)
        st.dataframe(pd.concat([tabla, tabla2]).round(3), hide_index=True)
        st.caption("La cota H_d nunca se viola; la familia adversarial muestra que el factor logarítmico es real.")
    else:
        png, tabla = _png_resumen(_mtime("mochila") + _mtime("dag") + _mtime("set_cover"))
        st.image(png, use_container_width=True)
        cols = [c for c in ("serie", "modelo", "R2", "razon_min", "razon_max", "pendiente_medida",
                            "pendiente_modelo", "factor_medido_+1", "factor_modelo_+1") if c in tabla.columns]
        st.dataframe(tabla[cols].round(3), hide_index=True, use_container_width=True)


# ================================================================================= main

def main() -> None:
    st.title("Proyecto Ruta")
    st.markdown("Análisis y Diseño de Algoritmos · 2026-2 — acelerar etapas bajo presupuesto, cobertura de "
                "auditoría y sus variantes, con validación experimental del T(n).")
    with st.sidebar:
        st.header("Guía rápida")
        st.markdown(
            "- **Mochila**: DP exacta, pseudo-polinomial Θ(n·B).\n"
            "- **Set Cover**: voraz con cota H_d vs. óptimo exacto.\n"
            "- **DAG**: ruta crítica O(n+m) y heurística que recalcula.\n"
            "- **Combinado**: presupuesto conjunto Mochila + Set Cover.\n"
            "- **Experimentos**: medido vs. teórico, desde los CSV.")
        st.divider()
        st.caption("Los tiempos solo se miden en `experimentos/`. Esta app muestra resultados.")
    t1, t2, t3, t4, t5 = st.tabs(["Mochila", "Set Cover", "DAG", "Combinado", "Experimentos"])
    with t1:
        tab_mochila()
    with t2:
        tab_set_cover()
    with t3:
        tab_dag()
    with t4:
        tab_combinado()
    with t5:
        tab_experimentos()


main()
