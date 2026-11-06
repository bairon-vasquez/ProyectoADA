# Manual técnico — Proyecto Ruta (Grupo 3)

**Análisis y Diseño de Algoritmos · 2026-B** · Primera entrega

**Integrantes:** Bairon Vasquez · Sergio Velasquez

**Repositorio:** https://github.com/bairon-vasquez/ProyectoADA

Este manual describe la solución base: los algoritmos, la estructura del código, los formatos de entrada y salida, los pasos para ejecutarla y sus limitaciones. La formalización, las pruebas de NP-dureza y la deducción de T(n) están en el *Informe de la primera entrega*.

---

## 1. Alcance

La solución base resuelve las dos partes del proyecto:

- **Parte 1:** aceleración óptima de una cadena de n etapas bajo un presupuesto B (Mochila 0/1), con programación dinámica.
- **Parte 2:** cobertura mínima de auditoría (Set Cover), con el algoritmo voraz.

Además incluye, como trabajo adicional, la Variante A1 (auditoría ponderada por costo), las variantes B (presupuesto conjunto) y C (DAG), un conjunto de experimentos de validación y una aplicación para la sustentación. Esta entrega se centra en las dos partes base.

---

## 2. Requisitos e instalación

- **Python 3.11 o superior.**
- Dependencias (`requirements.txt`): `numpy`, `matplotlib`, `pandas`, `networkx`, `streamlit` y `pytest`. Los algoritmos de `core/` y el ejecutor de casos no usan ninguna de ellas (solo la biblioteca estándar); las demás se necesitan para gráficas, aplicación y tests.

```
python -m venv .venv
.venv\Scripts\activate            (Windows; en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
```

---

## 3. Algoritmos

| Problema | Algoritmo | Módulo y función | T(n) | Calidad |
|---|---|---|---|---|
| Parte 1 | Programación dinámica con reconstrucción | `core/mochila.py` · `mochila_dp` | Θ(n·B) | Exacto |
| Parte 1 | Fuerza bruta (referencia) | `mochila_fuerza_bruta` | Θ(n·2^n) | Exacto |
| Parte 2 | Voraz (más categorías nuevas) | `core/set_cover.py` · `cobertura_voraz` | O(n·r·min(n, r)) ⊆ O(n·r²) | ≤ H_r · óptimo |
| Parte 2 | Exacto por tamaño creciente (referencia) | `cobertura_exacta` | O(2^n·n·r) | Exacto |
| Variante A1 | Voraz ponderado (menor a_j / nuevas) | `cobertura_voraz_ponderada` | O(n·r·min(n, r)) ⊆ O(n·r²) | ≤ H_d · óptimo |
| Variante A1 | Exacto ponderado (referencia) | `cobertura_exacta_ponderada` | O(2^n·n·r) | Exacto |
| Variante A1 | Exacto por máscaras de categorías (r pequeño, a lo sumo una opción por grupo) | `cobertura_exacta_mascaras` | O(n·2^r) | Exacto |
| Variante C | Heurística de la ruta crítica sobre el flujo (acelera en la ruta crítica la etapa de mejor d_i/c_i) | `core/dag.py` · `dag_heuristica` | O(n·(n+m)) | Sin garantía; se contrasta con la Mochila (cadena) o el exacto (n ≤ 16) |
| Variante B | Cobertura de costo mínimo a\* + Mochila con B − a\* | `core/combinado.py` · `combinado_cobertura_obligatoria_mascaras` | O(n·2^r + n·B) | Exacto |

### 3.1 Parte 1: programación dinámica

`construir_tabla_dp` llena `DP[i][b]` = máxima reducción de tiempo con las primeras i etapas y presupuesto b:

    DP[i][b] = DP[i−1][b]                                  si c_i > b
    DP[i][b] = max(DP[i−1][b], DP[i−1][b−c_i] + d_i)       si c_i ≤ b          DP[0][b] = 0

`reconstruir_etapas` recorre la tabla desde DP[n][B] hacia atrás: la etapa i se acelera si y solo si DP[i][b] ≠ DP[i−1][b], y entonces b baja en c_i. `mochila_dp` compone ambas y devuelve las etapas, la reducción, el costo y la duración final. Es **pseudo-polinomial**: el tiempo crece con el valor de B, no con sus bits.

### 3.2 Parte 2: voraz

Primero se comprueba la factibilidad (la unión de todos los conjuntos debe ser U; si no, la función devuelve `None`). Después, mientras queden categorías sin cubrir, se elige la interacción que cubre más categorías **todavía no cubiertas** (desempate: menor índice) y se marcan como cubiertas. Cada elección se registra (`pasos`), con las categorías nuevas que aportó. Hay a lo sumo min(n, r) rondas.

