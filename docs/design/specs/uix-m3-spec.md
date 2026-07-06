---
title: UIX-M3 Spezifikation — „Hände frei, Lage im Blick" (UIX-080/081/082)
type: reference
audience: [agent, entwickler, qa]
owner: Claude
status: aktiv
last_reviewed: 2026-07-07
version: 1.0.0
description: Implementierungsreife Specs für Voice-Aktionen/Freisprech-Wiegen, Twin-Panel und ESG-Kacheln.
---

# UIX-M3 Spezifikation — „Hände frei, Lage im Blick"

Voraussetzungen: 072 (VoiceBar/STT-Adapter) für 080; 061 (Cockpit-Muster)
für 081. 082 ist unabhängig (Backend-lastig). Reihenfolge: **082 ∥ 081 → 080**
(080 hat die höchste Sicherheits- und Feldtest-Last).

---

## UIX-080 — Voice-Aktionen V3 + Freisprechmodus Waage (V4-Pilot)

### Ziel / Nicht-Ziele
Whitelisted Aktions-Kommandos per Stimme mit Echo + visueller Bestätigung;
Pilot: Annahme-Wiegung end-to-end freihändig. **Nicht-Ziele:** Danger-Aktionen
per Stimme (Gate-verboten), Voll-Duplex-Dialog (M5), Sprecher-Biometrie.

### Schema-Erweiterung (Action-Ebene)

```python
# ScreenDefinition action — additiv
{"key": "zweitwiegung_bestaetigen", "label": "Zweitwiegung bestätigen",
 "dangerLevel": "moderate", "requiresConfirmation": True,
 "commandEndpoint": "...", "method": "POST",
 "voiceEnabled": True,
 "voiceSynonyms": ["zweitwiegung bestätigen", "wiegung abschließen"]}
```

### Readiness-Gate (mandatory, beidseitig)
Frontend `generatorReadiness.ts` + Backend `_check_readiness`:
`voiceEnabled=True ∧ dangerLevel ∈ {high, critical}` → **Error** (blockiert
generatorReady). `voiceEnabled=True ∧ forbiddenForAgents=True` → Error
(Stimme ist ein Mensch-Kanal, aber die Kombination signalisiert Modellfehler
— explizit entscheiden statt still erlauben). Test in beiden Readiness-Suiten.

### VoiceCommandRouter (transaction-Floorplan)
`src/lib/voice/command-router.ts`:
1. Aktiv nur wenn `shell.voice.enabled` ∧ Floorplan `transaction` ∧
   Freisprech-Session aktiv (s. u.) — sonst gilt weiter V2 (Navigation).
2. Grammatik wird **zur Laufzeit aus dem RenderPlan** gebaut:
   `actions.filter(a => a.voiceEnabled)` → `label + voiceSynonyms`,
   plus Systemkommandos `abbrechen`, `wiederholen`, `hilfe`.
3. Match (normalisiert, Levenshtein-Toleranz 0.2) → **Echo-Overlay**:
   Vollbild-nahe Bestätigung (W-03) mit Aktion + Wirkungszusammenfassung;
   Bestätigung per zweitem Kommando `ja, bestätigen` ODER Klick/Enter;
   Timeout 8 s → verworfen. Danach normaler `ActionRuntime`-Pfad
   (Confirmation-Ritual wird durch das Echo-Overlay **erfüllt**, nicht
   übersprungen — AuditReason, falls gefordert, wird diktiert und muss
   sichtbar bestätigt werden).
4. Akustisches Feedback: kurzer Ton bei Erkennung, distinkter Ton bei
   Ausführung/Fehler (Web Audio, abschaltbar).

### Freisprech-Session (V4-Pilot)
- Aktivierung je Gerät: Geräte-Registrierung (`device_id` localStorage +
  Server-Eintrag `voice_devices`: tenant, device_id, standort, freigegeben_von),
  Start mit Session-PIN (4-stellig, je Schicht), Inaktivitäts-Timeout 10 min.
- Session-Kontext bindet Standort (Waage 1) — Kommandos wirken nur auf die
  dort offene Transaktion.
- **Vollprotokoll:** jedes erkannte Kommando (auch verworfen) als
  Audit-Event `voice.command` {transcript_hash, action_key|null, outcome:
  executed|cancelled|timeout|unmatched, device_id, session_id}.

