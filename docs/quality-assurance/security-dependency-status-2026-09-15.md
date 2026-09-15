---
title: Security-Dependency-Status 2026-09-15
type: reference
audience: [entwickler, agent, qa, sicherheit]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-15
---

# Security-Dependency-Status 2026-09-15

Verbindliche Policy: [ADR-071](../adr/adr-071-security-dependency-gate.md).
Keine bekannte, praktisch ausnutzbare kritische Schwachstelle darf unbehandelt
in ein Release. Eine ältere Library ist zulässig, wenn das Risiko analysiert
und beherrscht ist. Dependabot merget nicht; davor sitzt der
Security-Dependency-Gate-Agent.

Dieser Text ist der **Ist-Stand der Wellen und des Inventars**. Die
Gate-Spezifikation und der CI-Nachweis stehen in
[Codex Policy-QA](security-dependency-policy-2026-09-15.md). Cursor ändert
keine Gate-Dateien, keine `dependabot.yml` und keine Entscheidungsliste.

## Betriebsmodell

```
Scanner (Dependabot / pip-audit / npm-audit / Grype / Trivy)
        │  Rohbefunde bleiben sichtbar
        ▼
Security-Dependency-Gate-Agent
        │  versionsscharfe Entscheidung + Evidenz + Wiedervorlage
        │  ändert keine Pins, merget keine PRs
        ▼
Release / Merge
```

| Rolle | Darf | Darf nicht |
|---|---|---|
| Dependabot | Alerts, Graph, optional PRs als Sensor | Auto-Merge, Major-Bumps ohne Nachweis |
| pip-audit / npm-audit in CI | Jeden Rohbefund melden | Ignore-Listen als stille Freigabe |
| Gate-Agent | `not_affected` / `unreachable` mit Evidenz durchlassen | erreichbare Criticals, unbekannte IDs, abgelaufene Reviews |
| Manifest-Slices | Herstellerfix oder reproduzierbaren Pin setzen | Advisory-Fixversion erzwingen, wenn der Resolver bricht |

GitHub beschreibt Auto-Merge für Dependabot-PRs als optionales Actions-Muster
([Doku](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/automate-dependabot-with-actions)).
VALEO aktiviert dieses Muster nicht.

## Geliefert auf `main` (Python-Service-Welle)

| Slice | Inhalt | Nachweis |
|---|---|---|
| SERVICE-CVE-PINS-20260914 | cryptography 50.0.1, aiohttp 3.14.3, langgraph-checkpoint-sqlite 3.1.1; crm-ai transformers/torch | Linux-Image, nicht nur Resolver |
| SERVICE-FASTAPI-STARLETTE-20260914 | FastAPI 0.136.3, Starlette 1.3.1 in 23 Service-Manifesten | Import-Pin-Check |
| SERVICE-REMAINDER-GAPS-20260914 | python-jose entfernt, httpx 0.28.1, Pins, Lifespan, auth-shared Images | siehe unten |
| SERVICE-SECURITY-GATES-20260914 | Audit aller 23 Manifeste, crm-ai Image/HTTP | CI-Lauf [34898484483](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/34898484483) |
| SECURITY-DEPENDENCY-POLICY-20260915 | Gate-Agent, Dependabot als Sensor, Chroma-Bewertung | [Policy-QA](security-dependency-policy-2026-09-15.md) |
| SECURITY-REMAINDER Node | 19 Manifeste; 0 Critical im npm-Audit | 2 High image-size ohne Fix, 1 Moderate stream-json versionsbasiert |
| Auth fail-closed | SILENT-FAILURE-20260914 | bereits vorher geliefert |

**python-jose** war in keinem Dienst importiert. Es war Träger von
`pyasn1 0.4.8` und `ecdsa 0.19.2`. Entfernt in crm-gdpr, crm-marketing,
crm-security, dms-adapter, fibu-core, fibu-gateway und services/ai.
pip-audit danach ohne Befund für die sechs CRM-/Finance-/DMS-Dienste
(crm-security im Linux-Container; Windows scheitert an vorbestehendem
`uvloop==0.19.0`).

**click** in `services/ai`: 8.2.1 → 8.3.3 (Fixversion).

**httpx** überall 0.28.1. Offene pydantic-/uvicorn-Untergrenzen geschlossen.
uvicorn 0.23.2 → 0.24.0 wo nötig. Höhere Exact-Pins (0.27.1, 0.30.1, 0.32.0)
nicht gesenkt.

**on_event** → Lifespan in `services/crm/main.py` und
`services/dms-adapter/app/main.py`.

**auth-shared:** inventory und workflow bauen aus dem Wurzelkontext.
`docker-compose.yml` für `inventory-service` entsprechend.

Nach `a9b720a75`: Dependabot-Graph **6 offene Meldungen** (1 critical,
4 high, 1 moderate) statt 39 bzw. 51. Der Graph läuft asynchron nach;
die Zahl ist ein Sensorstand, kein Release-Zeugnis.

## Bewusst nicht automatisch gehoben

### chromadb 0.5.23 in `services/ai`

Kein Herstellerfix (last affected 1.5.9, Patch-PR offen). Ein Sprung auf
1.5.9 behielte denselben Befund und bräche die 0.5-API. Der **Scanner**
bleibt für `services/ai` rot. Das ist Absicht, kein Ignore. Der
**Policy-Gate** bewertet die drei CVEs für genau Version 0.5.23 bis
**2026-10-15** als `not_affected` / `unreachable`.

