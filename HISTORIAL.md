# Historial local del proyecto

Bitácora de lo que se hizo en cada prompt/fase. Se agrega una entrada nueva al final de cada interacción.

---

## Prompt 1 — Fase 1: Esqueleto

**Pedido:** crear la estructura del proyecto, `CLAUDE.md`, `README.md`, `requirements.txt`, `instancias.py` y `generadores.py`.

**Hecho:**
- Estructura `core/`, `experimentos/`, `visualizacion/`, `docs/`, `tests/`, `figuras/` creada en la raíz (sin carpeta anidada `proyecto-ruta/`).
- `CLAUDE.md` (contexto, arquitectura, convenciones, decisiones, preguntas abiertas), `README.md`, `requirements.txt`, `pytest.ini`, `.gitignore`.
- `core/instancias.py`: dataclasses inmutables `InstanciaMochila`, `InstanciaSetCover`, `InstanciaDAG`, `InstanciaCombinada` con validación.
- `core/generadores.py`: generadores con semilla propia (`random.Random`); Set Cover con factibilidad garantizada.
- Stubs con docstring en el resto de módulos y en `docs/01…05`.
- Verificado: factibilidad en 200 semillas y reproducibilidad.

---

## Prompt 2 — Fase 2: Parte 1, Mochila (+ creación de este historial)

**Pedido:** pasar a la Fase 2 y crear un `.md` que lleve el historial de lo hecho en cada prompt.

**Hecho:**
- `HISTORIAL.md` (este archivo).
- `core/mochila.py`: `mochila_fuerza_bruta` O(2^n·n); `construir_tabla_dp` O(n·B); `reconstruir_etapas` O(n); `mochila_dp` (compone ambas). Comentarios que cuentan operaciones.
- `tests/test_mochila.py`: ejemplo de la Etapa 0 (óptimo {2,3}, duración 18), DP vs. fuerza bruta en 40 instancias con n ≤ 15, casos borde (B=0, c>B, n=0), tabla monótona. **46 tests pasan** (suite completa).
- `docs/03_eficiencia_exactos.md`: deducción de T(n,B) = Θ(n·B) y de la fuerza bruta Θ(n·2^n); explicación de pseudo-polinomialidad (B ocupa log B bits).
- `docs/02_reducciones.md`: equivalencia formal Mochila 0/1 ↔ ACELERACIÓN-CADENA en ambos sentidos con prueba (⇒) y (⇐); conclusión NP-completo en sentido débil.

---

## Prompt 3 — Fase 3: Parte 2, Set Cover

**Pedido:** pasar a la Fase 3 (voraz, exacto por fuerza bruta, tests, deducciones, reducción desde Vertex Cover, cota H_r).

**Hecho:**
- `core/set_cover.py`: `cobertura_voraz` O(n·r²) con traza paso a paso (`pasos`) para la app; `cobertura_exacta` por subconjuntos de tamaño creciente O(2^n·n·r); `numero_armonico`; `SolucionCobertura`. Ambos devuelven `None` si la instancia es infactible. Comentarios que cuentan operaciones.
- `tests/test_set_cover.py`: ejemplo de la Etapa 0 (óptimo {1,4}), "trampa" donde el voraz da 3 y el óptimo 2, infactible, universo vacío, 40 instancias aleatorias (n ≤ 15) con exacto verificado contra enumeración independiente por máscaras y `óptimo ≤ voraz ≤ H_r·óptimo`. **91 tests pasan** (suite completa).
- `docs/03_eficiencia_exactos.md`: deducción de T(n,r) = O(n·r²) del voraz (≤ r rondas × n conjuntos × O(r)) y de la complejidad del exacto Σ C(n,k)·k·r ⊆ O(2^n·n·r).
- `docs/02_reducciones.md`: Vertex Cover ≤ₚ Set Cover (U = E, S_v = aristas incidentes), pruebas (⇒) y (⇐), conclusión NP-completo (dureza fuerte).
- `docs/04_aproximaciones.md`: enunciado G ≤ H_d·OPT ≤ H_r·OPT con citas (Johnson 1974, Chvátal 1979), demostración por argumento de precios, ajuste de la cota y ejemplo concreto.

---

## Prompt 4 — Fase 4: Variantes A1, B y C

**Pedido:** pasar a la Fase 4 (A1 voraz ponderado; B combinado con cobertura obligatoria y heurística para λ general; C DAG con ruta más larga O(n+m), exacto y heurística iterativa; T(n) en docs; tests, incluido el ejemplo A→B, A→C, B→D, C→D con óptimo 7).