### 3.3 Variante A1

Igual que el voraz, pero elige la interacción de menor `a_j / nuevas` (costo por categoría nueva), comparado con productos cruzados enteros para evitar divisiones.

### 3.4 Comentarios que cuentan operaciones

Cada algoritmo de `core/` está escrito con ciclos explícitos (sin vectorizar) y lleva comentarios `# O(.)` que indican el costo de cada línea y cuántas veces corre cada ciclo. Esos comentarios coinciden con la deducción de T(n) del informe.

---

## 4. Estructura del código

```
ProyectoADA/
├── core/                  Capa 1 · algoritmos puros (sin prints, sin gráficas, sin archivos)
│   ├── instancias.py      dataclasses de entrada: InstanciaMochila, InstanciaSetCover, ...
│   ├── generadores.py     generadores sintéticos con semilla fija
│   ├── mochila.py         fuerza bruta, DP y reconstrucción
│   ├── set_cover.py       voraz, voraz ponderado y exactos
│   ├── dag.py, combinado.py   variantes C y B (trabajo adicional)
├── experimentos/          Capa 2 · medición y ejecución de casos (único lugar donde se mide el tiempo)
│   ├── casos.py           lector y validación de casos (JSON)
│   ├── correr_casos.py    ejecutor: resultado, tiempo y traza por caso
│   ├── generar_casos.py   crea los casos de ejemplo en casos/
│   ├── medir.py, correr_*.py   experimentos de validación (CSV)
├── casos/                 casos de entrada (JSON)
├── visualizacion/         Capa 3 · gráficas y aplicación; solo lee resultados
├── docs/                  análisis formal
├── entrega/               informe y manual de la primera entrega
└── tests/                 pytest
```

**Regla de capas.** `core/` no importa nada de las otras carpetas y no hace entrada/salida: los algoritmos que se analizan son exactamente los que se miden. Los archivos se leen y escriben solo en `experimentos/`.

**Clases principales** (todas `dataclass` inmutables):

- `InstanciaMochila(t, c, d, B)`: la cadena de etapas y el presupuesto.
- `InstanciaSetCover(r, conjuntos, a, w)`: categorías, conjuntos de cada interacción y costos.
- `SolucionMochila(etapas, reduccion, costo, duracion)` y `SolucionCobertura(indices, costo, pasos)`.

Dentro del código los índices son **base 0**; en los archivos de entrada y salida y en los documentos son **base 1**. La conversión la hace únicamente `experimentos/casos.py` (al leer) y `experimentos/correr_casos.py` (al escribir).

---

## 5. Formatos de entrada y salida

### 5.1 Entrada: un archivo JSON por caso

```json
{
  "id": "caso_01_etapa0",
  "descripcion": "texto libre (opcional)",
  "parte1": { "t": [5, 8, 6, 4], "c": [3, 4, 2, 3], "d": [2, 4, 1, 2], "B": 6 },
  "parte2": {
    "r": 5,
    "conjuntos": [[1, 2, 3], [2, 4], [3, 4], [4, 5], [1, 5]],
    "costos": [1, 1, 1, 1, 1]
  }
}
```

| Campo | Tipo | Significado y restricciones |
|---|---|---|
| `id` | texto (opcional) | Nombre del caso; sin él se usa el nombre del archivo. Da nombre a los archivos de salida. |
| `descripcion` | texto (opcional) | Texto libre. |
| `parte1.t` | lista de enteros ≥ 0 | Duración normal de cada etapa (longitud n). |
| `parte1.c` | lista de enteros ≥ 1 | Costo de acelerar cada etapa (longitud n). |
| `parte1.d` | lista de enteros ≥ 0 | Reducción de tiempo de cada etapa; debe cumplir d_i ≤ t_i (longitud n). |
| `parte1.B` | entero ≥ 0 | Presupuesto total. |
| `parte2.r` | entero ≥ 1 | Número de categorías de riesgo (1…r). |
| `parte2.conjuntos` | lista de listas de enteros | Para cada interacción, las categorías (1…r) que cubre. |
| `parte2.costos` | lista de enteros ≥ 1 (opcional) | Costo de auditar cada interacción. **Si está presente**, se resuelve la Variante A1 (minimizar el costo total); si no, cada interacción cuesta 1 (Parte 2 original). |

Reglas: `parte1` y `parte2` son opcionales, pero debe venir al menos una. Todos los valores son enteros (no se aceptan decimales ni booleanos).

### 5.1b Entrada en el formato del docente (G3)

