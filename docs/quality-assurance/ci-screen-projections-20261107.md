# Frueher Projektionsabgleich

Der gemeinsame Generatorcheck prueft jetzt auch generate_capture_screens.py --check und generate_screen_registry_snapshot.py --check. Beide vorhandenen Generatorvertraege werden unveraendert verwendet. Damit wird der Drift zwischen den 31 kanonischen Definitionen und ihren beiden Frontend-Projektionen vor dem Backendtestlauf erkannt. Die unabhaengige Frontend-Synchronisierungssuite bleibt bestehen.

Gezielte Abnahme: beide Generatorchecks gruen. Keine Coverage-/Testschwelle reduziert, kein Datenbankzugriff und keine zusaetzliche Datenbank. Vollstaendiger Meta-Check folgt nach Abschluss der parallel veraenderten Antwort-/Studiovertraege und deren OpenAPI-Regeneration.
