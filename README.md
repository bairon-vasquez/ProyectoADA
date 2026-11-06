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

## Ejecutar casos (primera entrega)

Cada caso es un JSON (formato y salidas en [entrega/Manual_Tecnico.md](entrega/Manual_Tecnico.md)); por caso se obtienen resultado, tiempo y traza:

```bash
python -m experimentos.correr_casos                              # todos los casos de casos/
python -m experimentos.correr_casos casos/caso_01_etapa0.json    # uno solo
python -m experimentos.correr_casos casos/entrada_G3_mochila_20_nodos.json   # caso del docente
python -m experimentos.generar_casos                             # regenera los casos de ejemplo
```

El lector acepta el formato propio y el del docente (detectado por la clave `etapas`): ids como E01 o R01, variaciones de auditoría, flujo (ejecuta la Variante C) y presupuesto conjunto (ejecuta la Variante B). Salida en `experimentos/resultados/casos/`: `<id>.json`, `<id>_traza.md`, `<id>_dp.csv`, `<id>_tiempos.csv` y `resumen_casos.csv`. Informe y manual de la entrega: carpeta [entrega/](entrega/) (Markdown y Word; se regeneran con `python entrega/md_a_docx.py`, con Word cerrado).

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
