"""Variante C: flujo con etapas en paralelo (DAG).

Tamaño de la entrada: n = |V|, m = |E| y B. La duración del flujo es la de la
ruta más larga (ruta crítica) con pesos τ_i = t_i − d_i·x_i, entre una fuente y
un sumidero ficticios de duración 0.

Los comentarios "# O(.)" cuentan operaciones y coinciden con la deducción de
T(n, m) en docs/03_eficiencia_exactos.md. Ciclos explícitos, sin numpy.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.instancias import InstanciaDAG


@dataclass(frozen=True)
class PrepDAG:
    """Grafo preprocesado: orden topológico y listas de sucesores (se calcula una vez)."""

    orden: tuple[int, ...]
    sucesores: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class RutaCritica:
    """Duración del flujo y una de sus rutas más largas (0-based, en orden de ejecución)."""

    longitud: int
    camino: tuple[int, ...]


@dataclass(frozen=True)
class SolucionDAG:
    """Resultado de una decisión de aceleración sobre el DAG.

    ``pasos[k] = (etapa, L)``: en el paso k de la heurística se aceleró ``etapa``
    y la ruta crítica pasó a durar ``L`` (vacío en el exacto).
    """

    aceleradas: tuple[int, ...]
    costo: int
    duracion: int
    duracion_inicial: int
    camino_inicial: tuple[int, ...]
    camino_final: tuple[int, ...]
    pasos: tuple[tuple[int, int], ...] = ()


def preparar_dag(n: int, aristas: tuple[tuple[int, int], ...]) -> PrepDAG:
    """Orden topológico por el algoritmo de Kahn. T(n, m) = O(n + m).

    Lanza ValueError si el grafo tiene un ciclo. No supone que los índices ya
    estén en orden topológico.
    """
    sucesores: list[list[int]] = [[] for _ in range(n)]  # O(n)
    grado_entrada = [0] * n  # O(n)
    for u, v in aristas:  # m iteraciones
        sucesores[u].append(v)  # O(1) amortizado
        grado_entrada[v] += 1  # O(1)
    orden = [i for i in range(n) if grado_entrada[i] == 0]  # O(n)
    cabeza = 0  # O(1)
    while cabeza < len(orden):  # cada nodo entra una sola vez: n iteraciones
        u = orden[cabeza]  # O(1)
        cabeza += 1  # O(1)
        for v in sucesores[u]:  # sumando sobre todos los u: m iteraciones en total
            grado_entrada[v] -= 1  # O(1)
            if grado_entrada[v] == 0:  # O(1)
                orden.append(v)  # O(1) amortizado
    # Total: O(n) + O(m) + O(n) + O(n + m) = O(n + m)
    if len(orden) != n:
        raise ValueError("el grafo tiene un ciclo")
    return PrepDAG(tuple(orden), tuple(tuple(s) for s in sucesores))


def ruta_critica(
    inst: InstanciaDAG, x: tuple[int, ...] | list[int], prep: PrepDAG | None = None
) -> RutaCritica:
    """Ruta más larga con pesos τ_i = t_i − d_i·x_i, por DP en orden topológico.

    ``fin[v]`` = duración de la ruta más larga que termina en v. La fuente
    ficticia conecta con todos los nodos (τ ≥ 0, así que no cambia el máximo) y
    el sumidero ficticio recibe de todos: L = max_v fin[v].
    T(n, m) = O(n + m) (más O(n + m) de ``preparar_dag`` si no se pasa ``prep``).
    """
    n = inst.n  # O(1)
    if prep is None:
        prep = preparar_dag(n, inst.aristas)  # O(n + m)
    if n == 0:
        return RutaCritica(0, ())
    tau = [inst.t[i] - inst.d[i] * x[i] for i in range(n)]  # n iteraciones, O(1) c/u
    fin = list(tau)  # O(n): ruta que empieza en el propio nodo
    padre = [-1] * n  # O(n)
    for u in prep.orden:  # n iteraciones
        for v in prep.sucesores[u]:  # sumando sobre todos los u: m iteraciones en total
            candidato = fin[u] + tau[v]  # O(1)
            if candidato > fin[v]:  # O(1)
                fin[v] = candidato
                padre[v] = u
    # DP: O(n) + O(m)
    fin_nodo = 0  # O(1)
    for v in range(1, n):  # sumidero ficticio: máximo de fin, n − 1 iteraciones
        if fin[v] > fin[fin_nodo]:  # O(1)
            fin_nodo = v
    camino: list[int] = []
    v = fin_nodo
    while v != -1:  # a lo sumo n iteraciones
        camino.append(v)
        v = padre[v]
    camino.reverse()  # O(n)
    # Total: O(n + m)
    return RutaCritica(fin[fin_nodo], tuple(camino))


def _armar_solucion(
    inst: InstanciaDAG,
    x: list[int],
    prep: PrepDAG,
    inicial: RutaCritica,
    pasos: tuple[tuple[int, int], ...] = (),
) -> SolucionDAG:
    final = ruta_critica(inst, x, prep)  # O(n + m)
    aceleradas = tuple(i for i in range(inst.n) if x[i] == 1)
    return SolucionDAG(
        aceleradas=aceleradas,
        costo=sum(inst.c[i] for i in aceleradas),
        duracion=final.longitud,
        duracion_inicial=inicial.longitud,
        camino_inicial=inicial.camino,
        camino_final=final.camino,
        pasos=pasos,
    )


def dag_exacto(inst: InstanciaDAG) -> SolucionDAG:
    """Exacto por fuerza bruta: 2^n vectores x, se queda con el de menor L(x) y costo ≤ B.

    T(n, m) = O(2^n · (n + m)): por máscara, O(n) para el costo y O(n + m) para L(x)
    (el orden topológico se calcula una sola vez fuera del ciclo).
    """
    n = inst.n  # O(1)
    prep = preparar_dag(n, inst.aristas)  # O(n + m), una sola vez
    inicial = ruta_critica(inst, [0] * n, prep)  # O(n + m)
    mejor_x = [0] * n
    mejor_l = inicial.longitud  # la máscara 0 siempre es factible
    for mascara in range(1 << n):  # 2^n iteraciones
        x = [(mascara >> i) & 1 for i in range(n)]  # O(n)
        costo = 0
        for i in range(n):  # O(n)
            costo += inst.c[i] * x[i]
        if costo <= inst.B:  # O(1)
            longitud = ruta_critica(inst, x, prep).longitud  # O(n + m)
            if longitud < mejor_l:  # O(1)
                mejor_l = longitud
                mejor_x = x
    return _armar_solucion(inst, mejor_x, prep, inicial)


def dag_heuristica(inst: InstanciaDAG) -> SolucionDAG:
    """Heurística iterativa: acelerar en la ruta crítica la etapa con mejor d_i/c_i y recalcular.

    En cada iteración: (1) calcular la ruta crítica, (2) entre sus etapas aún no
    aceleradas, con d_i > 0 y c_i ≤ presupuesto restante, elegir la de mayor
    d_i/c_i (comparación por productos cruzados; desempate: menor índice),
    (3) acelerarla. Termina cuando no hay candidata.
    Cada iteración acelera una etapa distinta ⇒ ≤ n iteraciones de O(n + m):
    T(n, m) = O(n · (n + m)). No tiene garantía de optimalidad (docs/04).
    """
    n = inst.n  # O(1)
    prep = preparar_dag(n, inst.aristas)  # O(n + m)
    x = [0] * n  # O(n)
    restante = inst.B  # O(1)
    inicial = ruta_critica(inst, x, prep)  # O(n + m)
    ruta = inicial
    pasos: list[tuple[int, int]] = []
    while True:  # ≤ n iteraciones: cada una acelera una etapa nueva
        mejor = -1  # O(1)
        for i in ruta.camino:  # ≤ n iteraciones
            if x[i] == 0 and inst.d[i] > 0 and inst.c[i] <= restante:  # O(1)
                if mejor == -1 or inst.d[i] * inst.c[mejor] > inst.d[mejor] * inst.c[i]:  # O(1)
                    mejor = i
        # elegir candidata: O(n)
        if mejor == -1:
            break
        x[mejor] = 1  # O(1)
        restante -= inst.c[mejor]  # O(1)
        ruta = ruta_critica(inst, x, prep)  # O(n + m): la ruta crítica puede cambiar
        pasos.append((mejor, ruta.longitud))
    # Total: n · O(n + m) = O(n·(n + m))
    return _armar_solucion(inst, x, prep, inicial, tuple(pasos))