**Hecho:**
- `core/set_cover.py`: `cobertura_voraz_ponderada` (mín. a_j/nuevas con productos cruzados, O(n·r²)) y `cobertura_exacta_ponderada` (2^n máscaras, O(2^n·n·r)).
- `core/dag.py`: `preparar_dag` (Kahn, O(n+m), detecta ciclos), `ruta_critica` (DP en orden topológico, O(n+m), devuelve también el camino), `dag_exacto` O(2^n·(n+m)), `dag_heuristica` O(n·(n+m)) con traza `pasos` y rutas antes/después para la app.
- `core/combinado.py`: `combinado_cobertura_obligatoria` (cobertura de costo mínimo + Mochila con B − a(C*), exacta o voraz), `combinado_heuristica` (cobertura voraz por beneficio/costo evaluando cada prefijo contra la última fila de una sola DP, O(n·B + N·r·min(N,r))), `combinado_exacto` (referencia, O(n·B + 2^N·N·r)).
- `tests/test_variantes.py`: ejemplo DAG (ruta inicial 10, acelerar solo B da 9, exacto = heurística = 7), ruta crítica contra enumeración independiente de caminos, orden topológico válido y ciclo, cadena DAG = Mochila, heurística ≥ exacto, A1 respeta H_d, B obligatoria = exacto con λ grande, heurística B factible y ≤ "sin auditar". **287 tests pasan** (suite completa).
- `docs/03`: T(n) de A1, B (3 variantes), C (toposort, ruta, exacto, heurística) y tabla resumen. `docs/02`: NP-completitud de A1, B y C con reducciones (⇒)(⇐). `docs/04`: cota H_d del voraz ponderado y límites (con contraejemplos reales, verificados por ejecución) de las heurísticas de B y C.

---

## Prompt 5 — Fase 5: Experimentos

**Pedido:** pasar a la Fase 5 (≥ 5 tamaños por algoritmo; Mochila variando n y B; Set Cover variando n y r; DAG variando n y m; mediana de repeticiones; CSV con algoritmo, n, B/r/m, repetición, tiempo_s, valor_solución).

**Hecho:**
- `experimentos/medir.py`: `medir` (1 calentamiento + R repeticiones con `perf_counter`, GC apagado), `medir_caso`, `mediana`, `escribir_csv`.
- Scripts `correr_mochila.py`, `correr_set_cover.py`, `correr_dag.py`, `correr_combinado.py`, `correr_razones.py` y `correr_todo.py`, todos con `--rapido`. CSV en `experimentos/resultados/`: `mochila`, `set_cover`, `dag`, `combinado` y cuatro `razon_*`. Corrida completa ≈ 40 s.
- Columnas = las pedidas + `barrido` (qué parámetro varía) y `extra` (trabajo del modelo fino).
- `core/generadores.py`: `generar_set_cover_adversarial(k)` (óptimo 2, voraz k).
- Ajustes hechos al ver los datos: el exacto de Set Cover se detiene en k*, así que con n ≤ 18 no mostraba el crecimiento exponencial; se pasó a r = 24, n = 12…22 (1 ms → 1,4 s). Los barridos DAG con m fijo se limitaron a n con n(n−1)/2 ≥ m. `extra` registra rondas × Σ|S_j| (voraz) y evaluaciones × (n+m) (heurística DAG) porque esas heurísticas hacen muchas menos rondas que la cota de peor caso.
- `tests/test_experimentos.py`: medición, modo rápido (columnas y ≥ 5 tamaños por serie), razones y familia adversarial. **291 tests pasan** (suite completa).
- `docs/05_validacion_experimental.md` §1: protocolo, columnas, tabla de series, significado de `extra`, experimentos de calidad y primeras observaciones. `README.md` y `CLAUDE.md` actualizados.

---

## Prompt 6 — Fase 6: Gráficas e informe experimental

**Pedido:** tiempo medido vs. curva teórica escalada (mínimos cuadrados de la constante), gráfica de tiempo/T_teórico (≈ constante), log-log con pendiente estimada y razón voraz/óptimo vs. H_r; PNG en `figuras/` y análisis en `docs/05_validacion_experimental.md`.

