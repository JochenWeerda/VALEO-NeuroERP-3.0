# ADR-012 Dokument-/Audit-Evidence-Modell

**Status:** Accepted
**Date:** 2026-03-11

## Context
VALEO NeuroERP bewegt sich in stark dokumentations- und prüfungsrelevanten Prozessen: GoBD, DMS, Freigaben, OCR, Anhänge, Exportpfade, Audit-Nachweise und fachliche Belegketten. Ohne gemeinsames Modell entstehen isolierte Dokumentobjekte, unklare Referenzen, schwache Nachvollziehbarkeit und unterschiedliche Audit-Standards je Domäne.

Das Zielbild verlangt daher ein gemeinsames Dokument- und Audit-Evidence-Modell.

## Decision
VALEO NeuroERP führt ein gemeinsames Modell für Dokumente, Anhänge und Audit-Evidence ein.

Verbindliche Grundsätze:
1. Dokumente, Anhänge, OCR-Ergebnisse, Prüfbelege und Exportartefakte werden als zusammenhängender Modellraum behandelt.
2. Jedes Evidence-Objekt besitzt eine fachliche Referenz auf Prozess, Objekt oder Workflow-Schritt.
3. Audit-relevante Dokumentpfade müssen Herkunft, Zeitbezug und Änderungsbezug nachvollziehbar machen.
4. DMS, OCR, Freigaben, GoBD-Exporte und Agentenaktionen dürfen keine isolierten Sondermodelle etablieren.
5. Sichtbarkeit, Aufbewahrung und Exportierbarkeit sind pro Evidence-Klasse definierbar.
6. Dokument- und Evidence-Modelle müssen in Workflow, Policy und Audit verwendbar sein.

## Consequences
Positiv:
- Einheitlichere Beleg- und Nachweisketten über mehrere Domänen
- Bessere Grundlage für GoBD, Freigaben, DMS und OCR
- Weniger Sonderlogik in einzelnen Fachmodulen

Negativ:
- Zusätzlicher Modellierungsaufwand im Dokumentenbereich
- Bestehende Dateianhänge und Spezialpfade müssen harmonisiert werden
- Höhere Anforderungen an Klassifikation und Referenzpflege

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-005 Workflow-/Policy-Kern](adr-005-workflow-policy-kern.md)
- [AGENT-INTEGRATION.md](../AGENT-INTEGRATION.md)
