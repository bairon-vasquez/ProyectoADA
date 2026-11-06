# Diagramas de clases (Mermaid)

Diagramas de lo implementado en el proyecto. Las **clases** son las `dataclass` (instancias y soluciones); los **módulos** de funciones (algoritmos, experimentos, visualización) se representan con el estereotipo `<<module>>`, porque en el código son archivos de funciones y no clases.

Para verlos: GitHub los renderiza directamente; en VS Code instala la extensión *Markdown Preview Mermaid Support*; o pega cada bloque en <https://mermaid.live>.

Convenciones del dibujo:

- `*--` composición (un objeto contiene a otros).
- `..>` dependencia (la función recibe o devuelve ese tipo).
- `-->` uso entre módulos.

---

## 1. Capa `core`: datos y algoritmos

```mermaid
classDiagram
    direction LR

    class InstanciaMochila {
        <<dataclass>>
        +tuple~int~ t
        +tuple~int~ c
        +tuple~int~ d
        +int B
        +n() int
    }
    class InstanciaSetCover {
        <<dataclass>>
        +int r
        +tuple~frozenset~ conjuntos
        +tuple~int~ a
        +tuple~int~ w
        +n() int
        +es_factible() bool
    }
    class InstanciaDAG {
        <<dataclass>>
        +tuple~int~ t
        +tuple~int~ c
        +tuple~int~ d
        +tuple aristas
        +int B
        +n() int
        +m() int
    }
    class InstanciaCombinada {
        <<dataclass>>
        +InstanciaMochila cadena
        +InstanciaSetCover cobertura
        +int B
        +int lam
    }

    class SolucionMochila {
        <<dataclass>>
        +tuple~int~ etapas
        +int reduccion
        +int costo
        +int duracion
    }
    class SolucionCobertura {
        <<dataclass>>
        +tuple~int~ indices
        +int costo
        +tuple pasos
        +tamano() int
    }
    class PrepDAG {
        <<dataclass>>
        +tuple~int~ orden
        +tuple sucesores
    }
    class RutaCritica {
        <<dataclass>>
        +int longitud
        +tuple~int~ camino
    }
    class SolucionDAG {
        <<dataclass>>
        +tuple~int~ aceleradas
        +int costo
        +int duracion
        +int duracion_inicial
        +tuple~int~ camino_inicial
        +tuple~int~ camino_final
        +tuple pasos
    }
    class SolucionCombinada {
        <<dataclass>>
        +tuple~int~ etapas
        +tuple~int~ interacciones
        +int costo
        +int duracion
        +int penalizacion
        +int objetivo
    }

    class generadores {
        <<module>>
        +generar_mochila(n, B, semilla) InstanciaMochila
        +generar_set_cover(n, r, semilla, prob, a_max) InstanciaSetCover
        +generar_set_cover_adversarial(k) InstanciaSetCover
        +generar_dag(n, m, B, semilla) InstanciaDAG
        +generar_combinada(n, N, r, semilla) InstanciaCombinada
    }
    class mochila {
        <<module>>
        +mochila_fuerza_bruta(inst) SolucionMochila
        +construir_tabla_dp(inst) tabla
        +reconstruir_etapas(inst, tabla) tuple
        +mochila_dp(inst) SolucionMochila
    }
    class set_cover {
        <<module>>
        +numero_armonico(k) float
        +cobertura_voraz(inst) SolucionCobertura
        +cobertura_exacta(inst) SolucionCobertura
        +cobertura_voraz_ponderada(inst) SolucionCobertura
        +cobertura_exacta_ponderada(inst) SolucionCobertura
    }
    class dag {
        <<module>>
        +preparar_dag(n, aristas) PrepDAG
        +ruta_critica(inst, x, prep) RutaCritica
        +dag_exacto(inst) SolucionDAG
        +dag_heuristica(inst) SolucionDAG
    }
    class combinado {
        <<module>>
        +evaluar_combinada(inst, etapas, interacciones) SolucionCombinada
        +combinado_cobertura_obligatoria(inst, exacta) SolucionCombinada
        +combinado_heuristica(inst) SolucionCombinada
        +combinado_exacto(inst) SolucionCombinada
    }

    InstanciaCombinada *-- InstanciaMochila : cadena
    InstanciaCombinada *-- InstanciaSetCover : cobertura
    PrepDAG ..> RutaCritica : permite calcular
    SolucionDAG o-- RutaCritica : ruta antes y despues

    generadores ..> InstanciaMochila : crea
    generadores ..> InstanciaSetCover : crea
    generadores ..> InstanciaDAG : crea
    generadores ..> InstanciaCombinada : crea

    mochila ..> InstanciaMochila : recibe
    mochila ..> SolucionMochila : devuelve
    set_cover ..> InstanciaSetCover : recibe
    set_cover ..> SolucionCobertura : devuelve
    dag ..> InstanciaDAG : recibe
    dag ..> PrepDAG : usa
    dag ..> RutaCritica : devuelve
    dag ..> SolucionDAG : devuelve
    combinado ..> InstanciaCombinada : recibe
    combinado ..> SolucionCombinada : devuelve

    combinado --> mochila : DP con el presupuesto restante
    combinado --> set_cover : cobertura de costo minimo
```

