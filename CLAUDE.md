# Proyecto Ruta — ADA 2026-2

Proyecto semestral de Análisis y Diseño de Algoritmos. **La nota NO depende de que el código corra**, sino de demostrar formalmente la eficiencia: definición de n, deducción explícita de T(n), prueba de NP-dureza por reducción, cota de aproximación y validación experimental (tiempo medido vs. T(n) teórico). Se sustenta sin notas: todo debe quedar explicado y ser entendible por el equipo.

## Problemas (formalizados en `docs/Etapa 0 — Formalización del problema.md`)

- **Parte 1 (Mochila 0/1):** n etapas en serie; etapa i dura t_i, acelerarla cuesta c_i y reduce d_i (0 ≤ d_i ≤ t_i). Presupuesto B. Elegir x ∈ {0,1}^n con Σc_i·x_i ≤ B minimizando Σt_i − Σd_i·x_i (≡ maximizar Σd_i·x_i). Exacto: `DP[i][b] = max(DP[i-1][b], DP[i-1][b-c_i] + d_i)`, T(n,B) = O(n·B), pseudo-polinomial.
- **Parte 2 (Set Cover):** n interacciones, r categorías, U = {1..r}, S_j ⊆ U. Mínimo C con ∪S_j = U. Voraz (más categorías nuevas): T(n,r) = O(n·r²); cota H_r ≈ ln r + 1 (Johnson 1974, Chvátal 1979).
- **Variante A1 (ponderada):** costo a_j ≥ 1 por interacción; minimizar Σa_j cubriendo U. Voraz por menor a_j / |nuevas|; cota H_d, d = max|S_j|.
- **Variante B (combinada):** presupuesto conjunto Σc_i·x_i + Σa_j ≤ B. Minimizar (Σt_i − Σd_i·x_i) + λ·Σ(w_k no cubiertas). Con λ grande: cobertura de costo mínimo + Mochila con el presupuesto restante.
- **Variante C (DAG):** G=(V,E), n=|V|, m=|E|, fuente y sumidero ficticios. Duración = ruta más larga con pesos t_i − d_i·x_i (DP en orden topológico, O(n+m)). Minimizar la ruta crítica con Σc_i·x_i ≤ B. Al acelerar, la ruta crítica puede cambiar.

Todos los valores son enteros no negativos. Instancias sintéticas con semilla fija.

## Arquitectura (3 capas)

1. `core/` — algoritmos puros: sin prints, sin gráficas, sin I/O.
2. `experimentos/` — medición (ÚNICO lugar donde se miden tiempos) → CSV en `experimentos/resultados/`.
3. `visualizacion/` — presentación; solo LEE CSV, nunca mide. `graficas.py` (PNG en `figuras/`) y `app.py` (Streamlit).

`docs/` contiene el análisis formal (Markdown + LaTeX). `tests/` usa pytest.

## Convenciones

- Python 3.11+, type hints, docstrings en español.
- En cada algoritmo, comentarios que **cuentan operaciones** (qué línea es O(1), qué ciclo corre cuántas veces); deben coincidir con la deducción de T(n) en `docs/`.
- Algoritmos de `core/` con ciclos explícitos, **sin vectorizar con numpy**, para que el conteo corresponda al código.
- Índices 0-based en código, 1-based en los documentos.
- Tests: cada exacto contra fuerza bruta en instancias pequeñas aleatorias (n ≤ 15); voraz ≤ H_r · óptimo.
- Generadores: cada uno usa su propio `random.Random(semilla)`; Set Cover garantiza factibilidad.

## Decisiones tomadas

- La estructura se creó en la raíz del repo (`ProyectoADA/`), sin carpeta anidada `proyecto-ruta/`.
- Las instancias son dataclasses inmutables (`frozen=True`) con tuplas / frozensets.
- `InstanciaSetCover` sirve para Parte 2 (a_j = 1) y A1 (a_j ≥ 1); lleva también los pesos w_k para la Variante B.
- `InstanciaDAG` guarda solo los nodos reales; fuente/sumidero ficticios los añade el algoritmo. Los algoritmos no deben asumir que los índices ya están en orden topológico.

- CSV de tiempos: columnas `algoritmo, barrido, n, parametro, valor_parametro, repeticion, tiempo_s, valor_solucion, extra`. `extra` guarda el trabajo del modelo fino (rondas × Σ|S_j| en el voraz; evaluaciones × (n+m) en la heurística DAG) para validar sin depender solo de la cota de peor caso.
- Los CSV de razones (`razon_*.csv`) miden calidad (heurística / óptimo), no tiempo.
- `generar_set_cover_adversarial(k)`: familia con óptimo 2 y voraz k (r = 2^(k+1) − 2).
- Fase 6: pendiente medida y factor de crecimiento se comparan con los del PROPIO modelo en el mismo rango (no con el exponente asintótico). Ajuste c·f por mínimos cuadrados; c·f + c0 donde hay término constante (Combinado). Hallazgo: las cotas de peor caso n·r² y n·(n+m) son válidas pero no ajustadas; el modelo fino (`extra`) sí ajusta.
- Gráficas: paleta de referencia validada (slots 1-3, todos los pares), trazos finos, rejilla recesiva, leyenda siempre, PNG en `figuras/`.
- App (Fase 7): `visualizacion/app.py` + `dibujos.py`; tema claro en `.streamlit/config.toml`. Usa `core` solo para mostrar resultados y lee los CSV; no mide. Tope de tamaños en la UI para que el exacto sea instantáneo (Mochila n ≤ 10, Set Cover n ≤ 12, DAG n ≤ 11, Combinado N ≤ 10). `tests/test_app.py` usa `streamlit.testing.v1.AppTest`.

- Casos de la profesora (JSON en `casos/`): `experimentos/cargar_caso.py` los traduce a instancias (cada variación de auditoría = una interacción) y `python -m experimentos.correr_caso <json|carpeta>` escribe en `experimentos/resultados/casos/` la traza (`_traza.md`), la tabla DP (`_dp.csv`) y los tiempos (`_tiempos.csv`). Con N = 35 la enumeración 2^N es inviable, por eso se añadió `cobertura_exacta_dp` (DP sobre máscaras de categorías, O(N·2^r)) y `combinado_cobertura_obligatoria_dp`.

## Preguntas abiertas para el docente (de la Etapa 0)

- Variante ponderada: ¿A1 (costos por interacción) o A2 (pesos por categoría con límite de auditorías)? Se implementa A1.
- Variante combinada: ¿penalización λ o cobertura obligatoria? Se implementan ambas (cobertura obligatoria + heurística para λ general).
- Reducción de la Parte 2: se propone desde Vertex Cover.

## Fases

1 Esqueleto ✔ · 2 Mochila ✔ · 3 Set Cover ✔ · 4 Variantes A1/B/C ✔ · 5 Experimentos ✔ · 6 Gráficas e informe ✔ · 7 App Streamlit ✔. Una fase a la vez; detenerse al final de cada una para revisión.
