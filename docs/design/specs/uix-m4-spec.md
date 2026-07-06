---
title: UIX-M4 Spezifikation — „Das ERP baut sich selbst" (UIX-090/091/092)
type: reference
audience: [agent, entwickler, qa]
owner: Claude
status: aktiv
last_reviewed: 2026-07-07
version: 1.0.0
description: Implementierungsreife Specs für ScreenDefinition-Studio, Prozessband und Ambient-Agent-Worklists.
---

# UIX-M4 Spezifikation — „Das ERP baut sich selbst"

Voraussetzungen: M1–M3 (insbesondere 071-Overlays als Vorarbeit für Studio-
Draft-Mechanik, 063-Worklist-Muster für 092). Reihenfolge: **091 → 092 → 090**
(091 ist klein und entsperrt Chain-Kontext für 092; 090 ist der größte Slice).

---

## UIX-091 — Prozessband (P9) flächendeckend

### Ziel / Nicht-Ziele
Jede Beleg-/Objektmaske zeigt ihre Prozesskette als navigierbares Band.
**Nicht-Ziele:** Workflow-Engine-Änderungen, neue Prozessdefinitionen
(nur Sichtbarmachung), Instanz-Fortschritt einzelner Belege (v2).

### Ketten-Konfiguration

```yaml
# config/process_chains.yaml — deklarativ, tenant-überschreibbar
chains:
  k1_ernte:
    label: "Ernte"
    steps:
      - { key: kontrakt,     label: "Kontrakt",     screenId: "agrar/kontrakt" }
      - { key: avis,         label: "Avis",          screenId: "agrar/anlieferavis" }
      - { key: wiegung,      label: "Wiegung",       screenId: "agrar/annahme-wiegung" }
      - { key: qualitaet,    label: "Qualität",      screenId: "agrar/qualitaet" }
      - { key: einlagerung,  label: "Einlagerung",   screenId: "lager/silo-zelle" }
      - { key: abrechnung,   label: "Abrechnung",    screenId: "agrar/sammelabrechnung" }
  k2_verkauf: { … }   # Angebot→Auftrag→Lieferschein→Wiegung→Rechnung→OP→Zahlung
  k3_einkauf: { … }
  k4_crm:     { … }
```

### SD-Contract & Compiler

```python
# ScreenDefinition — additiv
"processChain": { "chainId": "k1_ernte", "stepKey": "wiegung" }
```

Compiler lädt `process_chains.yaml` (Backend liefert sie über den bestehenden
SD-Endpoint mit aus — ein Katalog-Feld `processChains` im Registry-Response,
kein Extra-Roundtrip) und leitet ab:

```ts
// RenderShellPlan additiv
processRibbon?: { chainId: string; steps: { key: string; label: string
  routePath: string; state: 'done'|'current'|'upcoming' }[] }
// v1: state nur current (aus stepKey) vs. neutral; done/upcoming folgt mit
// Instanz-Kontext in v2 — Feld ist dafür vorbereitet.
```

`ProcessRibbonRenderer`: Chips unter dem ObjectHeader (W-02), aktueller
Schritt gold, Klick navigiert (mit Objektkontext, sofern die Ziel-Maske über
`entity_id`-Route erreichbar und eine Verknüpfung ableitbar ist — sonst
Liste). Tastatur: Band ist eine `nav` mit Links.

### Gate (advisory v1, mandatory ab M4-Abschluss)
Readiness-Warnung: SD mit `domain ∈ {sales, einkauf, finance, agrar}` und
`mode ∈ {detail, transaction}` ohne `processChain` → Warning
`missing_process_chain`. Nach Rollout auf alle Beleg-SDs wird die Warnung
für diese Domänen auf Error angehoben (separater Commit, im Slice dokumentiert).

### Tests
Vitest: Compiler (chainId/stepKey → Ribbon, unbekannte chainId → kein Ribbon +
Warnung), Renderer (current-Markierung, Navigation). pytest: YAML-Schema-
Validierung (`scripts/check_process_chains.py` in quality-gate: jede
screenId existiert in der Registry), Readiness-Warnfall.

---

## UIX-092 — Ambient-Agent-Worklists

### Ziel / Nicht-Ziele
Rahmenwerk für beobachtende Agenten, die Read Models überwachen und
erklärte Worklist-Einträge erzeugen. **Nicht-Ziele:** autonome Mutationen
(Agenten buchen nie), LLM-Pflicht (v1-Agenten sind deterministische Regeln),
Benachrichtigungs-Spam (Dedupe-Pflicht).

