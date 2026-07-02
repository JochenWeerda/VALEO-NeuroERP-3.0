---
title: C4 — System Context
type: explanation
audience: [entwickler, integrator, architect]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-02
version: 1.1.0
description: C4 Level 1 — VALEO NeuroERP im Zusammenspiel mit Nutzern und externen Systemen.
---

# C4 — System Context (Level 1)

> **Generierte View** — Quelle: [`docs/architecture/c4/workspace.dsl`] · Renderer: `python scripts/render_c4_views.py` · **Nicht manuell editieren.**

VALEO NeuroERP als **Software-System** in seiner Umgebung. Stand: Dev-Stack + dokumentierte Integrationen.

```mermaid
C4Context
  title System Context — VALEO NeuroERP 3.0

  Person(user, "Sachbearbeiter", "Annahme, Verkauf, Lager, FiBu")
  Person(admin, "Admin / IT", "Mandant, Deploy, Integrationen")
  Person(mobileUser, "Mobile Nutzer", "Waage, Annahme, CRM unterwegs")
  System(valeo, "VALEO NeuroERP", "Multi-Mandanten ERP Landhandel/Agrar")
  System_Ext(l3, "L3 Legacy", "Bestandssystem Waage, Kontrakte, Migration")
  System_Ext(datev, "DATEV", "Steuerberater-Export, FiBu-Übergabe")
  System_Ext(elster, "ELSTER / ERiC", "UStVA, eBilanz")
  System_Ext(fiskaly, "Fiskaly / TSE", "KassenSichV, DSFinV-K")
  System_Ext(superglue, "Superglue / Partner", "REST, EDI, MCP")
  System_Ext(webshop, "Webshop / B2B", "Bestellimport")
  System_Ext(bank, "Bank / FinTS", "Kontoauszug, Zahlungsverkehr")
  System_Ext(waage, "Waagen / Hardware", "Wiegescheine, L3-Anbindung")

  Rel(user, valeo, "Fachmasken, Flow Spine")
  Rel(admin, valeo, "Admin, Monitoring")
  Rel(mobileUser, valeo, "Mobile App, Waage")
  Rel(valeo, l3, "Migration, Waage, Kontrakte")
  Rel(valeo, datev, "Export Buchungsstapel")
  Rel(valeo, elster, "UStVA, eBilanz Submit")
  Rel(valeo, fiskaly, "TSE Signatur POS")
  Rel(valeo, superglue, "Integrationen API/EDI")
  Rel(valeo, webshop, "B2B Orders")
  Rel(valeo, bank, "FinTS / CAMT")
  Rel(valeo, waage, "Wiegeschein-Daten")
```

## Externe Systeme — Detailreferenzen

| System | Dokumentation |
|---|---|
| DATEV | [process-map § FiBu](../process-map.md), [fin-001 Workflow](../../workflows/fin-001-finance-to-reporting.md) |
| ELSTER | [Open Gaps VALEO-FIBU-006](../../project-context/open-gaps-and-known-issues.md) |
| Fiskaly/TSE | [POS Fiscalization](../pos-fiscalization-providers.md) |
| Paperless/DMS | [dms-paperless-integration.md](../dms-paperless-integration.md) |
| Keycloak | [Deployment](../../admin/deployment.md), [ADR-032](../../adr/adr-032-auth-enforcement-router-global-dependency.md) |
| L3 | [Open Gaps L3-*](../../project-context/open-gaps-and-known-issues.md) |
| Superglue | [superglue-integration-bewertung.md](../superglue-integration-bewertung.md) |
| Integration allgemein | [ADR-014](../../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md) |

## Nächste Zoom-Stufe

→ [C4 Container (Level 2)](c4-02-containers.md)
