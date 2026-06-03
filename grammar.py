"""
Gramática libre de contexto (CFG) para mensajes de commit de git.
Especifica las producciones que el analizador CYK utiliza para
construir árboles de derivación.

No terminales: COMMIT, SIMPLE, ACCION, OBJETO, UBICACION
Terminales   : VERBO, SUST, PREP_COMP, PREP_LOC, DET, CONJ

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

    # Objeto directo del verbo.
    'OBJETO': [
        ['SUST', 'PREP_COMP', 'SUST'],
        ['SUST'],
    ],

    # Ubicación del cambio (sin artículo DET).
    'UBICACION': [
        ['PREP_LOC', 'SUST', 'PREP_COMP', 'SUST'],
        ['PREP_LOC', 'SUST'],
    ],
}
