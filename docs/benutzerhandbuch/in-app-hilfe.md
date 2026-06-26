---
title: In-App-Hilfe (Route → Dokumentation)
description: Mapping von Frontend-Routen auf Dokumentationsseiten für die In-App-Hilfe.
type: reference
audience: [entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# In-App-Hilfe — Route → Dokumentation

> Slice: **DOC-INAPP-HELP-002**
> Mapping: [`src/lib/docs-help.ts`](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/blob/main/packages/frontend-web/src/lib/docs-help.ts)

## Konzept

Der Hook `useInAppHelp()` liest die aktuelle Route, sucht den längsten Präfix-Treffer
in `ROUTE_HELP_MAP` und öffnet die passende MkDocs-Seite.

```ts
import { findHelpEntry } from '@/lib/docs-help';

// In einer Komponente:
const entry = findHelpEntry('verkauf/auftrag/123');
// → { label: 'Verkaufsauftrag', url: 'https://.../benutzerhandbuch/verkauf/' }
```

## Gemappte Routen

| Route-Präfix | Hilfe-Seite | Label |
|---|---|---|
| `admin/agenten-integration` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/ai-approvals` | [AI-Freigaben](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/agent-docs/guardrails/) | AI-Freigaben |
| `admin/externe-gates` | [Externe Gate-Dashboards](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/monitoring-und-slo/) | Externe Gate-Dashboards |
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
| `admin/gap-pipeline` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/GapPipelineConsole` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/integrationen-quarantaene` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/monitoring/alerts` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/monitoring/regeln` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
| `admin/nummernkreise` | [Administration](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/) | Administration |
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
| `agrar` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/aussaat` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/aussaat/:id` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/aussaat/liste` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/aussaat/neu` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/biostimulanzien` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/biostimulanzien-liste` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/biostimulanzien-stamm` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/biostimulanzien-stamm/:id` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/bodenprobe/:id` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/bodenprobe/neu` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/bodenproben` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/bodenproben/liste` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/duenger` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/duenger-liste` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/duenger-stamm` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/duenger-stamm/:id` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/duenger/bedarfsrechner` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |
| `agrar/duenger/liste` | [Agrar-Modul](https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/) | Agrar-Modul |

## Erweiterung

1. `scripts/generate_inapp_help_map.py` — `HELP_MAP` erweitern
2. Script neu ausführen: `python scripts/generate_inapp_help_map.py`
3. `src/lib/docs-help.ts` committen

*Stand: 2026-06-26 · 50 Routen gemappt · Slice: DOC-INAPP-HELP-002*