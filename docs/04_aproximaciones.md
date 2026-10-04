# Aproximaciones y cotas

## 1. Set Cover — cota del voraz: H_r

Código: `cobertura_voraz` en [core/set_cover.py](../core/set_cover.py). Tiempo: O(n·r²) ([03_eficiencia_exactos.md](03_eficiencia_exactos.md)).

### 1.1 Enunciado

Sea (U, F) una instancia factible de Set Cover con |U| = r, y sea d = max_j |S_j| ≤ r. Sea OPT el tamaño de una cobertura mínima y G el tamaño de la que devuelve el voraz ("tomar el conjunto con más elementos aún no cubiertos"). Entonces

$$G \;\le\; H_d \cdot \mathrm{OPT} \;\le\; H_r \cdot \mathrm{OPT}, \qquad H_k = \sum_{i=1}^{k}\frac1i \le \ln k + 1,$$

es decir, el voraz es una **(ln r + 1)-aproximación**.

**Citas.** D. S. Johnson, *Approximation algorithms for combinatorial problems*, J. Computer and System Sciences 9(3):256–278, 1974 (cota H_r). V. Chvátal, *A greedy heuristic for the set-covering problem*, Mathematics of Operations Research 4(3):233–235, 1979 (versión ponderada con H_d). L. Lovász (1975) obtuvo un resultado análogo en el caso no ponderado.

### 1.2 Esquema de la demostración (argumento de precios)

1. **Precios.** Cuando el voraz elige un conjunto que cubre por primera vez q elementos, asigna a cada uno de esos q elementos el **precio 1/q**. Cada elección cuesta 1 en total, así que
   G = Σ_{e∈U} precio(e).
2. **Cada elemento está en algún conjunto óptimo.** Sea O₁,…,O_OPT una cobertura óptima. Como todo e ∈ U está en algún O_i,
   Σ_{e∈U} precio(e) ≤ Σ_{i=1}^{OPT} Σ_{e∈O_i} precio(e).
3. **Cota por conjunto óptimo.** Fijemos O = O_i con |O| = s y ordenemos sus elementos por el momento en que el voraz los cubre: e₁, e₂, …, e_s (los empates, en cualquier orden). Cuando se cubre e_j, todavía quedan sin cubrir al menos los s − j + 1 elementos e_j,…,e_s de O. El voraz podía haber elegido O, que cubriría ≥ s − j + 1 elementos nuevos; como elige el máximo, el q de ese paso cumple q ≥ s − j + 1. Entonces
   precio(e_j) ≤ 1/(s − j + 1), y
   Σ_{e∈O} precio(e) ≤ 1/s + 1/(s−1) + … + 1/1 = H_s ≤ H_d.
4. **Conclusión.** G ≤ OPT · H_d ≤ OPT · H_r. Y H_r ≤ 1 + ln r por comparar la suma con ∫₁^r dx/x. ∎

### 1.3 ¿Es ajustada?

- **Ejemplo concreto del proyecto** ([tests/test_set_cover.py](../tests/test_set_cover.py)): U = {0..5}, S₁ = {0,1,3,4}, S₂ = {0,1,2}, S₃ = {3,4,5}. El voraz toma S₁ (4 nuevas) y luego necesita S₂ y S₃ ⇒ G = 3, mientras OPT = 2 (S₂ y S₃). Razón 1,5 ≤ H₆ ≈ 2,45.
- **Cota inferior de dificultad.** Feige (1998) y Dinur–Steurer (2014) demostraron que no existe un algoritmo polinomial con razón (1 − ε)·ln r para ningún ε > 0, salvo P = NP (Feige, bajo supuestos algo más fuertes). Luego el voraz es esencialmente **óptimo entre los algoritmos polinomiales**.
- En la práctica la razón observada es mucho menor que H_r; esto se verifica en la Fase 6.

### 1.4 Para la Variante A1 (ponderada)

Con costos a_j ≥ 1 se elige en cada paso el mínimo a_j / |S_j \ cubiertas|, y el precio de cada elemento nuevo es esa razón. El mismo argumento (Chvátal, 1979) da G ≤ H_d · OPT con d = max|S_j|. Se desarrolla en la Fase 4.

---

## 2. Variante A1 — voraz ponderado: costo ≤ H_d · óptimo

**Enunciado (Chvátal, 1979).** Con costos a_j ≥ 1 y d = max_j |S_j|, el voraz que elige en cada paso el mínimo a_j / |S_j ∩ (sin cubrir)| devuelve una cobertura de costo G con

