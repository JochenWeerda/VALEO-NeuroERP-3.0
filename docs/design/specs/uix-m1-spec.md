---
title: UIX-M1 Spezifikation — „Ein Eingabefeld" (UIX-060/061/062/063)
type: reference
audience: [agent, entwickler, qa]
owner: Claude
status: aktiv
last_reviewed: 2026-07-06
version: 1.0.0
description: Implementierungsreife Specs für Omnibox, Rollen-Workspaces, Collab-Rail und Planungskalender v1.
---

# UIX-M1 Spezifikation — „Ein Eingabefeld"

Basis: [Masterplan](../uix-zukunft-masterplan.md) · [Roadmap](../uix-zukunft-roadmap.md).
Reihenfolge/Abhängigkeiten in M1: **063-Backend ∥ 060 → 061 → 062**; 063-Frontend
braucht 060 nicht, profitiert aber (Zeit-Intents).

---

## UIX-060 — Omnibox-Shell + Intent-Vorschau (read-only)

### Ziel / Nicht-Ziele
Ziel: ⌘K-Overlay in der AppShell; natürliche Sprache → deterministischer
Navigations-/Filter-Plan mit Vorschau. **Nicht-Ziele:** Mutationen (UIX-070),
LLM-Pflicht (nur optionaler Fallback), Ersatz der Navigation.

### Contract (Frontend)

`packages/frontend-web/src/lib/omnibox/types.ts`:

```ts
export type IntentPlan =
  | { kind: 'navigate'; screenId: string; routePath: string;
      filters?: Record<string, string>; label: string; confidence: number }
  | { kind: 'formPrefill'; screenId: string; actionKey: string;
      label: string; confidence: number }          // öffnet Maske, füllt nichts aus (v1)
  | { kind: 'none'; suggestions: string[] }

export interface OmniboxCatalogEntry {
  screenId: string; title: string; domain: string; routePath: string
  synonyms: string[]                 // kuratiert, deutsch (z. B. "OP", "offene Posten")
  examplePrompts: string[]           // aus agentContract der SD
  filterableFields: { key: string; label: string; type: 'enum'|'date'|'text'|'number';
                      enumValues?: string[] }[]
}
```

