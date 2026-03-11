# ADR-020 Cross-Domain-Referenzmodell für Kontrakt, Charge, Qualität und Settlement

**Status:** Accepted  
**Date:** 2026-03-11

## Context
Die zentrale Landhandels-Prozesskette verbindet Kontrakt, Annahme, Charge, Qualität, Preislogik und Settlement. Ohne ein explizites Cross-Domain-Referenzmodell entstehen lose IDs, Schattenbezüge und fachliche Inkonsistenzen zwischen operativen Domänen.

Ein reines Nebeneinander einzelner Aggregate reicht für belastbare End-to-End-Prozesse nicht aus.

## Decision
VALEO NeuroERP führt ein explizites Cross-Domain-Referenzmodell für Kontrakt, Charge, Qualität und Settlement ein.

Verbindliche Grundsätze:
1. Referenzbeziehungen zwischen diesen Domänen werden als fachlich definierte Bezüge modelliert, nicht nur als zufällige Fremdschlüssel.
2. Jede End-to-End-Transaktion muss nachvollziehbar auf ihren Kontrakt-, Annahme-, Qualitäts- und Settlement-Kontext referenzieren können.
3. Cross-Domain-Referenzen dürfen keine zweite Wahrheit neben dem Canonical Domain Model aufbauen.
4. Preis-, Abzugs-, Qualitäts- und Freigabeentscheidungen müssen ihren fachlichen Referenzraum explizit benennen.
5. Read-Models und Audit-Pfade bauen auf demselben Referenzmodell auf.
6. Domänen bleiben getrennt verantwortet, aber fachlich verbindlich verknüpft.

## Consequences
Positiv:
- Höhere Konsistenz entlang der Kernprozesskette
- Bessere Nachvollziehbarkeit für Audit, Analyse und Support
- Weniger Schattenbezüge zwischen operativen Modulen

Negativ:
- Zusätzlicher Modellierungsaufwand an Domänengrenzen
- Mehr Sorgfalt bei Referenzpflege und Migrationen
- Bestehende implizite Bezüge müssen harmonisiert werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](adr-003-canonical-domain-model.md)
- [ADR-018 Qualitäts-/Labordatenmodell](adr-018-qualitaets-labordatenmodell.md)
