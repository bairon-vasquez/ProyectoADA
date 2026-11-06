# Eficiencia de los algoritmos exactos

Código de referencia: [core/mochila.py](../core/mochila.py). Los comentarios `# O(.)` del código coinciden línea a línea con esta deducción.

## Parte 1 — Mochila 0/1 (aceleración de la cadena)

### 1. Definición de n

- **n** = número de etapas de la cadena.
- **B** = presupuesto (entero ≥ 0).
- T se expresa como función **T(n, B)**: ambos parámetros crecen y los dos influyen en el tiempo.

**Operación elemental** (costo 1): una comparación, suma, resta, asignación o acceso a un elemento de lista/tabla. Todo lo que no es un ciclo es O(1).

### 2. Fuerza bruta: T(n) = O(2^n · n)

```
mejor ← −1                                  1 asignación
para mascara = 0 … 2^n − 1:                 2^n iteraciones
    costo ← 0; reduccion ← 0                2 asignaciones
    para i = 0 … n − 1:                     n iteraciones
        si bit i de mascara está en 1:      1 comparación (≤ 3 ops de bits)
            costo += c_i; reduccion += d_i  2 sumas
    si costo ≤ B y reduccion > mejor: …     2 comparaciones (+ O(n) solo si mejora)
```

- Cuerpo del ciclo interno: ≤ k₁ operaciones (constante) ⇒ ciclo interno: **k₁·n**.
- Cuerpo del ciclo externo: k₁·n + k₂ (k₂ = inicializaciones y comparaciones finales).
- Reconstruir `mejor_etapas` cuesta O(n), pero solo ocurre al mejorar; en el peor caso ocurre en las 2^n máscaras, lo que sigue sumando O(n) por máscara.

$$T(n) = 1 + 2^n\,(k_1 n + k_2 + O(n)) = \Theta(n\,2^n)$$

Es exponencial en n: duplicar n eleva el tiempo al cuadrado, y n = 40 ya es inviable.

### 3. Programación dinámica: T(n, B) = O(n · B)

**Subestructura óptima.** Sea `DP[i][b]` la máxima reducción total usando solo las etapas 1…i con presupuesto b. Para la etapa i hay dos opciones:

- No acelerarla: valor `DP[i−1][b]`.
- Acelerarla (solo si c_i ≤ b): valor `DP[i−1][b − c_i] + d_i`.

$$DP[i][b] = \begin{cases} DP[i-1][b] & c_i > b \\ \max\big(DP[i-1][b],\; DP[i-1][b-c_i] + d_i\big) & c_i \le b\end{cases}\qquad DP[0][b]=0$$

La respuesta es `DP[n][B]`; la duración mínima es Σt_i − DP[n][B].

**Conteo de operaciones** (`construir_tabla_dp`):

| Paso | Veces | Costo por vez | Total |
|---|---|---|---|
| Crear la tabla de (n+1)×(B+1) ceros | (n+1)(B+1) celdas | 1 | (n+1)(B+1) |
| Leer n, B | 1 | 1 | O(1) |
| Ciclo externo `i = 1…n`: leer c_i, d_i | n | 2 | 2n |
| Ciclo interno `b = 0…B`: **una celda** | n·(B+1) | k (constante) | **k·n·(B+1)** |

Una celda cuesta k operaciones constantes: leer `DP[i−1][b]`, comparar `c_i ≤ b`, leer `DP[i−1][b−c_i]`, sumar d_i, comparar, escribir. Así k ≤ 6 como cota.

**Reconstrucción** (`reconstruir_etapas`): recorre i = n…1 una sola vez; en cada paso hace una comparación, y a veces una resta y un `append`. Son ≤ k′ operaciones por paso ⇒ **k′·n**. El `reverse` final cuesta O(n).

**Total:**

$$T(n,B) = (n+1)(B+1) + 2n + k\,n\,(B+1) + k'n + O(n) = \Theta(n\,B)$$

