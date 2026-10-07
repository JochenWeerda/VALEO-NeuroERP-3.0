---
title: Gap-Hub VALEO NeuroERP
type: reference
audience: [produkt, management, agent, entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-10-07
version: 1.0.0
description: Kanonischer Einstieg fuer Capability-/Usability-Gaps — ersetzt die 2025er Archiv-Analysen als Source of Truth.
---

# Gap-Hub — aktueller Stand

**Dieses Verzeichnis ist die Source of Truth für Gap-Übersichten ab 2026-10-07.**

Die Analysen unter [`docs/_internal/archive/gap/`](../_internal/archive/gap/) (u. a. „~38 % Maturity“, Stand 2025-01) sind **historisch**. Sie dürfen nicht mehr für Priorisierung, Roadmaps oder Management-Reports zitiert werden, ohne gegen diesen Hub und den Code validiert zu werden.

## Aktuelle Artefakte

| Dokument | Inhalt |
|---|---|
| [executive-summary-20261007.md](executive-summary-20261007.md) | Management-Übersicht Domänenreife + Top-Gaps |
| [domain-maturity-matrix-20261007.csv](domain-maturity-matrix-20261007.csv) | Domänen × Reife × Evidenz |
| [usability-systemaudit-matrix-20261007.csv](usability-systemaudit-matrix-20261007.csv) | Usability-Cluster-Scores |
| [usability-systemaudit-findings-20261007.csv](usability-systemaudit-findings-20261007.csv) | Usability-/Future-Befunde |

## Lebende Tracker (weiterführend)

| Tracker | Rolle |
|---|---|
| [open-gaps-and-known-issues.md](../project-context/open-gaps-and-known-issues.md) | Operative Detail-Gaps / Handshakes |
| [usability-erp-vergleichsdossier-20261007.md](../quality-assurance/usability-erp-vergleichsdossier-20261007.md) | Usability + Tier-1 + Light + AI-Peers |
| [l3-full-mask-functional-gap-inventory.md](../design/l3-full-mask-functional-gap-inventory.md) | L3-Gewohnheits-/Funktionsparität |
| [domain-depth-plan-2026-05-17.md](../project-context/domain-depth-plan-2026-05-17.md) | Historischer Soll-Katalog Mai/Juni 2026 (Closure-Welle) |
| [active-workboard.md](../agent-ops/active-workboard.md) | Laufende Slices |

## Bewertungsmaßstab (verbindlich)

1. **Primär:** Landhandel-/Genossenschafts-SoR (zvoove/L3-Gewohnheit, DE/EU).
2. **Sekundär:** Tier-1 UX-Muster (Fiori/Dynamics/Odoo) wo relevant.
3. **Zukunft:** Light + ERPClaw/OpenLedger/TaxHacker/OpenAccountants — eigene Spalte, keine Vermischung mit Ops-Reife.
4. **Keine** Fortschreibung der Archiv-Prozentzahl ~38 % gegen SAP-100 %.
