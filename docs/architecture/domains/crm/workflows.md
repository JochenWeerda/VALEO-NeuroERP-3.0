---
title: CRM — Workflows
type: explanation
audience: [entwickler, fachlich]
owner: domain/crm
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# CRM — Workflows

## Order-to-Cash (O2C) — CRM-Anteil

1. **Lead / Prospect** → Geschäftspartner anlegen
2. **Angebot / Auftrag** → Verkaufsbeleg (siehe Verkauf)
3. **Lieferung / Rechnung** → Übergabe an Logistik/FiBu

→ [Process Map § Vertrieb](../../process-map.md)
→ [Sequenz O2C/FiBu](../../views/sequences/seq-o2c-fibu.md)

## Bedarfsdeckung (Durchdringungs-CRM)

Service: `bedarfsdeckung_service` — „Die Lücke ist das Vertriebsobjekt".

## Consent & Marketing

- `consent_engine` — Einwilligungen (NC-004)
- `competitor_monitor` — Wettbewerbspreise

## Process Kernel

Lieferstatus pro Capability: [process-kernel/STATUS.md](../../process-kernel/STATUS.md) — CRM/Vertrieb-Slices.
