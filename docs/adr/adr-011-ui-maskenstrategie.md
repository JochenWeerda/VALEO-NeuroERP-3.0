# ADR-011 UI-Maskenstrategie

**Status:** Accepted
**Date:** 2026-03-11

## Context
VALEO NeuroERP nutzt bereits generische Patterns, Builder-Ansätze und fachspezifische Seiten. Ohne klare Strategie drohen zwei Fehlentwicklungen: zu viel generische UI in fachlich komplexen Prozessen oder zu viele Einzellösungen trotz wiederkehrender Muster. Beides erhöht langfristig Kosten, Inkonsistenz und UX-Drift.

Das Zielbild verlangt deshalb eine explizite Regel, wann generische Mask-/Process-Builder Pflicht sind und wann fachliche Spezialmasken bewusst zulässig bleiben.

## Decision
VALEO NeuroERP führt eine verbindliche UI-Maskenstrategie mit drei Klassen ein.

Klasse A: Generische Standardmasken
- für strukturierte Objektseiten, einfache Listen, Standardformulare und Routine-Workflows
- bevorzugt auf Basis gemeinsamer Builder, Patterns und Felddefinitionen

Klasse B: Prozessmasken mit erweitertem Pattern-Rahmen
- für fachlich reichere Kernprozesse mit Commands, Freigaben, Explainability, Workflow-Status und Read-Models
- basieren auf gemeinsamen Prozesspatterns, dürfen aber prozessspezifische Kompositionen enthalten

Klasse C: Fachliche Spezialmasken
- nur für stark domänenspezifische Bedienlogik wie Waage, Ernteannahme, visuelle Disposition, Silo-/IoT- oder hochverdichtete Operator-UIs
- müssen ihre Abweichung vom generischen Standard explizit begründen

Verbindliche Grundsätze:
1. Neue Standardobjekte starten in Klasse A.
2. Abweichungen in Klasse B oder C müssen mit Prozesskomplexität, Interaktionsdichte oder Geräte-/Rollenlogik begründet werden.
3. Auch Spezialmasken binden auf Canonical Domain Model, Command-/Action-Layer und Workflow-/Policy-Kern.
4. Gemeinsame Patterns für Fehler, Freigabe, Explainability, Audit und Quick Actions bleiben verbindlich.
5. Builder und Spezialmasken dürfen keine konkurrierenden Fachmodelle etablieren.

## Consequences
Positiv:
- Klarere Entscheidung zwischen Wiederverwendung und Spezial-UI
- Weniger Wildwuchs bei neuen Masken
- Bessere Balance zwischen Liefergeschwindigkeit und fachlicher UX-Qualität

Negativ:
- Mehr Architekturdisziplin vor UI-Implementierung
- Diskussionen über Klassifizierung neuer Seiten müssen explizit geführt werden
- Bestehende Mischformen müssen schrittweise eingeordnet und bereinigt werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](adr-003-canonical-domain-model.md)
- [ADR-004 Command-/Action-Layer](adr-004-command-action-layer.md)
