# ADR-004 Command-/Action-Layer
**Status:** Accepted
**Date:** 2026-03-11
## Context
Das Produkt besitzt bereits UI-Masken, Toolbar-Aktionen, Quick Actions, Command Palette, Voice- und Agent-Ansatzpunkte. Fuer prozessrelevante Fachlogik reicht ein page-zentriertes CRUD-Modell jedoch nicht aus. Agenten, Policies, Workflows, Retries, Audit und Explainability benoetigen stabile Business-Aktionen mit klarer Semantik.
Das Zielbild priorisiert daher einen gemeinsamen Command-/Action-Layer als bevorzugte Schnittstelle fuer geschaeftsrelevante Aktionen.
## Decision
VALEO NeuroERP etabliert einen gemeinsamen Command-/Action-Layer als Standard fuer prozesskritische Business-Aktionen.
Beispiele fuer solche Aktionen:
- contract.approve
- intake.capture
- quality.release
- settlement.post
- invoice.send
Verbindliche Regeln:
1. Neue Kernprozesse werden zuerst als fachliche Commands modelliert, nicht nur als UI-Handler oder ad-hoc REST-Aufrufe.
2. Quick Actions, Command Palette, Voice und Agent-UX binden auf dieselbe Action-Schicht.
3. Policies pruefen Commands und Prozessuebergaenge auf dieser Schicht.
4. Wichtige Commands erhalten stabile Result- und Error-Modelle.
5. Idempotenz ist fuer wiederholbare oder automatisierbare Commands explizit zu bewerten.
## Consequences
Positiv:
- Einheitliche Fachaktionen fuer Mensch, UI, Workflow und Agent
- Weniger doppelte Implementierung zwischen Frontend, API und Automatisierung
- Bessere Auditierbarkeit und Explainability
Negativ:
- Mehr initiales Design fuer Aktionen und Fehlervertraege
- Bestehende CRUD-orientierte Pfade muessen schrittweise migriert werden
- Teams muessen Business-Aktionen sauber von UI-Interaktionen trennen
## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [Konsolidierte Strategie](../roadmap/status/2026-03-06-valeo-spitzenposition-konsolidiert.md)
