"""
Tokenizador léxico para mensajes de commit en español.

DFA implementado con re (módulo estándar de Python). Las categorías
se prueban en orden de prioridad; la primera que coincide gana.

5-tupla formal:
  Q  = {q0, q_verbo, q_prep_comp, q_prep_loc, q_det, q_conj, q_sust, q_unk}
  Σ  = palabras en minúsculas (tokens separados por espacios)
  q0 = q0
  F  = {q_verbo, q_prep_comp, q_prep_loc, q_det, q_conj, q_sust}
  δ  = función de transición definida por las reglas RE en REGLAS
"""

import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Gramática regular — cada entrada es (categoria, patron_re)
# El orden importa: el DFA prueba las reglas de arriba hacia abajo.
# ---------------------------------------------------------------------------

VERBOS = (
    "agrega|añade|actualiza|corrige|arregla|elimina|borra|"
    "implementa|modifica|mueve|renombra"
)

PREPS_COMP = r"del|de|al|para|con|por|a"
PREPS_LOC  = r"en|sobre|desde|hacia"
DETS       = r"el|la|los|las|un|una"

CONJS = r"\by\b|\bo\b|\be\b|\bu\b"

REGLAS = [
    ("VERBO",     re.compile(rf"\b({VERBOS})\b",     re.IGNORECASE)),
    ("PREP_COMP", re.compile(rf"\b({PREPS_COMP})\b", re.IGNORECASE)),
    ("PREP_LOC",  re.compile(rf"\b({PREPS_LOC})\b",  re.IGNORECASE)),
    ("DET",       re.compile(rf"\b({DETS})\b",       re.IGNORECASE)),
    ("CONJ",      re.compile(CONJS,                  re.IGNORECASE)),
    ("SUST",      re.compile(r"\b\w[\w\-]*\b")),     # patrón residual
]


def _normalizar(texto: str) -> str:
    """Pasa a minúsculas y elimina signos de puntuación externos."""
    texto = texto.lower().strip()
    texto = re.sub(r"[\"'.,;:!?¿¡()[\]{}]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def _sin_tilde(palabra: str) -> str:
    """Elimina tildes convirtiendo a NFD y descartando caracteres de categoría Mn."""
    return "".join(
        c for c in unicodedata.normalize("NFD", palabra)
        if unicodedata.category(c) != "Mn"
    )


def tokenizar(mensaje: str) -> list[tuple[str, str]]:
    """
    Recibe un mensaje de commit en español y devuelve una lista de
    (palabra_original, categoria) donde categoria ∈ {VERBO, PREP_COMP, PREP_LOC, DET, CONJ, SUST}.

    El tokenizador es un DFA: cada palabra pasa por las transiciones en
    orden; la primera regla que coincide determina el estado aceptor.
    """
    texto = _normalizar(mensaje)
    palabras = texto.split()
    tokens = []

    for palabra in palabras:
        categoria = "UNK"
        palabra_cmp = _sin_tilde(palabra)
        for cat, patron in REGLAS:
            if patron.fullmatch(palabra_cmp):
                categoria = cat
                break
        tokens.append((palabra, categoria))

    return tokens


# ---------------------------------------------------------------------------
# CLI / prueba rápida
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ejemplos = [
        "agrega validación de correo en el módulo de registro",
        "corrige error",
        "actualiza estilos y corrige bug en login",
        "elimina del archivo las dependencias obsoletas",
        "agrÉga soporte para tildes en verbos",
    ]

    for msg in ejemplos:
        print(f"\nEntrada: \"{msg}\"")
        print("-" * 50)
        for palabra, cat in tokenizar(msg):
            print(f"  {palabra:<20} -> {cat}")
