# ADR-022 Regelmodell für Reklamation, Abzug und Ausnahmebehandlung

**Status:** Accepted
**Date:** 2026-03-11

## Context
Reklamation, Abzug, Qualitätsabweichung, Freigabeausnahme und Sonderbehandlung sind im Landhandel keine Randfälle, sondern Teil des operativen Kerns. Ohne ein explizites Regelmodell werden diese Fälle in UI-Sonderlogik, Einzelservices oder manuelle Ausnahmen gedrückt.

Das schwächt Reproduzierbarkeit, Audit und Prozesssicherheit.

## Decision
VALEO NeuroERP führt ein explizites Regelmodell für Reklamation, Abzug und Ausnahmebehandlung ein.

Verbindliche Grundsätze:
1. Reklamationen, Abzüge und Ausnahmefälle werden als fachlich modellierte Regel- und Entscheidungsräume behandelt.
2. Regeldefinition, Begründung, Freigabe und Ergebnis müssen nachvollziehbar miteinander verknüpft sein.
3. Ausnahmebehandlung darf nicht nur implizit in UI oder Einzelfall-Skripten stattfinden.
4. Qualitätsdaten, Vertragskontext, Preislogik und Policy müssen in dasselbe Entscheidungsmodell einfließen können.
5. Manuelle Overrides sind zulässig, aber nur auditierbar, begründet und mit Verantwortlichkeit versehen.
6. Simulation und Explainability gelten auch für Ausnahme- und Abzugspfadentscheidungen.

## Consequences
Positiv:
- Höhere Reproduzierbarkeit von Sonderfällen und Abzügen
- Weniger verdeckte Fachlogik in Einzelfallpfaden
- Bessere Auditierbarkeit und Supportfähigkeit

Negativ:
- Mehr Modellierungsaufwand für fachliche Ausnahmefälle
- Höhere Anforderungen an Regeltestung und Explainability
- Bestehende manuelle Sonderpfade müssen konsolidiert werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-010 Policy-Override-Modell](adr-010-policy-override-modell.md)
- [ADR-018 Qualitäts-/Labordatenmodell](adr-018-qualitaets-labordatenmodell.md)
