"""Erzeugt texthaftes PDF für Playwright E2E (Compound-Upload / Rationsoptimierung).

Nutzt ReportLab (requirements.txt). Ausführung aus Repo-Root:

    python scripts/generate_rations_e2e_compound_pdf.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


OUT = Path("packages/frontend-web/tests/fixtures/rations/e2e-compound-label.pdf")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    buf_path = OUT.with_suffix(".pdf.tmp")
    c = canvas.Canvas(str(buf_path), pagesize=A4)
    text = c.beginText(40, 800)
    for line in (
        "Milchleistungsfutter Test E2E",
        "",
        "Inhaltsstoffe: Rohprotein 16,5 % Rohfett 3,0 % Rohfaser 6,0 % Rohasche 7,0 %",
        "Zusammensetzung: 40,0 % Gerste 60,0 % Mais",
    ):
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()
    buf_path.replace(OUT)
    print(f"Written {OUT.resolve()} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
