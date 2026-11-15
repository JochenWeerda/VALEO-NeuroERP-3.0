---
title: Studio-Verhaltenstests Waagenliste
status: abgeschlossen
last_reviewed: 2026-11-13
---

# Studio-Verhaltenstests Waagenliste

Die drei Runtime46-Altprüfungen der Waagenliste sind durch ausführbare Verhaltenstests ersetzt. Die Tests laden die vorhandene native ScreenDefinition-Fixture und durchlaufen den echten Studio-Compiler, die Runtime und den Renderer. Anmeldung, Definitionstransport, Overlay und API sind Testgrenzen; die Waagendaten entsprechen dem API-Format.

Geprüft werden das Laden und Anzeigen von Standort und Typ, die Navigation zur Hofliste über die Studio-Aktion, die Suche nach Typ und Standort sowie eine leere Antwort und einen API-Fehler mit erfolgreichem Wiederholungsversuch. Der erste Lauf fand einen Fehler im Test selbst: Die Tabelle verwendet keine HTML-table-Wurzel. Die Suche wird deshalb über die zugänglichen Zeilenaktionen geprüft.

Nachweis vom 13.11.2026, Arbeitsverzeichnis `packages/frontend-web`: `.\node_modules\.bin\vitest.cmd run src/__tests__/pages/waage/liste.test.tsx --maxWorkers=2` — 5 Tests bestanden. Der Aufruf über pnpm scheiterte zuvor an einem EPERM bei der Installation seiner eigenen Version; der lokale Vitest-Aufruf war erfolgreich. Keine Datenbank verwendet.

Die Tests belegen keine Prüfung realer Backendberechtigungen, MCP-/CLI-Parität oder Browser-Gesamtabnahme. Der ergänzende Backend-Test `test_frontend_behavior_fixtures_match_current_studio_definitions` in `tests/test_intake_weighing_screen_contracts.py` vergleicht die sechs Intake-/Waagen-Fixtures vollständig mit den aktuellen kanonischen Buildern. Fixture-Vertrag und gesenkte Altlast-Ratsche: neun Tests bestanden. Der Studio-Umbau der Waage bleibt laut Workboard separat offen.

Die UI-Rollenprüfung ist nicht Bestandteil dieser Tests: Das vorhandene Intake-Harness ersetzt die Berechtigungsprojektion; die relevanten Schreibaktionen verlangen eigene Rechte. Ein Test mit diesem Ersatz wäre kein Nachweis der echten Rollenauswertung.
