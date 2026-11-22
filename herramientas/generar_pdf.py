"""Genera informe.pdf a partir de README.md (mismo contenido).

Requiere el paquete `markdown-it-py` (pip install markdown-it-py), que sigue
CommonMark como GitHub, y Google Chrome o Chromium instalado. Ejecutar
desde la raíz del repositorio:

    python herramientas/generar_pdf.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from markdown_it import MarkdownIt

RAIZ = Path(__file__).resolve().parents[1]
CANDIDATOS_CHROME = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser", "chrome",
]

ESTILO = """
@page { size: Letter; margin: 1.3cm 1.5cm; }
body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
       font-size: 8.8pt; line-height: 1.3; color: #1f2328; }
p { margin: 3px 0 5px; }
ul, ol { margin: 2px 0 5px; padding-left: 17px; }
li { margin: 0; }
h1 { font-size: 15pt; border-bottom: 2px solid #2a78d6; padding-bottom: 3px;
     margin: 0 0 6px; }
h2 { font-size: 12.5pt; border-bottom: 1px solid #d0d7de; margin: 12px 0 4px;
     padding-bottom: 2px; }
h3 { font-size: 10.5pt; margin: 10px 0 3px; }
h4 { font-size: 9.4pt; margin: 8px 0 2px; }
table { border-collapse: collapse; margin: 4px 0 7px; font-size: 7.8pt;
        width: 100%; page-break-inside: avoid; }
th, td { border: 1px solid #d0d7de; padding: 2px 4px; vertical-align: top; }
th { background: #f0f4f8; }
code { font-family: Menlo, Consolas, monospace; font-size: 7.8pt;
       background: #f3f4f6; padding: 0 2px; border-radius: 3px; }
pre { background: #f6f8fa; padding: 5px 8px; border-radius: 4px;
      font-size: 7.6pt; line-height: 1.25; page-break-inside: avoid;
      white-space: pre-wrap; margin: 4px 0 6px; }
pre code { background: none; padding: 0; }
img { display: block; max-width: 64%; margin: 4px auto 6px;
      page-break-inside: avoid; }
a { color: #1c5cab; text-decoration: none; }
hr { border: none; border-top: 1px solid #d0d7de; margin: 8px 0; }
"""


def buscar_chrome() -> str:
    """Encuentra el ejecutable de Chrome o Chromium.

    Returns:
        La ruta del ejecutable.

    Raises:
        SystemExit: si no se encuentra ninguno.
    """
    for candidato in CANDIDATOS_CHROME:
        ruta = shutil.which(candidato) or (
            candidato if Path(candidato).exists() else None)
        if ruta:
            return ruta
    sys.exit("No se encontró Google Chrome ni Chromium.")


def readme_a_html() -> str:
    """Convierte README.md en un documento HTML con estilos de impresión.

    Returns:
        El HTML completo, con rutas relativas a la raíz del repositorio.
    """
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    cuerpo = MarkdownIt("commonmark").enable("table").render(texto)
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f'<base href="{RAIZ.as_uri()}/"><title>Informe Pulso</title>'
            f"<style>{ESTILO}</style></head><body>{cuerpo}</body></html>")


def main() -> None:
    """Escribe informe.pdf en la raíz del repositorio."""
    salida = RAIZ / "informe.pdf"
    with tempfile.TemporaryDirectory() as carpeta:
        html = Path(carpeta) / "informe.html"
        html.write_text(readme_a_html(), encoding="utf-8")
        subprocess.run(
            [buscar_chrome(), "--headless=new", "--disable-gpu",
             "--allow-file-access-from-files", "--no-pdf-header-footer",
             f"--print-to-pdf={salida}", html.as_uri()],
            check=True, capture_output=True,
        )
    print(f"PDF generado: {salida}")


if __name__ == "__main__":
    main()