**Cómo leerlo.** Cada problema tiene su instancia (entrada), su módulo de algoritmos y su solución (salida). La Variante B es la única que **compone** otros dos problemas: `InstanciaCombinada` contiene una cadena y una cobertura, y `combinado` reutiliza `mochila` y `set_cover`.

---

## 2. Capas `experimentos` y `visualizacion`

```mermaid
classDiagram
    direction TB

    class medir {
        <<module>>
        +COLUMNAS list
        +RESULTADOS Path
        +medir(funcion, repeticiones, calentamiento) tiempos
        +mediana(tiempos) float
        +medir_caso(algoritmo, barrido, n, ...) filas
        +escribir_csv(ruta, filas, columnas)
    }
    class correr_mochila {
        <<module>>
        +main(rapido, carpeta) Path
    }
    class correr_set_cover {
        <<module>>
        +main(rapido, carpeta) Path
    }
    class correr_dag {
        <<module>>
        +main(rapido, carpeta) Path
    }
    class correr_combinado {
        <<module>>
        +main(rapido, carpeta) Path
    }
    class correr_razones {
        <<module>>
        +main(rapido, carpeta) list
    }
    class CSV {
        <<archivos>>
        mochila
        set_cover
        dag
        combinado
        razones 4 archivos
    }

    class Modelo {
        <<dataclass>>
        +str nombre
        +str formula
        +f(fila) float
        +float exponente
    }
    class Serie {
        <<dataclass>>
        +str archivo
        +str algoritmo
        +str barrido
        +str titulo
        +tuple~Modelo~ modelos
        +bool exponencial
        +bool intercepto
    }
    class Ajuste {
        <<dataclass>>
        +Serie serie
        +Modelo modelo
        +float c
        +float c0
        +float r2
        +float err_rel_medio
        +razon
    }
    class ajuste {
        <<module>>
        +SERIES list~Serie~
        +cargar(archivo) DataFrame
        +medianas(df, serie) DataFrame
        +ajustar(med, serie, modelo) Ajuste
        +pendiente_loglog(x, t) float
        +factor_por_paso(x, t) float
        +resumen() DataFrame
        +ajuste_conjunto_ruta() dict
    }
    class graficas {
        <<module>>
        +figura_serie(serie, df, destino) Ajuste
        +figura_ruta_conjunta(destino) dict
        +figura_razon_set_cover(carpeta, destino) DataFrame
        +figura_razon_heuristicas(carpeta, destino) DataFrame
        +figura_resumen(tabla, destino)
        +main() list~Path~
    }
    class dibujos {
        <<module>>
        +camino_reconstruccion(inst, tabla) list
        +fig_tabla_dp(inst, tabla, nombres) Figure
        +fig_cobertura(inst, indices, paso, titulo) Figure
        +capas_dag(inst) list
        +posiciones_dag(inst) dict
        +fig_dag(inst, x, camino, longitud, titulo, nombres) Figure
    }
    class app {
        <<module Streamlit>>
        +tab_mochila()
        +tab_set_cover()
        +tab_dag()
        +tab_combinado()
        +tab_experimentos()
        +main()
    }
    class PNG {
        <<archivos>>
        figuras 21 PNG
        tabla_ajustes
        tabla_razones
    }
    class core {
        <<capa 1>>
        algoritmos puros
    }

    Serie o-- Modelo : modelos
    Ajuste --> Serie
    Ajuste --> Modelo
    ajuste ..> Serie : define SERIES
    ajuste ..> Ajuste : devuelve

    correr_mochila --> medir
    correr_set_cover --> medir
    correr_dag --> medir
    correr_combinado --> medir
    correr_razones --> medir
    correr_mochila --> core : ejecuta y mide
    correr_set_cover --> core : ejecuta y mide
    correr_dag --> core : ejecuta y mide
    correr_combinado --> core : ejecuta y mide
    correr_razones --> core : compara con el exacto

    medir ..> CSV : escribe

    ajuste ..> CSV : lee
    graficas --> ajuste
    graficas ..> PNG : escribe
    dibujos ..> graficas : paleta y estilo
    dibujos --> core : dibuja resultados
    app --> core : muestra resultados
    app --> dibujos
    app --> graficas
    app --> ajuste
```

