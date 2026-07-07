---
title: UIX-Zukunft Roadmap — Milestones, Slices & Prompts
type: reference
audience: [agent, entwickler, design, qa, produkt]
owner: Claude
status: aktiv
last_reviewed: 2026-07-06
version: 1.0.0
description: Umsetzungs-Roadmap zum UIX-Zukunft-Masterplan — Milestones M1–M5 mit gegliederten Aufgaben, Akzeptanzkriterien und agent-fähigen Prompts.
---

# UIX-Zukunft Roadmap

Basis: [uix-zukunft-masterplan.md](uix-zukunft-masterplan.md).
Arbeitsregeln für **jeden** Slice (nicht verhandelbar):

1. Slice claimen (Workboard + `docs/agent-ops/slices/<ID>.yaml`), Claim sofort committen.
2. Kein Bypass der Kette `ScreenDefinition → RenderPlan → Renderer → Gates`;
   keine parallelen Seiten, keine kopierten Referenz-UIs.
3. Jede neue Fähigkeit = Contract-Feld + Compiler-Ableitung + Renderer-Primitive
   + Readiness-Gate + Test (Unit + ggf. Playwright-Visual).
4. Prioritätsleitplanke bleibt: Landhandel-Kern → Canonical Model/Workflow →
   Medienbruch-Reduktion → Maskenarbeit.
5. Performance-Gates (mask-render-performance) und Visual-Audit
   (1366/1440/1920) bleiben grün; `pnpm exec tsc --noEmit` grün.

Statusliste (lebendes Dokument): Häkchen je Slice nachziehen.

---

## M0 — Fundament (fertig, Stand 2026-07-06)

Meridian-Vertrag in `ScreenDefinition.layout` + `RenderPlan.shell`, Readiness-
Gates, 13 native SDs, ActionRuntime (UIX-045), CommandEndpoints (046), Agent-
Safety-Tests (048), Meridian-Visual-Audit, Worklist-Muster, Capture-Inbox-Muster,
Promotion-Pfad temp→native. **Alles Weitere baut hierauf.**

---

## M1 — „Ein Eingabefeld" (Ziel: Q3/2026)

**Ergebnis:** Omnibox als zentraler Einstieg (⌘K), Rollen-Workspaces als
Startseiten, Kollaborations-Rail v1, Planungskalender v1. Nutzer navigieren
per Intent statt Menü; Zeitbezogenes visualisiert sich selbst.

### Slices

**UIX-060 Omnibox-Shell + Intent-Vorschau (Read-only)**
- [ ] `RenderPlan.shell.omnibox`-Capability + AppShell-Einbau (⌘K, Fokus-Management)
- [ ] Intent-Compiler v1: NL → `{screenId, filters}` gegen Masken-Registry
      (Nutzung `examplePrompts` + route-aliases als Trainings-/Matching-Basis)
- [ ] Vorschau-Panel (W-00): Treffer als „Verstanden als" — Enter navigiert nur
- [ ] Telemetrie: erkannte/verworfene Intents (Datenbasis für M2)
- Akzeptanz: 20 Kern-Intents (je Domäne 4) treffen die richtige Maske+Filter;
  0 Mutation möglich; Visual-Audit + a11y (Fokusfalle, Screenreader-Labels) grün.

```text
PROMPT UIX-060
Rolle: UIX-Slice-Agent im VALEO Single Mask Builder.
Lies docs/design/uix-zukunft-masterplan.md (Abschnitte 4, 5/P11) und
docs/design/valeo-meridian-experience.md. Claim UIX-060 im Workboard + Slice-YAML.
Baue die Omnibox als Shell-Capability (kein Parallel-Router!): ⌘K-Overlay in der
AppShell, Intent-Compiler v1 (Registry-basiertes Matching über screen_definitions
examplePrompts + route-aliases.json), „Verstanden-als"-Vorschau, Enter=Navigation.
Verboten: jede Mutations-Ausführung, eigener Chat-Endpoint, Seiten-Kopien.
Tests: Unit für Intent-Matching (20 Kern-Intents), Playwright-Smoke Omnibox
öffnen/Intent/Navigation, tsc grün. Doku: Masterplan-Verweis in
universal-mask-runtime-status.md ergänzen. Workboard-Abschluss mit Messwerten.
```

