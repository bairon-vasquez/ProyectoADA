# Reducciones y NP-dureza

## 1. Parte 1 ≡ Mochila 0/1

### 1.1 Los dos problemas de decisión

**MOCHILA-01** (problema clásico, NP-completo; Karp, 1972).
Entrada: pesos w₁,…,w_n ≥ 1, valores v₁,…,v_n ≥ 0 enteros, capacidad W y objetivo V.
Pregunta: ¿existe S ⊆ [n] con Σ_{i∈S} w_i ≤ W y Σ_{i∈S} v_i ≥ V?

**ACELERACIÓN-CADENA** (Etapa 0).
Entrada: t_i ≥ 0, c_i ≥ 1, 0 ≤ d_i ≤ t_i, presupuesto B y entero K.
Pregunta: ¿existe S ⊆ [n] con Σ_{i∈S} c_i ≤ B y D(S) = Σ t_i − Σ_{i∈S} d_i ≤ K?

Ambos son claramente **verificables en tiempo polinomial** (dado S, se suman n números): están en NP.

### 1.2 MOCHILA-01 ≤ₚ ACELERACIÓN-CADENA (ACELERACIÓN es NP-difícil)

**Transformación f.** Dada (w, v, W, V), construir:

- t_i = v_i, c_i = w_i, d_i = v_i (así 0 ≤ d_i ≤ t_i se cumple con igualdad),
- B = W,
- K = Σ_i v_i − V.

Se calcula en O(n) (una suma y n copias): tiempo polinomial.

**Corrección (⇒).** Si existe S con Σw ≤ W y Σv ≥ V, entonces el mismo S cumple Σc = Σw ≤ B y
D(S) = Σt − Σ_{S} d = Σv − Σ_{S} v ≤ Σv − V = K.

**Corrección (⇐).** Si existe S con Σc ≤ B y D(S) ≤ K, entonces Σ_S w = Σ_S c ≤ B = W y
Σ_S v = Σ_S d = Σt − D(S) ≥ Σv − K = V.

Luego (w,v,W,V) es instancia positiva de MOCHILA-01 ⇔ f(w,v,W,V) es instancia positiva de ACELERACIÓN-CADENA. ∎

### 1.3 ACELERACIÓN-CADENA ≤ₚ MOCHILA-01 (equivalencia en el otro sentido)

**Transformación g.** Dada (t, c, d, B, K), construir:

- w_i = c_i, v_i = d_i, W = B,
- V = Σ t_i − K (si V < 0 se toma V = 0, pues Σv ≥ 0 siempre se cumple).

Se calcula en O(n).

**Corrección (⇒).** Si existe S con Σc ≤ B y Σt − Σ_S d ≤ K, entonces Σ_S w = Σ_S c ≤ W y Σ_S v = Σ_S d ≥ Σt − K = V.

**Corrección (⇐).** Si existe S con Σ_S w ≤ W y Σ_S v ≥ V, entonces Σ_S c ≤ B y Σt − Σ_S d ≤ Σt − V = K (cuando V se truncó a 0, K ≥ Σt ≥ D(S) trivialmente). ∎

### 1.4 Conclusión

- Ambos problemas se reducen entre sí en tiempo lineal ⇒ son **equivalentes**: cada uno es tan difícil como el otro.
- Como MOCHILA-01 es NP-completo (Karp, 1972), **ACELERACIÓN-CADENA es NP-completo**: está en NP (§1.1) y es NP-difícil (§1.2).
- Es NP-difícil **en sentido débil**: el DP O(n·B) de [03_eficiencia_exactos.md](03_eficiencia_exactos.md) lo resuelve en tiempo pseudo-polinomial.
- Versión de optimización: el vector óptimo x* de la cadena es exactamente el de la Mochila con valor d_i y peso c_i, porque Σt_i es constante: minimizar D(x) ⇔ maximizar Σ d_i·x_i.