### Framework

```python
# app/services/ambient_agents/base.py
@dataclass
class WorklistProposal:
    agent_id: str
    tenant_id: str
    dedupe_key: str            # idempotent je Sachverhalt
    title: str
    reason: str                # Pflicht: warum meldet der Agent das?
    source_ref: str            # Beleg-/Objekt-Verweis (object_type:object_id)
    confidence: float          # 1.0 bei deterministischen Regeln
    severity: str              # info|warning|critical
    target_screen_id: str
    target_route: str
    payload: dict

class AmbientAgent(Protocol):
    agent_id: str
    schedule: str              # 'nightly' | 'hourly'
    def watch(self, db: Session, tenant_id: str) -> list[WorklistProposal]: ...
```

Registry `app/services/ambient_agents/registry.py` + Scheduler-Anbindung
(bestehende Nightly-/Interval-Infrastruktur). **Kill-Switch:** je Agent und
Tenant über TENANT_MODULE_FLAGS-Muster (`AMBIENT_AGENTS_DISABLED`-Liste);
Registry prüft vor jedem Lauf.

### Persistenz

```sql
CREATE TABLE domain_shared.ambient_worklist_items (
  id           uuid PRIMARY KEY,
  tenant_id    varchar NOT NULL REFERENCES domain_shared.tenants(id),
  agent_id     varchar(64) NOT NULL,
  dedupe_key   varchar(160) NOT NULL,
  title        varchar(200) NOT NULL,
  reason       text NOT NULL,
  source_ref   varchar(160) NOT NULL,
  confidence   numeric(3,2) NOT NULL,
  severity     varchar(16) NOT NULL,
  target_screen_id varchar(96), target_route varchar(200),
  payload      jsonb NOT NULL DEFAULT '{}',
  status       varchar(16) NOT NULL DEFAULT 'open',   -- open|done|dismissed
  resolved_by  varchar(64), resolved_at timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, agent_id, dedupe_key)
);
```

Lauf-Semantik: upsert je dedupe_key; Sachverhalt entfallen → `open`-Items
des Agents außerhalb der aktuellen Proposal-Menge werden `done`
(auto-resolved, `resolved_by='agent'`). `dismissed` bleibt (Nutzer-Wille).

### Agenten-Katalog v1 (deterministisch, je ~1 Query)

| agent_id | Regel | severity | Ziel |
|---|---|---|---|
| `kontrakt_untererfuellung` | Kontrakt < 80 % angedient ∧ Andienungsfrist < 21 Tage | warning | Kontrakt-Maske |
| `preisabweichung_einkauf` | Rechnungspreis > Bestellpreis + Toleranz (config) | warning | Rechnungsprüfung |
| `op_eskalation` | OP überfällig > 30 Tage ∧ keine Mahnung seit 14 Tagen | critical | Offene Posten |
| `qs_fristen` | QS-/Sachkunde-Zertifikat läuft < 30 Tage | warning | Zertifikate |

### API & UI
`GET /api/v1/ambient/worklist?agent_id=&status=` ·
`POST .../items/{id}/dismiss` (mit Grund, Audit). UI: Kacheln in den
Rollen-Workspaces (UIX-061-tiles zeigen counts je Agent) + Einträge als
P10-Karten (reason/source/confidence sichtbar); Abarbeitung ausschließlich
über die Ziel-Maske (target_route) — die Worklist selbst hat keine
Fach-Aktionen außer dismiss.

### Tests
pytest je Agent: Fixture → Proposal (Positivfall, Grenzwert, kein Treffer),
Dedupe-Doppellauf, Auto-Resolve, Kill-Switch, Tenant-Isolation; API-Suite
Coverage ≥ 60 %. Runtime-Sweep: neue GETs. Vitest: P10-Karte.

---

## UIX-090 — ScreenDefinition-Studio (No-Code für Fach-Admins)

### Ziel / Nicht-Ziele
Browser-Editor, mit dem Fach-Admins SDs erstellen/ändern — Ausgabe ist eine
**normale SD**, die durch **dieselben Gates** muss. **Nicht-Ziele:** freies
HTML/JS (nur deklarative SD-Bausteine), Bypass von advisoryScore/Meridian-
Gates, Custom-Code-Felder, Änderung nativer Registry-SDs im Studio
(nur Kopie-als-Draft → Promotion).

### Draft-Persistenz

