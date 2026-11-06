"""Lectura y validación de casos de prueba (JSON). Capa 2: aquí SÍ hay I/O (``core`` no lo tiene).

Formato de entrada (índices de etapas, interacciones y categorías en BASE 1, como en los docs)::

    {
      "id": "caso_01",
      "descripcion": "texto libre (opcional)",
      "parte1": {"t": [5, 8, 6, 4], "c": [3, 4, 2, 3], "d": [2, 4, 1, 2], "B": 6},
      "parte2": {"r": 5,
                 "conjuntos": [[1, 2, 3], [2, 4], [3, 4], [4, 5], [1, 5]],
                 "costos": [1, 1, 1, 1, 1]}
    }

- ``parte1`` y ``parte2`` son opcionales (se resuelve la que venga), pero debe haber al menos una.
- ``costos`` (opcional) activa la Variante A1 (auditoría ponderada por costo, a_j ≥ 1);
  sin él, cada interacción cuesta 1 (Parte 2 original).
- ``conjuntos[j]`` lista las categorías (1..r) que cubre la interacción j+1.

Formato del docente (G3, se detecta por la clave ``etapas``)::

    {"parametros": {"numero_etapas": 20, "presupuesto_aceleracion_B": 72,
                    "presupuesto_conjunto_aceleracion_y_auditoria": 100, "numero_categorias_riesgo": 12},
     "flujo": [{"origen": "E01", "destino": "E02"}, ...],
     "categorias_riesgo": [{"id": "R01", "categoria": "sesgo", "importancia": 4}, ...],
     "etapas": [{"id": "E01", "duracion_normal": 18, "costo_aceleracion": 7,
                 "reduccion_tiempo_si_acelera": 5,
                 "variaciones_auditoria": [{"id": "parcial", "costo": 3, "riesgos_cubiertos": ["R01"]}, ...]}]}

Se convierte a las mismas instancias del núcleo así:
- Parte 1: t_i = duracion_normal, c_i = costo_aceleracion, d_i = reduccion_tiempo_si_acelera, B = presupuesto_aceleracion_B.
  ``flujo`` se valida como DAG; si es una cadena en serie la Mochila es exacta (Parte 1), y si no, la duración
  es la ruta crítica y se resuelve la Variante C (``Caso.aristas``, ``Caso.es_cadena``).
- Parte 2 (Variante A1): cada VARIACIÓN de auditoría de cada etapa es una interacción (S_j = riesgos_cubiertos,
  a_j = costo); las categorías son los riesgos y w_k = importancia. De cada etapa se audita como máximo
  UNA variación (``grupo_interaccion``). ``riesgos_cubiertos_auditoria_completa`` es redundante y se ignora.
- Variante B: si viene ``presupuesto_conjunto_aceleracion_y_auditoria`` (cobertura obligatoria + Mochila con el resto).

Cualquier incumplimiento lanza ``CasoInvalido`` con un mensaje que dice qué campo falla.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from core.instancias import InstanciaMochila, InstanciaSetCover


class CasoInvalido(ValueError):
    """El archivo de caso no cumple el formato."""


@dataclass(frozen=True)
class Caso:
    """Un caso ya validado, con índices pasados a base 0 para los algoritmos.

    Los campos con nombre (``nombres_*``) conservan los ids del archivo original (E01, R01,
    "E03 parcial") para la salida; vacíos si el formato usa solo índices numéricos.
    """

    id: str
    descripcion: str
    mochila: InstanciaMochila | None
    cobertura: InstanciaSetCover | None
    ponderado: bool  # True si el caso trae ``costos`` (Variante A1)
    nombres_etapas: tuple[str, ...] = ()
    nombres_interacciones: tuple[str, ...] = ()
    nombres_categorias: tuple[str, ...] = ()
    grupo_interaccion: tuple[int, ...] = ()  # etapa (0-based) de cada interacción; de cada grupo, a lo sumo una
    presupuesto_conjunto: int | None = None  # B de la Variante B (aceleración + auditoría)
    aristas: tuple[tuple[int, int], ...] = ()  # precedencias del flujo (0-based); vacío si el caso no trae flujo
    es_cadena: bool = True  # False si el flujo es un DAG general (entonces aplica la Variante C, no la Mochila)


def _entero(valor, campo: str, minimo: int = 0) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise CasoInvalido(f"{campo}: se esperaba un entero, llegó {valor!r}")
    if valor < minimo:
        raise CasoInvalido(f"{campo}: debe ser >= {minimo}, llegó {valor}")
    return valor


def _lista_enteros(valor, campo: str, minimo: int = 0) -> list[int]:
    if not isinstance(valor, list):
        raise CasoInvalido(f"{campo}: se esperaba una lista")
    return [_entero(v, f"{campo}[{i + 1}]", minimo) for i, v in enumerate(valor)]


def _parte1(d: dict, id_caso: str) -> InstanciaMochila:
    for clave in ("t", "c", "d", "B"):
        if clave not in d:
            raise CasoInvalido(f"{id_caso}: parte1 sin el campo '{clave}'")
    t = _lista_enteros(d["t"], "parte1.t", 0)
    c = _lista_enteros(d["c"], "parte1.c", 1)
    dd = _lista_enteros(d["d"], "parte1.d", 0)
    B = _entero(d["B"], "parte1.B", 0)
    if not (len(t) == len(c) == len(dd)):
        raise CasoInvalido(f"{id_caso}: parte1.t, c y d deben tener la misma longitud "
                           f"({len(t)}, {len(c)}, {len(dd)})")
    for i, (ti, di) in enumerate(zip(t, dd), start=1):
        if di > ti:
            raise CasoInvalido(f"{id_caso}: etapa {i}: d ({di}) no puede superar t ({ti})")
    return InstanciaMochila(t=tuple(t), c=tuple(c), d=tuple(dd), B=B)


def _parte2(d: dict, id_caso: str) -> tuple[InstanciaSetCover, bool]:
    for clave in ("r", "conjuntos"):
        if clave not in d:
            raise CasoInvalido(f"{id_caso}: parte2 sin el campo '{clave}'")
    r = _entero(d["r"], "parte2.r", 1)
    if not isinstance(d["conjuntos"], list) or not d["conjuntos"]:
        raise CasoInvalido(f"{id_caso}: parte2.conjuntos debe ser una lista no vacía")
    conjuntos = []
    for j, s in enumerate(d["conjuntos"], start=1):
        cats = _lista_enteros(s, f"parte2.conjuntos[{j}]", 1)
        for k in cats:
            if k > r:
                raise CasoInvalido(f"{id_caso}: interacción {j}: categoría {k} fuera de 1..{r}")
        conjuntos.append(frozenset(k - 1 for k in cats))
    ponderado = "costos" in d
    costos = _lista_enteros(d["costos"], "parte2.costos", 1) if ponderado else [1] * len(conjuntos)
    if len(costos) != len(conjuntos):
        raise CasoInvalido(f"{id_caso}: parte2.costos tiene {len(costos)} valores y hay "
                           f"{len(conjuntos)} interacciones")
    return InstanciaSetCover(r=r, conjuntos=tuple(conjuntos), a=tuple(costos), w=(1,) * r), ponderado


def _texto(valor, campo: str) -> str:
    if not isinstance(valor, str) or not valor:
        raise CasoInvalido(f"{campo}: se esperaba un texto no vacío, llegó {valor!r}")
    return valor


def _objeto(valor, campo: str) -> dict:
    if not isinstance(valor, dict):
        raise CasoInvalido(f"{campo}: se esperaba un objeto")
    return valor


def _requerir(d: dict, claves: tuple[str, ...], donde: str) -> None:
    for clave in claves:
        if clave not in d:
            raise CasoInvalido(f"{donde}: falta el campo '{clave}'")


def _leer_flujo(ids: list[str], flujo, id_caso: str) -> tuple[tuple[tuple[int, int], ...], bool]:
    """Valida ``flujo`` como DAG de las etapas y devuelve (aristas 0-based, ¿es una cadena en serie?).

    Una cadena es un DAG con n−1 aristas donde cada etapa tiene a lo sumo un sucesor y un predecesor:
    ahí la duración es Σt − Σd y la Parte 1 (Mochila) es exacta. Si no lo es, la duración es la de la ruta
    crítica y el problema es la Variante C.
    """
    if not isinstance(flujo, list):
        raise CasoInvalido(f"{id_caso}: 'flujo' debe ser una lista de aristas")
    indice = {e: i for i, e in enumerate(ids)}
    aristas: list[tuple[int, int]] = []
    for k, a in enumerate(flujo, start=1):
        a = _objeto(a, f"{id_caso}: flujo[{k}]")
        _requerir(a, ("origen", "destino"), f"{id_caso}: flujo[{k}]")
        for x in (a["origen"], a["destino"]):
            if x not in indice:
                raise CasoInvalido(f"{id_caso}: flujo[{k}] nombra una etapa inexistente ({x!r})")
        u, v = indice[a["origen"]], indice[a["destino"]]
        if u == v:
            raise CasoInvalido(f"{id_caso}: flujo[{k}]: la etapa {a['origen']} no puede preceder a sí misma")
        if (u, v) in aristas:
            raise CasoInvalido(f"{id_caso}: flujo[{k}]: arista repetida {a['origen']}→{a['destino']}")
        aristas.append((u, v))
    n = len(ids)
    grado_entrada, sucesores = [0] * n, [[] for _ in range(n)]
    for u, v in aristas:
        grado_entrada[v] += 1
        sucesores[u].append(v)
    pendientes, vistas = [i for i in range(n) if grado_entrada[i] == 0], 0
    entrada = grado_entrada[:]
    while pendientes:  # Kahn: si no se procesan las n etapas, hay un ciclo. O(n + m)
        u = pendientes.pop()
        vistas += 1
        for v in sucesores[u]:
            entrada[v] -= 1
            if entrada[v] == 0:
                pendientes.append(v)
    if vistas != n:
        raise CasoInvalido(f"{id_caso}: el flujo tiene un ciclo; debe ser un grafo acíclico")
    es_cadena = (len(aristas) == n - 1 and max(grado_entrada, default=0) <= 1
                 and max((len(s) for s in sucesores), default=0) <= 1)
    return tuple(aristas), es_cadena


def _formato_docente(datos: dict, id_caso: str) -> Caso:
    """Convierte el formato del docente (etapas + variaciones de auditoría) a las instancias del núcleo."""
    par = _objeto(datos.get("parametros", {}), f"{id_caso}: parametros")
    _requerir(par, ("presupuesto_aceleracion_B",), f"{id_caso}: parametros")
    B = _entero(par["presupuesto_aceleracion_B"], "parametros.presupuesto_aceleracion_B", 0)
    conjunto = par.get("presupuesto_conjunto_aceleracion_y_auditoria")
    if conjunto is not None:
        conjunto = _entero(conjunto, "parametros.presupuesto_conjunto_aceleracion_y_auditoria", 0)
    etapas = datos["etapas"]
    if not isinstance(etapas, list) or not etapas:
        raise CasoInvalido(f"{id_caso}: 'etapas' debe ser una lista no vacía")
    if "numero_etapas" in par and _entero(par["numero_etapas"], "parametros.numero_etapas", 1) != len(etapas):
        raise CasoInvalido(f"{id_caso}: parametros.numero_etapas = {par['numero_etapas']} pero hay {len(etapas)} etapas")

    # categorías de riesgo: id -> índice 0-based, importancia w_k
    categorias = datos.get("categorias_riesgo", [])
    if not isinstance(categorias, list):
        raise CasoInvalido(f"{id_caso}: 'categorias_riesgo' debe ser una lista")
    idx_cat: dict[str, int] = {}
    pesos: list[int] = []
    for k, cat in enumerate(categorias, start=1):
        cat = _objeto(cat, f"{id_caso}: categorias_riesgo[{k}]")
        _requerir(cat, ("id", "importancia"), f"{id_caso}: categorias_riesgo[{k}]")
        cid = _texto(cat["id"], f"categorias_riesgo[{k}].id")
        if cid in idx_cat:
            raise CasoInvalido(f"{id_caso}: categoría repetida {cid!r}")
        idx_cat[cid] = k - 1
        pesos.append(_entero(cat["importancia"], f"categorias_riesgo[{k}].importancia", 1))
    if "numero_categorias_riesgo" in par and _entero(par["numero_categorias_riesgo"], "parametros.numero_categorias_riesgo", 0) != len(categorias):
        raise CasoInvalido(f"{id_caso}: parametros.numero_categorias_riesgo = {par['numero_categorias_riesgo']} "
                           f"pero hay {len(categorias)} categorías")

    ids, t, c, dd = [], [], [], []
    conjuntos, costos, nombres_int, grupos = [], [], [], []
    for i, e in enumerate(etapas):
        e = _objeto(e, f"{id_caso}: etapas[{i + 1}]")
        _requerir(e, ("id", "duracion_normal", "costo_aceleracion", "reduccion_tiempo_si_acelera"), f"{id_caso}: etapas[{i + 1}]")
        eid = _texto(e["id"], f"etapas[{i + 1}].id")
        if eid in ids:
            raise CasoInvalido(f"{id_caso}: etapa repetida {eid!r}")
        ids.append(eid)
        t.append(_entero(e["duracion_normal"], f"{eid}.duracion_normal", 0))
        c.append(_entero(e["costo_aceleracion"], f"{eid}.costo_aceleracion", 1))
        dd.append(_entero(e["reduccion_tiempo_si_acelera"], f"{eid}.reduccion_tiempo_si_acelera", 0))
        if dd[-1] > t[-1]:
            raise CasoInvalido(f"{id_caso}: etapa {eid}: reducción ({dd[-1]}) no puede superar la duración ({t[-1]})")
        vistas: set[str] = set()
        for v in e.get("variaciones_auditoria", []):
            v = _objeto(v, f"{eid}.variaciones_auditoria")
            _requerir(v, ("id", "costo", "riesgos_cubiertos"), f"{id_caso}: {eid}.variaciones_auditoria")
            vid = _texto(v["id"], f"{eid}.variaciones_auditoria.id")
            if vid in vistas:
                raise CasoInvalido(f"{id_caso}: etapa {eid}: variación repetida {vid!r}")
            vistas.add(vid)
            riesgos = v["riesgos_cubiertos"]
            if not isinstance(riesgos, list):
                raise CasoInvalido(f"{id_caso}: {eid} {vid}: riesgos_cubiertos debe ser una lista")
            for rid in riesgos:
                if rid not in idx_cat:
                    raise CasoInvalido(f"{id_caso}: {eid} {vid}: riesgo inexistente {rid!r}")
            conjuntos.append(frozenset(idx_cat[rid] for rid in riesgos))
            costos.append(_entero(v["costo"], f"{eid} {vid}.costo", 1))
            nombres_int.append(f"{eid} {vid}")
            grupos.append(i)
    aristas, es_cadena = _leer_flujo(ids, datos["flujo"], id_caso) if "flujo" in datos else ((), True)

    mochila = InstanciaMochila(t=tuple(t), c=tuple(c), d=tuple(dd), B=B)
    cobertura = None
    if conjuntos and categorias:
        cobertura = InstanciaSetCover(r=len(categorias), conjuntos=tuple(conjuntos), a=tuple(costos), w=tuple(pesos))
    return Caso(id=id_caso, descripcion=str(datos.get("descripcion", "")), mochila=mochila, cobertura=cobertura,
                ponderado=True, nombres_etapas=tuple(ids), nombres_interacciones=tuple(nombres_int),
                nombres_categorias=tuple(str(cat["id"]) for cat in categorias), grupo_interaccion=tuple(grupos),
                presupuesto_conjunto=conjunto, aristas=aristas, es_cadena=es_cadena)


def parsear_caso(datos: dict, nombre_por_defecto: str = "caso") -> Caso:
    """Valida un diccionario ya leído del JSON y lo convierte en ``Caso``."""
    if not isinstance(datos, dict):
        raise CasoInvalido("el archivo debe contener un objeto JSON")
    id_caso = str(datos.get("id", nombre_por_defecto))
    if "etapas" in datos:  # formato del docente
        return _formato_docente(datos, id_caso)
    if "parte1" not in datos and "parte2" not in datos:
        raise CasoInvalido(f"{id_caso}: debe traer 'parte1' o 'parte2'")
    mochila = _parte1(datos["parte1"], id_caso) if "parte1" in datos else None
    cobertura, ponderado = (_parte2(datos["parte2"], id_caso) if "parte2" in datos else (None, False))
    return Caso(id=id_caso, descripcion=str(datos.get("descripcion", "")), mochila=mochila,
                cobertura=cobertura, ponderado=ponderado)


def cargar_caso(ruta: Path) -> Caso:
    """Lee un archivo JSON de caso. El id por defecto es el nombre del archivo."""
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise CasoInvalido(f"{Path(ruta).name}: JSON mal formado ({e})") from e
    return parsear_caso(datos, nombre_por_defecto=Path(ruta).stem)


def listar_casos(ruta: Path) -> list[Path]:
    """Un archivo .json, o todos los .json de una carpeta (orden alfabético)."""
    ruta = Path(ruta)
    if ruta.is_file():
        return [ruta]
    if not ruta.is_dir():
        raise CasoInvalido(f"no existe la ruta de casos: {ruta}")
    archivos = sorted(ruta.glob("*.json"))
    if not archivos:
        raise CasoInvalido(f"no hay archivos .json en {ruta}")
    return archivos