## 2. Parte 2 — Vertex Cover ≤ₚ Set Cover

### 2.1 Los dos problemas de decisión

**VERTEX-COVER** (NP-completo; Karp, 1972).
Entrada: grafo no dirigido G = (V, E) y entero k.
Pregunta: ¿existe V′ ⊆ V con |V′| ≤ k tal que toda arista tiene al menos un extremo en V′?

**COBERTURA-AUDITORÍA** (Etapa 0).
Entrada: universo U = [r], familia F = {S₁,…,S_n} con S_j ⊆ U (con ∪S_j = U) y entero k.
Pregunta: ¿existe C ⊆ [n] con |C| ≤ k y ∪_{j∈C} S_j = U?

**Pertenece a NP:** dado C, se verifica |C| ≤ k y se calcula la unión en O(n·r).

### 2.2 Transformación f

Dada (G = (V,E), k), con V = {v₁,…,v_n} y E = {e₁,…,e_m}, construir:

- **Universo:** U = E, es decir r = m (cada arista es una "categoría de riesgo").
- **Familia:** una interacción por vértice, S_v = { e ∈ E : v es extremo de e } (las aristas incidentes a v). Así n = |V|.
- **Umbral:** el mismo k.

Si G tiene una arista, toda arista pertenece a S_u y S_v de sus dos extremos, por lo que ∪_v S_v = E = U: la instancia es **factible**, como exige la formalización. Costo de f: recorrer las aristas una vez, O(|V| + |E|) (polinomial).

### 2.3 Corrección

**(⇒)** Sea V′ una cobertura de vértices con |V′| ≤ k. Tomar C = { j : v_j ∈ V′ }. Para toda arista e = {u,v}, algún extremo está en V′, luego e ∈ S_u o e ∈ S_v con ese vértice en C. Entonces ∪_{j∈C} S_j = E = U y |C| = |V′| ≤ k.

**(⇐)** Sea C con |C| ≤ k y ∪_{j∈C} S_j = U = E. Tomar V′ = { v_j : j ∈ C }. Toda arista e está en algún S_j con j ∈ C, o sea, v_j es un extremo de e y está en V′. Luego V′ es cobertura de vértices con |V′| ≤ k.

Por lo tanto, (G, k) ∈ VERTEX-COVER ⇔ f(G, k) ∈ COBERTURA-AUDITORÍA. ∎

### 2.4 Conclusión

- Como VERTEX-COVER es NP-completo y f es computable en tiempo polinomial, **COBERTURA-AUDITORÍA es NP-difícil**; junto con su pertenencia a NP (§2.1), es **NP-completa**.
- Las instancias producidas por f tienen cada elemento en **exactamente 2** conjuntos (frecuencia 2). Esto muestra que el problema ya es difícil en esa familia restringida.
- A diferencia de la Mochila, aquí no hay ningún número grande: la dureza es **fuerte**, y no existe un algoritmo pseudo-polinomial salvo P = NP. Por eso se recurre a la aproximación voraz ([04_aproximaciones.md](04_aproximaciones.md)).
- *Alternativa disponible:* Exact Cover by 3-Sets (X3C) también reduce a Set Cover, pero la reducción desde Vertex Cover es más corta y es la que se propone al docente (pregunta abierta de la Etapa 0).

**Ejemplo.** G con aristas e₁={a,b}, e₂={b,c}, e₃={c,d}: U = {e₁,e₂,e₃}, S_a={e₁}, S_b={e₁,e₂}, S_c={e₂,e₃}, S_d={e₃}. El mínimo es C = {b, c} (k = 2), que corresponde a la cobertura de vértices {b, c}.

## 3. Variante A1 — Set Cover con costos

**Decisión (A1-DEC).** Dados U, F, costos a_j ≥ 1 y un entero K: ¿existe C con ∪S_j = U y Σ_{j∈C} a_j ≤ K? Está en NP (suma y unión en O(n·r)).