$$G \le H_d\cdot \mathrm{OPT}\le H_r\cdot\mathrm{OPT}.$$

**Esquema de la demostración.** Es el mismo argumento de precios de §1.2, con una sola modificación:

1. Cuando se elige S_j que cubre q elementos nuevos, cada uno de ellos paga **a_j / q**. El costo total pagado es exactamente G.
2. Sea O un conjunto de la cobertura óptima, con |O| = s y elementos ordenados por el momento en que el voraz los cubre: e₁,…,e_s. Cuando se cubre e_j, quedan ≥ s − j + 1 elementos de O sin cubrir; elegir O habría costado a_O / (s−j+1) por elemento. Como el voraz elige el mínimo, precio(e_j) ≤ a_O / (s − j + 1).
3. Sumando sobre O: Σ_{e∈O} precio(e) ≤ a_O · H_s ≤ a_O · H_d.
4. Como todo elemento está en algún conjunto óptimo: G ≤ Σ_{O∈OPT} a_O · H_d = H_d · OPT. ∎

Cuando todos los a_j = 1, se recupera §1. El test `test_a1_voraz_respeta_cota_hd` verifica `óptimo ≤ voraz ≤ H_d · óptimo` en 40 instancias.

## 3. Variante B — sin garantía de aproximación

- **Cobertura obligatoria con cobertura exacta:** es **exacta**, no una aproximación (ver la prueba de optimalidad en [03_eficiencia_exactos.md](03_eficiencia_exactos.md)). Con el voraz ponderado en la cobertura, el costo de cobertura es ≤ H_d · a(C\*), pero el presupuesto restante para la Mochila baja, y el efecto sobre el objetivo no está acotado por un factor constante: se trata como heurística.
- **Heurística para λ general:** garantiza solo (i) factibilidad (costo ≤ B) y (ii) no ser peor que "acelerar sin auditar nada" (el prefijo vacío es candidato). Ambas se verifican en `test_b_heuristica_factible_y_acotada`.
- **No es óptima.** Contraejemplo (verificado por ejecución), con λ = 2, B = 16, etapas t = (13, 14, 2), c = (5, 9, 8), d = (6, 14, 1) y categorías con pesos w = (1, 3, 1, 1); interacciones S₁ = {1, 3, 4} con a = 3, S₂ = {4} con a = 2, S₃ = {1, 2} con a = 5 (1-based). El exacto audita {S₂, S₃} y acelera la etapa 2: objetivo **17**. La heurística elige primero S₁ (razón peso/costo 3/3 = 1, la mejor), luego S₃; ningún prefijo de esa secuencia (21, 21, 23) mejora al vacío, y termina con objetivo **21** (acelera las etapas 1 y 2 sin auditar). La causa: la cobertura voraz decide por razón beneficio/costo sin considerar cuánto presupuesto le quita a la Mochila, y el óptimo {S₂, S₃} no es un prefijo de su secuencia.

## 4. Variante C — heurística de aceleración en la ruta crítica

- **Garantías demostrables:** factibilidad (solo acelera si c_i ≤ presupuesto restante), terminación (cada iteración acelera una etapa distinta ⇒ ≤ n iteraciones) y que **la duración nunca empeora** (acelerar reduce τ_i ≥ 0, y L(x) es monótona no creciente en x).
- **No es óptima ni tiene factor constante.** En una cadena es el voraz por razón d/c de la Mochila, que puede ser arbitrariamente malo. Contraejemplo mínimo (verificado por ejecución): cadena 1→2→3 con t = (4, 3, 6), c = (3, 2, 4), d = (0, 2, 3) y B = 4. Razones d/c: etapa 2 = 1,0; etapa 3 = 0,75. La heurística acelera la etapa 2 (costo 2) y la etapa 3 ya no cabe: duración **11**. El óptimo acelera solo la etapa 3 (costo 4): duración **10**.
- **Qué se valida experimentalmente:** la razón heurística/óptimo en instancias pequeñas, contra el exacto de O(2^n·(n+m)) (Fase 6).

## 5. Resumen

| Problema | Algoritmo | Garantía |
|---|---|---|
| Parte 2 | Voraz | ≤ H_d · OPT ≤ H_r · OPT |
| A1 | Voraz ponderado | ≤ H_d · OPT |
| B | Obligatoria + cobertura exacta | Óptima |
| B | Heurística λ general | Factible; ≤ "sin auditar"; sin factor |
| C | Heurística iterativa | Factible; nunca empeora; sin factor |