El lector reconoce automáticamente este formato por la presencia de la clave `etapas`. Ejemplo reducido (el completo es `casos/entrada_G3_mochila_20_nodos.json`):

```json
{
  "parametros": { "numero_etapas": 20, "presupuesto_aceleracion_B": 72,
                  "presupuesto_conjunto_aceleracion_y_auditoria": 100, "numero_categorias_riesgo": 12 },
  "flujo": [ { "origen": "E01", "destino": "E02" } ],
  "categorias_riesgo": [ { "id": "R01", "categoria": "sesgo", "importancia": 4 } ],
  "etapas": [
    { "id": "E01", "duracion_normal": 18, "costo_aceleracion": 7, "reduccion_tiempo_si_acelera": 5,
      "variaciones_auditoria": [
        { "id": "parcial",  "costo": 3, "riesgos_cubiertos": ["R01", "R02"] },
        { "id": "completa", "costo": 6, "riesgos_cubiertos": ["R01", "R02", "R03", "R10"] } ] }
  ]
}
```

| Campo | Se convierte en |
|---|---|
| `etapas[i].duracion_normal`, `costo_aceleracion`, `reduccion_tiempo_si_acelera` | t_i, c_i, d_i de la Parte 1 (enteros; c_i ≥ 1, d_i ≤ t_i) |
| `parametros.presupuesto_aceleracion_B` | B de la Parte 1 |
| cada elemento de `etapas[i].variaciones_auditoria` | una interacción de la Parte 2 (Variante A1): conjunto = `riesgos_cubiertos`, costo = `costo` (≥ 1). Se nombra «E01 parcial» |
| `categorias_riesgo[k].id` / `importancia` | categoría k de U y su peso w_k (≥ 1) |
| `parametros.presupuesto_conjunto_aceleracion_y_auditoria` | presupuesto de la Variante B (opcional; si falta, no se ejecuta la Variante B) |
| `flujo` | se valida como DAG (etapas existentes, sin ciclos, sin aristas repetidas ni autoaristas). Si es una **cadena en serie** se resuelve la Parte 1 (Mochila, exacta) y la heurística de la Variante C sirve de contraste; si tiene ramas, la Parte 1 y la Variante B se **omiten** (la duración es la ruta crítica) y se resuelve la Variante C |
| `parametros.numero_etapas`, `numero_categorias_riesgo` | solo se verifican contra los tamaños reales de las listas |
| `riesgos_cubiertos_auditoria_completa` | redundante con la variación `completa`: se ignora |

Regla del modelo: de cada etapa se audita **a lo sumo una variación**. Los errores de este formato se reportan igual que en §5.1, por ejemplo `etapa repetida 'E01'`, `riesgo inexistente 'R99'`, `el flujo tiene un ciclo`.

**Errores.** Si un caso no cumple el formato, el ejecutor se detiene con un mensaje que indica el caso y el campo, por ejemplo:

    Caso inválido: caso_01: etapa 2: d (9) no puede superar t (8)
    Caso inválido: caso_07: interacción 3: categoría 9 fuera de 1..5
    Caso inválido: malo.json: JSON mal formado (...)

Una instancia de la Parte 2 que no se puede cubrir (alguna categoría no está en ningún conjunto) **no es un error de formato**: se reporta como `"factible": false` con el mensaje "sin solución".

### 5.2 Salida por caso

Para cada caso se escriben cuatro archivos más un resumen común en la carpeta de salida (por defecto `experimentos/resultados/casos/`): `<id>.json`, `<id>_traza.md`, `<id>_dp.csv` y `<id>_tiempos.csv`, y al final `resumen_casos.csv`.

**`<id>.json`**: resultado, tiempo y traza (lectura por programa). Estructura:

```
{
  "id", "descripcion",
  "parte1": {
    "entrada":   { "n", "B" },
    "resultado": { "etapas_aceleradas": [..], "costo_usado", "presupuesto", "reduccion",
                   "duracion_inicial", "duracion_final" },
    "complejidad", "celdas_dp",
    "tiempo_s", "tiempo_min_s", "tiempo_max_s", "repeticiones",
    "traza": { "etapas": [ {etapa, t, c, d, acelerada, t_final} ],
               "reconstruccion": [ {etapa, presupuesto_b, dp_i_1_b (sin acelerar), dp_acelerando_i,
                                    dp_i_b, decision, presupuesto_siguiente} ],
               "tabla_dp": [[..]]            (se omite si tiene más de 5000 celdas) },
    "verificacion": { "metodo", "reduccion_optima", "coincide" }   (fuerza bruta, solo si n ≤ 20)
  },
  "parte2": {
    "entrada":   { "interacciones", "categorias", "variante", "d" },
    "factible",
    "resultado": { "interacciones_auditadas": [..], "orden_de_eleccion": [..], "cantidad",
                   "costo_total", "categorias_cubiertas", "categorias_totales", "cobertura_completa" },
    "cota", "H_d", "H_r", "complejidad", "tiempo_s", "tiempo_min_s", "tiempo_max_s", "repeticiones",
    "traza": { "pasos": [ {paso, interaccion, categorias_nuevas, n_nuevas, costo_a,
                           costo_acumulado, categorias_cubiertas, categorias_pendientes,
                           razon_a_sobre_nuevas (solo en A1)} ] },
    "verificacion": { "metodo", "optimo", "optimo_interacciones",
                      "razon_voraz_sobre_optimo", "cumple_cota_Hd" }   (≤ 16 interacciones por fuerza bruta;
                                                                       con grupos y r ≤ 20, por máscaras)
  },
  "variante_c": {                         (solo si el caso trae `flujo`)
    "entrada": { "n", "m", "B", "es_cadena" },
    "resultado": { "etapas_aceleradas", "costo_usado", "duracion_inicial", "duracion_final",
                   "ruta_critica_inicial", "ruta_critica_final" },
    "traza": { "pasos": [ {paso, etapa, ruta_critica_tras} ] },
    "verificacion": { "metodo", "duracion_optima", "coincide" }   (Mochila si es cadena; exacto si n ≤ 16)
  },
  "variante_b": {                         (solo con presupuesto conjunto, las dos partes y flujo en cadena)
    "presupuesto_conjunto",
    "exacta": { "interacciones_auditadas", "costo_auditoria", "presupuesto_para_acelerar",
                "etapas_aceleradas", "costo_total", "duracion_final", "reduccion", "tiempo_s", ... },
    "voraz":  { igual, con la cobertura voraz },
    "comparacion": { "a_estrella", "a_voraz", "razon_a_voraz_sobre_a_estrella",
                     "duracion_exacta", "duracion_voraz", "tiempo_perdido_por_exceso_de_auditoria" }
  },
  "nombres": { "etapas", "interacciones", "categorias" }   (solo en el formato del docente)
}
```

Con el formato del docente, `resultado` incluye además listas con los ids originales (`etapas_aceleradas_nombres`, `interacciones_auditadas_nombres`) y `una_variacion_por_etapa` (`cumple`, `etapas_repetidas`, `interacciones_reparadas`, `costo_reparado`).

**`<id>_traza.md`**: la misma información en texto legible: etapas y costos, tabla DP completa (casos pequeños), tabla de reconstrucción paso a paso, y las elecciones del voraz; con flujo, la Variante C; con presupuesto conjunto, la Variante B.

**`<id>_dp.csv`**: la tabla DP[i][b] completa (filas i = 0…n, columnas b = 0…B); se omite si tiene más de 5000 celdas.

**`<id>_tiempos.csv`**: una fila por repetición de cada algoritmo medido (Mochila, voraz de cobertura, heurística del DAG y Variante B exacta), con las columnas de `medir.COLUMNAS` (`algoritmo, barrido, n, parametro, valor_parametro, repeticion, tiempo_s, valor_solucion, extra`); `barrido` lleva el id del caso.

**`resumen_casos.csv`**: una fila por caso. Columnas: `caso, n_etapas, B, duracion_inicial, duracion_final, reduccion, costo_usado, etapas_aceleradas, tiempo_parte1_s, verif_parte1, interacciones, categorias, variante, tamano_cobertura, costo_cobertura, optimo, razon_voraz_optimo, tiempo_parte2_s, B_conjunto, duracion_b_exacta, duracion_b_voraz, duracion_variante_c` (`B_conjunto` y las dos `duracion_b_*` solo se llenan en los casos con Variante B; `duracion_variante_c`, en los que traen flujo).

**Convenciones de la salida.** Etapas, interacciones y categorías en base 1 (en el formato del docente se muestran sus ids: E01, R01, «E12 completa»). Los tiempos son segundos (mediana de las repeticiones; se guardan también el mínimo y el máximo). `verif_parte1` vale `ok`, `omitida` (n > 20) o `FALLA` (no debería ocurrir).

**Consola.** Una línea por caso con los tiempos de la Parte 1 y de la Parte 2.

---

## 6. Pasos de ejecución

**1. Instalar** (ver §2).

**2. Ejecutar los casos:**