**UIX-061 Rollen-Workspaces (kontextabhängige Startseiten)**
- [ ] `cockpit`-SDs je Kernrolle: Einkauf, Verkauf/Innendienst, Lager/Annahme,
      Buchhaltung, Geschäftsleitung (5 Stück, Registry-nativ)
- [ ] Worklist-Kacheln (P5) aus bestehenden Worklists; KPI-Zeile aus Read Models
- [ ] Saison-/Zeitkontext (Erntepeak-Modus: Annahme-KPIs nach vorn)
- Akzeptanz: Login → Rollen-Workspace statt generischem Menü; alle 5 SDs
  generatorReady mit Meridian-Metadaten; Advisory-Score ≥ 0.8.

```text
PROMPT UIX-061
Rolle: UIX-Slice-Agent. Lies Masterplan Abschnitt 3 (Workspaces) + 6/W-04.
Claim UIX-061. Erzeuge 5 native cockpit-ScreenDefinitions (einkauf/verkauf/
lager/fibu/leitung) ausschließlich deklarativ in app/core/screen_definitions.py:
KPI-Summary aus vorhandenen Read-Model-/Summary-Endpoints, Worklist-Kacheln auf
bestehende Worklists verlinkt, contextRail combined. Keine neuen React-Seiten —
Rendering muss durch UniversalMaskRenderer laufen (native Route + Alias).
Gates: generatorReady, advisoryScore>=0.8, uix-056-Route-Smoke erweitert.
```

**UIX-062 Collab-Rail v1 (Notizen & @-Mentions am Datensatz)**
- [ ] `contextRail: 'collab'`-Sektion (P6-Erweiterung): Notizen je Entity
      (business_partner_id/Beleg-UUID), @-Mention → Benachrichtigungs-Inbox
- [ ] Backend: generische `entity_notes`-API (Tenant-isoliert, auditierbar)
- [ ] Keine Schatten-Kommunikation: Notiz ist Datensatz-gebunden, exportierbar
- Akzeptanz: Notiz an Kunde/Beleg aus ObjectPage-Rail; Mention erzeugt
  Inbox-Eintrag; Audit-Profil listet Notiz-Ereignisse.

```text
PROMPT UIX-062
Rolle: Fullstack-Slice-Agent. Lies Masterplan P6/P8 + Abschnitt 3 (Kollaboration).
Claim UIX-062. Backend: entity_notes-Endpoint (FastAPI, response_model-typisiert,
X-Tenant-Id, Alembic-Migration am Single Head, Audit-Events). Frontend: Collab-
Sektion im WorkflowPanelRenderer (kein neues Panel-System), Mention-Autocomplete
über bestehende User-API, Inbox-Badge in der Shell-Statuszeile. Mutation-Lifecycle-
Invariante (Guard/disabled/finally/Toast) einhalten. Tests: Endpoint-Coverage>=60,
Renderer-Unit-Test, 1 Playwright-Flow (Notiz anlegen → Mention → Inbox).
```

**UIX-063 Planungskalender v1 (Zeit als Projektion)**
- [x] `calendar_items`-Read-Model + `calendarProjection`-Deklaration (Feld → Termin-Typ)
      für die ersten Quellen: periodische Buchungen (wiederkehrende Umsätze),
      OP-Fälligkeiten, Kontrakt-/Rabattfristen (Ende Frühbezugsrabatt),
      CRM-Wiedervorlagen, Sachkunde-/Schulungsabläufe
