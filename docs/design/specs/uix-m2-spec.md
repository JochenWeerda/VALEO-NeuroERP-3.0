---
title: UIX-M2 Spezifikation — „Vom Suchen zum Sagen" (UIX-070/071/072/073)
type: reference
audience: [agent, entwickler, qa]
owner: Claude
status: aktiv
last_reviewed: 2026-07-06
version: 1.0.0
description: Implementierungsreife Specs für Conversational Commands, Nutzer-Overlays, Diktat/Sprach-Navigation und E-Mail-Termin-Extraktion.
---

# UIX-M2 Spezifikation — „Vom Suchen zum Sagen"

Voraussetzungen: M1 (Omnibox 060, Kalender 063). Reihenfolge: **071 ∥ 072 → 070 → 073**
(070 nutzt 072-Diktat optional; 073 braucht 063).

---

## UIX-070 — Command-Ausführung aus der Omnibox (mit Ritual)

### Ziel / Nicht-Ziele
NL → vorbereiteter Command mit vollständigem Bestätigungs-Ritual.
**Nicht-Ziele:** Autonomie (kein Auto-Submit), high/critical-Actions
(nur Navigation zur Maske), Freitext-Payloads ohne Schema.

### Contract-Erweiterung

```ts
// IntentPlan um Command-Variante erweitert (lib/omnibox/types.ts)
| { kind: 'commandDraft'; screenId: string; actionKey: string
    payloadDraft: Record<string, unknown>          // nur Schema-Felder
    missingFields: string[]                        // Pflichtfelder ohne Wert
    label: string; confidence: number }
```

Slot-Filling: Compiler v2 mappt erkannte Entitäten (Kunde, Datum, Menge,
Freitext-Rest) auf die Feld-Definitionen der Ziel-SD (`fields[]` der Action
bzw. des Formular-Tabs): type-aware (date→ISO, number→Dezimal, lookup→
Lookup-Resolution über bestehende Lookup-API mit Top-1 nur bei eindeutigem
Treffer, sonst `missingFields`).

### Sicherheitsmatrix (hart, testbewehrt)

| dangerLevel | forbiddenForAgents | NL-Verhalten |
|---|---|---|
| safe | false | Formular-Prefill ODER Ritual (wenn action.requiresConfirmation) |
| moderate | false | immer Confirmation-Ritual (UIX-047) mit Payload-Zusammenfassung |
| high / critical | egal | **nur Navigation** zur Maske, kein Draft |
| egal | true | wie Maske: Aktion existiert im NL-Pfad nicht |

Konfidenz-Schwelle: `confidence < 0.75` → Degradation auf `formPrefill`
(Maske öffnen, Felder vorfüllen, nichts armieren).

### Ausführungspfad
Omnibox → `ActionRuntime.prepare(screenId, actionKey, payloadDraft,
{source:'omnibox'})` → bestehender ConfirmationDialog (Payload-Diff sichtbar,
AuditReason-Feld wenn gefordert) → bestehender CommandEndpoint. **Kein neuer
Endpoint.** Audit-Event erhält `trigger_source: omnibox`.

### Spiegel-Testsuite (Abnahme-Kern)
`tests/test_uix070_conversational_safety.py` — parametrisiert über
`ALL_SCREEN_IDS` (Muster von test_uix046_048): für jede Action jeder SD wird
der NL-Pfad simuliert und geprüft: identische Gate-Entscheidung wie
Masken-Pfad (Confirmation-Pflicht, forbiddenForAgents unsichtbar,
high/critical nicht draftbar). Plus Frontend-Vitest: Sicherheitsmatrix als
Tabelle über den Compiler.

### Telemetrie
060-Telemetrie erweitert: `{kind:'commandDraft', action_key, confirmed:bool,
edited_fields:int}` — Korrektur-Quote ist die M2-Metrik.

---

## UIX-071 — Nutzer-Overlays v1 (Personalisierung ohne Fork)

### Datenmodell

```sql
CREATE TABLE domain_shared.user_screen_overlays (
  tenant_id      varchar NOT NULL REFERENCES domain_shared.tenants(id),
  user_id        varchar(64) NOT NULL,
  screen_id      varchar(96) NOT NULL,
  schema_version integer NOT NULL,
  overlay        jsonb NOT NULL,          -- validiertes Diff, siehe Allowlist
  updated_at     timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, user_id, screen_id)
);
```

