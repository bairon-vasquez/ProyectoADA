# Guía del Proyecto Ruta (ADA 2026-2)

Documento de estudio para la sustentación. Reúne, fase por fase, **qué se hizo, cómo correrlo, qué ideas hay que saber defender, qué decisiones se tomaron y qué conviene revisar**. La bitácora cronológica de cada interacción está en [HISTORIAL.md](HISTORIAL.md); el contexto y las convenciones, en [CLAUDE.md](CLAUDE.md).

**Estado:** las 7 fases están completas. La suite tiene **394 tests** y pasan todos.

---

## Primera entrega (grupo G3 · Ruta)

Requisitos de la guía del curso y dónde está cada uno:

| Requisito | Dónde |
|---|---|
| Informe único: formalización + NP-dureza | [entrega/Informe_Primera_Entrega.md](entrega/Informe_Primera_Entrega.md) (y `.docx`) |
| Reducciones G3: Mochila 0/1 y Cobertura de Vértices | Informe §4 y §5; detalle en [docs/02_reducciones.md](docs/02_reducciones.md) |
| Justificación de complejidad | Informe §6; detalle en [docs/03_eficiencia_exactos.md](docs/03_eficiencia_exactos.md) |
| Repositorio, dependencias, README | Raíz del repositorio |
| Manual técnico (algoritmo, estructura, formatos E/S, ejecución, limitaciones) | [entrega/Manual_Tecnico.md](entrega/Manual_Tecnico.md) (y `.docx`) |
| Resultados, tiempo y traza por caso | `python -m experimentos.correr_casos` → `experimentos/resultados/casos/` |
| Casos de la profesora | **Pendientes de recibir**; ver Manual §6.2 |

---

## Índice