```sql
CREATE TABLE domain_shared.screen_definition_drafts (
  id             uuid PRIMARY KEY,
  tenant_id      varchar NOT NULL REFERENCES domain_shared.tenants(id),
  screen_id      varchar(96) NOT NULL,        -- 'tenant/<slug>' Namensraum!
  base_screen_id varchar(96),                 -- Kopiervorlage (optional)
  definition     jsonb NOT NULL,              -- vollständige SD
  status         varchar(16) NOT NULL DEFAULT 'draft',
                 -- draft|review|published_temp|retired
  readiness      jsonb,                       -- letzter Gate-Report (Cache)
  created_by     varchar(64) NOT NULL,
  updated_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, screen_id)
);
```

Namensraum-Regel (hart): Studio-SDs leben unter `tenant/<slug>` und können
native `screenId`s weder überschreiben noch beschatten (Registry-Lookup:
nativ vor Draft; Kollision → Validierungsfehler beim Speichern).

### Editor (Frontend, `features/screen-studio/`)
- **Baukasten statt Freiform:** Drag-and-drop über Kataloge — Feldtypen
  (aus `ScreenFieldType`), Tab-/Sektion-Bausteine, Tabellen (Spalten aus
  Datenquellen-Katalog), Actions (nur aus CommandEndpoint-Katalog mit
  vorgegebenen dangerLevel — Studio kann dangerLevel **erhöhen**, nie senken).
- **Datenquellen-Katalog:** kuratierte Liste zulässiger Endpoints/Read Models
  (`config/studio_data_sources.yaml`) — kein freies URL-Feld.
- **Live-Vorschau:** rechter Bereich rendert den Draft über den echten
  `UniversalMaskRenderer` (RenderPlan aus Draft kompiliert, Mock-Datenmodus).
- **Gate-Panel:** jede Speicherung ruft `_check_readiness` (bestehender
  Endpoint) — Fehler/Warnungen inline; **Publish-Button ist deaktiviert,
  solange mandatory Gates rot sind** (Server erzwingt es zusätzlich).

### Publish-Workflow (nutzt bestehende Promotion-Mechanik)
`draft → review` (Vier-Augen: zweiter Fach-Admin, Audit) →
`published_temp`: SD wird als **temporäre** SD in den Laufzeit-Katalog
eingehängt (bestehender temp→native-Promotionspfad; advisoryScore + Meridian-
Pflicht identisch zu nativen SDs). Native Promotion (Code-Registry) bleibt
Entwickler-Weg — Studio-SDs können als YAML-Export für einen Registry-PR
heruntergeladen werden. Jede Statusänderung = Audit-Event
`studio.sd.{saved|reviewed|published|retired}`.

### API
`GET/POST/PUT /api/v1/studio/drafts` · `POST .../drafts/{id}/submit-review`
· `POST .../{id}/publish` (Permission `studio.publish`, Vier-Augen-Check:
publisher ≠ letzter Editor) · `POST .../{id}/retire` ·
`GET .../catalog/data-sources|actions|fields`. Alle typisiert, Coverage ≥ 60 %.

### Sicherheit (hart, testbewehrt)
- Server-seitige SD-Validierung gegen JSON-Schema der ScreenDefinition
  (neues `config/screen_definition.schema.json`, aus `schema.ts` abgeleitet
  und im CI auf Drift geprüft).
- Verbotene Felder im Studio-Input werden abgelehnt (nicht bereinigt):
  `forbiddenForAgents=false` auf kopierten Actions, dangerLevel-Senkung,
  eigene commandEndpoints außerhalb des Katalogs, `temporary=false`.
- Draft-Rendering läuft im Mock-Datenmodus ohne Mutationen (ActionRuntime
  disabled im Vorschau-Kontext).

### Abnahme-Szenario (End-to-End)
Fach-Admin baut „Lieferanten-Bewertung" (worklist + Detail mit 6 Feldern,
1 safe-Action aus Katalog) ohne Code; Gate-Panel grün; Review durch zweiten
Admin; published_temp; Maske über Omnibox auffindbar; Versuch, eine
critical-Action ohne Confirmation zu publishen, scheitert serverseitig (Test).

### Tests
pytest: Draft-CRUD, Namensraum-Kollision, Schema-Validierung (10 böse
Fixtures), Vier-Augen-Regel, Publish-Gate-Verweigerung; Coverage ≥ 60 %.
Vitest: Editor-Reducer (Baustein-Operationen), Gate-Panel-Zustände.
Playwright: Abnahme-Szenario komplett.