### Overlay-Schema (vollständige Allowlist — alles andere wird verworfen)

```jsonc
{
  "tables": { "<tableKey>": {
      "visibleColumns": ["nr","kunde","betrag"],      // Reihenfolge = Anzeige
      "columnWidths":   { "kunde": 240 },
      "activeVariant":  "mahnvorschlag",
      "customVariants": [ { "key":"meine", "label":"Meine Sicht",
                            "filters": {"status":"offen"} } ] } },
  "density": "expertDense",                            // nur enger, nie lockerer als SD? → frei
  "tileOrder": ["klaerfaelle","avis","rfq"],
  "collapsedSections": ["doku"]
}
```

**Nicht overlaybar (Compiler wirft `OverlayViolation`, Feld wird ignoriert +
telemetriert):** actions, permissions, dangerLevel, confirmation,
contextRailSections, fields (Sichtbarkeit von Pflicht-/Statusfeldern),
tableProfile, floorplan.

### Compiler-Integration
`schema-compiler`: `compile(sd) → plan`; neu `applyOverlay(plan, overlay) →
plan'` **nach** Compile, **vor** Render-Cache; Cache-Key um
`hash(overlay)+schemaVersion` erweitert (`render-plan/cache.ts`).
Drift: Overlay-Keys, die im Plan nicht existieren → `invalidPaths[]` →
Rail-Hinweis „Anpassung prüfen" + `PATCH` bereinigt beim nächsten Speichern.
`schema_version`-Mismatch: Overlay wird angewendet soweit gültig, Hinweis
angezeigt, nie Fehler.

### API
`GET/PUT /api/v1/ux/overlays/{screen_id}` (User-scoped aus Token; PUT
validiert gegen Allowlist serverseitig — Zweitverteidigung), 204 bei DELETE
(Zurücksetzen). Coverage ≥ 60 %.

### Frontend-UX
Tabellen-Toolbar: Spalten-Picker + „Als Variante speichern"; Kacheln:
Drag-Sortierung (keyboard-fähig: Alt+↑↓); „Zurücksetzen auf Standard" je
Maske. Alles über den Plan — keine lokalen Sonderpfade in Masken.

### Tests
Vitest: applyOverlay (Merge, Allowlist-Verletzung → ignoriert+gemeldet,
Drift, Cache-Key). pytest: PUT-Validierung (böses Overlay mit actions →
400/bereinigt), Tenant-/User-Isolation. Playwright: Spalten ändern → Reload
→ erhalten → Zurücksetzen.

---

## UIX-072 — Diktat & Sprach-Eingabe V1/V2 (VoiceBar)

### Adapter-Contract

```ts
// src/lib/voice/stt-provider.ts
export interface SttProvider {
  readonly id: 'webspeech' | 'server'
  isAvailable(): boolean
  start(opts: { lang: 'de-DE'; interim: boolean }): void
  stop(): void
  onPartial(cb: (text: string) => void): void
  onFinal(cb: (text: string, confidence?: number) => void): void
  onError(cb: (err: { code: string; message: string }) => void): void
}
```

Provider 1 `webspeech`: Web Speech API (Chromium/Edge, de-DE) — Default,
keine Serverkosten. Provider 2 `server`: Verallgemeinerung des bestehenden
CRM-Telefon-STT-Gateways (`POST /api/v1/voice/transcribe`, Audio-Chunk →
Text; Provider je Tenant konfigurierbar wie LLM-Gateway, On-Prem-Option).
Auswahl: `shell.voice.provider` aus Tenant-Config; Fallback-Kette
webspeech → server → disabled.

### Shell-Capability

```ts
// RenderShellPlan additiv
voice?: { enabled: boolean; provider: 'webspeech'|'server' }
```

VoiceBar-Primitive: Push-to-talk-Button (gedrückt halten oder Alt+V Toggle),
Live-Transkript als Overlay am fokussierten Feld bzw. in der Omnibox,
**Übernahme erst bei Loslassen/Bestätigen** (Transkript editierbar).
Feld-Diktat: fokussiertes `input/textarea` erhält Insert an Cursor-Position.
V2-Navigation: finaler Text mit Präfix-Grammatik (`öffne|zeige|filtere|suche`)
→ Omnibox-Intent-Compiler (nur `navigate`/`none` — Commands sind UIX-070/080).