### API
`POST /api/v1/voice/devices` (Registrierung, Admin-Permission) ·
`POST /api/v1/voice/sessions` (PIN-Start) · `DELETE .../sessions/{id}`.
Alle response_model-typisiert, Tenant-isoliert, Coverage ≥ 60 %.

### Pilot-Abnahme (Feldtest)
Protokollierte Durchführung an ≥ 1 Standort: 20 reale Wiegungen freihändig
(bestätigen/Klärfall/Probe anhängen), Erkennungsquote ≥ 90 % im Waagenhaus-
Lärm, 0 Fehlausführungen. Ergebnis als `docs/testing/voice-pilot-<datum>.md`.

### Tests
Vitest: Router-Grammatik aus Plan, Echo-Pflicht (kein Pfad ohne Overlay),
Timeout, Systemkommandos. pytest: Readiness-Gate-Fälle, Session-/Device-API,
Audit-Events. Safety-Suite: parametrisiert über alle SDs — keine Action mit
high/critical ist voice-erreichbar (Spiegel zu UIX-070-Matrix). Playwright
mit STT-Stub: Wiegung W-03 end-to-end.

---

## UIX-081 — Twin-Panel v1 (Hofplan/Silo im Leitstand)

### Ziel / Nicht-Ziele
Interaktive 2D-Belegungsansicht als Renderer-Primitive im cockpit-Floorplan.
**Nicht-Ziele:** 3D/WebGL (M5-Option), Editor für Plan-Geometrie (Studio-
Folge), Echtzeit-Streaming < 30 s.

### SD-Contract

```python
"twin": {
  "planSource": "config",              # v1: statische Geometrie; 'studio' als Folge
  "planRef": "emden-hofplan-v1",       # Schlüssel in config/twin_plans/
  "cellBinding": {
    "endpoint": "/api/v1/lager/silo/cells?standort=emden",   # Read Model
    "idField": "cell_id",
    "metrics": [
      {"key": "fill_pct",  "label": "Füllstand", "kind": "percent"},
      {"key": "moisture",  "label": "Feuchte %", "kind": "number",
       "warnAbove": 14.5},
      {"key": "locked",    "label": "Gesperrt",  "kind": "flag"},
      {"key": "qs_status", "label": "QS",        "kind": "status"}
    ],
    "targetScreenId": "lager/silo-zelle"      # Klick-Durchstich
  },
  "suggestEndpoint": "/api/v1/lager/silo/target-cell"   # optional (Rail-Karte)
}
```

### Geometrie-Format `config/twin_plans/emden-hofplan-v1.yaml`

```yaml
plan_id: emden-hofplan-v1
canvas: { width: 1200, height: 800 }          # logische Einheiten
background: assets/hofplan-emden.svg          # optional (Hofplan-Asset vorhanden)
cells:
  - id: S1-Z01
    label: "Silo 1 / Zelle 1"
    shape: { kind: rect, x: 80, y: 120, w: 60, h: 140 }   # oder kind: polygon, points []
  - id: S1-Z02
    shape: { kind: polygon, points: [[150,120],[210,120],[210,260],[150,260]] }
```

Quelle der Geometrie kann aus `packages/agrar-silo-materialfluss-studio`
exportiert werden (Konverter-Skript im Slice); v1-Abnahme mit handgepflegtem
YAML ist zulässig.

### Read Model (Backend)
`GET /api/v1/lager/silo/cells?standort=` — aggregiert bestehende Silo-/
Bestands-APIs in ein flaches Zellen-Array `{cell_id, fill_pct, moisture,
locked, qs_status, artikel, menge_t, updated_at}`; Cache 30 s; 0×5xx-Pflicht
(Runtime-Sweep). Kein neues Schreiben — reine Projektion.