- [x] Kalender-Renderer-Primitive (Monat/Woche/Agenda + Fristenband, Layer je Quelle)
      als `cockpit`-SD — Klick-Durchstich zur ObjectPage, kein eigener Seitenbaum
- [ ] Erinnerungen über Benachrichtigungs-Inbox
- [x] ICS-Export (read-only)
- Akzeptanz: 5 Quellen projizieren automatisch (0 manuelle Doppelpflege);
  jeder Eintrag verlinkt sein Objekt; W-07-Visual-Audit; Omnibox-Intent
  „was steht nächste Woche an?" öffnet gefilterte Agenda.

```text
PROMPT UIX-063
Rolle: Fullstack-Slice-Agent. Lies Masterplan W-07/P16. Claim UIX-063.
Backend: calendar_items-Read-Model (Tenant-isoliert, Alembic Single Head) +
Projektions-Registrierung calendarProjection je Quelle (periodische_buchungen,
open_items-Fälligkeiten, Kontrakt-/Staffel-Fristen, CRM-Wiedervorlagen,
agrar_sachkunde-Abläufe) — Projektion idempotent, Quell-Feld dokumentiert.
Frontend: Kalender-Primitive im Renderer-Baukasten (Bibliothek nur als internes
Primitive hinter dem RenderPlan, kein Parallel-UI), planung/kalender als native
cockpit-SD mit Layern + Fristenband.
Verboten: manueller Termin-CRUD als Hauptweg, Einträge ohne Objekt-Link.
Tests: Projektions-Units je Quelle, Endpoint-Coverage>=60, Playwright:
Layer-Toggle + Klick-Durchstich. Gates: generatorReady, Visual-Audit, Perf.
```

---

## M2 — „Vom Suchen zum Sagen" (Ziel: Q4/2026)

**Ergebnis:** Conversational Layer führt vorbereitete Commands mit Vorschau und
Ritual aus; Nutzer personalisieren Masken per Overlay; Diktat überall.

### Slices

**UIX-070 Command-Ausführung aus der Omnibox (mit Ritual)**
- [ ] Intent-Compiler v2: NL → Command-Plan (`commandEndpoint` + Payload-Entwurf)
- [ ] Übergabe an bestehendes Confirmation-Ritual (UIX-047) — nie Direktausführung
- [ ] `dangerLevel`-Matrix: safe=Formular-Prefill, moderate+=Ritual, high/critical
      =nur Navigation zur Maske; `forbiddenForAgents` gilt auch für NL-Pfad
- Akzeptanz: „lege Aktivität für Folkerts an: Rückruf morgen 9 Uhr" erzeugt
  vorbefülltes create_activity mit Bestätigung; Safety-Testsuite (UIX-048-Stil)
  für den NL-Pfad; 0 Wege an Confirmation vorbei (Test beweist es).

```text
PROMPT UIX-070
Rolle: UIX-Slice-Agent mit Agent-Safety-Fokus. Lies Masterplan 1/4/8 und
tests/test_uix046_048_command_endpoints_safety.py. Claim UIX-070.
Erweitere den Omnibox-Intent-Compiler: NL → {commandEndpoint, payloadDraft} nur
für Actions mit dangerLevel safe/moderate und ohne forbiddenForAgents.
Ausführung ausschließlich über ActionRuntime + ConfirmationDialog (UIX-047).
Schreibe die Spiegel-Testsuite test_uix070_conversational_safety.py: für JEDE
native SD wird geprüft, dass der NL-Pfad dieselben Gates erzwingt wie die Maske.
Telemetrie: Command-Intents mit Konfidenz + Korrektur-Quote.
```

**UIX-071 Nutzer-Overlays v1 (Personalisierung ohne Fork)**
- [ ] Overlay-Modell (JSON-Diff: Spalten, Varianten, Dichte, Kachel-Anordnung)
      + Server-Persistenz je User/SD/schemaVersion
- [ ] Compiler-Merge: SD ⊕ Overlay → RenderPlan (Sicherheitsfelder nicht overlaybar
      — Allowlist im Schema-Compiler)
