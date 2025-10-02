import os
import sys
import subprocess
from pathlib import Path

"""
Öffnet Exportdateien (CSV/PNG) in LibreOffice (Calc/Draw).
Verwendung:
  python scripts/export_bi_to_libreoffice.py path/to/file.csv
  python scripts/export_bi_to_libreoffice.py path/to/chart.png
"""


def open_in_libreoffice(file_path: str) -> int:
    p = Path(file_path).resolve()
    if not p.exists():
        print(f"Datei nicht gefunden: {p}")
        return 1

    soffice = os.environ.get('SOFFICE_PATH', 'soffice')

    # Zuordnung nach Endung
    ext = p.suffix.lower()
    args = [soffice]
    if ext in ('.csv', '.tsv', '.xlsx', '.ods'):
        args += ['--calc', str(p)]
    elif ext in ('.png', '.svg'):
        args += [str(p)]
    else:
        args += [str(p)]

    try:
        subprocess.Popen(args)
        print(f"LibreOffice gestartet: {' '.join(args)}")
        return 0
    except Exception as e:
        print(f"Fehler beim Start von LibreOffice: {e}")
        return 2


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(open_in_libreoffice(sys.argv[1]))
