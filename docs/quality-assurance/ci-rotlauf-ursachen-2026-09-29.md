---
title: CI-Rotlauf — Ursachen und was davon behoben ist
type: reference
audience: [entwickler, agent, betrieb]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-29
version: 1.0.0
description: Warum viele GitHub-Läufe rot waren, welche vier Ursachen dahinterstecken und was offen bleibt.
---

# CI-Rotlauf — Ursachen

Am 29.09. waren zweistellig viele Workflows rot. Dahinter standen **vier**
Ursachen, nicht vierzehn.

## 1. Eine Migration, die nur auf gewachsenen Datenbanken lief

Die Kontensaat (`erp_kontenrahmen_skr03_20260927`) schrieb unter
`tenant_id = 'system'`. `chart_of_accounts.tenant_id` zeigt per Fremdschlüssel
auf `tenants` — die Zeile `system` gibt es in einer gewachsenen Datenbank
längst, in einer frischen nicht.

Damit brach `alembic upgrade head`, und zwar **an dieser Stelle für alles
danach**. Gerissen hat das vier Workflows gleichzeitig:

- Pytest (PostgreSQL / require_db)
- OpenAPI Drift
- Runtime API Sweep
- Compliance Checks

Behoben: Die Migration legt den Mandanten selbst an (`ON CONFLICT DO NOTHING`).

**Regel daraus:** Eine Migration gegen die eigene gewachsene Datenbank zu
prüfen sagt nichts darüber, ob sie auf einer leeren läuft.

```bash
createdb valeo_probe
DATABASE_URL="postgresql://…/valeo_probe" python -m alembic upgrade head
dropdb valeo_probe
```

## 2. Liegengebliebene Generatorläufe

Docs Build war seit dem **17. September** rot, nacheinander aus zwei Gründen:

- ADR-072 wurde angelegt, ohne `scripts/generate_adr_nav.py` zu laufen.
- Danach waren die Code-Inventare veraltet
  (`scripts/generate_code_inventories.py`).

Beide Meldungen nennen den Befehl wörtlich. Behoben.

## 3. Zwei Paketverwaltungen in einem Arbeitsbereich

`Universal Mask Platform CI` installierte mit `npm install`, während
`packages/*` laut `pnpm-workspace.yaml` zum pnpm-Arbeitsbereich gehört und
jeder andere Workflow `pnpm install --frozen-lockfile` benutzt.

npm zerbrach an `packages/frontend-web/package-lock.json`: Die Sperrdatei
stammt vom 10. Februar, die `package.json` wurde am 14. September von der
Security-Welle angehoben. Fehlerbild:
`Cannot read properties of null (reading 'edgesOut')`.

Eine neu erzeugte npm-Sperrdatei wäre **keine** Lösung, sondern eine zweite
Wahrheit: Der Versuch ergab 170 statt 772 Pakete, weil npm den pnpm-Baum nur
zum Teil lesen kann. Stattdessen benutzen beide betroffenen Jobs jetzt pnpm.

Der BFF-Job bleibt bewusst bei npm — er läuft grün, und
`packages/bff/bff-web` hat eine eigene, passende Sperrdatei.

## 4. Workflows, die auf einen geschützten Branch schreiben wollen

Drei Läufe scheitern an derselben Repository-Einstellung, nicht an Code:

- OpenAPI Drift
- Doc Drift Report
- AI Engineering Metrics (Nightly)

Sie erzeugen Artefakte und wollen sie nach `main` zurückschreiben:
`GH006: Protected branch update failed for refs/heads/main`. Solange der
Branchschutz steht, werden sie bei **jedem** Lauf rot.

Drei Wege, und das ist eine Entscheidung des Hauses:

1. Der Actions-Bot darf an den geschützten Branch.
2. Die Workflows öffnen einen Pull Request.
3. Sie prüfen nur und schlagen bei Drift fehl, ohne zu schreiben.

Der dritte Weg wäre der konsequente: Ein Workflow, der selbsttätig auf `main`
schreibt, umgeht genau den Schutz, den der Branch haben soll.

## Offen, gehört anderen

- **E2E Full UAT** — die CRM-360-Aktivitätsmaske: `#btn-trigger-history-form`
  war sichtbar, der Klickpunkt lag aber unter dem Seitencontainer
  (`intercepts pointer events`). Auf 1280×720 fraßen Kopf und Aktionsleiste
  die Höhe, das Historienpanel rutschte aus dem Outlet. Behoben: das Cockpit
  bleibt in der vorhandenen Höhe, die Kopfzeile scrollt ab 40 %, das
  Historienpanel behält mindestens 11 rem, die Registerleiste darin bricht
  nicht um. Am 29.09. im Browser geprüft: Erfassen- und Speichern-Knopf
  treffen ihren eigenen Klickpunkt. Der nächste nächtliche Lauf ist der
  Nachweis auf GitHub.
- **Security Scan** (Grype) und **Service Security**
  (`services/ai/requirements.txt`) — Abhängigkeitsbefunde, nicht untersucht.
- **Deploy Production** (10.06.), **Deploy Staging** (06.07.),
  **Rotate Secrets** (01.09.), **Procurement Domain CI/CD** (14.09.) — lange
  rot, vermutlich stillgelegt.
