# ADR-026 Modell für Import-/Staging-/Prüfpipelines

**Status:** Accepted  
**Date:** 2026-03-11

## Context
ERP-nahe Fachprozesse benötigen robuste Import-, Vorprüf- und Freigabepfade für Stammdaten, Bewegungsdaten, EDI, Dokumente und Fremdsystemimporte. Ohne gemeinsames Modell entstehen direkte Imports in produktive Kernobjekte, inkonsistente Prüflogik und schwer auditierbare Fehlerbehandlung.

## Decision
VALEO NeuroERP führt ein explizites Modell für Import-, Staging- und Prüfpipelines ein.

Verbindliche Grundsätze:
1. Externe oder bulk-orientierte Datenflüsse werden nicht direkt in produktive Kernobjekte geschrieben.
2. Zwischen Importquelle und produktivem Write-Pfad existiert ein expliziter Staging- und Prüfkontext.
3. Validierung, Dublettenprüfung, Mapping, Freigabe und Fehlerbehandlung sind als Pipeline-Schritte modelliert.
4. Importentscheidungen und Korrekturen sind auditierbar.
5. Importpipelines referenzieren Canonical Domain Model, Query-Contracts und Dokument-/Evidence-Modelle.
6. Erfolgreiche Übernahme in produktive Objekte erfolgt kontrolliert über definierte Commands oder bestätigte Prozessschritte.

## Consequences
Positiv:
- Weniger Risiko durch direkte Rohdatenübernahme
- Bessere Prüfbarkeit, Nachvollziehbarkeit und Wiederholbarkeit
- Einheitlicherer Umgang mit EDI-, CSV-, OCR- und Fremdsystemimporten

Negativ:
- Mehr Modellierungs- und Implementierungsaufwand im Importbereich
- Höhere Anforderungen an Pipeline-UX und Fehlerhandling
- Bestehende direkte Importpfade müssen migriert werden

## References
- [ADR-006 Read-Model / Query-Contract-Prinzip](adr-006-read-model-query-contract-prinzip.md)
- [ADR-012 Dokument-/Audit-Evidence-Modell](adr-012-dokument-audit-evidence-modell.md)