Die drei Advisories betreffen den **Chroma-Server** (HTTP-API,
`trust_remote_code`, Server-AuthZ, SimpleRBAC-Mandant). VALEO betreibt
ausschließlich den eingebetteten Client:

- `services/ai/app/services/vector_store.py` → `chromadb.PersistentClient`
- `app/infrastructure/rag/vector_store.py` → `chromadb.Client(Settings(persist_directory=...))`
- kein Compose-/K8s-Chroma-Server
- Vertragstest: `tests/test_chromadb_embedded_only_contract.py`
- Entscheidungsliste: `config/security/dependency-decisions.json`
- ältere Triage: `config/security/triage-exceptions.json` (Wiedervorlage 2026-12-11)

Eine Bewertung ist kein Exploit-Nachweis. Ändert sich der Aufruf auf
`HttpClient` / `AsyncHttpClient` / `chroma_server_*` oder die Fingerprints,
fällt die Bewertung und das Release bleibt zu Recht rot.

### transformers 4.46.3 in `services/ai`

Explizit gepinnt. chromadb 0.5.23 verlangt `tokenizers<=0.20.3`;
transformers ab 4.47 zieht `tokenizers>=0.22`. 4.57.6 macht das Manifest
unauflösbar. Die Advisories von 4.46.3 bleiben sichtbar. Der CI-Audit auf `a9b720a75` enthält **26 unterschiedliche Transformers-Befunde**.
Codex hat sie bewusst **nicht** freigegeben: fehlender Import im Anwendungscode
ist kein Nachweis aller transitiven Modellladepfade. Sie bleiben blockierend.
Kein Major-Bump „weil Dependabot es so will“.

### image-size (Node)

Kein Herstellerfix. Bereits dokumentierte Ausnahme in der Node-Restwelle.
Rohbefund bleibt im Audit sichtbar (2 High).

### stream-json 1.9.1 (Node)

Lokaler Tiefenbegrenzungs-Backport; der versionsbasierte Moderate-Treffer
bleibt. Kein 3.x-Sprung, weil StreamArray-Verbraucher (dockerode/bunyamin)
brechen.

## CI-Stand Service-Security

[Run 34898484483](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/34898484483)
auf Commit `a9b720a75` (Nachweis später mit Finance-/crm-ai-Folgeläufen
bestätigt):

- **22 / 23** Service-Audits grün
- nur `services/ai` rot (chromadb, transformers; click/jose geschlossen)
- crm-ai Image-/HTTP-Job [104158391173](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/34898484483/job/104158391173) grün

Der zusammenfassende Scanner-Workflow ist deshalb rot. Das ist der
Rohbefund-Stand, nicht die Behauptung „das ERP ist unsicher zum Release“,
und auch nicht die Behauptung „alle Advisories sind beherrscht“.

## Gate-Agent geliefert (Codex)

Slice `SECURITY-DEPENDENCY-POLICY-20260915` ist **abgeschlossen**. Nachweis:
[Policy-QA](security-dependency-policy-2026-09-15.md).

- Dependabot: Sensor und Security-PRs; `open-pull-requests-limit: 0` für
  pip/npm (keine Routine-Version-PRs); kein Auto-Merge-Workflow.
- Policy-Prüfer: nur `not_affected` + `unreachable` mit Owner, Quellen,
  Fingerprints, max. 90 Tage Wiedervorlage. Erreichbare Befunde und
  `accepted_risk` werden nicht akzeptiert.
- Reale CI-Evidence Run 34898484483: **3 Chroma-Befunde** `not_affected`,
  **26 Transformers-Befunde** blockierend; Release-Entscheidung **false**.
- `release-gates.yml` verlangt denselben Gate für die Release-SHA.
- 18 Regressionen grün (9 Policy + 9 Audit-Runner).

Cursor fasst diesen Dateibesitz nicht an. Nächster fachlicher Schritt für
`services/ai` ist die **Transformers-Pfadanalyse**, kein Versionsbump.

## Technische Restpunkte außerhalb der Policy

Diese Punkte sind Betriebs-/Produktarbeit, keine Advisory-Freigabe:

- `services/crm/Dockerfile` mischt Wurzelpfade (`packages/auth-shared`) mit
  Dienstpfaden (`requirements.txt`, `app/`). Compose mit `context: .` ist
  dadurch inkonsistent.
- `services/workflow` und `fibu-gateway` haben keinen vollständigen
  Compose-Build; fibu-gateway hat kein Dockerfile.
- `scripts/implement_all.py` listet noch python-jose (Generator, kein Dienst).
- uvicorn bleibt dienstweise unterschiedlich gepinnt (bewusste Nicht-Senkung).

## Agenten-Grenze

| Agent | Besitz |
|---|---|
| Cursor | Service-Manifest-Pins, FastAPI/Starlette, Restlücken, dieser Ist-Stand, ADR-071 |
| Codex | Service-Security-Workflow, Node-Welle, Policy-Gate (geliefert), Dependabot-Konfiguration |
| Claude | Design/UI; bestehende Chroma-Triage in `triage-exceptions.json` |

Kein Agent hebt funktionierende Komponenten auf neue Majors, nur weil ein
Scanner eine höhere Version nennt.
