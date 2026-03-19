# ADR-003 Canonical Domain Model
**Status:** Accepted
**Date:** 2026-03-11
## Context
VALEO NeuroERP deckt bereits viele Fachbereiche ab. Mit wachsender Prozessbreite steigt aber das Risiko konkurrierender Fachmodelle in UI, API, Read-Models, Agent-Contracts und Integrationen. Ohne verbindliches Referenzmodell entstehen Schattenmodelle, doppelte Transformationen und inkonsistente Prozesslogik.
Das Zielbild in [target-state-landhandel-erp.md](../architecture/target-state-landhandel-erp.md) priorisiert deshalb ein Canonical Domain Model als Kern der weiteren Produktentwicklung.
## Decision
VALEO NeuroERP fuehrt ein verbindliches Canonical Domain Model als Referenz fuer neue Kernlogik, Integrationen, Read-Models und Agent-Vertraege.
Kernaggregate des Modells sind:
- Tenant / Company
- User / Role / Permission
- Business Partner
- Item / Product / Material
- Location / Warehouse / Silo / Bin
- Contract
- Order
- Delivery / Intake / Shipment
- Quality Result / Lab Result
- Invoice / Credit / Settlement
- Payment / Bank Transaction
- Inventory Move / Stock Position
- Journal Entry / Ledger Posting
- Workflow Instance / Approval
- Document / Attachment / Audit Evidence
Agrar- und Landhandel-spezifische Pflichtaggregate sind zusaetzlich:
- Field / Schlag
- Season / Campaign / Harvest Window
- PSM / Duenger / Saatgut Anwendung
- Weighing Ticket
- Commodity Lot / Charge / Partie
Verbindliche Regeln:
1. Neue Kernlogik wird an bestehende Aggregate angebunden oder erweitert diese explizit.
2. Read-Models, APIs und Agent-Contracts werden aus dem Canonical Domain Model abgeleitet, nicht parallel dazu erfunden.
3. UI-spezifische View-Modelle duerfen keine konkurrierende fachliche Wahrheit etablieren.
4. Fuer jedes Kernaggregat ist Domain Ownership explizit festzulegen.
## Consequences
Positiv:
- Weniger doppelte Fachlogik und geringere Integrationskosten
- Klarere Grundlage fuer Workflow, Policy, Audit und Agentenfaehigkeit
- Bessere Datenqualitaet und stabilere Read-Models
Negativ:
- Hoehere Disziplin bei neuen Features und Refactorings
- Zusaetzlicher Modellierungsaufwand vor schneller UI-Implementierung
- Bestehende Schattenmodelle muessen schrittweise abgebaut werden
## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [Top-50 Gap Backlog Landhandel](../roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md)
