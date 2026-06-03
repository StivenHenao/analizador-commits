"""
Gramática de contexto libre para mensajes de commit en español.

G = (V, T, P, S) donde:
  V = {COMMIT, SIMPLE, ACCION, OBJETO, UBICACION}
  T = {VERBO, SUST, PREP_COMP, PREP_LOC, DET, CONJ}
  S = COMMIT
  P = producciones listadas en GRAMATICA

Los terminales son las categorías que produce el tokenizador (DFA).
Separar PREP_COMP (de/del) de PREP_LOC (en/a/para/...) elimina la
ambigüedad espuria entre objeto compuesto y ubicación.
"""

GRAMATICA = {
    # Punto de entrada.
    # COMMIT → SIMPLE CONJ COMMIT es right-recursive → sin left recursion.
    'COMMIT': [
        ['SIMPLE', 'CONJ', 'COMMIT'],   # "corrige X y agrega Y en Z"
        ['SIMPLE'],
    ],

    # Commit simple: acción con o sin ubicación.
    # Un commit sin UBICACION se considera incompleto (lo detecta el analyzer).
    'SIMPLE': [
        ['ACCION', 'UBICACION'],
        ['ACCION'],
    ],

    # Acción: verbo + objeto, opcionalmente coordinado con otra acción.
    # Esta producción compuesta genera el Árbol 2 del caso ambiguo.
    'ACCION': [
        ['VERBO', 'OBJETO', 'CONJ', 'ACCION'],  # "actualiza X y corrige Y"
        ['VERBO', 'OBJETO'],
    ],

    # Objeto directo: sustantivo con o sin complemento de PREP_COMP (de/del).
    # Solo PREP_COMP puede aparecer aquí → "bug en login" NO parsea como objeto.
    'OBJETO': [
        ['SUST', 'PREP_COMP', 'SUST'],   # "validación de correo"
        ['SUST'],
    ],

    # Ubicación del cambio dentro del sistema.
    # Siempre empieza con PREP_LOC; el artículo DET es opcional.
    'UBICACION': [
        ['PREP_LOC', 'DET', 'SUST', 'PREP_COMP', 'SUST'],  # "en el módulo de registro"
        ['PREP_LOC', 'DET', 'SUST'],                         # "en el módulo"
        ['PREP_LOC', 'SUST', 'PREP_COMP', 'SUST'],          # "en módulo de registro"
        ['PREP_LOC', 'SUST'],                                # "en login"
    ],
}