**Reducción COBERTURA-AUDITORÍA ≤ₚ A1-DEC.** Dada (U, F, k), usar las mismas U y F, con a_j = 1 para todo j y K = k. Entonces Σ_{j∈C} a_j = |C|, de modo que C cubre con |C| ≤ k ⇔ C cubre con costo ≤ K. (⇒) y (⇐) son inmediatas por la igualdad Σa_j = |C|. Es computable en O(n). Así que **A1 es NP-completo** (la Parte 2 es el caso particular a_j ≡ 1).

## 4. Variante B — presupuesto conjunto

**Decisión (B-DEC).** Dado K: ¿existe (x, C) con Σc_i·x_i + Σ_{j∈C} a_j ≤ B y objetivo ≤ K? Está en NP (verificar costo y objetivo en O(n + N·r)).

**NP-difícil (dos reducciones, cada una por un caso particular):**

1. *ACELERACIÓN-CADENA ≤ₚ B-DEC.* Dada (t,c,d,B,K), usar N = 0 interacciones (sin cobertura; r = 0 categorías, por lo que la penalización es 0). Entonces el objetivo es D(x) y la restricción es Σc_i·x_i ≤ B: (⇒) y (⇐) son idénticas a las de ACELERACIÓN-CADENA.
2. *COBERTURA-AUDITORÍA ≤ₚ B-DEC.* Dada (U, F, k): n = 0 etapas, a_j = 1, w_k = 1, B = k, λ = 1 y K = 0. Con n = 0 la duración es 0, así que el objetivo es el peso sin cubrir. (⇒) Si C cubre con |C| ≤ k, el presupuesto se respeta y la penalización es 0 ≤ K. (⇐) Si el objetivo es ≤ 0, no queda categoría sin cubrir (todos los w_k ≥ 1), es decir ∪S_j = U, con |C| = Σa_j ≤ B = k.

Luego B contiene a la Mochila y a Set Cover, y es **NP-completo**. Con cobertura obligatoria se **separa** en un Set Cover con costos más una Mochila (ver [03_eficiencia_exactos.md](03_eficiencia_exactos.md)), pero la suma de dos problemas difíciles sigue siendo difícil.

## 5. Variante C — DAG

**Decisión (DAG-DEC).** Dado G = (V, E) acíclico, t, c, d, B y K: ¿existe x ∈ {0,1}^n con Σc_i·x_i ≤ B y L(x) ≤ K, donde L(x) es la ruta más larga con pesos t_i − d_i·x_i?

**En NP.** Dado x se verifica el costo en O(n) y L(x) en O(n + m) por DP.

**Reducción ACELERACIÓN-CADENA ≤ₚ DAG-DEC.** Dada (t, c, d, B, K) con n etapas, construir el DAG con E = {(i, i+1) : 1 ≤ i < n} (un único camino), con los mismos t, c, d, B y K. Costo: O(n).

- Como la única ruta fuente→sumidero pasa por todas las etapas, L(x) = Σ_i (t_i − d_i·x_i) = D(x).
- (⇒) Si x cumple Σc·x ≤ B y D(x) ≤ K, entonces L(x) = D(x) ≤ K. (⇐) Si x cumple Σc·x ≤ B y L(x) ≤ K, entonces D(x) = L(x) ≤ K.

Por tanto, **DAG-DEC es NP-completo** (al menos tan difícil como la Mochila, que a su vez es NP-completa).

**Por qué no basta con la Mochila.** Con rutas paralelas, las ganancias no son aditivas: la reducción efectiva de L al acelerar un conjunto de etapas depende de qué rutas dejan de ser críticas (ejemplo A→B, A→C, B→D, C→D en la Etapa 0 y en `tests/test_variantes.py`: acelerar solo B da ganancia real 1, no 3; el óptimo exige acelerar B **y** C y resulta 7).
