# Etapa 0 — Formalización del problema

Oct 3, 2026 · @Bairon Vasquez

## Introducción y notación común

Este documento formaliza los cinco problemas del Proyecto Ruta: las dos partes base y las tres variantes obligatorias. Para cada uno se define el tamaño de entrada, la entrada, la salida, las restricciones y el objetivo, sin código todavía.

Notación usada en todo el documento:

- &#91;n\] = {1, 2, …, n} denota el conjunto de índices de 1 a n.
- Todas las cantidades numéricas (duraciones, costos, reducciones, presupuesto) son **enteros no negativos**. Este supuesto es necesario para la programación dinámica sobre el presupuesto.
- Para cada problema de optimización se da también su **versión de decisión**, que es la que se usa en las pruebas de NP-dureza.
- "Tamaño de la representación" significa el número de bits necesarios para escribir la entrada. Se distingue del valor numérico de los parámetros, lo cual es clave para explicar por qué O(n·B) es pseudo-polinomial.

## Parte 1 — Aceleración de la cadena bajo presupuesto

El problema consiste en elegir qué etapas acelerar sin exceder B para minimizar la duración total. Es equivalente a la Mochila 0/1.

**Tamaño de la entrada.** Los parámetros que crecen son n, el número de etapas, y B, el presupuesto. En bits, la entrada ocupa Θ(n·log M + log B), donde M es el mayor valor entre los t\_i, c\_i y d\_i. Por eso B aporta solo log B bits, aunque la tabla de la DP tenga B + 1 columnas.

**Entrada.**

- n ∈ ℕ, el número de etapas en serie.
- Para cada etapa i ∈ \[n\]: duración normal t\_i ≥ 0, costo de aceleración c\_i ≥ 1 y reducción d\_i con 0 ≤ d\_i ≤ t\_i.
- El presupuesto B ≥ 0.

**Salida.** Un subconjunto S ⊆ \[n\] de etapas a acelerar o, de forma equivalente, un vector x ∈ {0,1}^n con x\_i = 1 si la etapa i se acelera.

**Restricción.**

```latex
\sum_{i=1}^{n} c_i\,x_i \le B
```

**Objetivo.** Minimizar la duración total de la cadena. Como todas las etapas están en serie, todas pertenecen al camino crítico:

```latex
\min_{x \in \{0,1\}^n} \; D(x) = \sum_{i=1}^{n} t_i - \sum_{i=1}^{n} d_i\,x_i
```

Como la suma de los t\_i es constante, minimizar D(x) equivale a **maximizar la suma de los d\_i·x\_i** con la misma restricción. Esto es la Mochila 0/1 con valor d\_i y peso c\_i.

**Versión de decisión (ACELERACIÓN-CADENA).** Dados (t, c, d, B) y un entero K, ¿existe x ∈ {0,1}^n con costo total ≤ B y D(x) ≤ K?

**Supuestos.** Cada etapa se acelera como máximo una vez y su reducción es fija (todo o nada). Una etapa con c\_i > B nunca puede elegirse y puede descartarse.

**Ejemplo.** Con n = 4 y B = 6:

| Etapa | t\_i | c\_i | d\_i |
| --- | --- | --- | --- |
| 1 | 5 | 3 | 2 |
| 2 | 8 | 4 | 4 |
| 3 | 6 | 2 | 1 |
| 4 | 4 | 3 | 2 |

Sin acelerar, la cadena dura 23. La mejor elección es S = {2, 3}: cuesta 6, reduce 5 y deja la cadena en 18.

## Parte 2 — Cobertura mínima de auditoría

El problema consiste en elegir el menor número de interacciones cuya auditoría cubra las r categorías de riesgo. Es Cobertura de Conjuntos (Set Cover).

**Tamaño de la entrada.** Los parámetros son n, el número de interacciones candidatas, y r, el número de categorías de riesgo. La entrada ocupa Θ(n·r) si cada subconjunto se guarda como vector de bits de longitud r, o Θ(Σ|S\_j|) si se guarda como lista.

**Entrada.**

- El universo de categorías U = \[r\].
- Una familia F = {S\_1, …, S\_n}, donde S\_j ⊆ U es el conjunto de categorías que cubre la interacción j si se audita.

**Salida.** Un subconjunto C ⊆ \[n\] de interacciones a auditar.

**Restricción (cobertura completa).**

```latex
\bigcup_{j \in C} S_j = U
```

**Objetivo.**

```latex
\min_{C \subseteq [n]} \; |C|
```

**Versión de decisión (COBERTURA-AUDITORÍA).** Dados U, F y un entero k, ¿existe C con |C| ≤ k que cubra U?

