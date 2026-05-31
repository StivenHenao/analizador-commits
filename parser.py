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