Más precisamente, con constante: T(n, B) ≈ (k+1)·n·(B+1) + O(n + B). El término dominante es n·B. Espacio: O(n·B) por la tabla completa (se necesita completa para reconstruir; solo con valor óptimo bastarían 2 filas, O(B)).

### 4. ¿Por qué es pseudo-polinomial?

Un algoritmo es **polinomial** si su tiempo es polinomial en el **tamaño de la representación** de la entrada, es decir, en el número de **bits** necesarios para escribirla. Es **pseudo-polinomial** si lo es en el **valor numérico** de los datos.

- Escribir B en binario ocupa ⌈log₂(B+1)⌉ bits. Por tanto, la entrada completa tiene tamaño |I| = Θ(n·log M + log B), con M el mayor valor entre los t_i, c_i, d_i.
- El tiempo O(n·B) es lineal en el **valor** B, pero **B = 2^{log₂ B}**: expresado en el tamaño |I|, es **exponencial**. Con B de 30 bits (|I| minúsculo), B ≈ 10⁹ y la tabla tendría ~10⁹·n celdas.
- Ejemplo: pasar de B a 2B cuesta solo **un bit más** en la entrada, pero **duplica** el tiempo del algoritmo.

Si B está acotado por un polinomio en n (por ejemplo B = O(n²)), el algoritmo sí es polinomial en n. Eso es lo que se hace en los experimentos al variar n con B proporcional. Esto no contradice la NP-dureza: la Mochila es **NP-difícil en sentido débil** (solo es difícil cuando los números son exponencialmente grandes), y el DP es precisamente el algoritmo pseudo-polinomial que lo confirma. La prueba de NP-dureza está en [02_reducciones.md](02_reducciones.md).

### 5. Resumen

| Algoritmo | Tiempo | Espacio | Nota |
|---|---|---|---|
| Fuerza bruta | Θ(n·2^n) | O(n) | Exponencial en n |
| DP + reconstrucción | Θ(n·B) | O(n·B) | Pseudo-polinomial |

---

## Parte 2 — Set Cover

Código de referencia: [core/set_cover.py](../core/set_cover.py).

### 1. Definición de n

- **n** = número de interacciones (conjuntos S_j), **r** = número de categorías (|U|).
- T se expresa como **T(n, r)**. Cada S_j se guarda como conjunto de a lo sumo r categorías, y se usa un arreglo de booleanos `cubierta[0..r−1]` con acceso O(1).
- Operación elemental (costo 1): comparación, suma, asignación o acceso a arreglo/conjunto.

### 2. Voraz: T(n, r) = O(n · r · min(n, r)) ⊆ O(n · r²)

```
paso 0: unión ← ∪ S_j ; si unión ≠ U → «sin solución»   O(Σ|S_j|) ⊆ O(n·r)
cubierta ← [falso]*r ; n_cubiertas ← 0                  O(r)
mientras n_cubiertas < r:                               ≤ min(n, r) iteraciones
    mejor_nuevas ← 0
    para j = 1 … n:                                     n iteraciones
        nuevas ← 0
        para cada k en S_j:                             |S_j| ≤ r iteraciones
            si no cubierta[k]: nuevas ← nuevas + 1      ≤ 2 ops
        si nuevas > mejor_nuevas: guardar j             1 comparación
    marcar como cubiertas las categorías de S_{mejor}   ≤ r iteraciones
    n_cubiertas ← n_cubiertas + mejor_nuevas
```

1. **Contar las nuevas de un S_j:** a lo sumo r iteraciones de ≤ 2 operaciones ⇒ ≤ 2r.
2. **Una ronda:** n conjuntos × (2r + 1) + marcar (≤ 2r) ⇒ ≤ 2nr + n + 2r = **O(n·r)**.
3. **Número de rondas:** cada ronda cubre **al menos una** categoría nueva (el paso 0 garantiza que siempre existe una), y un conjunto ya elegido no aporta categorías nuevas, así que cada ronda elige un conjunto distinto. Por tanto hay **a lo sumo min(n, r) rondas**.

