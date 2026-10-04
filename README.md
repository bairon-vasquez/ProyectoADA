# Proyecto Ruta — Análisis y Diseño de Algoritmos 2026-2

Algoritmos exactos y aproximados para acelerar un flujo de etapas bajo presupuesto (Mochila 0/1), cobertura de auditoría (Set Cover) y sus variantes, con validación experimental de la eficiencia teórica. Contexto y decisiones en [CLAUDE.md](CLAUDE.md); guía de estudio para la sustentación en [GUIA_DEL_PROYECTO.md](GUIA_DEL_PROYECTO.md); bitácora en [HISTORIAL.md](HISTORIAL.md).

## Instalación

Requiere Python 3.11+.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
```

## Tests

```bash
pytest
```

## Experimentos (Fase 5)

Cada `experimentos/correr_*.py` escribe sus CSV en `experimentos/resultados/` (mochila, set_cover, dag, combinado y razones heurística/óptimo):

```bash
python -m experimentos.correr_todo            # todo (~40 s)
python -m experimentos.correr_todo --rapido   # tamaños pequeños, prueba de humo
python -m experimentos.correr_mochila         # uno solo
```

Diseño, columnas y tamaños: [docs/05_validacion_experimental.md](docs/05_validacion_experimental.md).

## Gráficas (Fase 6)

```bash
python -m visualizacion.graficas     # lee los CSV y genera PNG + tablas en figuras/
```

## App de sustentación (Fase 7)

```bash
streamlit run visualizacion/app.py
```

Cinco pestañas: **Mochila** (tabla DP coloreada y reconstrucción), **Set Cover** (voraz paso a paso vs. óptimo, incluida la variante con costos y una familia donde el voraz falla), **DAG** (ruta crítica antes y después de acelerar, heurística paso a paso), **Combinado** (cobertura obligatoria, heurística y exacto) y **Experimentos** (gráficas dibujadas en vivo desde los CSV). La app no mide tiempos. Si faltan los CSV, ejecuta antes `python -m experimentos.correr_todo`.

## Estructura

```
core/            algoritmos puros (instancias, generadores, mochila, set_cover, dag, combinado)
experimentos/    medición de tiempos -> CSV
visualizacion/   gráficas (PNG) y app Streamlit; solo lee CSV
docs/            análisis formal (Markdown + LaTeX)
tests/           pytest
```