```
python -m experimentos.correr_casos                          # todos los .json de casos/
python -m experimentos.correr_casos casos/caso_01_etapa0.json   # un solo caso
python -m experimentos.correr_casos casos/ --repeticiones 11 --salida mi_salida/
```

Opciones: el primer argumento es un archivo o una carpeta (por defecto `casos/`); `--repeticiones` fija cuántas veces se mide cada algoritmo (por defecto 7); `--salida` cambia la carpeta de salida.

**3. Regenerar los casos de ejemplo** (opcional; son reproducibles, semilla fija):

```
python -m experimentos.generar_casos
```

**4. Ejecutar los tests:**

```
pytest
```

**5. Trabajo adicional** (opcional):

```
python -m experimentos.correr_todo        # experimentos de validación (CSV)
python -m visualizacion.graficas          # gráficas y tablas en figuras/
streamlit run visualizacion/app.py        # aplicación de sustentación
```

### 6.1 Reproducibilidad

- Los resultados salen del código entregado **sin editar la lógica de los algoritmos**: el ejecutor solo lee el caso, llama a `core/` y registra el resultado, el tiempo y las decisiones.
- Los generadores usan una semilla fija: los mismos parámetros dan siempre la misma instancia, y los casos de `casos/` se pueden regenerar idénticos.
- Los resultados (etapas, costos, coberturas) son deterministas. Los tiempos varían un poco entre ejecuciones; por eso se reporta la mediana de varias repeticiones tras un calentamiento.

### 6.2 Usar los casos de la profesora

1. Copiar los archivos a la carpeta `casos/` (o a otra) y ejecutar `python -m experimentos.correr_casos <ruta>`.
2. Si los casos usan el formato de §5.1 o el del docente (§5.1b), no hay que cambiar nada. El caso `entrada_G3_mochila_20_nodos.json` del docente ya está en `casos/` y se ejecuta así: `python -m experimentos.correr_casos casos/entrada_G3_mochila_20_nodos.json`.
3. Si usan otro formato, se adapta **solo** la función de lectura de `experimentos/casos.py` para que produzca las mismas estructuras (`InstanciaMochila` e `InstanciaSetCover`, más los nombres y los grupos de `Caso`). Los algoritmos, el ejecutor y las salidas no cambian.

---

## 7. Pruebas

`pytest` ejecuta, entre otras, estas comprobaciones:

- Cada algoritmo exacto (DP y exactos de Set Cover) se compara contra la fuerza bruta en instancias aleatorias pequeñas (n ≤ 15).
- El voraz cumple `voraz ≤ H_r · óptimo` en instancias aleatorias, y existe un test con la "trampa" donde el voraz no es óptimo.
- El lector de casos rechaza cada tipo de entrada inválida con un mensaje claro.
- La traza de cada caso es consistente con su resultado (las decisiones de la reconstrucción son las etapas aceleradas; DP[n][B] es la reducción; la última elección del voraz deja 0 categorías pendientes).
- Los casos versionados en `casos/` coinciden con los que genera `generar_casos.py`.
- El exacto por máscaras se compara con la fuerza bruta (con y sin la regla «una opción por grupo») en instancias aleatorias pequeñas, y el lector del docente se prueba con el caso real (`tests/test_formato_docente.py`).

---

## 8. Limitaciones

- **Pseudo-polinomial:** la DP de la Parte 1 solo es práctica para presupuestos B moderados; su tabla ocupa (n+1)·(B+1) celdas.
- **Voraz no óptimo:** el voraz de la Parte 2 garantiza solo `≤ H_r · óptimo`. En la práctica es casi óptimo, pero existen instancias donde se aleja (se incluye una en `casos/caso_02_trampa_voraz.json`).
- **Verificación exacta limitada:** la comparación de la Parte 1 con la fuerza bruta se hace solo para n ≤ 20; en casos mayores se reporta como `omitida`. En la Parte 2, el óptimo se calcula por fuerza bruta con ≤ 16 interacciones o, si hay grupos y r ≤ 20, por máscaras.
- **Tabla DP grande:** si supera 5000 celdas no se guarda completa en el JSON (se conserva la reconstrucción completa).
- **Tiempos:** son del equipo donde se ejecuta (Python puro); lo que se valida es la forma del crecimiento, no los segundos.
- **Un solo caso del docente disponible:** el formato de §5.1b se dedujo de `entrada_G3_mochila_20_nodos.json`. Se asumió que las variaciones `parcial` y `completa` de una etapa son excluyentes y que cada variación es una interacción de la Parte 2 (ver §6.2 si otros casos difieren).
- **Heurísticas de las variantes B y C:** son factibles pero no tienen factor de aproximación demostrado.
