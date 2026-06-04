"""
Extractor de componentes semánticos de un árbol de derivación.

Implementa DCG/Unificación del estilo de Ejercicio_DCGs.py:
- unificar()     → misma función de la profesora, aplicada a componentes de commit
- LEXICO_VERBOS  → DAG de cada verbo: {accion, tipo}
- extraer()      → recorre el árbol y unifica componentes en un DAG de commit

DAG resultante para commit bien formado:
    {'accion': str, 'tipo': str, 'objeto': str, 'modulo': str}

Para commits compuestos o acciones compuestas el DAG tiene:
    {'estructura': 'commits_multiples' | 'accion_compuesta',
     'partes': [dag1, dag2],
     'modulo': str}         ← modulo solo aparece en 'accion_compuesta'
"""

import re
import sys
sys.stdout.reconfigure(encoding="utf-8")

from parser import Nodo, parsear


# ---------------------------------------------------------------------------
# Unificación
# ---------------------------------------------------------------------------

def unificar(dag1, dag2):
    """
    Combina dos DAGs. Retorna None si algún rasgo tiene valores distintos.
    Unificación recursiva para rasgos anidados (dicts dentro de dicts).
    """
    resultado = dict(dag1)
    for rasgo, valor in dag2.items():
        if rasgo in resultado:
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None
                resultado[rasgo] = sub
            elif resultado[rasgo] != valor:
                return None   # conflicto: mismo rasgo, valores distintos
        else:
            resultado[rasgo] = valor
    return resultado


# ---------------------------------------------------------------------------
# Léxico de verbos de commit — DAG semántico de cada verbo
# Estructura: {accion: str, tipo: str}
# ---------------------------------------------------------------------------

LEXICO_VERBOS = {
    # feat — agrega funcionalidad nueva
    'agrega':      {'accion': 'agrega',      'tipo': 'feat'},
    'añade':       {'accion': 'añade',       'tipo': 'feat'},
    'implementa':  {'accion': 'implementa',  'tipo': 'feat'},
    'crea':        {'accion': 'crea',        'tipo': 'feat'},
    'expone':      {'accion': 'expone',      'tipo': 'feat'},
    'habilita':    {'accion': 'habilita',    'tipo': 'feat'},
    'soporta':     {'accion': 'soporta',     'tipo': 'feat'},
    'integra':     {'accion': 'integra',     'tipo': 'feat'},
    'conecta':     {'accion': 'conecta',     'tipo': 'feat'},
    # fix — corrección de errores
    'corrige':     {'accion': 'corrige',     'tipo': 'fix'},
    'arregla':     {'accion': 'arregla',     'tipo': 'fix'},
    # refactor — reorganización sin cambio funcional
    'refactoriza': {'accion': 'refactoriza', 'tipo': 'refactor'},
    'elimina':     {'accion': 'elimina',     'tipo': 'refactor'},
    'extrae':      {'accion': 'extrae',      'tipo': 'refactor'},
    'remueve':     {'accion': 'remueve',     'tipo': 'refactor'},
    'reorganiza':  {'accion': 'reorganiza',  'tipo': 'refactor'},
    'separa':      {'accion': 'separa',      'tipo': 'refactor'},
    'unifica':     {'accion': 'unifica',     'tipo': 'refactor'},
    'reemplaza':   {'accion': 'reemplaza',   'tipo': 'refactor'},
    'revierte':    {'accion': 'revierte',    'tipo': 'refactor'},
    # chore — mantenimiento y configuración
    'actualiza':   {'accion': 'actualiza',   'tipo': 'chore'},
    'modifica':    {'accion': 'modifica',    'tipo': 'chore'},
    'mueve':       {'accion': 'mueve',       'tipo': 'chore'},
    'renombra':    {'accion': 'renombra',    'tipo': 'chore'},
    'mejora':      {'accion': 'mejora',      'tipo': 'chore'},
    'optimiza':    {'accion': 'optimiza',    'tipo': 'chore'},
    'ajusta':      {'accion': 'ajusta',      'tipo': 'chore'},
    'cambia':      {'accion': 'cambia',      'tipo': 'chore'},
    'configura':   {'accion': 'configura',   'tipo': 'chore'},
    'inicializa':  {'accion': 'inicializa',  'tipo': 'chore'},
    'migra':       {'accion': 'migra',       'tipo': 'chore'},
    'limpia':      {'accion': 'limpia',      'tipo': 'chore'},
    'borra':       {'accion': 'borra',       'tipo': 'chore'},
    'deshabilita': {'accion': 'deshabilita', 'tipo': 'chore'},
    'protege':     {'accion': 'protege',     'tipo': 'chore'},
    'valida':      {'accion': 'valida',      'tipo': 'chore'},
    # docs / test
    'documenta':   {'accion': 'documenta',   'tipo': 'docs'},
    'prueba':      {'accion': 'prueba',      'tipo': 'test'},
}


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _parsear_hoja(etiqueta: str) -> tuple[str, str]:
    """'agrega  [VERBO]' → ('agrega', 'VERBO')"""
    m = re.match(r'(.+?)\s+\[(\w+)\]', etiqueta.strip())
    if m:
        return m.group(1).strip(), m.group(2)
    return etiqueta.strip(), 'UNK'