- [ ] Drift-Erkennung: SD-Update invalidiert verwaiste Overlay-Pfade → Worklist
- Akzeptanz: Spaltenwahl/Variante überlebt Reload & SD-Minor-Update; Versuch,
  dangerLevel per Overlay zu ändern, wird vom Compiler verworfen (Test).

```text
PROMPT UIX-071
Rolle: Builder-Core-Agent. Lies Masterplan 10. Claim UIX-071.
Implementiere Overlays als deklarative Diffs im schema-compiler (render-plan/):
merge(SD, overlay) mit strikter Feld-Allowlist (columns/variants/density/
tileOrder). Persistenz: user_screen_overlays-API (Tenant+User+screenId+
schemaVersion). Drift-Job: bei SD-Änderung verwaiste Overlay-Keys erkennen →
„Anpassung prüfen"-Worklist. Verboten: Overlay auf actions/permissions/
confirmation. Tests: Compiler-Unit (Merge, Allowlist-Verletzung, Drift),
Endpoint-Coverage>=60, Playwright: Spalten anpassen → Reload → erhalten.
```

**UIX-072 Diktat & Sprach-Eingabe V1/V2**
- [ ] VoiceBar-Primitive (P11): Push-to-talk, Live-Transkript, editierbar
- [ ] STT-Gateway-Anbindung (vorhandenes CRM-STT verallgemeinern; Provider
      hinter Adapter, DSGVO: keine Cloud-Pflicht, On-Prem-Option)
- [ ] V2-Grammatik: öffne/zeige/filtere → Omnibox-Intents (Read-only)
- Akzeptanz: Diktat in jedes Textfeld (Feld-Fokus + 🎤); „zeige offene Posten
  Folkerts" navigiert korrekt; Transkript nie ohne Sichtprüfung übernommen.

```text
PROMPT UIX-072
Rolle: UIX-Slice-Agent. Lies Masterplan 8 (V1/V2). Claim UIX-072.
Baue VoiceBar als Renderer-Primitive (shell.voice-Capability): Push-to-talk,
Streaming-Transkript in fokussiertes Feld bzw. Omnibox, Editierbarkeit vor
Übernahme. STT über Adapter-Interface (bestehenden CRM-Transkript-Pfad
verallgemeinern, Provider konfigurierbar je Tenant). Nur Read-Intents (V2) —
keine Action-Ausführung (das ist UIX-080). A11y: Tastatur-Alternative überall.
Tests: Adapter-Unit mit Fake-STT, Playwright mit Transkript-Stub.
```

**UIX-073 Termin-Extraktion aus E-Mails (Kalender ⨯ Capture-Inbox)**
- [ ] Capture-Inbox-Erweiterung: Datums-/Termin-Extraktion aus Mails
      (Lieferantentermine, Abholslots) → Kalender-**Vorschlag** (P8: editierbar,
      Quellen-Nachweis; Bestätigung erzeugt calendar_item + Objekt-Verknüpfung)
- [ ] Konflikt-Hinweis (Slot kollidiert mit Avis/Frist) im Vorschlag
- Akzeptanz: Mail „Anlieferung Do 14 Uhr" wird als Vorschlag im Logistik-Layer
  sichtbar, Bestätigung verlinkt die Bestellung; Falsch-Extraktion in 1 Klick
  verwerfbar; kein Vorschlag wird still zum Termin.

```text
PROMPT UIX-073
Rolle: Fullstack-Slice-Agent. Lies Masterplan W-07 (E-Mail-Zeile) + P8.
Claim UIX-073. Erweitere die bestehende crm_capture-Pipeline um Termin-
Extraktion (Datum/Zeit/Slot + Bezugsobjekt-Heuristik Bestellnr/Lieferant).
Ausgabe ist IMMER ein Vorschlag (status=vorgeschlagen) im calendar_items-
Read-Model; Bestätigen/Verwerfen sind normale Commands mit Audit.
Tests: Extraktions-Units (10 Mail-Fixtures dt./ambig), Safety: Vorschlag
mutiert nichts; Playwright: Mail-Fixture → Vorschlag → Bestätigen → Termin.
```

