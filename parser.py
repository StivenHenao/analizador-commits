"""
Parser recursivo descendente para mensajes de commit en español.

- 0 árboles → mensaje malformado (Caso 2)
- 1 árbol   → mensaje bien formado (Caso 1)
- 2+ árboles → ambigüedad detectada (Caso 3)
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from grammar import GRAMATICA
from tokenizer import tokenizar


# ---------------------------------------------------------------------------
# Nodo — árbol de derivación
# ---------------------------------------------------------------------------

class Nodo:
    def __init__(self, etiqueta, hijos=None):
        self.etiqueta = etiqueta
        self.hijos = hijos if hijos else []

    def es_hoja(self):
        return len(self.hijos) == 0

    def mostrar(self, nivel=0, prefijo="", es_ultimo=True):
        conector = "└── " if es_ultimo else "├── "
        linea = prefijo + (conector if nivel > 0 else "") + self.etiqueta + "\n"
        prefijo_hijo = prefijo + ("    " if es_ultimo else "│   ") if nivel > 0 else ""
        for i, hijo in enumerate(self.hijos):
            ultimo = (i == len(self.hijos) - 1)
            linea += hijo.mostrar(nivel + 1, prefijo_hijo, ultimo)
        return linea

    def __repr__(self):
        return self.mostrar()


# ---------------------------------------------------------------------------
# parse_todos
# ---------------------------------------------------------------------------

def parse_todos(simbolo, tokens, pos, gramatica):
    """
    Retorna lista de (Nodo, pos_final) para todas las derivaciones posibles
    del símbolo desde la posición pos.
    """
    # Caso terminal: símbolo es una categoría que no aparece en la gramática
    if simbolo not in gramatica:
        if pos < len(tokens) and tokens[pos][1] == simbolo:
            palabra, cat = tokens[pos]
            hoja = Nodo(f"{palabra}  [{cat}]")
            return [(hoja, pos + 1)]
        return []

    resultados = []
    for produccion in gramatica[simbolo]:
        # candidatos acumula (lista_de_hijos, posicion_actual)
        candidatos = [([], pos)]
        for sub in produccion:
            nuevos = []
            for hijos, p in candidatos:
                for hijo, p2 in parse_todos(sub, tokens, p, gramatica):
                    nuevos.append((hijos + [hijo], p2))
            candidatos = nuevos
            if not candidatos:
                break
        for hijos, p_final in candidatos:
            resultados.append((Nodo(simbolo, hijos), p_final))

    return resultados


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def parsear(mensaje: str) -> list[Nodo]:
    """
    Recibe un mensaje de commit en texto libre y retorna la lista de
    árboles de derivación completos.
    """
    tokens = tokenizar(mensaje)
    todos = parse_todos("COMMIT", tokens, 0, GRAMATICA)
    return [arbol for arbol, pos in todos if pos == len(tokens)]


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
        print(f"Entrada: \"{msg}\"")
        print(f"Tokens:  {[(p, c) for p, c in tokenizar(msg)]}")
        print(f"Árboles encontrados: {len(arboles)}")

        if len(arboles) == 0:
            print("\n  [MALFORMADO] El parser no encontró ninguna derivación.")
        elif len(arboles) == 1:
            print("\n  [BIEN FORMADO] Un único árbol de derivación:\n")
            print(arboles[0].mostrar())
        else:
            print(f"\n  [AMBIGUO] {len(arboles)} interpretaciones posibles:\n")
            for i, arbol in enumerate(arboles, 1):
                print(f"  --- Árbol {i} ---")
                print(arbol.mostrar())
