---
title: UIX-Zukunft Masterplan — VALEO NeuroERP 2035
type: reference
audience: [agent, entwickler, design, qa, produkt]
owner: Claude
status: aktiv
last_reviewed: 2026-07-06
version: 1.0.0
description: Zielbild, Pattern-Bibliothek, Wireframes und Prozessketten-Design für das Zukunfts-UIX auf der Meridian-Kette.
---

# UIX-Zukunft Masterplan — VALEO NeuroERP 2035

> **Leitsatz:** Die Maske ist keine Seite, die jemand gebaut hat. Die Maske ist eine
> Projektion aus Canonical Domain Model, Workflow-Zustand und Rollenkontext —
> erzeugt vom Single Mask Builder, bedienbar von Mensch **und** Agent, per Klick,
> Text **und** Sprache.

Dieses Dokument plant das UIX der nächsten 10 Jahre so, dass es **heute** begonnen
werden kann und **updatefähig** bleibt. Es ergänzt
[valeo-meridian-experience.md](valeo-meridian-experience.md) und ändert dessen
Architekturregel nicht:

```text
ScreenDefinition -> RenderPlan -> useUniversalMaskRuntime -> UniversalMaskRenderer
```

**Alles Folgende ist Builder-Evolution. Nichts Folgendes ist ein Parallelsystem.**

---

## 1. Die drei Interaktionsebenen — ein Vertrag

Der zentrale Entwurfsgedanke: Klassische Maske, Conversational UI und KI-Agent sind
**drei Frontends desselben Vertrags**. Was heute schon existiert
(`agentContract`, `examplePrompts`, `dangerousActions`, `commandEndpoint`,
ActionRuntime, Agent-Safety-Gates UIX-046/048) wird zur tragenden Säule:

| Ebene | Nutzer | Eingang | Ausgang | Sicherheitsmodell |
|---|---|---|---|---|
| **Maske** | Experte am Desktop | Klick, Tastatur, Diktat | Floorplan-Rendering | Permission + Confirmation + AuditReason |
| **Dialog** | Jeder (Omnibox, Sprache) | Natürliche Sprache → Intent | Vorschau (Worklist/Command-Preview) → Bestätigung | identische CommandEndpoints, `dangerousActions` nie ohne visuelle Bestätigung |
| **Agent** | KI (Copilot, Ambient) | AgentContract + Read Models | Worklist-Einträge, Vorschläge, HITL-Anträge | `forbiddenForAgents`, `humanApprovalRequired`, Audit-Pflicht |

**Konsequenz:** Es gibt keinen "Chatbot neben dem ERP". Die Omnibox kompiliert
Sprache/Text in dieselben ScreenDefinitions, Filter, Worklists und Commands, die
auch die Maske nutzt. Ein Intent, der keine Maske hat, hat auch keinen Chat-Weg —
das erzwingt Modellpflege statt Wildwuchs.

## 2. Design-Prinzipien (verbindlich)

1. **Prozess zuerst, Maske folgt.** Jede Maske kennt ihre Prozesskette und zeigt
   „Woher komme ich / Wo stehe ich / Was ist der nächste Schritt".
2. **Ein Vertrag, drei Ebenen.** Keine Funktion nur im Chat, keine nur in der Maske.
3. **Dichte ist Respekt.** `expertDense` für Profis ist Standard-Zielbild am Desktop;
   Karten ersetzen niemals ERP-Tabellen.
4. **Gefahr braucht Ritual.** Buchen, Stornieren, Freigeben, Zahlen: Confirmation,
   AuditReason, Vier-Augen — auf allen drei Ebenen identisch, per Sprache niemals
   verkürzt.
5. **KI erklärt sich.** Jeder Vorschlag trägt Begründung, Quelle und Konfidenz;
   der Copilot ist Rail, nie Vollbild-Übernahme.
6. **Kontext statt Navigation.** Rollen-Workspace + ContextRail ersetzen Menü-Tiefe;
   die Navigation ist der Fallback, nicht der Hauptweg.
