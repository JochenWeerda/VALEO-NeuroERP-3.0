---
title: In-App-Hilfe (Route → Dokumentation)
description: Mapping von Frontend-Routen auf Dokumentationsseiten für die In-App-Hilfe.
type: reference
audience: [entwickler, endnutzer]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.2.0
---

# In-App-Hilfe — Route → Dokumentation

> Slice: **DOC-USER-MANUAL-004** / **DOC-INAPP-HELP-002**
> Mapping: [`src/lib/docs-help.ts`](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/blob/main/packages/frontend-web/src/lib/docs-help.ts)

## Konzept

Der Hook `useInAppHelp()` liest die aktuelle Route, sucht den längsten Präfix-Treffer
in `ROUTE_HELP_MAP` und öffnet die passende MkDocs-Seite im Benutzerhandbuch.

**Abdeckung:** 895 App-Routen → 176 Präfix-Einträge.

## Beispiel-Routen (Auszug)

| Route-Präfix | Hilfe-Seite | Label |
|---|---|---|
| `(start)` | [Dashboard und Workflows](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/) | Dashboard und Workflows |
| `admin-suite` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/compliance` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/connectors` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/devices` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/diagnostics` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/ki-anbieter` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/migration` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/operations` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/pos-fiscalization` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/security` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/setup` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin-suite/system-status` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/agenten-integration` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/ai-approvals` | [AI-Freigaben](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/agent-docs/guardrails/) | AI-Freigaben |
| `admin/audit-log` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/benutzer` | [Benutzer & Rollen](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/rbac-und-rollen/) | Benutzer & Rollen |
| `admin/benutzer-liste` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/benutzer/:id` | [Benutzer & Rollen](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/rbac-und-rollen/) | Benutzer & Rollen |
| `admin/benutzer/neu` | [Benutzer & Rollen](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/rbac-und-rollen/) | Benutzer & Rollen |
| `admin/command-monitor` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/compliance` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/compliance-dashboard` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/control-center` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/control-center/agent-ops` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/control-center/superglue` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/data-quality` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/externe-gates` | [Externe Gate-Dashboards](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/monitoring-und-slo/) | Externe Gate-Dashboards |
| `admin/gap-pipeline` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/GapPipelineConsole` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/integrationen-quarantaene` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/monitoring/alerts` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/monitoring/regeln` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/nummernkreise` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/qualitaets-cockpit` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/report-berechtigungen` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/rolle/:id` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/rolle/neu` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/rollen-verwaltung` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/setup` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/setup/dms-integration` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/terminologie` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/voice-channel` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/webhooks` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/webshop` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `agrar` | [Agrar-Warenwirtschaft](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/) | Agrar-Warenwirtschaft |
| `agrar/aussaat` | [Agrar-Warenwirtschaft](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/) | Agrar-Warenwirtschaft |
| `agrar/aussaat/:id` | [Agrar-Warenwirtschaft](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/) | Agrar-Warenwirtschaft |
| `agrar/aussaat/liste` | [Agrar-Warenwirtschaft](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/) | Agrar-Warenwirtschaft |
| `agrar/aussaat/neu` | [Agrar-Warenwirtschaft](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/) | Agrar-Warenwirtschaft |

## Erweiterung

1. `scripts/generate_benutzerhandbuch_full.py` — Kapitel/Präfixe pflegen
2. `python scripts/generate_inapp_help_map.py`
3. `src/lib/docs-help.ts` committen

*Stand: 2026-06-26 · 895 Routen gemappt · Slice: DOC-USER-MANUAL-004*