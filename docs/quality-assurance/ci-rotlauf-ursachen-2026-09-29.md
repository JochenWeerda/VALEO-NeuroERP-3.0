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

## 5. Eine gewachsene Datenbank als Prüfstand

Die vierundzwanzig Fehlschläge in `Pytest` und `CI/CD Pipeline` hatten **eine**
Wurzel: Getestet wurde gegen eine über Monate gewachsene
Entwicklungsdatenbank. Die unterscheidet sich in beide Richtungen von einer
frischen:

- **Sie hat Bedingungen verloren.** Fremdschlüssel
  (`delivery_notes.customer_id` → `customers`, `delivery_note_positions.artikel_id`
  → `articles`), Prüfbedingungen (`ck_delivery_notes_status`) und NOT-NULL-Regeln
  sind dort nicht mehr da. Tests, die Kunden und Artikel nie anlegten, liefen
  deshalb grün.
- **Sie hat Spalten und Tabellen gewonnen, die keine Migration anlegt.**
  `sales_offers.customer_name`, `sales_offers.is_pauschale`,
  `sales_orders.is_pauschale`, `sales_order_items.ek_price` und `.unit` gab es
  nur lokal. Auf einer frischen Installation scheiterte schon das Anlegen
  eines Angebots.

Behoben:

- `lieferschein_status_bedingung_20260929` — die Statusbedingung kennt jetzt
  die neun Zustände, die der Code schreibt (vorher fünf). Buchen, Versenden,
  Sammelrechnung und Storno liefen auf einer frischen Datenbank in einen 500er.
  Der dabei sichtbare Widerspruch (drei Schreibweisen in einer Spalte) ist in
  `docs/project-context/lieferschein-statuswerte-2026-09-29.md` festgehalten.
- `verkauf_fehlende_spalten_20260929` — die fünf Spalten, `valid_until` wird
  optional, und den Attestierenden `system` gibt es als Benutzer. Ohne ihn
  scheiterte jeder Nachdruck eines gebuchten Lieferscheins am Fremdschlüssel
  `attestations.created_by → users`.
- Die Testfixtures legen Kunden, Artikel und Pflichtfelder wirklich an und
  räumen in der Reihenfolge ab, die die Fremdschlüssel verlangen.
- `scripts/check_table_references.py` — die Ratsche stand auf 26/19, gemessen
  an der gewachsenen Datenbank. Auf einer frischen sind es 28/25. Dieselbe
  Schuld, richtig gemessen.

**Regel daraus, zum zweiten Mal an einem Tag:** Eine gewachsene
Entwicklungsdatenbank ist kein Prüfstand.

```bash
createdb valeo_probe
DATABASE_URL="postgresql://…/valeo_probe" python -m alembic upgrade head
DATABASE_URL="postgresql://…/valeo_probe" pytest tests/…
dropdb valeo_probe
```

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
  (`services/ai/requirements.txt`) — noch offen: fünf CPython-Befunde
  (vier davon in `config/security/cpython-3.13.15/` zurückportiert, für
  `CVE-2026-82049` fehlt der Backport), drei Trivy-Funde in
  `services/ai/requirements.txt` und eine SonarCloud-Meldung in
  `services/crm-ai/main.py`.

## Code-Scanning-Meldungen: 2515 → 12

Die 2503 geschlossenen Meldungen stammten aus Juni und Juli und zeigten auf
einen Image-Stand, den es nicht mehr gibt (`valeo-backend:59dcd8b6…`, mit
`gcc`/`binutils` in der Laufzeit). `Dockerfile.backend` ist inzwischen
mehrstufig mit schlanker Laufzeit; die aktuellen Läufe melden fünf
Grype-Befunde und null im Trivy-Backend. GitHub schließt solche Meldungen
nicht von selbst — jede trägt jetzt diese Begründung.

Die **zwölf** verbliebenen sind aktuell und echt (siehe oben).

Bei den Dependabot-Meldungen bleiben drei zu **chromadb 0.5.23** offen: Es
gibt keinen veröffentlichten Patch. Die vierte (`stream-json`) ist mit
Begründung geschlossen — `config/security/npm-patches/stream-json@1.9.1.patch`
zieht die Tiefenschranke aus Upstream 3.5.0 in die 1.x-Fassung, weil 3.5.0
die CommonJS-API bricht, die Detox benutzt
(`node --test scripts/verify_node_dependency_security.cjs`, 8/8).
- **Deploy Production** (10.06.), **Deploy Staging** (06.07.),
  **Rotate Secrets** (01.09.), **Procurement Domain CI/CD** (14.09.) — lange
  rot, vermutlich stillgelegt.