7. **Kein Medienbruch.** Zettel, Excel-Export-Reimport, Telefonnotizen: jeder
   erkannte Bruch wird als Auto-Capture-/Inbox-Muster in die Kette geholt.
8. **Offline-fähig, wo Staub ist.** Waage, Lager, Feld: Transaktions-Floorplans
   funktionieren mit Queue (POS-Offline-Queue als Vorbild).
9. **Personalisierung ohne Fork.** Nutzer-Anpassung = deklaratives Overlay über
   der ScreenDefinition, nie kopierte Maske (Updatefähigkeit!).
10. **Messbar professionell.** Readiness-Gates, Visual-Audit (1366/1440/1920) und
    Performance-Budgets entscheiden, nicht Geschmack.

## 3. Trend-Mapping: 5 Zukunftstrends → Builder-Verträge

| Trend (10-Jahres-Erwartung) | VALEO-Umsetzung (Builder-Capability) | Fundament heute |
|---|---|---|
| Conversational UI & KI-Agenten | **Omnibox + Intent-Compiler**: NL → `{screen, filter, command}`-Plan mit Vorschau; Ausführung nur über CommandEndpoints | ActionRuntime (UIX-045), CommandEndpoints (046), Agent-Safety (048), examplePrompts je SD |
| Kontextabhängige Workspaces | **Rollen-Workspaces**: `cockpit`-Floorplans je Rolle aus Read Models + Worklist-Kacheln, Zeit-/Saisonkontext (Erntepeak!) | 13 native SDs, Worklist-Muster (Qualitäts-Nachtrag), Read-Model-Snapshots |
| 3D-Visualisierung & Digital Twins | **Twin-Panel als Renderer-Primitive** im `cockpit`-Floorplan: Hofplan/Silo-Belegung interaktiv, klickbare Zellen → ObjectPage | agrar-silo-materialfluss-studio, Hofplan-Asset, silo_target_cell-API, kunden_geo/Karten |
| Low-Code/No-Code | **ScreenDefinition-Studio**: Fach-Admin-Editor erzeugt/ändert SDs deklarativ; Nutzer-Overlays (Spalten, Varianten, Feld-Sichtbarkeit) | ScreenDefinition IST das No-Code-Artefakt; Promotion-Pfad temp→native + advisoryScore; vordruck-editor |
| Kollaboration & ESG | **ContextRail-Erweiterung**: Notizen/@-Mentions am Datensatz (`contextRail: 'collab'`), ESG-KPI-Kacheln (THG je Charge) im Summary/Cockpit | crm_capture_inbox, sustainability-/Massebilanz-APIs, KPI-Summary-Renderer |

## 4. Die AppShell der Zukunft

