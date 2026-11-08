# Dateigrößenratsche: formatneutrale Reparatur

Stand: 2026-10-12. Slice `ENDPOINT-SPACING-RATCHET-20261012`.

Nach den Rollenimporten überschritten zwei Endpunkte ihre exakte Baseline um
je eine Zeile. Eine überzählige Trennzeile vor dem Compat-Router und eine
Leerzeile innerhalb `send_anfrage` wurden entfernt. Der Python-AST vor und
nach der Änderung ist für beide vollständigen Dateien identisch.

`compat.py`: 3475 → 3474 Zeilen; `mask_frontend_bridges.py`: 1468 → 1467.
`python scripts/check_file_size.py` besteht mit unveränderter Baseline.
Routen, Rollen, Imports, SQL, Funktionen und Verhalten sind unverändert.
Keine neuen Tests für diese reine Formatänderung; keine Datenbank oder Container.

Dies ist eine eng begrenzte CI-Reparatur. Der strukturelle Abbau der bestehenden
15 großen Endpunktdateien, der physische Katalogdrift und die vollständige
GitHub-Abnahme bleiben offen.
