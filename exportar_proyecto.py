import os

OUTPUT_FILE = "PROYECTO_COMPLETO.md"

# Carpetas y patrones que deben ignorarse
IGNORAR = [
    "venv", "__pycache__", "migrations",
    ".git", ".idea", ".vscode"
]

# Extensiones útiles para IA
EXTENSIONES = (
    ".py", ".html", ".css", ".js",
    ".json", ".md", ".txt", ".yaml", ".yml"
)


def debe_ignorar(path):
    return any(ignorar in path for ignorar in IGNORAR)


with open(OUTPUT_FILE, "w", encoding="utf-8") as salida:
    salida.write("# Proyecto Django Completo\n\n")

    for root, dirs, files in os.walk("."):
        if debe_ignorar(root):
            continue

        for file in files:
            if not file.endswith(EXTENSIONES):
                continue

            filepath = os.path.join(root, file)

            if debe_ignorar(filepath):
                continue

            salida.write(f"\n\n---\n\n")
            salida.write(f"## 📄 {filepath}\n\n")
            salida.write("```python\n")

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    salida.write(f.read())
            except Exception as e:
                salida.write(f"[ERROR al leer archivo: {e}]")

            salida.write("\n```\n")

print(f"\n\n✅ Archivo generado exitosamente: {OUTPUT_FILE}\n")