### Wireframe W-00 — AppShell mit Omnibox (alle Auflösungen)

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ ⌂ VALEO  ▾Niederlassung Emden   [🔍⌘K  „Was möchten Sie tun?"    🎤]  🔔3 ◉JW│
├──────────┬─────────────────────────────────────────────────────┬───────────┤
│ NAV      │  WORKSPACE (rollenbasiert, Floorplan-Inhalt)        │ CONTEXT   │
│ (einge-  │                                                     │ RAIL      │
│ klappt,  │  … worklist / objectPage / transaction /            │ audit ·   │
│ Fallback)│    cockpit / wizard …                               │ workflow ·│
│          │                                                     │ copilot · │
│ ★ Favorit│                                                     │ collab    │
│ ⏱ Zuletzt│                                                     │           │
├──────────┴─────────────────────────────────────────────────────┴───────────┤
│ STATUSLEISTE: Tenant · Geschäftsjahr/Periode · Sync/Offline-Queue · Version │
└────────────────────────────────────────────────────────────────────────────┘
```

**Omnibox (⌘K) — das eine Eingabefeld.** Drei Modi, automatisch erkannt:

```text
┌─ ⌘K ────────────────────────────────────────────────────────────┐
│ > überfällige Aufträge mit fehlender Rohware        [🎤] [↵]    │
├─────────────────────────────────────────────────────────────────┤
│ VERSTANDEN ALS  (Intent-Vorschau — nichts wird ausgeführt)      │
│ 📋 Worklist: Verkaufsaufträge · Status=überfällig               │
│    + Join: Rohware-Verfügbarkeit < Bedarf          [Öffnen ↵]  │
│ 💡 Copilot: 3 Lösungsalternativen vorschlagen       [Vorschau]  │
│ ⚡ Befehle:  „Auftrag 4711 anlegen…"                 [Formular]  │
├─────────────────────────────────────────────────────────────────┤
│ zuletzt: Wiegekarte 8842 · Kunde Folkerts · Zahlungslauf Juli   │
└─────────────────────────────────────────────────────────────────┘
```

Regeln:
- **Vorschau vor Ausführung.** NL-Eingabe erzeugt einen sichtbaren Plan
  (Ziel-Maske + Filter oder Command + Payload). Enter öffnet/übergibt — führt nie
  direkt eine Mutation aus.
- **Befehle mit `dangerLevel >= moderate`** öffnen immer das reguläre
  Confirmation-Ritual der Maske (UIX-047), inkl. AuditReason.
- 🎤 = Push-to-talk; Transkript erscheint editierbar in der Omnibox (nie „blind").

## 5. Pattern-Bibliothek — was immer wiederkehrt

Jedes Muster ist eine Builder-/Renderer-Fähigkeit, **keine** Seiten-Kopiervorlage.

| # | Pattern | Vertrag/Renderer | Regeln |
|---|---|---|---|
| P1 | **ObjectHeader** | `RenderPlan.shell` → FastSummaryRenderer | Identität + Status-Chip + 3–5 KPIs + letzte Änderung + nächste empfohlene Aktion |
| P2 | **ActionBar** | ActionBarRenderer | genau 1 Primäraktion; Danger separiert; Confirmation+AuditReason ab `moderate` |
| P3 | **StatusChip-Semantik** | tokens | Entwurf/Aktiv/Gesperrt/Storniert/Abgeschlossen — farbfest über alle Domänen |
| P4 | **Tabellenprofile** | FastTableRenderer | `standard/financial/inventory/audit` — Beträge rechts, Summen, Sticky-Spalten, Varianten |
| P5 | **Worklist-Kachel** | Worklist + Registry | Titel, Zähler, Alter des ältesten Eintrags, 1-Klick zur gefilterten Liste |
| P6 | **ContextRail-Sektionen** | WorkflowPanelRenderer | audit/workflow/copilot/collab — zuklappbar, nie leer bei Detail/Cockpit |
| P7 | **Confirmation-Ritual** | UIX-047 Dialog | Zusammenfassung der Wirkung, AuditReason-Pflichtfeld, Vier-Augen-Hinweis |
| P8 | **Inbox/Klärfall** | capture-inbox-Muster | Quelle (Mail/Anruf/Scan), KI-Extrakt editierbar, Übernahme→Beleg, Rest→Klärliste |
| P9 | **Prozessband** | neu: shell.processRibbon | Kette als Chips: Kontrakt→Lieferung→Abrechnung; aktueller Schritt hervorgehoben; Klick=Navigation |
| P10 | **Copilot-Karte** | ContextRail | Vorschlag + Begründung + Quelle + Konfidenz + [Übernehmen]/[Verwerfen], Übernahme = normaler Command |
| P11 | **VoiceBar** | neu: shell.voice | Push-to-talk, Live-Transkript, Kommando-Echo („Verstanden: Zweitwiegung bestätigen?") |
| P12 | **Twin-Panel** | neu: Renderer-Primitive | 2D/3D-Belegungsansicht (Silo/Lager/Hof), Zellen klickbar, Live-Werte aus Read Model |
| P13 | **ESG-KPI-Kachel** | Summary/Cockpit | CO₂e je Charge/Prozess, Trend, Datenquelle sichtbar |
| P14 | **Offline-Badge + Queue** | Statusleiste | anstehende Offline-Buchungen sichtbar, Konfliktlösung als Worklist |
| P15 | **EmptyState/ProblemDetails** | vorhanden | nie stille Leere bei Datenfehlern (financial-Profil erzwingt das schon) |
| P16 | **Planungskalender** | neu: calendar-Primitive + `calendarProjection` | Termine sind automatische Projektionen aus Belegen/Feldern (keine Doppelpflege); Layer je Quelle; Klick = ObjectPage; ICS-Abo |

## 6. Wireframes je Floorplan

### W-01 `worklist` — z. B. Offene Posten (financial)

```text
┌ Offene Posten · Debitoren ────────────────────────────── [⟳] [⚙Varianten ▾] ┐
│ [🔍 Filter…] [Fällig ▾] [Niederlassung ▾] [Betrag ▾]   Chips: >30 Tage ✕    │
│ Σ 1.284.310,55 €   überfällig: 214.882,10 €   Anzahl: 312    [Mahnlauf ▶]   │
├──────┬──────────────┬──────────┬───────────┬────────────┬─────────┬─────────┤
│ Nr.  │ Kunde        │ Beleg    │  Fällig   │     Betrag │ Status  │ ⋮       │
│ 4711 │ Folkerts KG  │ RE-88213 │ 12.06.26 ⚠│  12.480,00 │ offen   │ [Mahnen]│
│ 4712 │ Janssen GbR  │ RE-88214 │ 28.06.26  │   3.290,50 │ offen   │ …       │
│ ████ sticky: Nr./Kunde ████            Beträge rechtsbündig, Summenzeile ███ │
├──────────────────────────────────────────────────────────────────────────── ┤
│ Summen (gefiltert): 214.882,10 €  ·  Seite 1/7  ·  Variante „Mahnvorschlag"  │
└──────────────────────────────────────────────────────────────────────────── ┘
```

### W-02 `objectPage` — z. B. Kunde 360 (CRM-Referenz)

```text
┌ Folkerts Landhandel KG · Kd-Nr 10233 ── [Aktiv] ── Ø-Zahlung 12 T ─ GAP ✓ ┐
│ Umsatz YTD 1,2 M€ · OP 12.480 € ⚠ · Letzter Kontakt: gestern (Anruf-STT)  │
│ [＋Aktivität]  [Auftrag anlegen]  [▾ mehr]                    ‖ CONTEXT   │
├ Prozessband: Lead ▸ Kunde ▸ Kontrakt ▸ Lieferung ▸ Abrechnung ┤‖ ────────  │
├ Tabs: Übersicht · Kontakte · Kontrakte · Belege · Geo · Doku ┤‖ Workflow:  │
│                                                              ‖ nächste:    │
│  [Kacheln: offene Bestellungen | Preisspiegel | Reklamation] ‖ „Kontrakt   │
│  [Aktivitäten-Timeline mit Mail/Anruf/Notiz — P8-Quellen]    ‖  verlängern"│
│                                                              ‖ Copilot 💡: │
│                                                              ‖ „Raps-Vor-  │
│                                                              ‖ kontrakt?"  │
│                                                              ‖ Collab 💬:  │
│                                                              ‖ @Meyer:     │
│                                                              ‖ „Skonto ok" │
└──────────────────────────────────────────────────────────────┴────────────┘
```

### W-03 `transaction` — z. B. Annahme-Wiegung (Voice-Vorzeigefall)

```text
┌ ANNAHME · Wiegung #8842 ──────────────────────────── [Offline-Queue: 0] ┐
│ Kontrakt 2026-RAPS-114 · Folkerts KG · Raps · avisiert 24,0 t          │
├─────────────────────────────────────────────────────────────────────────┤
│   ERSTGEWICHT        38.420 kg   ✓ 10:41                                │
│   ZWEITGEWICHT       14.180 kg   ● LIVE von Waage 1                     │
│   NETTO              24.240 kg   (+1,0 % über Avis — ok)                │
│   Feuchte 8,9 % ✓ · Besatz 1,8 % ✓ · [Labor: Probe 4471 anhängen]      │
├─────────────────────────────────────────────────────────────────────────┤
│           [  ZWEITWIEGUNG BESTÄTIGEN  ]        [Abbrechen] [Klärfall]   │
│  🎤 „Zweitwiegung bestätigen" → Echo + großer Bestätigungs-Screen       │
│  Validierung inline: Kontraktmenge, Sperren, QS-Status — vor dem Buchen │
└─────────────────────────────────────────────────────────────────────────┘
```

Freisprech-Regeln (Waage/Lager): große Targets, akustisches Echo, nur
whitelisted Kommandos (`voiceEnabled: true` je Action), niemals Danger-Aktionen.

### W-04 `cockpit` — z. B. Lager-/Silo-Leitstand mit Twin-Panel

```text
┌ LEITSTAND EMDEN · Erntewoche 29 ────────────────────────────────────────┐
│ KPI: Annahmen heute 42 · Ø Wartezeit 11 min ⚠ · Trocknergas 84 % · CO₂e │
├──────────────────────────────┬──────────────────────────────┬───────────┤
│ TWIN: Hofplan/Silo (P12)     │ WORKLISTS                    │ CONTEXT   │
│  ┌──┐┌──┐┌──┐  Zelle 7:      │ ▸ Qualitäts-Nachtrag (3)     │ RAIL      │
│  │S1││S2││S3│  Weizen 78 %   │ ▸ Klärfälle Annahme (1)      │ Workflow  │
│  │▓▓││▓░││░░│  12,4 % H₂O    │ ▸ Frachtaufträge offen (6)   │ + Copilot │
│  └──┘└──┘└──┘  [→ Zelle]     │ ▸ Trocknungsfreigaben (2)    │ „Zelle 3  │
│  Klick auf Zelle = ObjectPage│                              │ für Raps  │
│  silo_target_cell-Vorschlag  │                              │ freihalten"│
├──────────────────────────────┴──────────────────────────────┴───────────┤
│ Ausnahmen-Band: nur Abweichungen (Ampel), kein Daten-Tapetenmuster       │
└──────────────────────────────────────────────────────────────────────────┘
```

### W-05 `wizard` — z. B. Monatsabschluss/DATEV

```text
┌ MONATSABSCHLUSS 06/2026 ── Schritt 3/6: Abstimmung ──────────────────────┐
│ ①✓ Perioden-Check  ②✓ OP-Abgleich  ③● Abstimmung  ④ Export ⑤ Doku ⑥ Sperre│
├──────────────────────────────────────────────────────────────────────────┤
│ Blocker (2):  ✗ Neben-/Hauptbuch-Differenz 412,33 € [→ Klärung]          │
│               ✗ 3 Belege ohne Steuerschlüssel        [→ Worklist]        │
│ Gates: alle grün nötig für ④ — Wizard merkt Zwischenstand (resume)       │
├──────────────────────────────────────────────────────────────────────────┤
│ [◀ Zurück]                        [Weiter ▶ (gesperrt: 2 Blocker)]       │
│ Protokoll/Audit-Trail wird automatisch je Schritt geschrieben            │
└──────────────────────────────────────────────────────────────────────────┘
```

### W-06 Conversational-Overlay (aus Omnibox, komplexer Intent)

```text
┌ 💬 „Zeig mir alle überfälligen Kundenaufträge mit fehlender Rohware      │
│     und schlage Lösungsalternativen vor."                                │
├──────────────────────────────────────────────────────────────────────────┤
│ PLAN (transparent):                                                      │
│  1. Worklist sales/orders · fällig<heute · rohware.deckung<100 % → 7 Stk │
│  2. Copilot-Analyse je Auftrag (Zukauf | Umlagerung | Teillieferung)     │
├──────────────────────────────────────────────────────────────────────────┤
│ ERGEBNIS: Tabelle (worklist, standard-Profil) + Copilot-Spalte           │
│  4711 Folkerts  −6 t Raps  💡 Umlagerung aus Leer (Bestand 9 t) [Prüfen] │
│  4718 Janssen   −2 t Gerste 💡 Zukauf: 2 Angebote im Einkauf    [Prüfen] │
│ [Als Worklist speichern] [Ergebnis an @Disposition] — keine Auto-Buchung │
└──────────────────────────────────────────────────────────────────────────┘
```

### W-07 Planungskalender — Zeit als Projektion (P16)

**Konzept:** Niemand pflegt Termine doppelt. Jede Entität mit Zeitbezug deklariert
eine `calendarProjection` (Feld → Termin-Typ), der Builder projiziert sie in ein
kanonisches `calendar_items`-Read-Model. Der Kalender ist ein `cockpit`-Floorplan
mit Kalender-Primitive — dieselben Gates, derselbe Klick-Durchstich.

Automatische Quellen (Layer, je Rolle vorbelegt, einzeln schaltbar):

| Layer | Quelle (existiert heute) | Beispiele |
|---|---|---|
| 💶 Finanzen | periodische Buchungen, OP-Fälligkeiten, Zahlungsläufe | wiederkehrende Umsätze, Skonto-/Zahlungsziele |
| 📆 Fristen | Kontrakte, Rabattstaffeln, Zertifikate | Ende Frühbezugsrabatt, Andienungsfristen, QS-/Sachkunde-Ablauf |
| 👥 CRM | Wiedervorlagen, Reminder, Besuchsplanung | Kunden-Reminder, Saisongespräch vor Aussaat |
| 🚚 Logistik | Avis, Liefer-/Abholtermine, **E-Mail-Extraktion (P8)** | Lieferantentermin aus Mail → Vorschlag, editierbar |
| 🎓 Personal | Schulungen, Unterweisungen, Sachkunde | Pflichtschulung, Erste-Hilfe-Auffrischung |
| 🌾 Saison | Kulturkalender, Kampagnenfenster | Erntepeak-Vorbereitung, Düngefenster |

```text
┌ PLANUNGSKALENDER · Juli 2026 ──────── [Monat|Woche|Agenda] [＋Layer ▾] [ICS ⤓] ┐
│ Layer: 💶 Finanzen ✓  📆 Fristen ✓  👥 CRM ✓  🚚 Logistik ✓  🎓 ○  🌾 ○        │
├── FRISTENBAND (nächste 14 Tage, immer sichtbar) ────────────────────────────── │
│ ⚠ 15.07. Ende Frühbezugsrabatt DüKa │ 18.07. QS-Audit │ 31.07. UStVA          │
├────────┬────────┬────────┬────────┬────────┬─────────────────────────────────┤
│ Mo 13  │ Di 14  │ Mi 15  │ Do 16  │ Fr 17  │ ◀ DETAIL (Klick auf Eintrag)    │
│ 💶 Abo-│ 🚚 Avis│ 📆 FRIST│ 👥 Fol-│ 💶 Zah-│ 🚚 Lieferung Baywa 60 t KAS     │
│ RE Lauf│ Raps   │ Frühbe-│ kerts  │ lungs- │ Quelle: E-Mail 12.07. 09:14 ✉   │
│ (12)   │ 60 t   │ zug ⚠  │ Rückruf│ lauf 🔒│ [→ Bestellung 7712] [Bestätigen]│
│        │ ✉ Vor- │        │ 9:00   │        │ [Termin verschieben]            │
│        │ schlag │        │        │        │ Extraktion editierbar (P8)      │
├────────┴────────┴────────┴────────┴────────┴─────────────────────────────────┤
│ Agent-Zeile 💡: „3 Kontrakte laufen im August aus — Verlängerung planen?"     │
└────────────────────────────────────────────────────────────────────────────── ┘
```

Regeln:
- **Kein Eintrag ohne Objekt.** Jeder Termin verlinkt auf Beleg/Kunde/Kontrakt
  (ObjectPage); manuelle „lose" Termine sind erlaubt, aber markiert.
- **E-Mail-Termine sind Vorschläge** (P8-Muster): editierbar, bestätigbar,
  mit Quellen-Nachweis — nie stillschweigend fest.
- **Aktionen aus dem Kalender** (bestätigen, verschieben, Rechnung auslösen)
  sind normale Commands mit Ritual; der Zahlungslauf bleibt auch hier 🔒.
- **Erinnerungen** laufen über die Benachrichtigungs-Inbox der Shell (W-00),
  optional ICS-Abo für Outlook/Handy (read-only).
- Omnibox versteht Zeit: „was steht nächste Woche an?" → Agenda-Ansicht gefiltert.

## 7. Prozessketten end-to-end (Doc-Chain bleibt Gesetz)

Jede Kette definiert: Floorplan-Abfolge, Medienbruch-Killer, Voice-Punkte,
Agent-Punkte. Das Prozessband (P9) macht die Kette in jeder Maske sichtbar.

### K1 Ernte: Kontrakt → Avis → Wiegung → Qualität → Trocknung → Einlagerung → Abrechnung
- Floorplans: objectPage → worklist → **transaction(Voice)** → transaction → cockpit(Twin) → wizard(Sammelabrechnung)
- Medienbruch-Killer: Wiegezettel digital, Laborwerte-Auto-Übernahme, Nachtrag-Worklist (existiert)
- Agent: Zellen-Vorschlag (silo_target_cell), Trocknungskosten-Hinweis, Kontrakt-Erfüllungsgrad-Warnung

### K2 Verkauf: Angebot → Auftrag → Lieferschein → Wiegung → Rechnung → OP → Zahlung
- Konsistenzprinzip (docs/MASKEN.md): identische Layout-Struktur über die Belegkette
- Agent: Bestell-Inbox (Mail/Anruf→Auftragsentwurf, existiert als Muster), Kreditlimit-Ampel im ObjectHeader
- Voice: Kommissionier-/Verlade-Bestätigungen im Lager

### K3 Einkauf: Bedarf → Bestellung → Avis → Wareneingang → Rechnungsprüfung → **Zahlungslauf**
- Zahlungslauf bleibt Referenz für „Gefahr braucht Ritual": `forbiddenForAgents`,
  Vier-Augen, AuditReason, `dangerousActions` (heute schon so verdrahtet)
- Agent: 3-Wege-Match-Vorschläge (procurement_match), Abweichungs-Worklist

### K4 CRM-Durchdringung: Signal → Kontakt → Chance → Kontrakt
- Auto-Capture (Mail/IMAP, Telefon-STT) → Inbox (P8) → Kunde-360-Timeline
- Copilot: nächste beste Aktion je Kunde (Saison! Vorkontrakte vor Aussaat)

## 8. Sprachsteuerung — Ausbaustufen & Sicherheitsmodell

| Stufe | Fähigkeit | Sicherheit |
|---|---|---|
| V1 | Diktat in jedes Textfeld + Omnibox-Spracheingabe (Transkript editierbar) | rein Eingabehilfe, keine Ausführung |
| V2 | Kommando-Grammatik: „öffne", „filtere", „zeige" → Navigation/Filter | nur idempotente Reads |
| V3 | Aktions-Kommandos auf whitelisted Actions (`voiceEnabled`) mit Echo + visueller Bestätigung | nie `dangerLevel>=high`, nie ohne Screen-Confirm |
| V4 | Freisprech-Arbeitsmodus (Waage/Lager/Inventur): geführter Dialog, akustisches Feedback | Geräte-/Orts-Bindung, Session-PIN, Vollprotokoll |

Grundsätze: Transkript ist immer sichtbar und korrigierbar; Sprache ist ein
**Eingabekanal**, nie ein eigener Berechtigungsweg; `AuditReason` kann diktiert,
muss aber bestätigt werden.

## 9. Agentische Nutzung — vom Copilot zum Ambient Agent

1. **Copilot (Rail):** erklärt Maskeninhalt, schlägt nächste Aktion vor,
   beantwortet „Warum ist dieser Beleg gesperrt?" aus Audit+Workflow-Daten.
2. **Inbox-Agenten:** verwandeln Unstruktur (Mail, Anruf, Scan) in editierbare
   Entwürfe — Mensch übernimmt (P8). Heute: Bestell-Inbox, CRM-Capture.
3. **Ambient Agents:** überwachen Read Models, füllen Worklists (Klärfälle,
   Abweichungen, Fristen) — sie **buchen nicht**, sie **melden**.
4. **Delegierte Ausführung (Ausbau):** Agent darf whitelisted Commands mit
   `humanApprovalRequired` vorbereiten; Freigabe bleibt Mensch (HITL-Antrag
   erscheint als Confirmation-Ritual beim Verantwortlichen).

Vertragspflege: jede native SD hält `examplePrompts` aktuell (Agent-Handbuch wird
generiert — existiert), `sensitiveFields` deklariert, Gefahrenklassen gepflegt.
**Agent-Readiness wird Gate**: ohne vollständigen AgentContract kein
`generatorReady` (Erweiterung der bestehenden Readiness-Checks).

## 10. Personalisierung & No-Code — ohne Fork, ohne Update-Bruch

Schichtenmodell (unten schlägt oben nie):

```text
┌ Nutzer-Overlay      (Spaltenwahl, Varianten, Dichte, Kachel-Anordnung)   ┐
├ Rollen-Overlay      (Pflichtfelder-Sicht, Workspace-Zusammenstellung)    │
├ Tenant-Overlay      (Begriffe, Zusatzfelder aus Custom-Field-Registry)   │
├ ScreenDefinition    (nativ, versioniert, generatorReady, im Registry)    │
└ Canonical Domain Model + Workflow (Quelle der Wahrheit)                  ┘
```

- Overlays sind **deklarative Diffs** (JSON), serverseitig gespeichert,
  schemaversioniert — bei SD-Updates werden verwaiste Overlay-Einträge
  erkannt und als „Anpassung prüfen"-Worklist gemeldet statt still zu brechen.
- **ScreenDefinition-Studio** (Fach-Admin): erzeugt/ändert SDs im Browser
  (Drag-and-drop über Feld-/Tab-/Action-Katalog), Ausgabe ist eine normale SD,
  die durch **dieselben Readiness-Gates** muss (advisoryScore, Meridian-Pflicht).
  Promotion-Pfad temp→native existiert bereits und wird der Studio-Workflow.
- Verboten bleibt: Overlays, die Sicherheitsverhalten ändern (Confirmation,
  dangerLevel, Permissions sind nicht overlaybar).

## 11. Updatefähigkeit — wie 2035 heute schon passt

- **`schemaVersion` + Capability-Flags:** neue Shell-Fähigkeiten (voice, twin,
  collab, esg) sind optionale RenderPlan-Capabilities; alte Clients ignorieren
  sie, Gates fordern sie erst ab Aktivierung je Maskenklasse.
- **Renderer-Primitive statt Speziallayouts:** Twin-Panel, VoiceBar, Collab-Rail
  sind Primitive im Renderer-Baukasten — jede künftige Maske erbt sie gratis.
- **Read-Model-First:** Cockpits/KPIs hängen an Read Models, nicht an Endpunkten
  einzelner Masken — neue Sichten = neue Projektion, kein Maskenumbau.
- **Contract-Tests als Zeitmaschine:** Agent-Contract-Tests (270 grün) und
  Visual-Audits sichern, dass Evolution nie stillschweigend Verhalten ändert.

## 12. Figma-Übertrag

Kein direkter Figma-Zugriff aus der Agent-Umgebung; dieses Dokument + die
Wireframe-Galerie (HTML-Artefakt) sind die Vorlage. Empfohlene Frame-Struktur im
Figma-File (`Ohne Namen`, node 0-1):

```text
📁 00 Foundations   → Tokens: Dichte, Status-Farben, Tabellenprofile
📁 01 AppShell      → W-00 Omnibox (3 Zustände: leer/Intent-Vorschau/Voice)
📁 02 Floorplans    → W-01…W-05 je 1440x900 + 1366x768-Variante
📁 03 Conversational→ W-06 Overlay + Confirmation-Ritual (P7)
📁 04 Twin & ESG    → W-04-Detail: Silo-Zellen-Zustände, ESG-Kacheln
📁 05 Prozessketten → K1–K4 als Flow-Diagramme (Floorplan-Abfolge)
📁 06 Kalender      → W-07 Monat/Woche/Agenda + Fristenband + Layer-Zustände
📁 07 Komponenten   → P1–P16 als Komponenten-Sheet
```

## 13. Nächste Schritte

Umsetzungsreihenfolge, Milestones, Slices und agent-fähige Prompts:
→ [uix-zukunft-roadmap.md](uix-zukunft-roadmap.md)
