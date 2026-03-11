# ADR-017 Governance für Pricing-/Marktdatenquellen

**Status:** Accepted  
**Date:** 2026-03-11

## Context
Landhandel, Kontrakte und Rohwarenabrechnung hängen an Preislogiken, Formeln, Terminmarktdaten und externen Marktquellen. Ohne Governance für Pricing- und Marktdatenquellen drohen schwer prüfbare Preisentscheidungen, inkonsistente Berechnungen und fachlich unsaubere Abhängigkeiten von Fremddaten.

## Decision
VALEO NeuroERP führt eine verbindliche Governance für Pricing- und Marktdatenquellen ein.

Verbindliche Grundsätze:
1. Externe Preis- und Marktdatenquellen werden als klassifizierte Fachquellen modelliert.
2. Jede Preisentscheidung muss nachvollziehbar auf Quelle, Zeitbezug und Berechnungslogik referenzieren können.
3. Rohdaten, normalisierte Marktdaten und fachlich wirksame Preisparameter werden getrennt gehalten.
4. Preislogik darf nicht implizit in UI, Importskripten oder Einzelservices verstreut werden.
5. Fallback-, Ausfall- und Override-Regeln für Marktdatenquellen sind explizit festzulegen.
6. Preis- und Marktdatenflüsse müssen auditierbar und reproduzierbar sein.

## Consequences
Positiv:
- Höhere Nachvollziehbarkeit und Prüfbarkeit von Preisentscheidungen
- Weniger Drift zwischen Kontraktlogik, Kalkulation und Marktintegration
- Saubere Grundlage für Formellogik und Benchmarking

Negativ:
- Mehr Governance- und Modellierungsaufwand
- Höhere Anforderungen an Datenqualität und Historisierung
- Bestehende implizite Preisquellen müssen harmonisiert werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](adr-003-canonical-domain-model.md)
- [ADR-015 Analytics-/Benchmark-Datenproduktmodell](adr-015-analytics-benchmark-datenproduktmodell.md)
