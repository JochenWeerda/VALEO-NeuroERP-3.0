---
title: "Fütterungsberatung — API-Spezifikation"
type: reference
audience: [architektur, backend, frontend, integration, security, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
sources:
  - app/api/v1/endpoints/rations_lifecycle.py
  - app/api/v1/endpoints/rations_optimization.py
  - app/api/v1/endpoints/rations_integrations.py
  - app/api/v1/endpoints/rations_controlling.py
  - app/api/v1/endpoints/rations_readiness.py
  - docs/specs/feeding/05-datenmodell.md
---

# 06 — API-Spezifikation

## 1. Vertragsstatus

Dieses Kapitel katalogisiert Bestands- und Zielendpunkte. Der ausgelieferte
Maschinenvertrag wird aus FastAPI als OpenAPI generiert. Ein als **GEPLANT**
markierter Pfad darf erst nach Implementierung, Contract-Test und OpenAPI-Drift-
Gate von Clients verwendet werden.

Die Pfade sind unter dem globalen API-v1-Präfix zu verstehen. Deployment und
Gateway dürfen ein zusätzliches Basispräfix setzen.

## 2. Globale Konventionen

| ID | Konvention |
|---|---|
| FEED-API-001 | JSON-Felder sind `snake_case`; Zeitpunkte RFC 3339 UTC, Tage ISO 8601. |
| FEED-API-002 | Tenant kommt aus Auth-Kontext/Gateway und wird serverseitig autorisiert. |
| FEED-API-003 | Schreibende Integrations- und Jobendpunkte unterstützen `Idempotency-Key`. |
| FEED-API-004 | Geld ist `{amount: "12.3400", currency: "EUR"}`, Mengen sind Dezimalstring plus Einheit. |
| FEED-API-005 | Listen sind stabil sortiert und cursorbasiert; `limit` maximal 200. |
| FEED-API-006 | Konkurrenzschutz nutzt `ETag`/`If-Match` oder explizite Version. |
| FEED-API-007 | Statuswechsel sind Commands, keine freien Status-PATCHes. |
| FEED-API-008 | Export, Freigabe, Aktivierung und Grants schreiben Audit/Korrelation. |
| FEED-API-009 | Unbekannte Command-Felder werden abgewiesen. |
| FEED-API-010 | Deprecations werden mindestens einen Releasezug mit `Sunset` angekündigt. |

### 2.1 Standardheader

| Header | Richtung | Pflicht | Bedeutung |
|---|---|---:|---|
| Authorization | Request | ja | Bearer/Session gemäß Plattformvertrag |
| X-Tenant-ID | Request | Gateway | gegen Claims validierter Tenantkontext |
| X-Correlation-ID | beide | nein | übernommen oder erzeugt |
| Idempotency-Key | Request | bei externen Writes | Wiederholungsschutz |
| If-Match | Request | editierbare Ressourcen | Konkurrenzschutz |
| ETag | Response | editierbare Ressourcen | aktuelle Repräsentationsversion |

### 2.2 Standardfehler

Fehler folgen `application/problem+json`:

```json
{
  "type": "https://docs.valeo.local/problems/feed/ration-transition-not-allowed",
  "title": "Statuswechsel nicht zulässig",
  "status": 409,
  "code": "FEED_RATION_TRANSITION_NOT_ALLOWED",
  "detail": "Eine aktive Version kann nicht direkt in review gesetzt werden.",
  "instance": "/api/v1/rations/lifecycle/versions/rv_42/transitions",
  "correlation_id": "corr_01J...",
  "errors": [{"field": "to_status", "reason": "allowed: retired"}]
}
```

| HTTP | Codefamilie | Verwendung |
|---:|---|---|
| 400 | `FEED_INVALID_REQUEST` | unlesbarer Auftrag |
| 401 | `AUTH_REQUIRED` | keine Identität |
| 403 | `FEED_SCOPE_DENIED` | Rolle/Business-Grant fehlt |
| 404 | `FEED_*_NOT_FOUND` | im autorisierten Scope nicht sichtbar |
| 409 | `FEED_*_CONFLICT` | Zustand, ETag, Idempotenz, Eindeutigkeit |
| 422 | `FEED_VALIDATION_FAILED` | feldbezogene Validierung |
| 424 | `FEED_PROVIDER_DEPENDENCY_FAILED` | Providervertrag nicht erfüllbar |
| 429 | `RATE_LIMITED` | mit `Retry-After` |
| 503 | `FEED_SERVICE_NOT_READY` | Regel-/Solver-/Providerdienst nicht bereit |

404 ersetzt 403, wenn bereits die Existenz eines fremden Betriebsobjekts nicht
offengelegt werden darf.

## 3. Autorisierung

| Aktion | farmer | advisor | approver | operator | admin | agent/service |
|---|---:|---:|---:|---:|---:|---:|
| Betriebe lesen | eigene | Grant | Grant | Grant | ✓ | Scope |
| Stammdaten ändern | eigene | `advise` | – | – | ✓ | explizit |
| Ration entwerfen | ✓ | `advise` | – | – | ✓ | Vorschlag |
| Ration freigeben | Sonderrecht | – | `approve` | – | ✓ | nie autonom |
| Plan ausführen | – | – | – | `execute` | ✓ | Geräte-Scope |
| Export auslösen | nach Freigabe | Grant | Grant | Grant | ✓ | Policy |
| Grants verwalten | – | – | – | – | ✓ | nie |

KI-Agenten dürfen Vorschläge und Entwürfe erzeugen. Freigaben, Kostenbindungen,
Grant-Änderungen und Live-Exporte benötigen deterministische Policy und bei Bedarf
Human-in-the-loop.

## 4. Bestandsendpunkte

### 4.1 Lifecycle (`/rations/lifecycle`) — BESTAND

| Methode | Pfad | Zweck | Erfolg |
|---|---|---|---:|
| POST | `/groups` | Fütterungsgruppe anlegen | 201 |
| GET | `/groups` | Gruppen auflisten | 200 |
| GET | `/groups/{group_id}` | typisiertes Gruppendetail | 200 |
| PATCH | `/groups/{group_id}` | optimistisches Update mit Pflichtgrund | 200 |
| GET | `/groups/{group_id}/history` | append-only Parameterhistorie | 200 |
| POST | `/rations` | Ration mit Version 1 anlegen | 201 |
| GET | `/rations` | Rations-Worklist | 200 |
| GET | `/active-rations` | aktive Stallrationen | 200 |
| GET | `/rations/{ration_id}` | Kopf, Versionen, Lifecycle | 200 |
| POST | `/rations/{ration_id}/versions` | unveränderliche Version | 201 |
| GET | `/rations/{ration_id}/versions` | Versionsliste | 200 |
| POST | `/versions/{version_id}/transitions` | Statuswechsel | 200 |
| GET | `/rations/{ration_id}/audit` | Audit-Timeline | 200 |

Ration anlegen:

```json
{
  "group_id": "grp_fresh_01",
  "name": "Frischmelker Herbst",
  "description": "Entwurf nach neuer Maissilageanalyse",
  "source": "manual",
  "comment": "Beratung 15.07.",
  "snapshot": {
    "basis": "as_fed",
    "lines": [
      {"feed_id": "feed_maize_01", "amount_kg_cow_day": "21.500"}
    ],
    "requirement_profile_version": "req_gfe23_004"
  }
}
```

Statuswechsel:

```json
{
  "to_status": "in_review",
  "reason": "Nährstoff- und Preisprüfung abgeschlossen",
  "feeding_start": null
}
```

Die Snapshot-Prüfsumme wird serverseitig berechnet; Versionen werden nicht
gepatcht; Aktivierung setzt Freigabe voraus; pro Gruppe ist eine Version aktiv.
Gruppen-Updates erwarten `expected_revision`; stale Stände liefern 409. Listen
und Details kombinieren Domainrolle mit Ersteller oder aktivem Business-Grant;
verweigerte Einzelobjekte liefern 404 ohne Existenzsignal.

### 4.2 Optimierung und Regeln (`/rations`) — BESTAND

| Methode | Pfad | Zweck |
|---|---|---|
| GET | `/health` | Solver-/Regeldienst-Readiness |
| GET | `/feeds` | berechenbare Futtermittel |
| GET | `/feeds/{feed_id}` | Futtermitteldetail |
| POST | `/optimize/from-profile` | aus Bedarfsprofil optimieren |
| POST | `/optimize/demo` | expliziter Demo-Vertrag |
| POST | `/optimize` | deterministische Optimierung |
| POST | `/requirements/calculate` | Bedarf berechnen |
| POST | `/requirements/maintenance` | Erhaltungsbedarf |
| POST | `/feeds/validate` | Futtermittelwerte validieren |
| POST | `/dlg/strukturindex` | DLG-Strukturindex |
| GET | `/dlg/info` | geladene DLG-Regelversion |
| POST | `/dlg/refresh` | Regelquelle aktualisieren |
| POST | `/compound-feed/upload` | Mischfutterdokument verarbeiten |
| POST | `/feeds/from-grundfutter` | Grundfutterdaten normalisieren |

Optimierungsantworten enthalten `run_id`, Engine-/Regelversion,
Inputchecksumme, Feasibility, Constraints, Warnungen, Zielwerte und Candidate-
Snapshot. Ein fachlich unlösbares Modell antwortet erfolgreich mit
`feasible:false`; ein technischer Ausfall mit 503.

### 4.3 Controlling (`/rations/controlling`) — BESTAND

| Methode | Pfad | Zweck |
|---|---|---|
| POST | `/observations` | tägliche Beobachtung idempotent erfassen |
| GET | `/series` | gruppenbezogene Zeitreihe |

Kompatible Bestandsrouten existieren unter `/rations/feeding-control/evaluate`,
`/logs` und GET `/logs`. Sie werden nach Clientmigration konsolidiert und bis dahin
im OpenAPI-Vertrag als kompatibel/deprecated ausgewiesen.

Aggregation verwendet `cow_count` als Gewicht. Fehlende Tierzahl wird nicht als 1
interpretiert; die Antwort markiert eingeschränkte Datenqualität.

### 4.4 Readiness (`/rations/readiness`) — BESTAND

| Methode | Pfad | Zweck |
|---|---|---|
| POST | `/evaluate` | Entwurf gegen Bestand, Analyse und Preis prüfen |
| GET | `/materials` | Material-Readiness |

Readiness ist Gate, keine Optimierung. Findings nennen Material, Dimension,
Status, Quelle und konkrete Abhilfe.

### 4.5 Integrationen (`/rations/integrations`) — BESTAND

| Methode | Pfad | Zweck |
|---|---|---|
| POST | `/{adapter}/import` | externes Format normalisieren |
| GET | `/imports` | Importjournal |
| POST | `/herd-data/connections` | Verbindung konfigurieren |
| GET | `/herd-data/connections` | Verbindungen listen |
| POST | `/herd-data/connections/{id}/sync` | Delta-Sync |
| POST | `/herd-data/mock-import` | Mockvertrag prüfen |
| GET | `/herd-data/observations` | normalisierte Beobachtungen |

Provider-Namen und Endpoint-Templates sind Konfiguration, kein Versprechen einer
öffentlich verfügbaren DDW-API. Live wird erst nach Vertrag, Consent,
Credentialtest und Provider-Smoke aktiviert.

## 5. Kern-API Zielbild

### 5.1 Betriebe (`/feeding/businesses`) — BESTAND

| Methode | Pfad | Zweck |
|---|---|---|
| POST | `/businesses` | Betrieb anlegen/aktualisieren |
| POST | `/businesses/activate-from-partner` | Partner kontrolliert aktivieren |
| GET | `/businesses` | autorisierte Betriebe listen |
| GET | `/businesses/{business_id}` | Strukturbaum |
| POST | `/businesses/{business_id}/sites` | Standort anlegen/aktualisieren |
| POST | `/businesses/{business_id}/herds` | Herde anlegen/aktualisieren |
| POST | `/businesses/{business_id}/groups` | Gruppe zuordnen |
| POST | `/businesses/backfill-default` | Bestands-Backfill |
| POST | `/businesses/{business_id}/grants` | Zugriff vergeben |
| DELETE | `/businesses/{business_id}/grants` | Zugriff widerrufen |
| GET | `/businesses/{business_id}/grants` | Zugriffe lesen |

Quelle: `app/api/v1/endpoints/feeding_core.py`; Einbindung unter
`/api/v1/agrar/rations-optimization/feeding`. Alle Antworten besitzen explizite
Pydantic-Verträge. `activate-from-partner` erzeugt idempotent eine fachliche
Projektion mit Herkunftsreferenz. Domänenrollen und aktive Betriebs-Grants werden
serverseitig kombiniert; Grant-Widerrufe bleiben auditiert.

### 5.2 Futtermittel (`/feeding`) — GEPLANT

| Methode | Pfad | Zweck |
|---|---|---|
| GET/POST | `/feed-materials` | suchen bzw. anlegen |
| GET/PATCH | `/feed-materials/{id}` | Detail bzw. Stamm ändern |
| POST | `/feed-materials/{id}/archive` | archivieren |
| GET/POST | `/feed-materials/{id}/prices` | Preisverlauf bzw. Version |
| GET | `/nutrients` | Katalog und Einheiten |

### 5.3 Analysen (`/feeding/analyses`) — GEPLANT

| Methode | Pfad | Zweck |
|---|---|---|
| GET/POST | `/analyses` | Worklist bzw. Entwurf |
| POST | `/analyses/imports` | Datei/Laborpayload importieren |
| GET | `/analyses/imports/{job_id}` | Importstatus/Mappingfehler |
| GET/PATCH | `/analyses/{id}` | Detail bzw. Entwurf ändern |
| POST | `/analyses/{id}/validate` | plausibilisieren |
| POST | `/analyses/{id}/release` | freigeben |
| POST | `/analyses/{id}/supersede` | Korrektur beginnen |
| GET | `/analyses/{id}/document` | Originalnachweis |

Freigabe verlangt Einheitenkonvertierung, Pflichtwerte, Provenienz und ein
erfolgreiches Validierungsergebnis.

### 5.4 Bewertungen und Varianten — GEPLANT

| Methode | Pfad | Zweck |
|---|---|---|
| POST | `/rations/{id}/versions/{version_id}/evaluate` | Bewertung starten |
| GET | `/evaluations/{id}` | Kennzahlen/Findings |
| POST | `/rations/{id}/variants` | Varianten erzeugen |
| GET | `/rations/{id}/variants/compare` | 2–5 Versionen vergleichen |
| POST | `/optimization-runs` | asynchron optimieren |
| GET | `/optimization-runs/{id}` | Status/Kandidaten |
| POST | `/optimization-runs/{id}/candidates/{candidate_id}/adopt` | als Version übernehmen |

Fehlende Vergleichswerte sind `null` plus Qualitätsgrund, nicht 0.

### 5.5 Planung und Ausführung — GEPLANT

| Methode | Pfad | Zweck |
|---|---|---|
| GET/POST | `/plans` | Kalender/Worklist bzw. Plan erzeugen |
| GET | `/plans/{id}` | Plan und Batches |
| POST | `/plans/{id}/release` | operativ freigeben |
| POST | `/plans/{id}/export` | Mixerexportjob |
| GET | `/export-jobs/{id}` | Status/Receipt |
| POST/GET | `/plans/{id}/executions` | Ausführung erfassen/lesen |
| POST | `/executions/{id}/complete` | abschließen |

Export referenziert Rationsversion, Planrevision und Einheitenprofil. Derselbe
Idempotenzschlüssel erzeugt keinen zweiten Geräteauftrag.

### 5.6 Beratung und Reports — GEPLANT

| Methode | Pfad | Zweck |
|---|---|---|
| GET/POST | `/consulting/cases` | Fälle suchen/eröffnen |
| GET | `/consulting/cases/{id}` | 360°-Fallakte |
| POST | `/consulting/cases/{id}/decisions` | Entscheidung |
| POST | `/consulting/cases/{id}/tasks` | Aufgabe |
| PATCH | `/consulting/tasks/{id}` | Aufgabe bearbeiten |
| POST | `/consulting/cases/{id}/comments` | Kommentar/Nachtrag |
| POST | `/consulting/cases/{id}/close` | Fall schließen |
| POST | `/reports` | rollenprofilierten Report starten |
| GET | `/reports/{id}` | Jobstatus |
| GET | `/reports/{id}/download` | kurzlebiger Download |
| GET | `/report-profiles` | erlaubte Vorlagen |

Reportjobs speichern Eingabereferenzen und Checksummen. Downloadtokens sind
kurzlebig und principalgebunden; Inhalte hängen von Rolle und Grant ab.

## 6. Kanonische Schemas

Cursorliste:

```json
{
  "items": [{"id": "rat_01", "name": "Frischmelker"}],
  "next_cursor": "eyJ1cGRhdGVkX2F0Ijoi...",
  "has_more": true
}
```

Analysewert:

```json
{
  "nutrient_code": "NEL",
  "value": "6.720",
  "unit": "MJ_PER_KG_DM",
  "basis": "dry_matter",
  "method": "LAB_REPORTED",
  "uncertainty": null,
  "qualifier": "measured"
}
```

Finding:

```json
{
  "rule_code": "GFE23_RDP_BALANCE",
  "severity": "warning",
  "dimension": "protein_supply",
  "actual": "1.8",
  "lower_bound": "0.0",
  "upper_bound": "1.5",
  "unit": "KG_PER_DAY",
  "message_key": "feeding.finding.rdp_above_target",
  "recommendation_key": "feeding.recommendation.review_protein_sources",
  "evidence_refs": ["analysis:ana_17", "ration-version:rv_42"]
}
```

Delta-Sync:

```json
{
  "updated_since": "2026-07-14T00:00:00Z",
  "until": "2026-07-15T00:00:00Z",
  "kinds": ["group_kpi", "animal_health", "group_membership"],
  "dry_run": false
}
```

Providerparameter werden nur im Adapter erzeugt. Löschungen und Gruppenbewegungen
werden als Observations persistiert.

## 7. Asynchrone Jobs und Events

Import, Optimierung, Report und Export folgen einem Muster:

1. `POST` autorisiert/validiert und antwortet 202 mit `job_id`.
2. Status ist `queued`, `running`, `succeeded`, `failed`, `cancelled` oder
   `quarantined`.
3. Ergebnis enthält Checksummen, Zeiten, Warnungen und Referenzen.
4. Webhook/Event ist optional; Polling bleibt unterstützt.
5. Abbruch ist nur vor irreversiblen Provider-Commits möglich.

Versionierte Outbox-Ereignisse umfassen etwa:

- `feeding.ration.version.approved.v1`
- `feeding.ration.version.activated.v1`
- `feeding.analysis.released.v1`
- `feeding.plan.exported.v1`
- `feeding.execution.completed.v1`
- `feeding.controlling.deviation.detected.v1`

Envelope: `event_id`, Typ, Zeitpunkt, Tenant, Betrieb, Aggregate, Korrelation,
Schemaversion und minimierter `data`-Block. Zustellung ist at-least-once;
`event_id` dient der Idempotenz.

## 8. OpenAPI-Governance

- Stabile Operation IDs, z. B. `feeding_create_ration_version`.
- Happy-Path- und Fehlerbeispiele pro Schema.
- Breaking Change nur mit neuer Version oder dokumentierter Migration.
- Generierte OpenAPI wird gegen freigegebenen Snapshot geprüft.
- Commands dokumentieren Scope und Auditwirkung.
- Bestehende `dict`-Responses werden schrittweise typisiert; bis dahin ist die
  Laufzeit-OpenAPI normativ.

## 9. Contract-Tests

| ID | Nachweis |
|---|---|
| FEED-API-T001 | fremder Tenant erhält weder Daten noch Existenzsignal |
| FEED-API-T002 | Advisor sieht nur Betriebe seines Grants |
| FEED-API-T003 | gleicher Idempotency-Key/Body liefert dasselbe Ergebnis |
| FEED-API-T004 | gleicher Key, anderer Body liefert 409 |
| FEED-API-T005 | veraltetes ETag überschreibt nicht |
| FEED-API-T006 | Rationsversion kann nicht mutiert/gelöscht werden |
| FEED-API-T007 | ungültiger Übergang liefert stabilen Problemcode |
| FEED-API-T008 | Freigabe ohne Scope wird auditiert verweigert |
| FEED-API-T009 | Cursor erzeugt keine Duplikate bei Inserts |
| FEED-API-T010 | Dezimalwerte verlieren keine Präzision |
| FEED-API-T011 | unbekannte Einheit wird Fehler/Quarantäne |
| FEED-API-T012 | Delta-Sync dupliziert keine Observation |
| FEED-API-T013 | Providerlöschung wird Tombstone |
| FEED-API-T014 | Reportdownload endet bei Ablauf/Grantentzug |
| FEED-API-T015 | OpenAPI-Beispiele validieren gegen Schema |

## 10. Nichtfunktionale Ziele

| Klasse | Ziel |
|---|---|
| Worklist GET | p95 < 500 ms bei 100.000 Tenantobjekten |
| Detail GET | p95 < 350 ms ohne Provider-Livecall |
| synchroner Command | p95 < 800 ms exklusive Solver/Export |
| Jobannahme | p95 < 300 ms |
| Verfügbarkeit | 99,9 % für Kernlesen/-schreiben im Pilot |
| Rate Limit | principal-, tenant- und providerbezogen |
| Payload | regulär < 1 MiB; Uploadvertrag für Dateien |

## 11. Abnahme

- Jeder produktive Endpoint ist typisiert und in OpenAPI sichtbar.
- Jeder Command besitzt Autorisierung, Validierung, Audit und stabile Fehlercodes.
- Frontend verwendet keine Provider-/DB-Payloads.
- Solver-, Report- und Exportläufe sind reproduzierbare Jobs.
- Bestands- und Zielpfade sind eindeutig gekennzeichnet.
- Contract-, Tenant-, Idempotenz- und OpenAPI-Drifttests sind grün.

## 12. Implementierter Referenzdatenvertrag

| Methode/Pfad | Ergebnis |
|---|---|
| `GET /api/v1/agrar/rations-optimization/reference-data/nutrients` | effektive Naehrstoffdefinitionen mit Basis, Wertebereich, Herkunft und Revision |
| `GET /api/v1/agrar/rations-optimization/reference-data/units` | Einheiten mit Dimension, Basisfaktor und Praezision |
| `POST /api/v1/agrar/rations-optimization/reference-data/convert-basis` | gerundeter und ungerundeter Decimal-Wert samt vollstaendiger FM/TM-Provenienz |

Alle drei Pfade verlangen eine Feed-Read-Rolle und einen Tenantkontext. Ungueltige
TM-Prozente oder Vertragswerte liefern 422; Autorisierungsfehler 403. Die API
deutet einen Wert nie implizit als Menge oder Konzentration.

## 13. Implementierter Feed-Catalog-Vertrag

`/api/v1/agrar/rations-optimization/feed-catalog/feeds` stellt Suche/Anlage,
Detail und optimistisch versioniertes Patch bereit. Unterressourcen
`reference-values`, `products` und `history` liefern die echte ObjectPage.
Flexible Werte werden gegen den Naehrstoffkatalog, kanonische Einheit und
Wertebereich validiert. SKU-Wiederholung ist idempotent und erhoeht die
Produktrevision. Fremde Tenant-IDs liefern 404; fehlende Rollen 403; stale
Revisionen 409.

Die bestehende `/api/v1/futter/einzelfuttermittel`-Kompatibilitaetsstrecke bleibt
verfuegbar, delegiert Mutationen aber an denselben Rollen-/Versionsservice.

## 18. FeedAnalysis-API FEED-CORE-019

Unter `/api/v1/agrar/rations-optimization/feed-analyses` stehen List/Create,
Detail, Werte, Findings, History, Validate, Transition und Document-Reference
typisiert bereit. `import-preview` parst PDF/CSV ohne Persistenz, liefert
SHA-256 sowie Original-/Rechenwerte und kennzeichnet den Zustand ehrlich als
`preview_only`. Importierte Dateien bleiben ohne DMS-ID blockiert.

Release ist Approver-gebunden, optimistisch versioniert und ueber
`actions/release|reject` auch im ActionRuntime-Vertrag `validate`, `dryRun`,
`propose`, `execute` verfuegbar. Cross-Tenant-Zugriffe liefern 404,
Versions-/Lifecyclekonflikte 409 und Rollenfehler 403.