### Datenschutz (hart)
Kein Audio-Persist; Server-Provider verwirft Audio nach Transkription
(Vertrag im Adapter dokumentiert); Transkripte werden nicht geloggt
(Telemetrie nur `{used:bool, provider, duration_s, target:'field'|'omnibox'}`).
`prefers-reduced-motion` respektieren (kein pulsierendes Mikro).

### Tests
Vitest mit `FakeSttProvider` (partial/final/error-Sequenzen; Editierbarkeit
vor Übernahme; Grammatik-Routing). pytest für `voice/transcribe` (Adapter-
Contract, Tenant-Config, 413/415-Fälle) falls Server-Provider im Slice
aktiviert wird — sonst als Folge-Flag dokumentieren. Playwright mit
Provider-Stub: Diktat in Feld + „zeige offene posten" → Navigation.

---

## UIX-073 — Termin-Extraktion aus E-Mails (Kalender ⨯ Capture-Inbox)

### Pipeline-Erweiterung
Bestehende crm_capture-Pipeline erhält Stufe `termin_extraction`:
1. **Kandidaten-Erkennung** (deterministisch): dt. Datums-/Zeitmuster
   („12.07.", „Montag 14 Uhr", „KW 29", „morgen früh"), Slot-Fenster
   („zwischen 8 und 10"), Zeitzonen-Default Europe/Berlin.
2. **Bezugsobjekt-Heuristik**: Bestell-/Kontrakt-/Lieferschein-Nummern im
   Text (Regex je Nummernkreis) → Objekt-Lookup; Absender-Domain →
   Lieferanten-Match; `confidence` je Zuordnung.
3. **LLM-Fallback** (Feature-Flag, bestehendes Gateway): nur wenn Stufe 1
   Kandidaten ohne eindeutige Struktur liefert; Ausgabe wird gegen Stufe-1-
   Kandidaten validiert (kein frei erfundenes Datum).

### Ausgabe-Contract
`calendar_items` mit `status='proposed'`, `source='email_capture'`,
`source_key='{mail_id}:{n}'`, `layer='logistik'`, payload:

```jsonc
{ "mail_id": "…", "mail_subject": "…", "mail_received_at": "…",
  "extracted_text": "Anlieferung Do 14 Uhr",
  "matched_object": { "type": "purchase_order", "id": "7712",
                      "confidence": 0.86 },
  "conflicts": [ { "item_id": "…", "reason": "Slot überschneidet Avis" } ] }
```

Konflikt-Check: überlappende Items gleicher Ressource (Lieferant/Rampe)
im ±2h-Fenster → `conflicts[]` (nur Hinweis, keine Blockade).

### UX (P8-Regeln)
Vorschlag erscheint im Logistik-Layer gestrichelt mit ✉-Badge (W-07);
Detail-Rail zeigt Quelle (Betreff, Empfangszeit, extrahierter Satz) +
[Bestätigen] [Verwerfen] [Termin bearbeiten vor Bestätigung].
Bestätigen → `status=confirmed` + Objekt-Verknüpfung + Audit; Verwerfen →
`dismissed` (bleibt für Lern-Telemetrie). **Kein Vorschlag wird still zum
Termin** (kein Auto-Confirm, auch nicht bei confidence 1.0).

### Tests
pytest: 10 Mail-Fixtures (klar/ambig/mehrere Termine/kein Termin/englisch
gemischt), Idempotenz (Re-Ingest derselben Mail erzeugt keine Dubletten),
Safety (proposed mutiert nichts, confirm nur aus proposed), Konflikt-Fixture.
Playwright: Fixture-Mail → Vorschlag im Kalender → Bestätigen → confirmed +
Link auf Bestellung.

### Metrik
Extraktions-Präzision (bestätigt/vorgeschlagen) und Korrektur-Quote
(bearbeitet vor Bestätigung) — Ziel ≥ 70 % Bestätigungsquote nach 4 Wochen.
