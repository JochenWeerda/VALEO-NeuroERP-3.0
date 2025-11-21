# ADR-001: FiBu-Domain – Reuse vs. Rewrite

## Status
Accepted – 2025-11-14

## Kontext
- Die bestehende FiBu-Domain existiert fast ausschließlich als Node/TypeScript-Clean-Architecture (`packages/finance-domain` / `domains/finance`) mit umfangreichen Services (Ledger, AP/AR, Tax, AI, OCR).
- Der Python-Microservice `services/finance` ist lediglich ein nicht lauffähiger Stub.
- Zielbild laut `docs/specs/fibu_architektur_spezifikation.md`: GoBD-konforme Microservices (`fibu-core`, `fibu-master-data`, …) auf Basis FastAPI/SQLAlchemy/Event Sourcing.
- GoBD-Tests & Compliance-Hooks sollen in der Python-Landschaft verankert werden (gemeinsame Auth, Monitoring, Deployment Pipelines).

## Entscheidung
1. **Business-Logik (Modelle, Regeln, Events) aus der TypeScript-Domain wird konzeptionell wiederverwendet**, jedoch nicht 1:1 betrieben. Stattdessen:
   - Portierung kritischer Domänen (Ledger, Journal, Accounting Periods, AP/AR) nach Python.
   - Use-Case- und Event-Definitionen dienen als Referenz für Tests und Middleware-Verträge.
2. **Die bisherigen Node-Projekte (packages/finance-domain & domains/finance) werden konsolidiert**:
   - Nur eine Quelle bleibt als „Reference Implementation“ im Repo erhalten (Read-Only).
   - Zweite Quelle wird archiviert bzw. auf die Referenz verwiesen.
3. **Neue produktive Services entstehen ausschließlich in Python** (FastAPI, SQLAlchemy, Celery/Scheduler), damit Logging, Auth, Observability und GoBD-Kontrollen homogen betrieben werden können.
4. **Middleware/Anti-Corruption-Layer** nutzt `packages/shared/contracts/src/finance-schemas.ts` und neue Pydantic-Schemas als gemeinsame Wahrheit für Events.

## Konsequenzen
- **Pro**:
  - Einheitlicher Technologie-Stack für Backend (Python) → einfachere GoBD-Prüfungen, einheitliche Pipelines.
  - Domänenwissen geht nicht verloren: vorhandene TypeScript-Tests/Modelle dienen als Blaupause für neue Implementierungen.
  - Klare Verantwortlichkeit: Node-Code wird Referenz, aber kein produktives Artefakt mehr.
- **Contra**:
  - Portierung verursacht initialen Mehraufwand (Mapping der Geschäftslogik, Tests neu schreiben).
  - Doppelpflege in der Übergangsphase (Referenzcode + neue Services).
- **Folgen für spätere Phasen**:
  - Phase 2 (fibu-core) und Phase 4/6 (AR/AP/OP) verwenden die Portierungsstrategie als Leitplanke.
  - Middleware muss die neuen Event-Schemata publizieren, auch wenn alte Domains noch legacy Events senden.