# Categorías que son estructura gramatical, no parte del significado de la frase
_CATS_ESTRUCTURALES = {'PREP_LOC', 'DET', 'CONJ', 'VERBO', 'UNK'}


def _texto_frase(nodo: Nodo) -> str:
    """
    Reconstruye el texto semántico de un subárbol.
    Incluye SUST y PREP_COMP ('de'/'del'); excluye el resto.
    """
    if nodo.es_hoja():
        palabra, cat = _parsear_hoja(nodo.etiqueta)
        return palabra if cat not in _CATS_ESTRUCTURALES else ''
    partes = [_texto_frase(h) for h in nodo.hijos]
    return ' '.join(p for p in partes if p)


# ---------------------------------------------------------------------------
# Extracción recursiva del árbol
# ---------------------------------------------------------------------------

def _extraer_accion(nodo: Nodo) -> dict:
    """
    Extrae el DAG semántico de un nodo ACCION.
    Si el nodo contiene ACCION → VERBO OBJETO CONJ ACCION (producción compuesta),
    intenta unificar las dos acciones. Si falla, señala acción compuesta.
    """
    dag = {}
    for hijo in nodo.hijos:
        if hijo.es_hoja():
            palabra, cat = _parsear_hoja(hijo.etiqueta)
            if cat == 'VERBO':
                rasgos = LEXICO_VERBOS.get(
                    palabra,
                    {'accion': palabra, 'tipo': 'chore'}
                )
                dag = unificar(dag, rasgos) or dag
            # CONJ hojas se ignoran — son conectores estructurales
        elif hijo.etiqueta == 'OBJETO':
            texto = _texto_frase(hijo)
            dag = unificar(dag, {'objeto': texto}) or dag
        elif hijo.etiqueta == 'ACCION':
            # Producción compuesta: VERBO OBJETO CONJ ACCION
            sub = _extraer_accion(hijo)
            merged = unificar(dag, sub)
            if merged is None:
                # Conflicto → dos acciones distintas en un mismo ACCION
                return {'estructura': 'accion_compuesta', 'partes': [dag, sub]}
            dag = merged
    return dag


def extraer(arbol: Nodo) -> dict:
    """
    Recorre el árbol de derivación y retorna el DAG del commit.

    Casos:
      COMMIT → SIMPLE CONJ COMMIT  →  intenta unificar; si falla → commits_multiples
      SIMPLE → ACCION UBICACION    →  unifica accion-dag con {modulo: ...}
      SIMPLE → ACCION              →  solo accion-dag (modulo ausente)
    """
    label = arbol.etiqueta

    if label == 'COMMIT':
        if len(arbol.hijos) == 3:
            # COMMIT → SIMPLE CONJ COMMIT
            dag_izq = extraer(arbol.hijos[0])   # SIMPLE
            dag_der = extraer(arbol.hijos[2])   # COMMIT
            merged = unificar(dag_izq, dag_der)
            if merged is None:
                return {
                    'estructura': 'commits_multiples',
                    'partes': [dag_izq, dag_der],
                }
            return merged
        # COMMIT → SIMPLE
        return extraer(arbol.hijos[0])

    if label == 'SIMPLE':
        resultado = {}
        for hijo in arbol.hijos:
            if hijo.etiqueta == 'ACCION':
                sub = _extraer_accion(hijo)
                merged = unificar(resultado, sub)
                if merged is None:
                    resultado = sub   # sub ya es un dag compuesto
                else:
                    resultado = merged
            elif hijo.etiqueta == 'UBICACION':
                modulo = _texto_frase(hijo)
                merged = unificar(resultado, {'modulo': modulo})
                # unificar puede fallar si 'modulo' ya existe con distinto valor
                resultado = merged if merged is not None else resultado
        return resultado

    return {}


# ---------------------------------------------------------------------------
# Formato de salida
# ---------------------------------------------------------------------------

def _fmt_dag(dag: dict, sangria: str = "  ") -> str:
    """Formatea un DAG para mostrarlo en pantalla."""
    if 'estructura' not in dag:
        campos = ['accion', 'tipo', 'objeto', 'modulo']
        lineas = []
        for campo in campos:
            valor = dag.get(campo, '[no especificado]')
            lineas.append(f"{sangria}{campo:<8} : {valor}")
        return '\n'.join(lineas)

    estructura = dag['estructura']
    lineas = [f"{sangria}estructura : {estructura}"]
    for i, parte in enumerate(dag['partes'], 1):
        lineas.append(f"{sangria}  parte {i}:")
        lineas.append(_fmt_dag(parte, sangria + "    "))
    if 'modulo' in dag:
        lineas.append(f"{sangria}modulo     : {dag['modulo']}")
    return '\n'.join(lineas)


# ---------------------------------------------------------------------------
# CLI / prueba rápida
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    casos = [
        "agrega validación de correo en el módulo de registro",
        "corrige error",
        "actualiza estilos y corrige bug en login",
    ]

    for msg in casos:
        arboles = parsear(msg)
        print("=" * 60)
        print(f"Entrada  : \"{msg}\"")
        print(f"Arboles  : {len(arboles)}")

        for i, arbol in enumerate(arboles, 1):
            dag = extraer(arbol)
            print(f"\n  Arbol {i} -> DAG:")
            print(_fmt_dag(dag))
