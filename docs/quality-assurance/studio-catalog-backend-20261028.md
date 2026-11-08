# Flow-Spine-Katalog: Backend-Vertrag, 28.10.2026

Die registrierte Definition `workflow/flow-spine-studio` ist ein Cockpit mit `flowSpineCatalog: {enabled: true, warmWorkspaces: true}`. Der bestehende Frontend-Katalogweg lädt `/api/v1/process/flow-spines/catalog`; die Definition enthält keine eigene URL, generische Tabelle oder Exportattrappe. Die bisherige Deadletter-Quelle wurde entfernt. Warmup ist eine optionale Laufzeitoptimierung; der Vertrag verlangt einen expliziten booleschen Wert.

Der Draft-Validator akzeptiert das optionale Metadatenobjekt nur für diese Screen-ID und `mode=cockpit`; zusätzliche Schlüssel, URLs, fehlende Felder und nicht-boolesche Werte werden abgewiesen. Die bestehenden Draft-Namensraum- und Kollisionsregeln bleiben bestehen.

Nachweis: `python -m pytest tests/test_studio_catalog_contracts.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""` — 11 bestanden, ohne Datenbank. Der Python-Konsolenabschluss meldete anschließend einen Windows-Destruktorhinweis; der Testlauf selbst war erfolgreich. Browser- und Integrationsabnahme gehören zum Lead-Slice.
