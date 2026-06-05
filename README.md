# Analizador de mensajes de commit en español

Recibe un mensaje de git commit escrito en español y clasifica el resultado en uno de tres casos:

- **Caso 1** — bien formado: extrae los componentes semánticos del mensaje.
- **Caso 2** — incompleto: reporta qué componente falta y sugiere corrección.
- **Caso 3** — ambiguo: detecta la ambigüedad, muestra los dos árboles de derivación posibles y sus DAGs semánticos.

## Requisitos

- Python 3.10 o superior
- Sin dependencias externas de PLN (todo construido desde cero con la biblioteca estándar)

## Uso

```bash
python main.py "mensaje de commit"
```

Si no se pasa argumento, el sistema solicita el mensaje por stdin:

```bash
python main.py
Commit: corrige error de paginación en el módulo de búsqueda
```

## Ejemplos

**Caso 1 — mensaje bien formado**
```
$ python main.py "agrega validación de correo en el módulo de registro"

[BIEN FORMADO]
  accion  : agrega                          [OK]
  tipo    : feat                            [OK]
  objeto  : validación de correo            [OK]
  modulo  : módulo de registro              [OK]
```

**Caso 2 — mensaje incompleto**
```
$ python main.py "corrige error"

[INCOMPLETO] Campos ausentes: modulo
  accion  : corrige                         [OK]
  tipo    : fix                             [OK]
  objeto  : error                           [OK]
  modulo  : [falta]                         [??]

  Sugerencia: "corrige error en [módulo]"
```

**Caso 3 — mensaje ambiguo**
```
$ python main.py "actualiza estilos y corrige bug en login"

[AMBIGUO] 2 interpretaciones posibles.
  Interpretacion 1 — dos commits separados
  Interpretacion 2 — un commit con accion compuesta
  ...
```

## Módulos

| Archivo | Herramienta del curso | Responsabilidad |
|---|---|---|
| `tokenizer.py` | DFA + Gramática regular | Clasifica cada palabra del mensaje en una categoría léxica (`VERBO`, `SUST`, `PREP_COMP`, `PREP_LOC`, `DET`, `CONJ`) usando el módulo `re` como implementación del DFA. |
| `grammar.py` | CFG | Define la gramática formal del lenguaje de commits como diccionario Python. |
| `parser.py` | Parser + Árbol de derivación | Implementa `parse_todos()` de la Clase 6: retorna todos los árboles de derivación posibles para una secuencia de tokens. |
| `extractor.py` | DCG / Unificación | Recorre el árbol y unifica los nodos para extraer `{accion, tipo, objeto, modulo}`. Detecta ambigüedad cuando la unificación falla. |
| `analyzer.py` | Manejo de ambigüedad | Orquesta los módulos anteriores y clasifica el resultado en caso 1, 2 o 3. |
| `main.py` | — | Punto de entrada CLI. |

## Verbos reconocidos por tipo

| Tipo | Verbos |
|---|---|
| `feat` | agrega, añade, implementa, crea, expone, habilita, soporta, integra, conecta |
| `fix` | corrige, arregla |
| `refactor` | refactoriza, elimina, extrae, remueve, reorganiza, separa, unifica, reemplaza, revierte |
| `chore` | actualiza, modifica, mueve, renombra, mejora, optimiza, ajusta, cambia, configura, inicializa, migra, limpia, borra, deshabilita, protege, valida |
| `docs` | documenta |
| `test` | prueba |

## Estructura del proyecto

```
PLN/
├── main.py          Punto de entrada
├── analyzer.py      Orquestador y clasificador de casos
├── extractor.py     DCG / unificación semántica
├── parser.py        Parser recursivo + clase Nodo
├── grammar.py       CFG como diccionario Python
├── tokenizer.py     DFA / tokenizador léxico
├── README.md        Este archivo
└── informe/
    └── main.tex     Documentación formal de formalismos
```
