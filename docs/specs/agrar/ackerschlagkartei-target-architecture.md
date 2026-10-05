# Ackerschlagkartei — Zielarchitektur

Stand: 2026-07-16

## Leitentscheidung

Kein Parallelprodukt: die Ackerschlagkartei bleibt im Agrar-Domänenpaket von VALEO NeuroERP
(`domain_agrar`, Portal + ERP-Shell, bestehende Mask-/Terra-Tokens).

## Schichten

```
Portal/ERP UI (React)
    ↓ TanStack Query
FastAPI portal_feldbuch / agrar_feldbuch
    ↓
Domain helpers app/agrar/feldbuch/*
    ↓
SQLAlchemy FeldbuchSchlag / FeldbuchMassnahme (+ künftige Aggregate)
```

## Inkrement-1 (umgesetzt)

- `wirtschaftsjahr` am Schlag
- Arbeitskontext (stateless, aus Query/Body)
- Schlaginfo-Aggregation (read model)
- Jahreswechsel (Stammdatenkopie, idempotent)
- Sammeldüngung (flächenproportionale Maßnahmen)

## Ziel-Aggregate (später, Kap. 41)

CropYear, CultivationPlan, FieldOperation-Subtypen, WorkOrder, ComplianceRule,
SoilSample-Historie, GeometryVersion — schrittweise hinter denselben Portal-Verträgen,
ohne Breaking Changes an bestehenden DüV-Endpoints.

## Nicht-Ziele dieser Architektur

- eigene Offline-App-Runtime (ASK-MOB)
- amtliche ANDI-Antragstellung
- NÄON/ENNI ohne Partnervertrag