**Supuestos.** La instancia es factible: la unión de todos los S\_j es U. El generador de instancias debe garantizarlo, por ejemplo asignando cada categoría a al menos una interacción. Si no se cumple, el algoritmo debe reportar "sin solución".

**Ejemplo.** Con r = 5 y n = 5:

| Interacción | Categorías que cubre |
| --- | --- |
| 1 | {1, 2, 3} |
| 2 | {2, 4} |
| 3 | {3, 4} |
| 4 | {4, 5} |
| 5 | {1, 5} |

El óptimo es C = {1, 4}, con 2 auditorías. En este caso el voraz también lo encuentra: primero elige la interacción 1, que cubre 3 categorías, y luego la 4.

## Variante A — Cobertura ponderada

El enunciado pide que las categorías tengan distinta importancia, pero eso **por sí solo no cambia el problema**. Si hay que cubrir todas las categorías, sus pesos no afectan cuál es la cobertura mínima. Para que los pesos importen hay dos formalizaciones posibles. Proponemos la A1 y la A2 queda como alternativa, sujeta a confirmación del docente.

### A1 (propuesta) — Cobertura de conjuntos con costos

**Tamaño de la entrada:** n y r, igual que en la Parte 2.

**Entrada:** U = \[r\] y F = {S\_1, …, S\_n}, como en la Parte 2, más un costo de auditoría a\_j ≥ 1 por cada interacción. La importancia de cada categoría k se modela con un peso w\_k ≥ 1, y el costo puede derivarse de esos pesos o generarse de forma independiente.

**Salida:** C ⊆ \[n\] que cubra U.

**Objetivo:**

```latex
\min_{C \subseteq [n]} \; \sum_{j \in C} a_j \quad \text{s.a.} \quad \bigcup_{j \in C} S_j = U
```

**Cómo cambia la cota.** El voraz ponderado elige en cada paso la interacción con menor costo por categoría nueva cubierta, es decir, el menor a\_j / |S\_j \\ cubiertas|. Su garantía es H\_d, donde d = max |S\_j| ≤ r, así que la cota sigue siendo H\_r o mejor (Chvátal, 1979).

### A2 (alternativa) — Cobertura máxima ponderada con límite de auditorías

**Entrada:** U, F, pesos w\_k ≥ 1 por categoría y un límite k de auditorías.

**Salida:** C ⊆ \[n\] con |C| ≤ k.

**Objetivo:** maximizar el peso total de las categorías cubiertas.

```latex
\max_{|C| \le k} \; \sum_{\ell \in \bigcup_{j \in C} S_j} w_\ell
```

En esta versión la cota ya no es H\_r sino un factor (1 − 1/e) ≈ 0.632 del óptimo, un cambio mayor del que sugiere el enunciado. Por eso se propone A1.

**Pregunta abierta para el docente:** ¿la variante ponderada se refiere a costos por interacción (A1) o a pesos por categoría con cobertura parcial (A2)?

## Variante B — Aceleración y auditoría con presupuesto conjunto

Se decide al mismo tiempo qué etapas acelerar y qué interacciones auditar, pagando ambas cosas con un solo presupuesto B. Proponemos una función objetivo que pondera el tiempo de la cadena frente al riesgo que queda sin auditar.

**Tamaño de la entrada:** n (etapas), N (interacciones candidatas), r (categorías) y B (presupuesto). En esta variante se usa N para las interacciones, porque n ya designa las etapas.

**Entrada:**

- De la Parte 1: t\_i, c\_i y d\_i para i ∈ \[n\].
- De la Variante A1: S\_j ⊆ \[r\] y el costo a\_j para j ∈ \[N\], más los pesos de categoría w\_k para k ∈ \[r\].
- El presupuesto conjunto B y un factor de penalización λ > 0, que indica cuántas unidades de tiempo equivalen a una unidad de peso de riesgo sin cubrir.

**Salida:** un par (x, C), con x ∈ {0,1}^n las etapas aceleradas y C ⊆ \[N\] las interacciones auditadas.

**Restricción:**

```latex
\sum_{i=1}^{n} c_i\,x_i + \sum_{j \in C} a_j \le B
```

**Objetivo:** minimizar la duración de la cadena más la penalización por las categorías no cubiertas.

```latex
\min_{(x,\,C)} \; \Big( \sum_{i=1}^{n} t_i - \sum_{i=1}^{n} d_i\,x_i \Big) + \lambda \sum_{k \notin \bigcup_{j \in C} S_j} w_k
```

