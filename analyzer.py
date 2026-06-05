"""
Orquestador del sistema de análisis de commits.

Conecta tokenizador → parser → extractor y clasifica el resultado en
uno de cuatro casos:
  0 — malformado  : 0 árboles
  1 — bien formado: 1 árbol, DAG completo
  2 — incompleto  : 1 árbol, DAG con campos ausentes
  3 — ambiguo     : 2 o más árboles
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from tokenizer import tokenizar
from parser    import parsear
from extractor import extraer, unificar

# Campos semánticos que debe tener un commit completo
_CAMPOS = ('accion', 'tipo', 'objeto', 'modulo')


# ---------------------------------------------------------------------------
# Análisis
# ---------------------------------------------------------------------------

def analizar(mensaje: str) -> dict:
    """
    Tokeniza, parsea y extrae. Retorna un dict con:
      caso      : 0 | 1 | 2 | 3
      tokens    : [(palabra, cat), ...]
      arboles   : [Nodo, ...]
      dags      : [dict, ...]
      faltantes : [campo, ...]   solo presente en caso 2
    """
    tokens  = tokenizar(mensaje)
    arboles = parsear(mensaje)
    dags    = [extraer(a) for a in arboles]

    if len(arboles) == 0:
        return {'caso': 0, 'tokens': tokens, 'arboles': [], 'dags': []}

    if len(arboles) == 1:
        dag = dags[0]
        faltantes = [c for c in _CAMPOS if not dag.get(c)]
        if faltantes or 'estructura' in dag:
            return {'caso': 2, 'tokens': tokens, 'arboles': arboles,
                    'dags': dags, 'faltantes': faltantes}
        return {'caso': 1, 'tokens': tokens, 'arboles': arboles, 'dags': dags}

    return {'caso': 3, 'tokens': tokens, 'arboles': arboles, 'dags': dags}


# ---------------------------------------------------------------------------
# Helpers de reporte
# ---------------------------------------------------------------------------

def _marca(presente: bool) -> str:
    return "OK" if presente else "??"


def _fila_dag(dag: dict) -> str:
    """Una línea por campo del DAG, marcando ausentes."""
    partes = []
    for campo in _CAMPOS:
        valor = dag.get(campo)
        marca = _marca(valor is not None)
        partes.append(f"  {campo:<8}: {valor or '[falta]':30s}  [{marca}]")
    return '\n'.join(partes)


def _sugerencia_incompleto(dag: dict) -> str:
    """Reconstruye una sugerencia de commit completo a partir del DAG parcial."""
    accion = dag.get('accion', '<verbo>')
    objeto = dag.get('objeto', '[qué]')
    modulo = dag.get('modulo')
    if modulo:
        return f'"{accion} {objeto} en {modulo}"'
    return f'"{accion} {objeto} en [módulo]"'


def _sugerencia_malformado(tokens: list) -> str:
    """Detecta qué falta en un mensaje que no parseó."""
    cats = {c for _, c in tokens}
    verbos = [p for p, c in tokens if c == 'VERBO']
    susts  = [p for p, c in tokens if c == 'SUST']

    if not verbos:
        ejemplo = susts[0] if susts else '[objeto]'
        return (f"Falta verbo de acción al inicio.\n"
                f"  Sugerencia: \"<verbo> {ejemplo} en [módulo]\"")
    if not susts:
        return (f"Falta descripción del cambio.\n"
                f"  Sugerencia: \"{verbos[0]} [qué] en [módulo]\"")
    return (f"Estructura no reconocida.\n"
            f"  Sugerencia: \"{verbos[0]} {susts[0]} en [módulo]\"")


def _etiqueta_interpretacion(dag: dict, idx: int) -> str:
    """Etiqueta legible para cada interpretación en el caso ambiguo."""
    estructura = dag.get('estructura')
    if estructura == 'commits_multiples':
        return f"Interpretacion {idx} — dos commits separados"
    if estructura == 'accion_compuesta':
        return f"Interpretacion {idx} — un commit con accion compuesta"
    return f"Interpretacion {idx}"


def _fmt_dag_compuesto(dag: dict) -> str:
    """Formatea un DAG de tipo commits_multiples o accion_compuesta."""
    lineas = []
    for i, parte in enumerate(dag['partes'], 1):
        lineas.append(f"    Parte {i}:")
        for campo in _CAMPOS:
            valor = parte.get(campo, '[falta]')
            lineas.append(f"      {campo:<8}: {valor}")
    if 'modulo' in dag:
        lineas.append(f"    modulo  : {dag['modulo']}")
    return '\n'.join(lineas)


# ---------------------------------------------------------------------------
# Reporte por caso
# ---------------------------------------------------------------------------

def reportar(resultado: dict) -> None:
    caso    = resultado['caso']
    arboles = resultado['arboles']
    dags    = resultado['dags']
    tokens  = resultado['tokens']

    sep = "=" * 62

    if caso == 0:
        print(f"\n[MALFORMADO] El mensaje no pudo analizarse.")
        print(_sugerencia_malformado(tokens))

    elif caso == 1:
        dag = dags[0]
        print(f"\n[BIEN FORMADO]")
        print(_fila_dag(dag))

    elif caso == 2:
        dag       = dags[0]
        faltantes = resultado.get('faltantes', [])
        print(f"\n[INCOMPLETO] Campos ausentes: {', '.join(faltantes) or 'estructura no esperada'}")
        print(_fila_dag(dag))
        print(f"\n  Sugerencia: {_sugerencia_incompleto(dag)}")

    elif caso == 3:
        print(f"\n[AMBIGUO] {len(arboles)} interpretaciones posibles.\n")
        for i, (arbol, dag) in enumerate(zip(arboles, dags), 1):
            print(sep)
            print(_etiqueta_interpretacion(dag, i))
            print()
            # árbol de derivación
            print("  Arbol de derivacion:")
            for linea in arbol.mostrar().splitlines():
                print("  " + linea)
            # DAG
            print("\n  DAG:")
            if 'estructura' in dag:
                print(_fmt_dag_compuesto(dag))
            else:
                print(_fila_dag(dag))
            print()
        print(sep)
        print("  Por que hay ambiguedad?")
        # Explicación según el par de estructuras encontradas
        estructuras = [d.get('estructura') for d in dags]
        if 'commits_multiples' in estructuras and 'accion_compuesta' in estructuras:
            print("  'y' puede coordinar dos commits completos")
            print("  o unir dos acciones dentro de un mismo commit.")


def analizar_y_reportar(mensaje: str) -> None:
    resultado = analizar(mensaje)
    reportar(resultado)
