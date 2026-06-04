"""
Punto de entrada del analizador de commits en español.

Uso:
  python main.py "mensaje de commit"
  python main.py          ← pide el mensaje por stdin
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from analyzer import analizar_y_reportar


def main() -> None:
    if len(sys.argv) > 1:
        mensaje = ' '.join(sys.argv[1:])
    else:
        mensaje = input("Commit: ").strip()

    if not mensaje:
        print("Error: mensaje vacio.")
        sys.exit(1)

    print(f'\nMensaje: "{mensaje}"')
    analizar_y_reportar(mensaje)


if __name__ == "__main__":
    main()