$$T(n,r) \le O(n\,r) + O(r) + \min(n,r)\,(2nr + n + 2r) = O\big(n\,r\,\min(n,r)\big) \subseteq O(n\,r^2)$$

Además, el conteo de rondas es exactamente k = |solución voraz| ≤ min(n, r), de modo que T = Θ(k·n·r̄) donde r̄ es el tamaño medio de los S_j. En la cota general, con k ≤ min(n, r) y |S_j| ≤ r, es O(n·r·min(n,r)) ⊆ O(n·r²). Espacio: O(n·r) por la entrada, O(r) adicional.

*(Con una representación en máscaras de bits o contadores de actualización incremental se baja a O(Σ|S_j|·…), pero el código del proyecto usa ciclos explícitos para que el conteo corresponda al código.)*

### 3. Exacto por fuerza bruta: T(n, r) = O(2^n · n · r)

Se prueban los subconjuntos por **tamaño creciente** k = 0, 1, 2, …; el primer k donde alguno cubre U es el óptimo k\*.

- Para cada tamaño k hay C(n, k) subconjuntos.
- Verificar uno: unir k conjuntos de ≤ r elementos ⇒ **O(k·r)**.
- Subconjuntos examinados en el peor caso: Σ_{k=0}^{k\*} C(n,k).

$$T(n,r) = O\Big(\sum_{k=0}^{k^*}\binom{n}{k}\,k\,r\Big) \subseteq O(2^n\,n\,r)$$

Además, la factibilidad previa (unión de todos los S_j) cuesta O(n·r).

Observaciones útiles para la sustentación:

- Peor caso (k\* grande, p. ej. la unión necesita casi todos los conjuntos): se aproxima a 2^n subconjuntos ⇒ exponencial en n.
- Como k\* ≤ r, también vale la cota Σ_{k≤k\*} C(n,k) ≤ (n+1)^{k\*}: es polinomial **si el óptimo es pequeño y fijo**, pero exponencial en general. Por eso k\* aparece como parámetro.
- El ahorro de parar en k\* (en vez de enumerar los 2^n) hace que el tiempo medido dependa de k\*; en los experimentos conviene registrar el tamaño de la solución.

### 4. Resumen

| Algoritmo | Tiempo | Calidad |
|---|---|---|
| Voraz | O(n·r·min(n, r)) ⊆ O(n·r²) | ≤ H_r · óptimo ([04_aproximaciones.md](04_aproximaciones.md)) |
| Exacto (fuerza bruta) | O(2^n · n · r) | Óptimo |

## Variante A1 — Set Cover con costos

Código: `cobertura_voraz_ponderada` y `cobertura_exacta_ponderada` en [core/set_cover.py](../core/set_cover.py). Tamaño: **(n, r)**, igual que la Parte 2.

**Voraz ponderado.** Es el mismo esqueleto del voraz de la Parte 2; solo cambia el criterio de elección: en vez de maximizar `nuevas`, minimizar `a_j / nuevas`. La comparación se hace **sin división**, con productos cruzados enteros (`a_j · nuevas_m < a_m · nuevas_j`), que es O(1). Por tanto el conteo es idéntico:

$$T(n,r) = O(r) + r\,(n\cdot O(r) + O(r)) = O(n\,r^2)$$

(≤ r rondas, porque cada ronda cubre ≥ 1 categoría nueva; n conjuntos por ronda; O(r) para contar las nuevas de cada uno).

**Exacto ponderado.** Se enumeran las 2^n máscaras. Por máscara: inicializar `cubierta` O(r), y para cada j en la máscara recorrer S_j (≤ r) ⇒ O(n·r). Total:

$$T(n,r) = O(2^n\cdot n\cdot r)$$