### Renderer
`TwinPanelRenderer` (SVG): Zellen als Pfade aus Geometrie, Metrik-Layer als
Fill/Badge (Farbskalen: fill=Gold-Verlauf, warnAbove→danger-Kontur,
locked→Schraffur, qs→Status-Chip am Hover); Legende; Tastatur: Zellen
tab-bar, Enter=Durchstich. Tooltip mit allen Metriken. Poll 30 s
(sichtbar „Stand 10:41:20"), Layer-Toggles. Performance: ≤ 300 Zellen ohne
Virtualisierung; ein einziges SVG, keine per-Zelle-Components.

### Leitstand-SD
`lager/leitstand` (W-04): summary-KPIs (Annahmen heute, Ø Wartezeit,
Trocknerauslastung), `twin`-Block, tiles (Qualitäts-Nachtrag, Klärfälle,
Frachtaufträge, Trocknungsfreigaben), Ausnahmen-Band = Worklist-Tabelle
gefiltert auf Abweichungen, Rail: workflow+copilot (suggestEndpoint-Karte
mit Begründung/Konfidenz — P10-Pflichtfelder).

### Tests
pytest: cells-Read-Model (Aggregation, Tenant, Cache-Header), Coverage ≥ 60 %.
Vitest: Geometrie-Parser (rect/polygon/fehlerhafte YAML), Layer-Farblogik,
Keyboard-Navigation. Playwright: Leitstand → Zelle klicken → Zellen-Maske;
Visual-Audit-Erweiterung (Meridian-Suite) für 1366/1440/1920.
Performance-Gate: Leitstand ≤ bestehendes cockpit-Budget.

---

## UIX-082 — ESG-Kacheln v1 (CO₂e je Charge, audit-tauglich)

### Ziel / Nicht-Ziele
Nachvollziehbarer CO₂e-Fußabdruck je Charge/Prozess als Read Model +
Summary-Kachel. **Nicht-Ziele:** vollständige CSRD-Berichterstattung,
Scope-3-Lieferkette (Folge), Echtzeit-Sensorik.

### Emissionsfaktoren — versionierte Konfiguration

```yaml
# config/esg_factors.yaml  (versioniert; Änderungen nur mit Quellenangabe)
version: 2026-07
factors:
  trocknung_gas_kwh:   { co2e_kg: 0.201, source: "UBA 2025, Erdgas" }
  strom_kwh:           { co2e_kg: 0.380, source: "UBA 2025, Strommix DE" }
  transport_tkm:       { co2e_kg: 0.062, source: "GLEC v3, LKW 26-40t" }
```

### Read Model

```sql
CREATE TABLE domain_agrar.esg_charge_footprint (
  id           uuid PRIMARY KEY,
  tenant_id    varchar NOT NULL REFERENCES domain_shared.tenants(id),
  charge_id    varchar(64) NOT NULL,
  co2e_kg      numeric(12,3) NOT NULL,
  components   jsonb NOT NULL,
  -- [{key:'trocknung', input:{kwh: 1840}, factor_version:'2026-07',
  --   co2e_kg: 369.84, source_ref:'trocknungslauf:4711'}, …]
  factor_version varchar(16) NOT NULL,
  computed_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, charge_id, factor_version)
);
```

Berechnungs-Service `app/services/esg_footprint_service.py`:
Inputs aus Bestand — Trocknungsläufe (Gas/kWh je Charge), Touren/Frachten
(km × t je Lieferung → Charge-Zuordnung über Wiegekarten), Strom (Pauschale
je t Umschlag aus Config bis Zähler-Anbindung). Jede Komponente trägt
`source_ref` (Beleg-Verweis) — **Auditierbarkeit ist Abnahmekriterium**.
Neuberechnung idempotent je (charge, factor_version); Nightly + on-demand.

### API & UI
`GET /api/v1/esg/charges/{charge_id}/footprint` → FootprintOut (inkl.
Komponenten + Faktor-Quellen). Summary-Kachel (P13) auf Charge-/Kontrakt-
ObjectPage: `co2e_kg` + Trend vs. Betriebs-Ø; Popover „Herleitung" listet
Komponenten mit source_ref-Links (Klick → Beleg). Leitstand-KPI (W-04) =
Summe heute. Kennzeichnung `Faktorstand 2026-07` sichtbar.

### Tests
pytest: Service-Units (je Komponente Fixture → kg-Erwartung auf 3 Dezimalen,
fehlender Input → Komponente fehlt statt 0-Schätzung, Faktor-Versionierung),
API-Suite, Coverage ≥ 60 %. Vitest: Kachel + Popover. Reproduzierbarkeit:
Snapshot-Test — gleiche Inputs + gleiche Faktorversion ⇒ identisches Ergebnis.

### Governance
Faktor-Änderungen nur per PR mit Quellenangabe (CODEOWNERS auf
`config/esg_factors.yaml`); alte Footprints bleiben unter alter Version
stehen (kein stilles Neuschreiben der Historie).
