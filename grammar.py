"""
Gramática libre de contexto (CFG) para mensajes de commit de git.
Especifica las producciones que el analizador CYK utiliza para
construir árboles de derivación.

No terminales: COMMIT, SIMPLE, ACCION
Terminales   : VERBO, SUST, PREP_COMP, PREP_LOC, DET, CONJ

Esta versión inicial define únicamente COMMIT, SIMPLE y ACCION.
Las producciones de OBJETO y UBICACION se agregan en commits
posteriores.
"""

# ---------------------------------------------------------------------------
# Producciones de la gramática.
# Cada entrada: NoTerminal → lista de producciones (cada producción es
# una lista de símbolos terminales y/o no terminales).
# ---------------------------------------------------------------------------

GRAMATICA: dict[str, list[list[str]]] = {

    # Símbolo inicial.
    'COMMIT': [
        ['SIMPLE'],
    ],

    # Una acción con o sin ubicación.
    'SIMPLE': [
        ['ACCION'],
    ],

    # Núcleo verbal del mensaje.
    'ACCION': [
        ['VERBO', 'SUST'],
        ['VERBO'],
    ],
}
