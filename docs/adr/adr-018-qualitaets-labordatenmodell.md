# ADR-018 Qualitäts-/Labordatenmodell

**Status:** Accepted
**Date:** 2026-03-11

## Context
Qualitäts- und Labordaten sind im Agrarhandel zentral für Annahme, Charge, Partie, Preisfindung, Freigabe, Reklamation und Settlement. Ohne gemeinsames Modell entstehen isolierte Qualitätsobjekte, doppelte Regelpfade und unklare Bezüge zwischen Probe, Ergebnis, Charge und Geschäftsentscheidung.

## Decision
VALEO NeuroERP führt ein einheitliches Qualitäts-/Labordatenmodell ein.

Verbindliche Grundsätze:
1. Proben, Labormessungen, Qualitätswerte, Grenzwerte und fachliche Bewertungen werden als zusammenhängender Modellraum geführt.
2. Qualitätsdaten referenzieren immer ihr fachliches Bezugsobjekt, z. B. Annahme, Charge, Partie, Kontrakt oder Lieferung.
3. Rohmessungen, validierte Ergebnisse und fachliche Entscheidungen werden getrennt modelliert.
4. Qualitätsdaten dürfen Preislogik, Freigaben und Reklamationen beeinflussen, aber nur über explizite Regeln, Commands oder Policies.
5. Herkunft, Methode, Zeitbezug und Verantwortlichkeit von Laborergebnissen müssen nachvollziehbar bleiben.
6. Qualitäts- und Labordaten müssen mit Audit, Dokumenten und Workflow kompatibel sein.

## Consequences
Positiv:
- Saubere Verbindung zwischen Qualität, Charge, Preis und Freigabe
- Weniger Sonderlogik in Labor-, Annahme- und Settlementpfaden
- Bessere Grundlage für Reproduzierbarkeit und Audit

Negativ:
- Höherer Modellierungsaufwand im Qualitätsbereich
- Mehr Anforderungen an Datenklassifikation und Methodenbezug
- Bestehende Qualitätslogiken müssen konsolidiert werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-010 Policy-Override-Modell](adr-010-policy-override-modell.md)
- [ADR-012 Dokument-/Audit-Evidence-Modell](adr-012-dokument-audit-evidence-modell.md)