**Hecho:**
- `visualizacion/ajuste.py`: medianas por tamaño, ajuste c = Σt·f/Σf² (con intercepto donde hay término constante), pendiente log-log, factor de crecimiento por +1, 21 (serie, modelo) y ajuste conjunto a·n + b·m de la ruta crítica.
- `visualizacion/graficas.py`: 17 figuras de 3 paneles (A tiempo vs. teoría, B cociente medido/(c·T), C log-log o semilog), `dag__ruta_critica__conjunto.png`, `razon_set_cover.png` (aleatoria y adversarial vs. H_r), `razon_heuristicas.png`, `resumen_pendientes.png`, y `tabla_ajustes.csv` / `tabla_razones.csv`. Paleta validada con `validate_palette.js` (slots 1-3, todos los pares: PASS; el turquesa queda bajo 3:1, con leyenda visible y tablas como relieve).
- Correcciones al ver los datos: la pendiente medida se compara con la del propio modelo en el mismo rango (n+m con m fijo no es una potencia); el exacto de B necesita intercepto (tabla DP constante); la ruta crítica necesita dos constantes (a por nodo, b por arista).
- `docs/05` §2: método, tabla de 21 ajustes, qué se confirma (DP Θ(n·B) pendiente 1,02/1,04; exactos ×2,04–2,14 por +1; ruta crítica 296 ns/nodo + 154 ns/arista, R² 0,9956), qué NO coincide con la cota de peor caso (voraz r: pendiente 1,25 vs. 2; heurística DAG no monótona, R² −1,13 con la cota y 0,93–0,997 con el modelo fino), calidad (H_d violada 0 veces en 570; adversarial 5,0 con r = 2046 vs. H_r 8,2) y limitaciones.
- `tests/test_graficas.py`: ajuste recupera la constante exacta; modo rápido genera todos los PNG. **293 tests pasan** (suite completa).

---

## Prompt 7 — Fase 7: App Streamlit

**Pedido:** pestañas Mochila (tabla DP coloreada y etapas elegidas), Set Cover (voraz paso a paso vs. óptimo), DAG (grafo con ruta crítica antes/después), Combinado y Experimentos (gráficas desde los CSV); limpia y presentable.

**Hecho:**
- `visualizacion/dibujos.py`: `fig_tabla_dp` (mapa de calor con el recorrido de reconstrucción resaltado), `fig_cobertura` (matriz interacciones × categorías según el paso), `fig_dag` (ruta crítica en naranja, etapas aceleradas rellenas, τ en cada nodo, capas por camino más largo).
- `visualizacion/app.py` con 5 pestañas:
  - Mochila: ejemplo de la Etapa 0 o generada, métricas, tabla DP, explicación de la reconstrucción y verificación contra la fuerza bruta.
  - Set Cover: ejemplo, trampa, A1 (grande y caro vs. baratos), familia adversarial y aleatoria (con costos opcionales); slider de paso del voraz, voraz vs. óptimo, razón y cota H_d.
  - DAG: ejemplo A→B, A→C, B→D, C→D o generado; heurística paso a paso o exacto; antes/después; compara ganancia real vs. suma de d.
  - Combinado: cobertura obligatoria, heurística y exacto; λ grande o manual; desglose duración/penalización.
  - Experimentos: series de tiempo (17), calidad de la aproximación y resumen de ajustes, dibujados en vivo desde los CSV con tabla de medianas.
- `.streamlit/config.toml` (tema claro con la paleta del proyecto). La app no mide tiempos.
- `tests/test_app.py` (AppTest): ejemplos de la Etapa 0, todas las instancias de Set Cover, DAG generado/exacto, Combinado con λ manual y las 17 series de Experimentos. Servidor real arrancado y verificado (HTTP 200). **303 tests pasan**.

---

## Prompt 8 — Documento guía del proyecto

**Pedido:** un documento que detalle qué se hizo en cada fase, las recomendaciones y el contenido entregado en la Fase 7 (cómo correrla, pestañas, ideas clave, observaciones), con lo equivalente para todas las fases anteriores.

**Hecho:**
- `GUIA_DEL_PROYECTO.md` en la raíz: resumen en una página, mapa del proyecto, comandos, las 7 fases (qué se hizo, ideas clave, decisiones y observaciones; la Fase 7 con el texto completo de pestañas), hallazgos principales, 12 preguntas probables con respuesta corta, recomendaciones y pendientes, y limitaciones.
- `README.md` enlaza la guía y la bitácora. Sin cambios de código.