**Caso particular de cobertura obligatoria.** Si λ es suficientemente grande, por ejemplo mayor que la suma de todos los t\_i, siempre conviene cubrir todo. En ese caso el problema se separa en dos: primero se busca la cobertura C\* de costo mínimo (Variante A1) y luego se resuelve la Mochila de la Parte 1 con el presupuesto que queda, B − a(C\*). La razón es que la duración óptima de la Mochila nunca empeora cuando aumenta el presupuesto. Esta propiedad se demostrará en la etapa del algoritmo.

**Versión de decisión:** dado un entero K, ¿existe (x, C) dentro del presupuesto con valor objetivo ≤ K? Contiene a la Parte 1 como caso particular (N = 0), por lo que es NP-difícil.

**Pregunta abierta para el docente:** ¿acepta el objetivo con penalización λ, o prefiere la versión con cobertura obligatoria?

## Variante C — Flujo con etapas en paralelo (DAG)

El flujo deja de ser una cadena y pasa a ser un grafo acíclico dirigido. Su duración es la de la **ruta más larga** (ruta crítica), y acelerar una etapa solo ayuda si esa etapa está en la ruta crítica.

**Tamaño de la entrada:** n = |V| etapas, m = |E| dependencias y el presupuesto B.

**Entrada:**

- Un grafo dirigido acíclico G = (V, E) con V = \[n\]. Una arista (u, v) ∈ E significa que la etapa v no puede empezar hasta que termine u.
- Para cada etapa i ∈ V: t\_i, c\_i y d\_i, como en la Parte 1.
- El presupuesto B.

Se añaden una fuente s y un sumidero z ficticios de duración 0, de modo que todo camino empiece en s y termine en z.

**Subproblema previo — ruta crítica.** Dadas las duraciones efectivas τ\_i = t\_i − d\_i·x\_i, la duración del flujo es:

```latex
L(x) = \max_{P \,:\, s \leadsto z} \; \sum_{i \in P} \big( t_i - d_i\,x_i \big)
```

Se calcula por programación dinámica sobre el orden topológico en O(n + m).

**Salida:** x ∈ {0,1}^n, las etapas a acelerar.

**Restricción:** Σ c\_i·x\_i ≤ B.

**Objetivo:** minimizar L(x).

**Versión de decisión:** ¿existe x con costo ≤ B y L(x) ≤ K? La cadena de la Parte 1 es el caso particular con E = {(i, i+1)}, así que este problema es al menos tan difícil como la Mochila.

**Ejemplo: por qué no basta con la Mochila.** Aristas A→B, A→C, B→D y C→D, con presupuesto 4:

| Etapa | t\_i | c\_i | d\_i |
| --- | --- | --- | --- |
| A | 3 | 4 | 1 |
| B | 5 | 2 | 3 |
| C | 4 | 2 | 2 |
| D | 2 | 3 | 1 |

Sin acelerar, la ruta crítica es A→B→D, que dura 10. Acelerar solo B reduce esa ruta a 7, pero entonces A→C→D (9) pasa a ser la crítica, y la ganancia real es 1, no 3. La Mochila sumaría las reducciones como si fueran independientes. Lo mejor es acelerar B y C: ambas rutas quedan en 7.

## Resumen y supuestos generales

Los cinco problemas son NP-difíciles, y en todos el tamaño de la entrada incluye un presupuesto o un número de categorías, además de n.

| Problema | Tamaño de entrada | Salida | Objetivo | Problema clásico equivalente |
| --- | --- | --- | --- | --- |
| Parte 1 — Cadena | n, B | x ∈ {0,1}^n | min Σt\_i − Σd\_i·x\_i | Mochila 0/1 |
| Parte 2 — Auditoría | n, r | C ⊆ \[n\] | min ∣C∣ cubriendo U | Set Cover |
| Variante A1 — Ponderada | n, r | C ⊆ \[n\] | min Σa\_j cubriendo U | Set Cover con costos |
| Variante B — Combinada | n, N, r, B | (x, C) | min duración + λ·riesgo sin cubrir | Mochila + Set Cover |
| Variante C — DAG | n, m, B | x ∈ {0,1}^n | min ruta crítica L(x) | Generaliza la Mochila 0/1 |

**Supuestos generales:**

- Todos los valores son enteros no negativos, y los costos c\_i y a\_j son ≥ 1.
- Las instancias son sintéticas y las genera el equipo con semilla fija, para que los resultados sean reproducibles.
- En las Partes 2, A1 y B se garantiza que la unión de todos los S\_j es U.

**Preguntas abiertas para el docente:**

- [ ] Variante ponderada: ¿costos por interacción (A1) o pesos por categoría con límite de auditorías (A2)?
- [ ] Variante combinada: ¿objetivo con penalización λ o cobertura obligatoria?
- [ ] Reducción de la Parte 2: ¿desde Vertex Cover, Exact Cover by 3-Sets u otra reducción vista en el curso?