1. [Resumen en una página](#1-resumen-en-una-página)
2. [Mapa del proyecto](#2-mapa-del-proyecto)
3. [Cómo correr todo](#3-cómo-correr-todo)
4. [Fase por fase](#4-fase-por-fase)
5. [Hallazgos principales](#5-hallazgos-principales)
6. [Preguntas probables en la sustentación](#6-preguntas-probables-en-la-sustentación)
7. [Recomendaciones y pendientes](#7-recomendaciones-y-pendientes)
8. [Limitaciones conocidas](#8-limitaciones-conocidas)

---

## 1. Resumen en una página

| Problema | Tamaño de la entrada | Algoritmo exacto | Algoritmo eficiente | Garantía | Dureza |
|---|---|---|---|---|---|
| **Parte 1** — Cadena de etapas (Mochila 0/1) | n, B | Fuerza bruta Θ(n·2ⁿ) | **DP Θ(n·B)** (exacta) | Óptima | NP-completo **débil** (pseudo-polinomial) |
| **Parte 2** — Cobertura de auditoría (Set Cover) | n, r | Subconjuntos por tamaño creciente O(2ⁿ·n·r) | **Voraz O(n·r²)** | ≤ H_r · óptimo | NP-completo (fuerte), por reducción desde Vertex Cover |
| **Variante A1** — Set Cover con costos | n, r | Exacto O(2ⁿ·n·r) | **Voraz ponderado O(n·r²)** | ≤ H_d · óptimo | NP-completo |
| **Variante B** — Presupuesto conjunto | n, N, r, B | Referencia O(n·B + 2ᴺ·N·r) | Cobertura obligatoria (óptima con cobertura exacta) y **heurística** O(n·B + N·r·min(N,r)) | Heurística: factible y ≤ "sin auditar"; sin factor | NP-completo |
| **Variante C** — Etapas en paralelo (DAG) | n, m, B | Fuerza bruta O(2ⁿ·(n+m)) | **Heurística O(n·(n+m))**; ruta crítica O(n+m) | Factible, nunca empeora; sin factor | NP-completo |

**Las tres ideas que sostienen todo el proyecto:**

1. **Definir n bien.** El tamaño de la entrada no es solo n: es (n, B) en Mochila, (n, r) en Set Cover y (n, m) en DAG. Por eso B ocupa log B bits y O(n·B) es *pseudo*-polinomial.
2. **Deducir T(n) contando operaciones**, y comprobar que el código hace exactamente esas operaciones (los comentarios `# O(.)` del código coinciden con `docs/03`).
3. **Validar con datos**: el tiempo medido dividido entre c·T(n) debe ser ≈ constante. Cuando no lo es, se explica (cota de peor caso frente a modelo fino).

---

## 2. Mapa del proyecto

```
ProyectoADA/
├── CLAUDE.md             contexto, convenciones y decisiones
├── HISTORIAL.md          bitácora de cada prompt
├── GUIA_DEL_PROYECTO.md  este documento
├── README.md             instalación y comandos
├── requirements.txt      numpy, matplotlib, pandas, networkx, streamlit, pytest
├── core/                 CAPA 1 · algoritmos puros (sin prints, sin gráficas, sin I/O)
│   ├── instancias.py     dataclasses de cada tipo de instancia
│   ├── generadores.py    generadores sintéticos con semilla (+ familia adversarial)
│   ├── mochila.py        fuerza bruta, DP, reconstrucción
│   ├── set_cover.py      voraz, voraz ponderado, exactos
│   ├── dag.py            orden topológico, ruta crítica, exacto, heurística
│   └── combinado.py      cobertura obligatoria, heurística, exacto
├── experimentos/         CAPA 2 · medición (único lugar donde se miden tiempos)
│   ├── medir.py          perf_counter, calentamiento, repeticiones
│   ├── correr_*.py       un script por experimento → CSV
│   └── resultados/       CSV de tiempos y de razones
├── visualizacion/        CAPA 3 · presentación (solo LEE los CSV)
│   ├── ajuste.py         mínimos cuadrados, pendientes, factores
│   ├── graficas.py       PNG para el informe → figuras/
│   ├── dibujos.py        tabla DP, cobertura y DAG para la app
│   └── app.py            Streamlit para la sustentación
├── figuras/              PNG y tablas generadas
├── docs/                 análisis formal (Markdown + LaTeX)
│   ├── Etapa 0 — Formalización del problema.md   (tu formalización original)
│   ├── 01_formalizacion.md             (placeholder; ver §7)
│   ├── 02_reducciones.md               NP-dureza de los 5 problemas
│   ├── 03_eficiencia_exactos.md        deducción de T(n)
│   ├── 04_aproximaciones.md            cotas y límites de las heurísticas
│   └── 05_validacion_experimental.md   diseño y análisis experimental
└── tests/                pytest (394 tests)
```

**Regla de las tres capas:** `core/` no imprime ni grafica; los tiempos solo se miden en `experimentos/`; `visualizacion/` solo lee. Así, lo que se mide es exactamente el código que se analiza.

---

## 3. Cómo correr todo

```bash
# Instalación (Python 3.11+)
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

# Tests (≈ 1 min; la mitad es la app)
pytest

# Experimentos: regenera los CSV en experimentos/resultados/  (≈ 40 s)
python -m experimentos.correr_todo
python -m experimentos.correr_todo --rapido     # tamaños pequeños, prueba de humo
python -m experimentos.correr_mochila           # un solo experimento

# Gráficas y tablas: lee los CSV y escribe en figuras/
python -m visualizacion.graficas

# App de sustentación
streamlit run visualizacion/app.py
```

Si faltan los CSV, la app lo avisa y pide ejecutar `python -m experimentos.correr_todo`.

---

## 4. Fase por fase

### Fase 1 · Esqueleto

**Qué se hizo**
- Se creó la estructura de carpetas en la raíz (sin carpeta anidada `proyecto-ruta/`, porque ya existía `docs/` con la Etapa 0).
- `CLAUDE.md`, `README.md`, `requirements.txt`, `pytest.ini` y `.gitignore`.
- `core/instancias.py`: dataclasses inmutables `InstanciaMochila`, `InstanciaSetCover`, `InstanciaDAG` e `InstanciaCombinada`, que validan sus datos al crearse (por ejemplo 0 ≤ d ≤ t y c ≥ 1).
- `core/generadores.py`: un `random.Random(semilla)` propio por generador (reproducible). En Set Cover se **garantiza la factibilidad**: toda categoría sin cubrir se asigna a algún conjunto, y no quedan conjuntos vacíos.

**Ideas clave**
- Tres capas separadas (ver §2).
- La misma semilla y los mismos parámetros dan siempre la misma instancia.
- La factibilidad se garantiza al generar, así los algoritmos no necesitan ramas de "sin solución" en los experimentos.

**Decisiones**
- Índices 0-based en el código y 1-based en los documentos.
- `InstanciaSetCover` sirve para la Parte 2 (costos a_j = 1) y para A1 (a_j ≥ 1) y lleva también los pesos w_k de la Variante B.
- `InstanciaDAG` guarda solo los nodos reales; la fuente y el sumidero ficticios los añade el algoritmo.

---

### Fase 2 · Parte 1, Mochila

**Qué se hizo**
- `core/mochila.py`: `mochila_fuerza_bruta` (2ⁿ máscaras), `construir_tabla_dp` (recurrencia), `reconstruir_etapas` (recorrido hacia atrás) y `mochila_dp`.
- `tests/test_mochila.py`: ejemplo de la Etapa 0 (óptimo {2,3}, duración 18), DP contra fuerza bruta en 40 instancias con n ≤ 15, casos borde (B = 0, c > B, n = 0).
- `docs/03` (deducción de T(n, B) y pseudo-polinomialidad) y `docs/02` (equivalencia con la Mochila 0/1 en ambos sentidos).

**Ideas clave**
- **Recurrencia:** `DP[i][b] = max(DP[i-1][b], DP[i-1][b-cᵢ] + dᵢ)`. Dos opciones por etapa: no acelerarla, o acelerarla si cabe.
- **T(n, B) = Θ(n·B):** (n+1)·(B+1) celdas, cada una con un número constante de operaciones.
- **Pseudo-polinomial:** B ocupa log B bits, pero el tiempo es lineal en el *valor* de B. Un bit más en la entrada duplica el tiempo.
- **Reconstrucción:** la etapa i se eligió si y solo si `DP[i][b] ≠ DP[i-1][b]`; entonces b baja en cᵢ.
- **Equivalencia con la Mochila:** tᵢ = dᵢ = vᵢ, cᵢ = wᵢ, B = W, K = Σv − V (y la inversa). Como la Mochila es NP-completa (Karp), nuestro problema también; es débil porque la DP lo resuelve en tiempo pseudo-polinomial.

**Observación:** la reducción supone pesos wᵢ ≥ 1, coherente con la restricción cᵢ ≥ 1 de la Etapa 0.

---

### Fase 3 · Parte 2, Set Cover

**Qué se hizo**
- `core/set_cover.py`: `cobertura_voraz` (con traza paso a paso), `cobertura_exacta` (subconjuntos de tamaño creciente) y `numero_armonico`. Devuelven `None` si la instancia es infactible.
- `tests/test_set_cover.py`: ejemplo de la Etapa 0, una "trampa" donde el voraz da 3 y el óptimo 2, caso infactible, y 40 instancias aleatorias con óptimo ≤ voraz ≤ H_r · óptimo (el exacto se contrastó con una enumeración independiente por máscaras).
- `docs/03` (T = O(n·r²) del voraz y complejidad del exacto), `docs/02` (reducción Vertex Cover ≤ₚ Set Cover) y `docs/04` (cota H_r con demostración).

**Ideas clave**
- **Por qué el voraz es O(n·r²):** a lo sumo r rondas (cada una cubre al menos una categoría nueva) × n conjuntos × O(r) para contar las nuevas de cada uno.
- **Reducción Vertex Cover → Set Cover:** universo = aristas, un conjunto por vértice con sus aristas incidentes. Una cobertura de k vértices es exactamente una cobertura de k conjuntos. No hay números grandes, así que la dureza es **fuerte**.
- **Por qué G ≤ H_r · OPT** (argumento de precios): cada elemento nuevo cuesta 1/q si el conjunto elegido cubre q nuevos. Para un conjunto óptimo de tamaño s, el j-ésimo elemento que el voraz cubre cuesta como mucho 1/(s−j+1), así que la suma da H_s. Como todo elemento está en algún conjunto óptimo, G ≤ OPT · H_d.

**Observación:** el exacto se detiene al hallar el óptimo, por lo que su tiempo depende de k\* (tamaño del óptimo).

---

### Fase 4 · Variantes A1, B y C

**Qué se hizo**
- **A1** (`set_cover.py`): `cobertura_voraz_ponderada` (mínimo a_j/nuevas, comparado con productos cruzados enteros) y `cobertura_exacta_ponderada`.
- **C** (`dag.py`): `preparar_dag` (orden topológico de Kahn, detecta ciclos), `ruta_critica` (DP en orden topológico, devuelve también el camino), `dag_exacto` (2ⁿ máscaras) y `dag_heuristica` (acelera en la ruta crítica la etapa de mejor d/c y recalcula).
- **B** (`combinado.py`): `combinado_cobertura_obligatoria` (cobertura de costo mínimo + Mochila con B − a(C\*)), `combinado_heuristica` (λ general) y `combinado_exacto` (referencia).
- `tests/test_variantes.py`, incluyendo el ejemplo del DAG A→B, A→C, B→D, C→D (óptimo 7).
- `docs/03`, `docs/02` y `docs/04` ampliados con A1, B y C.

**Ideas clave**
- **Ruta crítica en O(n+m):** al procesar los nodos en orden topológico, cada arista se relaja exactamente una vez, así que Σ|sucesores| = m (no n·m).
- **Por qué hay que recalcular la ruta crítica:** acelerar solo B baja A→B→D de 10 a 7, pero A→C→D (9) pasa a ser la crítica; la ganancia real es 1, no 3. Las reducciones **no se suman**, por eso el DAG no es una Mochila.
- **Cobertura obligatoria es óptima con cobertura exacta:** el óptimo de la Mochila nunca empeora al subir el presupuesto, así que gastar lo mínimo en cubrir deja el máximo para acelerar.
- **Heurística de B:** crece la cobertura por beneficio/costo y evalúa cada prefijo en O(1) contra la última fila de una sola DP. El prefijo vacío es candidato, así que nunca es peor que "no auditar".
- **NP-completitud de A1, B y C:** B contiene a la Mochila (N = 0) y a Set Cover (n = 0); C contiene a la Mochila (la cadena es un DAG con un solo camino).

**Límites reales de las heurísticas** (contraejemplos verificados por ejecución, en `docs/04`)
- **DAG:** con t = (4,3,6), c = (3,2,4), d = (0,2,3) y B = 4, la heurística da 11 y el óptimo 10 (el fallo clásico del voraz por razón d/c).
- **B:** existe una instancia donde la heurística da 21 y el óptimo 17, porque el óptimo no es un prefijo de su secuencia voraz.
- Ambas garantizan factibilidad y no empeorar el punto de partida, pero **no tienen factor de aproximación**.

**Observación:** en B, "cobertura obligatoria" con el voraz solo es heurística; la versión con cobertura exacta sí es óptima.

---

### Fase 5 · Experimentos

**Qué se hizo**
- `experimentos/medir.py`: 1 calentamiento + R repeticiones con `perf_counter`, recolector de basura apagado; la instancia se genera **antes** de medir.
- Scripts `correr_mochila`, `correr_set_cover`, `correr_dag`, `correr_combinado`, `correr_razones` y `correr_todo`, todos con `--rapido`. Corrida completa ≈ 40 s.
- Series, todas con al menos 5 tamaños: Mochila DP (variando n y B) y fuerza bruta; voraz, voraz ponderado y exactos de Set Cover (variando n y r); ruta crítica, heurística y exacto del DAG (variando n y m); Combinado (n, B y N).
- CSV de tiempos con las columnas `algoritmo, barrido, n, parametro, valor_parametro, repeticion, tiempo_s, valor_solucion, extra` y CSV de razones heurística/óptimo (`razon_*.csv`).
- `generar_set_cover_adversarial(k)`: familia con óptimo = 2 y voraz = k, r = 2^(k+1) − 2.
- `docs/05` §1: protocolo, columnas, series y significado de `extra`.

**Ideas clave**
- **Protocolo:** instancia fuera del cronómetro, calentamiento, varias repeticiones, mediana y semilla fija.
- **Cota de peor caso contra modelo fino:** el voraz hace muchas menos rondas que r. Por eso `extra` guarda las iteraciones reales (rondas × Σ|S_j|) y permite validar sin depender solo de la cota.

**Decisiones**
- Se añadieron `barrido` y `extra` a las columnas pedidas. "B/r/m" quedó como `parametro` + `valor_parametro`.
- Los DAG con m fijo arrancan en n tal que n(n−1)/2 ≥ m (un DAG con ese m no existe para n menores).
- El exacto de Set Cover se movió a r = 24 y n = 12…22, porque con n ≤ 18 se detenía tan pronto que no mostraba crecimiento exponencial.

---

### Fase 6 · Gráficas e informe experimental

**Qué se hizo**
- `visualizacion/ajuste.py`: mediana por tamaño, constante c = Σ t·f / Σ f² por mínimos cuadrados (con término constante c₀ donde hay una parte fija), pendiente log-log y factor de crecimiento por +1.
- `visualizacion/graficas.py`: 17 figuras de tres paneles (A: medido vs. teoría escalada · B: cociente medido/(c·T) · C: log-log o semilog), más el ajuste a·n + b·m de la ruta crítica, la razón voraz/óptimo frente a H_r, la razón de las heurísticas y el resumen de pendientes. También `figuras/tabla_ajustes.csv` y `figuras/tabla_razones.csv`.
- Paleta validada con el validador de color (los tres colores usados pasan todos los chequeos; el turquesa queda bajo 3:1 de contraste y por eso lleva leyenda visible y tablas de respaldo).
- `docs/05` §2: método, tabla de 21 ajustes, qué se confirma, qué no coincide, calidad y limitaciones.

**Ideas clave**
- **Cómo se valida T(n):** con el cociente medido/(c·T); si el T(n) es correcto, queda ≈ 1 (constante).
- **Se compara contra la pendiente del propio modelo en el mismo rango**, no contra el exponente asintótico: n+m con m = 4000 fijo no crece como n.
- **Cota válida pero no ajustada:** que el cociente medido/cota *decrezca* no viola la cota; solo indica que el tiempo crece más despacio.

**Correcciones hechas al ver los datos**
- El exacto de B necesita un término constante (la tabla DP) además de 2ᴺ·N·r.
- La ruta crítica necesita dos constantes (costo por nodo y por arista): con una sola, el barrido en n da R² = 0,89.

---

### Fase 7 · App Streamlit

**Cómo correrla**

```bash
streamlit run visualizacion/app.py
```

Si faltan los CSV, ejecuta antes `python -m experimentos.correr_todo`.

**Qué hay en cada pestaña**

- **Mochila**
  - Elige entre el ejemplo de la Etapa 0 o una instancia generada, con sliders de B, n y semilla.
  - Muestra la tabla DP coloreada con el recorrido de la reconstrucción resaltado.
  - Explica, paso a paso, por qué cada etapa se acelera o no, y verifica el resultado contra la fuerza bruta.
- **Set Cover**
  - Incluye el ejemplo de la Etapa 0, una trampa del voraz y un ejemplo de la Variante A1 con costos.
  - Añade la familia adversarial y una opción aleatoria, con costos opcionales.
  - Un slider recorre el voraz paso a paso, junto al óptimo, la razón y la cota H_d.
- **DAG**
  - Usa el ejemplo A→B, A→C, B→D, C→D u otro generado.
  - La heurística se recorre paso a paso, o se muestra el exacto.
  - Los grafos "antes" y "después" tienen la ruta crítica en naranja.
  - Un aviso compara la ganancia real con la suma de los d, para mostrar que no se suman.
- **Combinado**
  - Muestra la cobertura obligatoria, la heurística y el exacto.
  - Permite elegir λ grande o manual, y un gráfico desglosa duración y penalización.
- **Experimentos**
  - Dibuja en vivo las 17 series y las gráficas de calidad de la aproximación a partir de los CSV.
  - Incluye el resumen de ajustes y la tabla de medianas.

**Ideas clave para defender**

1. **Reconstrucción visual.** Una etapa se acelera si y solo si `DP[i][b] ≠ DP[i−1][b]`, y entonces el presupuesto baja en cᵢ. En la tabla se ve el recorrido que lo hace.
2. **El voraz falla de forma visible.** En la trampa y en la familia adversarial se ve cómo toma el conjunto más grande y termina con más conjuntos que el óptimo, aunque dentro de H_d.
3. **Por qué el DAG no es una Mochila.** Al acelerar B, la ruta crítica pasa a A→C→D y la ganancia real es 1, no 3.

**Observaciones**

- **Topes de tamaño.** La interfaz limita los tamaños para que el exacto sea instantáneo: Mochila n ≤ 10, Set Cover n ≤ 12, DAG n ≤ 11 y Combinado N ≤ 10.
- **Rutas críticas empatadas.** Cuando hay empate se dibuja solo una ruta, y la app lo avisa.
- **Corrección durante la fase.** La primera versión de la tabla de medianas fallaba con columnas duplicadas; lo detectó el probador de la app y se corrigió.
- **Segundos de ejecución.** Los tests de la app tardan ~50 s, porque regeneran las 17 figuras.
- **Aviso en los tests.** Queda un aviso inofensivo de pytest.
- **La app no mide tiempos:** solo muestra resultados y lee los CSV.

---

## 5. Hallazgos principales

Detalle completo, con tablas, en [docs/05_validacion_experimental.md](docs/05_validacion_experimental.md) §2.

| Qué | Resultado |
|---|---|
| Mochila DP | Pendientes 1,02 (variando n) y 1,04 (variando B); R² ≥ 0,9998. Duplicar n o B duplica el tiempo: Θ(n·B). |
| Algoritmos exactos | El tiempo se multiplica por **2,04–2,14 por cada +1** en x (el modelo da 2,09–2,22): exponenciales. |
| Ruta crítica | t ≈ **296 ns·n + 154 ns·m**, R² = 0,9956: lineal en n y en m, con constantes propias. |
| Voraz variando r | Pendiente 1,25, no 2: la cota n·r² es válida pero **no ajustada**, porque el voraz termina en ≈ log r rondas, no en r. Con el modelo fino (rondas × Σ\|S_j\|) el cociente queda en 1,00–1,22. |
| Heurística DAG variando n | Tiempo no monótono; la cota n·(n+m) da R² = −1,13, el modelo fino (pasos+2)·(n+m) da 0,93. |
| Cota H_d | **0 violaciones en 570 comparaciones** de Set Cover. |
| Voraz en aleatorias | Razón media 1,02; óptimo en 92 % de los casos. |
| Familia adversarial | Razón hasta **5,0** con r = 2046, frente a H_r = 8,2: el factor logarítmico es real. |
| Heurísticas de C y B | Razón media ≤ 1,013 en la práctica, pero sin garantía (hay contraejemplos). |

---

## 6. Preguntas probables en la sustentación

**¿Qué es n en cada problema?**
Mochila: n etapas y B presupuesto. Set Cover: n interacciones y r categorías. DAG: n nodos y m aristas. La entrada ocupa Θ(n·log M + log B), Θ(n·r) y Θ(n+m) respectivamente.

**¿Por qué O(n·B) no es polinomial?**
Porque B ocupa solo log B bits. En función del tamaño de la entrada, n·B = n·2^(log B), que es exponencial en esos bits. Es polinomial en el *valor* de B.

**Si la Mochila es NP-completa, ¿por qué hay un algoritmo O(n·B)?**
Porque la dureza es débil: solo es difícil cuando los números son exponencialmente grandes. Con B acotado por un polinomio en n, la DP es polinomial.

**¿Cómo prueban que su problema es NP-difícil?**
Por reducción desde un problema NP-completo conocido, en tiempo polinomial, probando (⇒) y (⇐). Mochila: la transformación tᵢ = dᵢ = vᵢ. Set Cover: Vertex Cover (universo = aristas, un conjunto por vértice). Variantes: contienen a los anteriores como caso particular.

**¿Por qué el voraz de Set Cover es O(n·r²)?**
A lo sumo r rondas, porque cada una cubre al menos una categoría nueva; cada ronda recorre n conjuntos y contar las nuevas de uno cuesta O(r).

**¿Por qué el voraz es una H_r-aproximación?**
Argumento de precios: cada elemento cubierto por un conjunto de q nuevos paga 1/q. Dentro de un conjunto óptimo de tamaño s, el j-ésimo elemento más tardío paga como mucho 1/(s−j+1); la suma es H_s. Sumando sobre los conjuntos óptimos: G ≤ H_d · OPT ≤ H_r · OPT.

**¿Es ajustada esa cota?**
Sí en orden de magnitud: la familia adversarial da razón k/2 ≈ log₂(r)/2, que crece sin cota con r. Y no existe un algoritmo polinomial con mejor factor logarítmico salvo P = NP (ver la nota sobre las citas en §7).

**¿Por qué la ruta crítica es O(n+m)?**
Orden topológico en O(n+m) (Kahn) y una pasada por los nodos relajando cada arista exactamente una vez, con Σ|sucesores| = m.

**¿Por qué la Variante C no se resuelve con la Mochila?**
Porque las reducciones no se suman: al acelerar una etapa, otra ruta paralela puede pasar a ser la crítica. En el ejemplo, acelerar B da ganancia real 1 (de 10 a 9), no 3; el óptimo exige acelerar B y C (resultado 7).

**¿Su heurística del DAG es óptima?**
No. Es el voraz por razón d/c restringido a la ruta crítica; el contraejemplo t = (4,3,6), c = (3,2,4), d = (0,2,3), B = 4 da 11 frente a 10. Garantiza factibilidad y no empeorar, pero no tiene factor.

**¿Por qué sus tiempos medidos no siguen n·r² en el voraz?**
Porque n·r² es una cota de **peor caso** (r rondas con conjuntos de tamaño r). Con las instancias generadas el voraz termina en ≈ log r rondas. Con el modelo fino rondas × Σ|S_j| el ajuste es casi perfecto. La cota no se viola: el tiempo crece más despacio.

**¿Cómo validaron T(n) experimentalmente?**
Mediana de varias repeticiones por tamaño, ajuste de la constante c por mínimos cuadrados, y cociente medido/(c·T), que debe ser ≈ 1; además, la pendiente log-log (polinomiales) o el factor por +1 (exponenciales) frente a los del propio modelo.

**¿Qué mide el tiempo?**
Solo el algoritmo: la instancia se genera antes del cronómetro; se descarta una ejecución de calentamiento y se apaga el recolector de basura.

---

## 7. Recomendaciones y pendientes

### Antes de entregar (en orden de importancia)

1. **Verificar las citas de `docs/04`.** Las referencias a Feige (1998) y Dinur–Steurer (2014) sobre la dureza de aproximar Set Cover, y las de Johnson (1974) y Chvátal (1979), se escribieron de memoria. Confirmen autores, año, título y revista en la fuente antes de citarlas.
2. **Completar `docs/01_formalizacion.md`.** Hoy es un placeholder porque su Etapa 0 ocupa ese papel. Lo más simple es copiar la Etapa 0 ahí (o enlazarla). Pídanlo si quieren que se integre.
3. **Llevar las tres preguntas abiertas al docente** (están en la Etapa 0 y en `CLAUDE.md`):
   - Variante ponderada: ¿costos por interacción (A1, la implementada) o pesos por categoría con límite de auditorías (A2)?
   - Variante combinada: ¿penalización λ o cobertura obligatoria? (Ambas están implementadas.)
   - Reducción de la Parte 2: ¿desde Vertex Cover (la propuesta) o desde X3C?
4. **Hacer un commit.** El repositorio no tiene ningún commit; todo está sin versionar. Conviene versionar antes de seguir tocando archivos. Los CSV de resultados son pequeños y pueden incluirse.
5. **Confirmar el supuesto de n = 0 etapas** en la reducción de Set Cover a la Variante B (`docs/02` §4). Si el docente no admite instancias sin etapas, se resuelve con una etapa trivial (t = d = 0, c > B).

### Sobre los resultados experimentales

- **Los tiempos dependen de la máquina.** Los CSV incluidos se midieron en el equipo donde se hizo el trabajo. Si van a presentar con otro computador, repitan `python -m experimentos.correr_todo` (≈ 40 s) y luego `python -m visualizacion.graficas`: lo que se defiende es la *forma* del crecimiento, no los segundos.
- **No cierren otras aplicaciones pesadas** mientras corren los experimentos; el ruido sube en los tiempos menores a 1 ms.
- **Si el docente pide otras densidades o tamaños**, cambien los diccionarios `COMPLETO` al inicio de cada `correr_*.py`; el resto del flujo no cambia.

### Para la defensa (sin notas)

- **Estudien por algoritmo la tabla de conteo de operaciones** de `docs/03` y comparen con los comentarios `# O(.)` del código; deben poder reconstruir T(n) en voz alta.
- **Practiquen los tres contraejemplos:** la trampa del voraz (3 contra 2), el DAG de 4 nodos (ganancia 1 contra 3) y la heurística del DAG (11 contra 10).
- **Sepan decir qué NO garantiza cada heurística.** Las de B y C son factibles y no empeoran, pero no tienen factor de aproximación; no lo afirmen.
- **Usen la app como apoyo visual:** tabla DP para la reconstrucción, el slider del voraz para la trampa, el DAG de la Etapa 0 y la pestaña Experimentos para los cocientes.
- **Distingan cota y medición:** si les preguntan por qué el voraz "no sigue n·r²", la respuesta es peor caso frente a modelo fino (§5).

### Mantenimiento del código

- **Mantengan los comentarios `# O(.)` sincronizados** si modifican un algoritmo, y repitan los tests.
- **No midan tiempos fuera de `experimentos/`** (convención del proyecto).
- **No vectoricen con numpy** los algoritmos de `core/`: se perdería la correspondencia con el conteo de operaciones.

---

## 8. Limitaciones conocidas

- **Pocos tamaños por serie** (5–6) y 3–7 repeticiones: sirven para identificar el orden de crecimiento, no para estimar constantes con precisión. El rango mín.–máx. llega a ±10 % por debajo de 1 ms.
- **Python puro con ciclos explícitos:** los segundos absolutos no son comparables con implementaciones compiladas; solo la forma del crecimiento.
- **Instancias sintéticas con densidad fija** (p = 0,3 en Set Cover, m = 2n–4n en DAG). Otras densidades cambian las constantes y, en el voraz, el número de rondas.
- **R² en escala lineal** lo dominan los tamaños grandes; por eso se reporta también el rango del cociente.
- **El exacto de Set Cover depende de k\*** (se detiene al hallar el óptimo); el cociente llega a 1,4–1,6 en algún punto.
- **Las heurísticas de B y C no tienen factor de aproximación**; los contraejemplos están documentados en `docs/04`.
- **Topes de la app:** tamaños pequeños en la interfaz para que el exacto sea instantáneo.

---

*Generado al cierre de la Fase 7. Para el detalle cronológico de cada prompt, ver [HISTORIAL.md](HISTORIAL.md).*