---

## M3 — „Hände frei, Lage im Blick" (Ziel: H1/2027)

**Ergebnis:** Freisprech-Wiegen, Digital-Twin-Leitstand, ESG sichtbar.

### Slices

**UIX-080 Voice-Aktionen V3 + Freisprechmodus Waage (V4-Pilot)**
- [ ] `voiceEnabled`-Flag je Action (Schema + Gate: nie bei high/critical)
- [ ] Kommando-Echo + Groß-Bestätigung (W-03); Geräte-/Orts-Bindung, Session-PIN
- [ ] Pilot: Annahme-Wiegung end-to-end freihändig (bestätigen/Klärfall/Probe)
- Akzeptanz: Wiegeprozess ohne Tastatur durchführbar; Safety-Suite: Danger-
  Aktionen per Stimme nachweislich unmöglich; Feldtest-Protokoll mit ≥1 Standort.

**UIX-081 Twin-Panel v1 (Hofplan/Silo im Leitstand)**
- [ ] Twin-Renderer-Primitive (P12): 2D-Belegungsplan aus Konfiguration
      (Zellen→Read-Model-Bindung), Klick→ObjectPage, Zustands-Layer (Füllstand,
      Feuchte, Sperre, QS)
- [ ] agrar-silo-materialfluss-studio als Quelle der Plan-Geometrie einbinden
- [ ] Leitstand-SD (W-04) nutzt Twin + Worklist-Kacheln + Ausnahmen-Band
- Akzeptanz: Leitstand zeigt Live-Belegung; silo_target_cell-Vorschlag im Rail;
  Performance-Budget cockpit ≤ bestehendes Gate.

**UIX-082 ESG-Kacheln v1 (CO₂e je Charge/Prozess)**
- [ ] ESG-Read-Model (THG je Charge aus Massebilanz/Trocknung/Transport)
- [ ] P13-Kachel in Summary (Charge, Kontrakt) + Leitstand-KPI; Quelle sichtbar
- Akzeptanz: Charge-ObjectPage zeigt CO₂e mit Herleitungs-Popover; Werte
  reproduzierbar aus Read-Model-Snapshot (Audit-tauglich).

```text
PROMPT M3 (je Slice analog):
Rolle: UIX-/Fullstack-Slice-Agent. Lies Masterplan 6 (W-03/W-04), 8 (V3/V4),
Trend-Mapping Zeile 3/5. Claim <SLICE>. Neue Fähigkeiten ausschließlich als
RenderPlan-Capability + Renderer-Primitive + Gate. Für UIX-080 gilt die harte
Regel: voiceEnabled ist im Readiness-Gate mit dangerLevel gekoppelt (high/
critical => Gate-Fehler). Für UIX-081: Geometrie/Konfiguration deklarativ,
kein Canvas-Sonderweg außerhalb des Renderers. Für UIX-082: erst Read-Model
(Backend, dokumentiert, getestet), dann Kachel. Abschluss je Slice: Workboard,
Tests, Visual-Audit, Performance-Gate, Doku.
```

---

## M4 — „Das ERP baut sich selbst" (Ziel: H2/2027)

**Ergebnis:** Fach-Admins erstellen Masken im Studio; Agenten befüllen
Worklists flächendeckend; Prozessband überall.

### Slices

**UIX-090 ScreenDefinition-Studio (No-Code für Fach-Admins)**
- Editor über Feld-/Tab-/Action-Katalog (Drag-and-drop), Ausgabe = normale SD
  (temp), Vorschau über UniversalMaskRenderer, Promotion temp→native nur durch
  bestehende Gates (advisoryScore, Meridian-Pflichtfelder, Agent-Contract)
