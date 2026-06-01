"""
Analizador sintáctico CYK para mensajes de commit de git.
Construye árboles de derivación a partir de una secuencia de tokens
usando la gramática definida en grammar.py.

Integrantes:
  Stiven Henao
  Juan José Gallego
  Juan Sebastián Gomez
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Nodo:
    """Nodo de un árbol de derivación (parse tree).

    Atributos:
        etiqueta : símbolo de la gramática (terminal o no terminal).
        hijos    : nodos hijos; lista vacía si es hoja terminal.
    """

    etiqueta: str
    hijos: list["Nodo"] = field(default_factory=list)

    def es_hoja(self) -> bool:
        return len(self.hijos) == 0

    def mostrar(self, nivel=0):
        sangria = "  " * nivel
        resultado = sangria + self.etiqueta + "\n"
        for hijo in self.hijos:
            resultado += hijo.mostrar(nivel + 1)
        return resultado

    def __repr__(self) -> str:
        return f"Nodo({self.etiqueta!r}, hijos={len(self.hijos)})"


# ---------------------------------------------------------------------------
# Parsing con memoización — admite gramáticas con producciones de largo
# arbitrario (no requiere FNC).
# ---------------------------------------------------------------------------

def parse_todos(
    tokens: list[tuple[str, str]],
    gramatica: dict,
    simbolo_inicial: str = "COMMIT",
) -> list[Nodo]:
    """
    Retorna todos los árboles de derivación válidos para tokens bajo gramatica.

    tokens          : lista de (palabra, categoria) producida por tokenizar()
    gramatica       : diccionario {NoTerminal: [[símbolos], ...]}
    simbolo_inicial : raíz del árbol que se busca
    """
    categorias = [cat for _, cat in tokens]
    n = len(categorias)
    memo: dict = {}

    def _match(prod: list, inicio: int, fin: int):
        """Genera todas las listas de hijos que cubren [inicio, fin) para prod."""
        if not prod:
            if inicio == fin:
                yield []
            return
        primer, resto = prod[0], prod[1:]
        for corte in range(inicio + 1, fin - len(resto) + 1):
            for izq in _expand(primer, inicio, corte):
                for cola in _match(resto, corte, fin):
                    yield [izq] + cola

    def _expand(simbolo: str, inicio: int, fin: int) -> list[Nodo]:
        key = (simbolo, inicio, fin)
        if key in memo:
            return memo[key]
        memo[key] = []  # centinela anti-recursión infinita
        resultado: list[Nodo] = []

        if simbolo in gramatica:
            for prod in gramatica[simbolo]:
                for hijos in _match(prod, inicio, fin):
                    resultado.append(Nodo(simbolo, hijos))
        elif inicio + 1 == fin and categorias[inicio] == simbolo:
            resultado.append(Nodo(simbolo, [Nodo(tokens[inicio][0])]))

        memo[key] = resultado
        return resultado

    return _expand(simbolo_inicial, 0, n)


def parsear(
    tokens: list[tuple[str, str]],
    gramatica: dict,
    simbolo_inicial: str = "COMMIT",
) -> Nodo | None:
    """Retorna el primer árbol válido, o None si la entrada no es reconocida."""
    arboles = parse_todos(tokens, gramatica, simbolo_inicial)
    return arboles[0] if arboles else None