**Exacto ponderado por máscaras de categorías** (`cobertura_exacta_mascaras`). Cuando r es pequeño y n grande, 2^n es inviable pero 2^r no. Sea `dp[M]` el menor costo de una selección cuya unión es exactamente la máscara M ⊆ U (r bits); `dp[0] = 0`. Para cada opción j se recorre M = 0 … 2^r − 1 y se relaja `dp[M | S_j] ← min(dp[M | S_j], dp[M] + a_j)` en O(1). Si las opciones vienen en grupos (a lo sumo una por grupo, p. ej. una variación de auditoría por etapa), cada grupo se procesa con la fila anterior de `dp` como entrada, de modo que dos opciones del mismo grupo nunca se combinan. Conteo:

- Máscaras de las opciones: O(n·r). Agrupar: O(n).
- Por opción: 2^r iteraciones de O(1) ⇒ n · 2^r en total; por grupo, copiar `dp`: G · 2^r con G ≤ n.
- Reconstrucción: G pasos hacia atrás, O(G).

$$T(n,r) = O(n\cdot 2^r),\qquad \text{espacio } O(G\cdot 2^r)$$

Es exponencial en r, no en n: no contradice la NP-dureza (el problema sigue siendo exponencial en general), pero con r = 12 son 4096 máscaras. Se usa para obtener el óptimo de la Parte 2 y la cobertura de costo mínimo a\* de la Variante B en el caso del docente (n = 35 opciones, r = 12), donde la fuerza bruta 2^35 no es viable. Se contrasta con la fuerza bruta en `tests/test_formato_docente.py`.

Aquí no se puede parar en el primer tamaño que cubre (como en la Parte 2): un conjunto más grande puede costar menos, así que hay que mirar todas las máscaras.

## Variante B — Presupuesto conjunto

Código: [core/combinado.py](../core/combinado.py). Tamaño: **(n, N, r, B)** (n etapas, N interacciones).

**B.1 Cobertura obligatoria (λ grande).** Pasos y costos:

1. Cobertura de costo mínimo C\* (Variante A1): exacta O(2^N·N·r), o voraz ponderado O(N·r²).
2. Presupuesto restante B′ = B − a(C\*) (O(1)); si a(C\*) > B no hay solución.
3. Mochila con B′: O(n·B′) ≤ O(n·B).
4. Evaluar el objetivo: O(n + N·r).

$$T = O(2^N N r + n B)\ \text{(exacta)}\qquad T = O(N r^2 + n B)\ \text{(voraz)}$$

*Por qué es óptima la versión exacta:* sea f(b) la máxima reducción con presupuesto b. f es no decreciente (cualquier solución factible con b también lo es con b+1). Cualquier solución que cubra todo gasta al menos a(C\*) en cobertura, de modo que le quedan ≤ B − a(C\*) para acelerar, y f(B − a(C\*)) es lo máximo alcanzable. Con λ > Σt_i, además, cubrir todo siempre es mejor que dejar una categoría sin cubrir (penaliza ≥ λ·w_k ≥ λ > Σt_i ≥ cualquier ahorro de tiempo posible), siempre que cubrir quepa en B.

**B.2 Heurística para λ general.**

1. Tabla DP de la cadena con presupuesto B, **una sola vez**: O(n·B). Su última fila, f(b) = DP[n][b], da la mejor reducción para cualquier presupuesto b ≤ B.
2. Voraz de cobertura por beneficio/costo, "mayor w(nuevas)/a_j" entre las interacciones que caben (λ es común y se cancela). Hay a lo sumo min(N, r) rondas (cada una cubre ≥ 1 categoría nueva y se elige a lo sumo cada conjunto una vez); cada ronda recorre N conjuntos con O(r) c/u ⇒ O(N·r) por ronda.
3. Tras cada elección (cada prefijo C_p) el objetivo se evalúa en **O(1)**: Σt − f(B − a(C_p)) + λ·w(sin cubrir).
4. Se queda con el mejor prefijo (el vacío incluido) y reconstruye la Mochila con el presupuesto restante: O(n·B).

$$T = O(nB) + O(\min(N,r)\cdot N\cdot r) + O(nB) = O\big(nB + N r\min(N,r)\big)\subseteq O(nB + N r^2)$$