- Akzeptanz: Fach-Admin baut Lieferanten-Bewertungsmaske ohne Code; Studio kann
  keine Gate-Verletzung veröffentlichen (Test); Audit-Trail je Änderung.

**UIX-091 Prozessband (P9) flächendeckend**
- `shell.processRibbon` aus Workflow-/Doc-Chain-Deklaration; Klick-Navigation
  entlang K1–K4; Gate: Beleg-Masken ohne Kette = Warnung.

**UIX-092 Ambient-Agent-Worklists**
- Rahmenwerk: Agent-Jobs beobachten Read Models → Worklist-Einträge mit
  Begründung/Quelle/Konfidenz (P10-Karte); Katalog v1: Kontrakt-Untererfüllung,
  Preisabweichung Einkauf, OP-Eskalation, QS-Fristen.
- Akzeptanz: Worklists entstehen ohne Nutzeraktion; jeder Eintrag erklärt sich;
  Abarbeitung ausschließlich über normale Masken-Aktionen.

---

## M5 — Horizont 2028+ (bewusst grob)

- **Multimodal:** Foto → Beleg (Lieferschein-Scan an der Rampe), AR-Kommissionierung
- **Präskriptive Cockpits:** Simulation („Was passiert bei Trocknung jetzt vs.
  morgen?") als Copilot-Werkzeug mit Modell-Transparenz
- **Verhandlungs-Agenten:** Einkaufs-Agent bereitet Kontraktverhandlung vor
  (Marktdaten MATIF, Historie) — Abschluss bleibt Mensch
- **Voll-Duplex-Sprache:** Dialogisches Arbeiten (V5) nach Reifung V3/V4
- Einstiegskriterium je Thema: stabile Objekte im Canonical Model (kein
  „AI-first auf instabilen Objekten" — Positionierungsregel).

---

## Metriken (je Milestone messen, im Workboard dokumentieren)

| Metrik | Baseline erheben in | Ziel M2 | Ziel M4 |
|---|---|---|---|
| Klicks bis Kernaufgabe (Top-10-Aufgaben) | M1 | −30 % | −60 % |
| Anteil Omnibox-Einstiege an Navigationen | M1 | ≥ 25 % | ≥ 50 % |
| Intent-Trefferquote (ohne Korrektur) | M1 | ≥ 80 % | ≥ 92 % |
| Medienbrüche je Kette K1–K4 (Zählung) | M1 | −50 % | ~0 |
| Zeit Annahme-Wiegung (Ankunft→gebucht) | M3-Pilot | — | −40 % |
| SDs generatorReady mit Voll-AgentContract | heute 13 | 25 | 60 |
| Nutzer-Overlays aktiv ohne Support-Ticket | M2 | >0 | Standard |
| Automatisch projizierte Kalendereinträge (Quellen aktiv) | M1 | 5 Quellen | 10 Quellen inkl. E-Mail |

## Risiken & Gegenmittel

| Risiko | Gegenmittel |
|---|---|
| Chat wird Parallel-UI („Schatten-ERP") | Architekturregel + Test: kein Command ohne Masken-Pendant; Reviews gegen Meridian-Skill |
| Voice bucht falsch | V-Stufenmodell, voiceEnabled-Gate, Echo+Confirm, Danger nie voice |
| Overlay-Wildwuchs bricht Updates | schemaVersion-Bindung, Drift-Worklist, Sicherheits-Allowlist |
| Twin wird Deko statt Werkzeug | Twin nur mit Klick-Durchstich zu Objekt/Aktion abnehmbar |
| KI-Vorschläge ohne Vertrauen | P10-Pflichtfelder Begründung/Quelle/Konfidenz; Telemetrie Korrektur-Quote |
| Scope-Kriechen in M-Slices | Slice-YAML mit Dateibesitz + Akzeptanz; ein Slice = ein Push-Zyklus |