### Intent-Compiler v1 (deterministisch)
`src/lib/omnibox/intent-compiler.ts` — Pipeline:
1. Normalisierung (lowercase, Umlaut-Folding, Zahl-/Datums-Token: „überfällig",
   „heute", „>30 Tage", „Juli").
2. Screen-Matching: Token-Overlap gegen `synonyms+title+examplePrompts`
   (TF-gewichtet); Score ≥ 0.5 → Kandidat, Top-3.
3. Filter-Extraktion: erkannte Tokens gegen `filterableFields` (enum-Werte,
   Datumsphrasen → ISO-Ranges, Vergleiche → `feld_gt/lt`).
4. `confidence` = screenScore × filterCoverage; < 0.35 → `kind:'none'` mit
   Top-Synonym-Vorschlägen.
Optionaler LLM-Fallback (Feature-Flag `VITE_OMNIBOX_LLM_FALLBACK`, default off)
über bestehendes LLM-Gateway; Ergebnis wird gegen den Katalog validiert (nie
freie Routen).

### Backend
`GET /api/v1/masks/omnibox-catalog` (neuer Handler in
`app/api/v1/endpoints/mask_registry.py`): projiziert die Registry
(`get_screen_definition` je Eintrag) auf `OmniboxCatalogEntry[]`;
`synonyms` aus neuem optionalem SD-Feld `agentContract.synonyms: list[str]`
(Backfill für die 13+ nativen SDs gehört zum Slice). Response-Model typisiert,
ETag/Cache 5 min.

### UI/UX
- ⌘K/Ctrl+K öffnet Overlay (W-00b); Esc schließt; ↑↓ wählt; Enter navigiert.
- ARIA: `role=combobox` + `aria-activedescendant`; Fokus-Falle; Screenreader-
  Ansage der Vorschau („Worklist Offene Posten, 2 Filter").
- Abschnitt „zuletzt": letzte 5 Navigationen (localStorage, kein Server).

### Telemetrie
`POST /api/v1/ux-telemetry/omnibox` `{intent_hash, matched_screen_id|null,
confidence, accepted: bool}` — **kein Klartext** (SHA-256 des normalisierten
Texts); Aggregat-Endpoint für M2-Tuning.

### Tests / Gates
- Vitest `intent-compiler.test.ts`: die 20 Kern-Intents (Tabelle unten) treffen
  Screen+Filter exakt; 5 Negativfälle → `none`.
- Playwright `omnibox-smoke.spec.ts`: öffnen → tippen → Vorschau → Enter → URL.
- pytest: Catalog-Endpoint (Shape, Tenant-Header, 200/ETag), Coverage ≥ 60 %.
- a11y-Check (axe) auf das Overlay.

Kern-Intents (Abnahme-Fixture): „offene posten folkerts" · „überfällige rechnungen"
· „wiegekarte 8842" · „neuer auftrag" · „kontrakte raps 2026" · „qualitäts-nachtrag"
· „zahlungslauf juli" · „artikel weizen" · „mahnvorschlag" · „lieferscheine heute"
· „bestellungen offen baywa" · „klärfälle annahme" · „kunde 10233" · „silo belegung"
· „sachkunde läuft ab" · „urlaubsantrag" · „preisspiegel dünger" · „op > 30 tage"
· „aufträge überfällig rohware fehlt" · „was steht nächste woche an" (→ 063-Agenda).

---

## UIX-061 — Rollen-Workspaces (kontextabhängige Startseiten)

### Ziel / Nicht-Ziele
5 native `cockpit`-SDs als Startseiten je Rolle. **Nicht-Ziele:** frei
konfigurierbare Dashboards (M2-Overlays), neue KPI-Backends (nur vorhandene
Summary-/Worklist-Endpoints).

### Schema-Erweiterung (additiv, schemaVersion bleibt 1)

```python
# app/core/screen_definitions.py — neuer optionaler SD-Block
"tiles": [
  {"key": "qualitaet_nachtrag", "label": "Qualitäts-Nachtrag",
   "countEndpoint": "/api/v1/agrar/qualitaet/nachtrag/worklist?count_only=true",
   "targetScreenId": "agrar/qualitaet-nachtrag", "targetFilters": {},
   "tone": "warning"},          # tone: neutral|warning|danger
]
```

Compiler: `RenderPlan.tiles: RenderTilePlan[]`; neuer `TileGridRenderer`
(Kachel = Zähler + Alter des ältesten Eintrags optional via `ageField`).
Readiness (advisory v1): cockpit-SDs ohne `tiles` und ohne `tables` → Warnung.

### Die 5 Workspaces (Registry-IDs, Inhalte aus Bestand)

| screenId | KPI-Summary (vorhandene Endpoints) | Kacheln |
|---|---|---|
| `workspace/einkauf` | offene Bestellungen, Avis heute, Preisabweichung | Rechnungsprüfung-Abweichungen, offene Avis, RFQ |
| `workspace/verkauf` | Auftragsbestand, überfällig, Kreditlimit-Warnungen | Bestell-Inbox, Klärfälle, Angebots-Wiedervorlagen |
| `workspace/lager` | Annahmen heute, Ø Wartezeit, Trocknerauslastung | Qualitäts-Nachtrag, Klärfälle Annahme, Frachtaufträge |
| `workspace/fibu` | OP-Summen D/K, fällige Zahlungen, Mahnstufen | Zahlungslauf-Vorschlag, Buchungs-Klärfälle, UStVA-Frist |
| `workspace/leitung` | Umsatz YTD, Rohertrag, Top-Ausnahmen | Eskalationen, Audit-Hinweise, ESG-Vorschau (Platzhalter) |

### Rollen-Mapping & Saison
`config/workspace_roles.yaml`: `role → screenId` (+ Tenant-Override via
TENANT_MODULE_FLAGS-Muster). Login-Redirect: AppShell liest Rolle aus
OIDC-Claims → navigiert zu Workspace (Fallback: bisherige Startseite).
`seasonProfile` (optional je SD): `{activeFrom: "07-01", activeTo: "09-15",
tileOrderOverride: [...]}` — reine Umsortierung, kein Inhaltswechsel.

### Tests / Gates
pytest: 5 SDs generatorReady, advisoryScore ≥ 0.8, tiles-Endpoints antworten
(Runtime-Sweep nimmt count_only-GETs automatisch mit). Vitest: TileGridRenderer.
Playwright: Route-Smoke der 5 Workspaces (uix-056-Erweiterung).

---

## UIX-062 — Collab-Rail v1 (Notizen & @-Mentions am Datensatz)

### Datenmodell (Alembic, Single Head)

```sql
CREATE TABLE domain_shared.entity_notes (
  id            uuid PRIMARY KEY,          -- uuid7
  tenant_id     varchar NOT NULL REFERENCES domain_shared.tenants(id),
  entity_type   varchar(64)  NOT NULL,     -- 'customer'|'sales_order'|'invoice'|…
  entity_id     varchar(64)  NOT NULL,     -- UUID oder fachlicher Schlüssel
  body          varchar(4000) NOT NULL,
  mentions      jsonb NOT NULL DEFAULT '[]',   -- [{user_id, display}]
  created_by    varchar(64) NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz,
  deleted_at    timestamptz                -- soft delete, Audit bleibt
);
CREATE INDEX ix_entity_notes_lookup
  ON domain_shared.entity_notes (tenant_id, entity_type, entity_id, created_at DESC);
```

### API (`app/api/v1/endpoints/collab_notes.py`, response_model-typisiert)
- `GET  /api/v1/collab/notes?entity_type=&entity_id=&limit=50` → `list[NoteOut]`
- `POST /api/v1/collab/notes` `{entity_type, entity_id, body, mentions[]}`
  → 201 `NoteOut`; je Mention ein Eintrag über den bestehenden
  Benachrichtigungs-/Messages-Pfad (`messages.py`-Integration) + Outbox-Event
  `collab.note.created`.
- `PATCH/DELETE /api/v1/collab/notes/{id}` — nur Ersteller (sonst 403);
  DELETE = soft.
Sicherheit: Tenant-Isolation (Pflichttest Cross-Tenant 404), Mentions nur
gültige User-IDs, body ohne HTML-Interpretation (Frontend rendert Plaintext
mit Linkify).

### Frontend
`WorkflowPanelRenderer` erhält Sektion **collab** — Aktivierung deklarativ:
`layout.contextRailSections?: ('audit'|'workflow'|'copilot'|'collab')[]`
(additiv; `contextRail: 'combined'` ≙ bisherige Default-Sektionen; Compiler
mappt beides auf `shell.contextRailSections`). Composer mit
Mention-Autocomplete (bestehende User-Lookup-API), optimistisches Anfügen,
Mutation-Lifecycle-Invariante (Guard/disabled/finally/Toast). Inbox-Badge:
Shell-Statuszeile zählt ungelesene Mentions.

### Tests
pytest Endpoint-Suite (CRUD, Tenant-Isolation, Mention→Notification,
Soft-Delete) Coverage ≥ 60 %; Vitest Renderer-Sektion; Playwright: Notiz →
Mention → Badge → Inbox.

---

## UIX-063 — Planungskalender v1 (Zeit als Projektion)

### Datenmodell

```sql
CREATE TABLE domain_shared.calendar_items (
  id             uuid PRIMARY KEY,                   -- uuid7
  tenant_id      varchar NOT NULL REFERENCES domain_shared.tenants(id),
  source         varchar(48)  NOT NULL,   -- 'periodische_buchungen'|'open_items'|…
  source_key     varchar(128) NOT NULL,   -- idempotenter Schlüssel je Quelle
  layer          varchar(16)  NOT NULL,   -- finanzen|fristen|crm|logistik|personal|saison
  item_type      varchar(48)  NOT NULL,   -- 'frist'|'termin'|'lauf'|'reminder'
  title          varchar(200) NOT NULL,
  starts_at      timestamptz NOT NULL,
  ends_at        timestamptz,
  all_day        boolean NOT NULL DEFAULT false,
  status         varchar(16) NOT NULL DEFAULT 'projected',
                 -- projected|proposed|confirmed|dismissed
  object_type    varchar(64),   object_id varchar(64),
  object_screen_id varchar(96), object_route varchar(200),
  payload        jsonb NOT NULL DEFAULT '{}',        -- Quell-Detail (z. B. Betrag)
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz,
  UNIQUE (tenant_id, source, source_key)             -- Upsert-Idempotenz
);
CREATE INDEX ix_calendar_items_range
  ON domain_shared.calendar_items (tenant_id, starts_at, layer);
```

### Projektions-Framework
`app/services/calendar_projection_service.py`:

```python
class CalendarProjector(Protocol):
    source: str
    layer: str
    def project(self, db: Session, tenant_id: str,
                horizon_days: int = 120) -> list[CalendarItemDraft]: ...

# Registrierung analog Modul-Registry; Lauf idempotent:
# upsert per (tenant, source, source_key); nicht mehr gelieferte projected-Items
# im Horizont werden gelöscht (proposed/confirmed/dismissed bleiben).
```

Projektoren v1 (Quelle → source_key):
1. `periodische_buchungen` → nächste Ausführungstermine (`{buchung_id}:{datum}`),
   Layer finanzen, payload {betrag, rhythmus}.
2. `open_items` → Fälligkeiten (`{op_id}`), Layer finanzen.
3. `kontrakt_fristen` → Andienungs-/Staffel-/Rabatt-Enddaten
   (`{kontrakt_id}:{fristart}`), Layer fristen (Ende Frühbezugsrabatt!).
4. `crm_wiedervorlagen` → Aktivitäten mit due_date (`{activity_id}`), Layer crm.
5. `agrar_sachkunde` → gueltig_bis (`{sachkunde_id}`), Layer personal
   (Vorlauf-Erinnerung 60/30/7 Tage).

Ausführung: Nightly-Job (bestehende Scheduler-Infrastruktur) +
`POST /api/v1/planung/kalender/reproject` (idempotent, moderate, Audit).

### API
- `GET /api/v1/planung/kalender?from=&to=&layers=a,b` → `list[CalendarItemOut]`
- `POST /api/v1/planung/kalender/items/{id}/confirm` · `/dismiss`
  (nur `status=proposed`; normale Commands mit Audit — Vorbereitung für UIX-073)
- `GET /api/v1/planung/kalender/ics?token=` — read-only ICS-Feed; Token je
  User/Tenant (rotierbar, `GET /ics-token` + `POST /ics-token/rotate`), kein
  Bearer im Kalender-Client nötig; nur confirmed/projected.
- Erinnerungen: Nightly erzeugt Notifications für Items mit `remind_at`-Regeln
  (Layer-Default: Fristen 14/3 Tage vorher, personal 60/30/7).

### Frontend
`CalendarRenderer` als Renderer-Primitive (Monat/Woche/Agenda + Fristenband
14 Tage; Layer-Chips togglebar, Rollen-Default aus Workspace). SD
`planung/kalender` (cockpit, contextRailSections [workflow, copilot]).
Klick → `object_route`; Einträge ohne Objekt-Link nur für manuelle Items
(v1: nicht angeboten). Keine externe Kalender-Bibliothek als Parallel-UI —
falls Bibliothek, dann gekapselt hinter dem Primitive (Vorgabe: Eigenbau
Monat/Agenda mit CSS-Grid, Woche = Agenda-Variante; kein Drag-and-drop in v1).

### Tests / Gates
pytest: je Projektor Unit (Fixture → Draft-Liste, Idempotenz-Doppel-Lauf,
Horizont-Löschung, proposed bleibt), API-Suite (Range/Layer-Filter,
Tenant-Isolation, ICS-Token-Rotation), Coverage ≥ 60 %. Vitest: Renderer
(Monat/Agenda, Fristenband, Layer-Toggle). Playwright: Kalender öffnen →
Layer toggeln → Klick-Durchstich. Runtime-Sweep: neue GETs 0×5xx.

### Offene Entscheidung (im Slice zu treffen, dokumentieren)
Saison-Layer v1 leer lassen oder Kulturkalender-Stammdaten (statisch YAML)
mitliefern — Empfehlung: statisches `config/saison_kalender.yaml` (DE-Nord),
da reiner Anzeige-Layer.
