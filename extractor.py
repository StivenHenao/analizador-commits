"""
Extractor de información semántica a partir de árboles de derivación CYK.

Convierte el árbol producido por el analizador en un diccionario con los
campos: tipo, accion, objeto, ubicacion.

Expone:
    unificar(palabra)  → str   normaliza una palabra al lema canónico
    LEXICO_VERBOS      → dict  mapea tipo de commit → lista de verbos
"""

from __future__ import annotations

import unicodedata


# ---------------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------------

def unificar(palabra: str) -> str:
    """Devuelve la palabra en minúsculas y sin tildes."""
    nfkd = unicodedata.normalize("NFKD", palabra.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# Léxico de verbos por tipo de commit.
# Cada entrada: tipo → conjunto de formas verbales aceptadas.
# ---------------------------------------------------------------------------

LEXICO_VERBOS: dict[str, list[str]] = {

    "feat": [
        "agregar",
        "añadir",
        "implementar",
        "crear",
        "incorporar",
        "incluir",
    ],

    "fix": [
        "corregir",
        "arreglar",
        "reparar",
        "solucionar",
        "resolver",
        "parchear",
    ],

}