**Cómo leerlo.** Solo `experimentos` mide tiempos y escribe CSV. `visualizacion` los **lee** (`ajuste`), los grafica (`graficas`) y los muestra (`app`). `dibujos` y `app` usan `core` únicamente para mostrar resultados, nunca para medir.

---

## 3. Dependencias entre capas

```mermaid
classDiagram
    direction LR

    class core {
        <<capa 1>>
        instancias
        generadores
        mochila
        set_cover
        dag
        combinado
    }
    class experimentos {
        <<capa 2>>
        medir
        correr_scripts
        resultados CSV
    }
    class visualizacion {
        <<capa 3>>
        ajuste
        graficas
        dibujos
        app
    }
    class docs {
        <<analisis formal>>
        02_reducciones
        03_eficiencia_exactos
        04_aproximaciones
        05_validacion_experimental
    }
    class tests {
        <<pytest>>
        394 tests
    }

    experimentos --> core : mide
    visualizacion --> experimentos : lee los CSV
    visualizacion --> core : solo para mostrar
    docs ..> core : T deducido del codigo
    docs ..> experimentos : valida con los CSV
    tests --> core : exacto vs fuerza bruta
    tests --> experimentos : pruebas de humo
    tests --> visualizacion : pruebas de humo y app
```

La dependencia es **unidireccional**: `core` no importa nada de las otras capas, por lo que los algoritmos analizados son exactamente los que se miden.

---

## 4. Relación entre los problemas

```mermaid
classDiagram
    direction TB

    class Mochila01 {
        <<NP-completo clasico>>
        Karp 1972
    }
    class VertexCover {
        <<NP-completo clasico>>
        Karp 1972
    }
    class Parte1 {
        <<ACELERACION-CADENA>>
        DP exacta pseudo-polinomial
    }
    class Parte2 {
        <<COBERTURA-AUDITORIA>>
        voraz con cota H_r
    }
    class VarianteA1 {
        <<Set Cover con costos>>
        voraz ponderado con cota H_d
    }
    class VarianteB {
        <<presupuesto conjunto>>
        Mochila junto con Set Cover
    }
    class VarianteC {
        <<DAG>>
        ruta critica lineal en n y m
    }

    Mochila01 -- Parte1 : equivalentes, reduccion en ambos sentidos
    VertexCover --|> Parte2 : se reduce a
    Parte2 --|> VarianteA1 : caso particular con costos a_j iguales a 1
    Parte1 --|> VarianteB : caso particular sin interacciones
    Parte2 --|> VarianteB : caso particular sin etapas
    Parte1 --|> VarianteC : caso particular, DAG de un solo camino
```

**Cómo leerlo.** Las flechas `--|>` indican "es un caso particular de" o "se reduce a": un problema más general es al menos tan difícil como el particular. Las pruebas están en [02_reducciones.md](02_reducciones.md).