Como el prefijo vacío es candidato, nunca es peor que "solo acelerar y no auditar".

**B.3 Exacto de referencia (para tests).** Para cada C ⊆ [N] con a(C) ≤ B, la mejor Mochila es f(B − a(C)) (tabla única). Total: O(n·B) + 2^N·O(N·r):

$$T = O(nB + 2^N N r)$$

## Variante C — DAG

Código: [core/dag.py](../core/dag.py). Tamaño: **(n, m, B)**, n = |V|, m = |E|. Se añaden fuente y sumidero ficticios (duración 0), por lo que el grafo ampliado tiene n+2 nodos y ≤ m + 2n aristas: sigue siendo O(n + m).

**C.1 Orden topológico (Kahn).**

| Paso | Costo |
|---|---|
| Crear listas de sucesores y grados de entrada (recorrer las m aristas) | O(n + m) |
| Cola inicial con los nodos de grado 0 | O(n) |
| Cada nodo se extrae una vez (n extracciones, O(1) c/u) | O(n) |
| Al extraer u se recorren sus sucesores: **Σ_u |sucesores(u)| = m** en total | O(m) |

$$T_{topo}(n,m) = O(n+m)$$

El argumento clave es el segundo: no son n·m, porque cada arista se relaja exactamente una vez.

**C.2 Ruta más larga (DP en orden topológico).** Con τ_i = t_i − d_i·x_i y `fin[v]` = duración de la ruta más larga que termina en v:

$$fin[v] = \tau_v + \max_{(u,v)\in E} fin[u]\quad(\text{o } \tau_v\text{ si no hay predecesores})$$

- Calcular τ: O(n). Inicializar `fin`, `padre`: O(n).
- Recorrer los nodos en orden topológico (n) y para cada uno sus aristas salientes (m en total), con O(1) por relajación: O(n + m).
- Sumidero ficticio = máximo de `fin`: O(n). Reconstruir el camino por `padre`: O(n).

$$T_{ruta}(n,m) = O(n+m)$$

La corrección del orden: cuando se procesa u, todos sus predecesores ya fueron procesados, así que `fin[u]` ya es definitivo.

**C.3 Exacto por fuerza bruta.** Orden topológico una sola vez (O(n+m)); luego, para cada una de las 2^n máscaras: costo O(n) y, si cabe en B, ruta más larga O(n+m).

$$T(n,m) = O(2^n\,(n+m))$$

**C.4 Heurística iterativa.** Cada iteración (1) toma la ruta crítica actual, (2) elige en ella la etapa no acelerada con mayor d_i/c_i que quepa en el presupuesto restante (O(n), comparación por productos cruzados), (3) la acelera y recalcula la ruta en O(n+m). Como cada iteración acelera una etapa distinta, hay ≤ n iteraciones:

$$T(n,m) = O(n\,(n+m))$$

*Recalcular es indispensable:* en el ejemplo de la Etapa 0, acelerar solo B baja A→B→D de 10 a 7, pero la ruta crítica pasa a A→C→D (9), así que la ganancia real es 1 y no 3. Por eso el algoritmo vuelve a calcular la ruta después de cada aceleración.

## Resumen de complejidades

| Problema | Algoritmo | Tiempo |
|---|---|---|
| Parte 1 | DP | Θ(n·B) |
| Parte 2 | Voraz / exacto | O(n·r²) / O(2^n·n·r) |
| A1 | Voraz ponderado / exacto | O(n·r²) / O(2^n·n·r) |
| B | Obligatoria (exacta o voraz) | O(2^N·N·r + n·B) / O(N·r² + n·B) |
| B | Heurística λ general | O(n·B + N·r·min(N,r)) |
| B | Exacto de referencia | O(n·B + 2^N·N·r) |
| C | Orden topológico y ruta crítica | O(n + m) |
| C | Exacto / heurística | O(2^n·(n+m)) / O(n·(n+m)) |
