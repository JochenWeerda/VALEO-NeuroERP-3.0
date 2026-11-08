---
title: Belegmaskenfamilie — Vererbungsmodell und Migrationsplan
type: architecture
audience: [architect, agent, entwickler]
owner: Cursor Composer (Plan)
status: aktiv
last_reviewed: 2026-10-22
version: 1.0.0
description: OOP-analoge Parent/Child-Ordnung der eingehenden und ausgehenden Belegmasken; Vererbung von ScreenDefinition/Studio; Mapping der Alt-Einstiege; Migrationsreihenfolge ohne Studio-Import-Illusion.
---

# Belegmaskenfamilie — Vererbungsmodell und Migrationsplan

Stand: 2026-10-22. **Planungsartefakt** (keine Großimplementierung).
Meridian-/Builder-Regel: Qualität entsteht über `ScreenDefinition → RenderPlan → UniversalMaskRuntime → UniversalMaskRenderer`, nicht über Einzelmasken-Redesign.

## Zweck und Abgrenzung zu bestehender Doku

| Dokument | Rolle |
|---|---|
| **Dieses Dokument** | Familienbaum, Parent/Child-Vererbung, Routen-Mapping, Migrationsreihenfolge, Runtime-vs-Import-Grenze |
| [maskenfamilien-taxonomie.md](maskenfamilien-taxonomie.md) | **Systemweite** Kategorien (Beleg/Stamm/Liste/Worklist/Ausnahme) und Cluster-Roadmap P0–P3; Beleg ist Spezialfall |
| [beleg-studio-variantenmatrix.md](../../design/beleg-studio-variantenmatrix.md) | Kanonische 9 Varianten + Alt-Einstieg→Zielvariante (Zielweg) |
| [belegmaske-varianten-masterplan.md](../../design/belegmaske-varianten-masterplan.md) | Fachentscheidungen E1–E4, Wellen BELEG-010ff, Belegvertrag |
| [studio-native-migration.md](../studio-native-migration.md) | Versionsbindung, Studio-Import, Create/Edit-Guards |
| [MASKEN.md](../../MASKEN.md) | Gewohnheits-Prinzip (Layout-Parität in der Belegfolge) |
| [flow-spine-ebene1-kriterienkatalog.md](../../design/flow-spine-ebene1-kriterienkatalog.md) | ProcessBand / Alltagstauglichkeit |

Keine zweite „14 Masken neu bauen“-Roadmap. Die Familie existiert bereits als Builder + Register; dieses Dokument ordnet sie explizit als **Vererbungsbaum** und benennt, was noch fehlt (Anfrage, Einkaufsangebot, Runtime-Verdrahtung, ProcessBand/Ribbon).

---

## 1. Familien-Taxonomie

### 1.1 Prinzip (OOP-Analog)

```
BelegMaskeParent (abstrakt / Basis 1.x.0)
├── AusgehendFamily (Richtung verkauf, Partner = Kunde)
│   ├── sales_offer
│   ├── sales_order
│   ├── sales_delivery          ← oft ohne Preise
│   ├── sales_invoice           ← bucht
│   └── sales_credit_memo       ← bucht
└── EingehendFamily (Richtung einkauf, Partner = Lieferant)
    ├── purchase_order
    ├── goods_receipt           ← oft ohne Preise
    ├── purchase_invoice        ← bucht
    └── purchase_credit_memo    ← bucht

Kandidaten (noch nicht in BELEGARTEN / Register):
  purchase_rfq (Anfrage) → purchase_offer (Lieferantenangebot) → purchase_order …
  Belastung (kein Alias von Gutschrift)
  Reine Finanzrechnung (AR/AP ohne Warenbezug) — eigener Fachfall, nicht still als Warenbeleg
```

Gemeinsame Maske ≠ gemeinsamer Datensatz: jeder Schritt ist ein eigener Beleg mit Kettenreferenz (Gewohnheits-Prinzip + Masterplan Vorgabe 2).

### 1.2 Parent-Schablone (was alle Children teilen)

Aus `build_beleg_screen_definition` / Basis in `config/document_screen_versions.json`:

| Bereich | Inhalt im Parent |
|---|---|
| Floorplan | `transaction`, sticky Header/Footer, desktopDense |
| Reiter | `kopf`, `positionen`, `kette`, `dokumente`, `historie` |
| Header | Beleg-Nr., Status, Datum |
| Partner | Rolle aus Variante (Kunde/Lieferant), Lookup bei Create |
| Positionen | Mengen immer; Preise/Steuer/Aufwandskonto nur wenn `mit_preisen` |
| Summen | nur preisende Varianten; Server filtert ohne Preisrecht |
| Toolbar / Actions | aus Belegkommandos (`enabledWhen` aus Server-`aktionen`) |
| Create/Edit | zentral DocFlow Create/Update + Maskenprovenienz |
| Adapter | native Belegweg `/api/v1/belege/{belegart}/…` |

### 1.3 ProcessBand vs ProcessRibbon (nicht zusammenführen)

| Baustein | Aufgabe | Vererbung |
|---|---|---|
| **ProcessBand** | Stand des *einen* Vorgangs: Phasen, genau eine nächste Aktion, Blocker | Parent kann `workflow.phases` + Runtime-`WorkflowState` vorsehen; Children setzen Phasenlabels/Statusmapping |
| **ProcessRibbon** (UIX-091) | Navigation der *Belegkette* (Schritt → Zielmaske) | Parent deklariert Ketten-ID; Child setzt `stepKey` / erlaubte Folgeschritte aus `folgebelege` |
| **DocumentCaseBand** | Legacy-/Übergangsbindung an Flow-Spine | Nicht Teil der kanonischen Parent-SD; Paritätslücke z. B. Bestellung-Native |

Aktueller Parent setzt `noWorkflowReason` (Stand/Aktion kommen aus Server-`aktionen`). ProcessBand ist damit **noch nicht** über `workflow.phases` verdrahtet — geplante Parent-Erweiterung, kein Child-Sonderweg.

---

## 2. Vererbungsmodell (ScreenDefinition / Studio)

### 2.1 Was der Code heute schon tut

Authoring-Quelle: `app/core/screen_definitions_beleg.py` + Variantenmetadaten in `app/core/belegvertrag.py` (`BELEGARTEN`).
Materialisiertes Register: `config/document_screen_versions.json` (append-only Bases + Variant-Patches).

```
Base 1.x.0  (Parent-Felder: layout, mode, identityField, …)
    +
Variant-Patch (ersetzt ganze Root-Keys, insbesondere Arrays — kein positionsweises Deep-Merge)
    =
Aufgelöste Child-ScreenDefinition  (id: beleg/{belegart-mit-bindestrichen})
```

Studio: Ausgangsimport sichert Snapshot + Versionsverweis; editierter Entwurf hat eigene Revision. Import ≠ Runtime-Aktivierung (siehe §5).

### 2.2 Was Child erbt vs. überschreibt

| Schicht | Erbt vom Parent | Child-Override (deklarativ) |
|---|---|---|
| Layout / Floorplan / Density | ja | nur mit Begründung + neuer Basisversion |
| Reiter-Gerüst | ja | Zusatzreiter nur als registrierter Fachbaustein |
| Kopffelder | Basis + Partnerlabels | Bezeichner (`… Nr.`), Buchungsfelder wenn `bucht` |
| Positionsspalten | Mengen/Charge | Preise, Offen-Menge, Aufwandskonto |
| Actions | Kommando-Katalog-Anbindung | erlaubte Kommandos / Folge-Converts aus `folgebelege` |
| Validierung | DocFlow + Rechte serverseitig | Variante darf keine Fachlogik enthalten |
| Theme / Meridian | global geerbt | keine Masken-Sonderfarben (STUDIO-BELEG-THEME) |
| agentContract / testIds | Muster | Texte/Selectors je Belegart |

### 2.3 Override-Dokumentation (Pflicht)

Jeder Override gehört in **genau eine** der folgenden Quellen — nicht in die React-Seite:

1. `Belegvariante` in `belegvertrag.py` (Richtung, Preise, bucht, Folgekette)
2. Append-only Patch im Versionsregister (Release-Version, Hash, keine In-Place-Mutation)
3. Optional Studio-Entwurf (eigene Revision; Freigabe STUDIO-RELEASE-001; kein stiller Prod-Switch)

CI: Generator/Pytest vergleichen Builder ↔ materialisierte Fassung (Source-Drift = rot).

---

## 3. Mapping ~9–14 Einstiege → Parent/Child

Kanonische Children = 9. Alt-Einstiege ≈ 14 Navigations-/Editorpfade auf dieselben Children.

### 3.1 Ausgehend (Verkauf)

| Child (Variante) | Screen-ID (Familie) | Native / Runtime-Route (soweit vorhanden) | Legacy / Dual-Pfad | Dateien (Orientierung) |
|---|---|---|---|---|
| `sales_offer` | `beleg/sales-offer` | (Familie Create/Detail über Belegweg; Nav oft noch Legacy) | `sales/angebot/neu`, `sales/angebote` | `pages/sales/angebot-erstellen.tsx`, `angebote-liste.tsx` |
| `sales_order` | `beleg/sales-order` | `/sales/sales-order/:id` → SD `sales/sales-order` (älterer Native-Pfad parallel) | `sales/order-editor`, Neu-Editor | `sales-order-native.tsx`, `order-editor.tsx`, `OrderEditorLegacyPage.tsx` |
| `sales_delivery` | `beleg/sales-delivery` | `verkauf/lieferschein-native` (wo verdrahtet) | `verkauf/lieferschein-erfassung` | `verkauf/lieferschein-*.tsx` |
| `sales_invoice` | `beleg/sales-invoice` | Anzeige `verkauf/rechnung` (SD `sales/invoice`) | `sales/invoice-editor` (FormBuilder) | `verkauf/rechnung.tsx`, `sales/invoice-editor.tsx` |
| `sales_credit_memo` | `beleg/sales-credit-memo` | SD `sales/gutschrift` wo verdrahtet | `sales/credit-note-editor` | Credit-Note-Editor unter `pages/sales/` |

### 3.2 Eingehend (Einkauf)

| Child (Variante) | Screen-ID (Familie) | Native / Runtime-Route | Legacy / Dual-Pfad | Dateien |
|---|---|---|---|---|
| `purchase_order` | `beleg/purchase-order` | `/einkauf/bestellung/:id` (`bestellung-native`, SD `einkauf/purchase-order`) | Liste/Create: `/einkauf/bestellungen`, `/einkauf/bestellungen/neu` | `bestellung-native.tsx`, `bestellung-anlegen.tsx`, `bestellung-stamm.tsx`, `bestellungen-liste.tsx` |
| `goods_receipt` | `beleg/goods-receipt` | — (Ziel: Familie) | `einkauf/lieferschein-erfassung` | `einkauf/lieferschein-erfassung.tsx` |
| `purchase_invoice` | `beleg/purchase-invoice` | Finance-Zweitweg `finance/ap-invoice` | `einkauf/rechnung-eingang-erfassung`, `finance/ap-invoice-form` | entsprechende pages |
| `purchase_credit_memo` | `beleg/purchase-credit-memo` | — | `einkauf/gutschriften-belastungen` (Belastung = offener Fachfall) | `gutschriften-belastungen.tsx` |

### 3.3 Noch nicht in der kanonischen Familie (Kandidaten-Children)

| Fachfall | Status | Hinweis |
|---|---|---|
| Einkaufsanfrage (RFQ) | Seiten existieren (`anfrage-stamm`, `anfrage-erfassung`, `anfrage-native`) | Nicht in `BELEGARTEN`; vor Aufnahme Datenvertrag + Folge zu Bestellung |
| Einkaufsangebot (Lieferant) | `angebot-stamm`, `angebot-native`, Listen | Ebenfalls Kandidat, kein stiller Alias von `sales_offer` |
| Reine Finanz-AR/AP | `finance/invoice-form`, `finance/ap-invoice*` | Nur Waren-/Leistungsfälle auf sales/purchase_invoice mappen |

Authoring-Kern (Parent-Builder): `app/core/screen_definitions_beleg.py`, `app/core/belegvertrag.py`, `config/document_screen_versions.json`.

---

## 4. Migrationsreihenfolge

### 4.1 Reihenfolge (Parent zuerst)

1. **Parent härten** — Basisversion: Layout-Meridian (`floorplan`/`density`/`contextRail` wo nötig), gemeinsame Actions/Create/Edit, Override-Regeln, CI-Drift-Gate (größtenteils vorhanden bis 1.2.0).
2. **Process-Verträge am Parent** — Entscheidung: ProcessBand aus Server-`aktionen` *oder* `workflow.phases`; ProcessRibbon aus `folgebelege` / Flow-Spine-Chain — ohne Child-Forks.
3. **Children mit hoher Runtime-Nähe** — `purchase_order` (Nav-Native bereits umgehängt), `sales_order`, `sales_invoice` / `purchase_invoice` (Buchungswirkung).
4. **Mengen-Children** — `sales_delivery`, `goods_receipt` (Preisrecht/Lagerwirkung).
5. **Angebot/Gutschrift** — `sales_offer`, Credit-Memos.
6. **Kandidaten registrieren** — RFQ / Einkaufsangebot nur nach Variantenvertrag + Kettenprofil.
7. **Alt-Einstiege ablösen** — je Einstieg Funktionsinventur → Nav-Umhängen → Legacy entfernen (BELEG-050-Muster). Create bleibt Legacy bis Create-Parität (UIX-057-Analog).

### 4.2 Abnahmekriterien (je Child)

- [ ] Child kommt ausschließlich aus Parent-Builder + Patch (kein handgeschriebenes Parallel-SD).
- [ ] Create und Edit über zentrale Runtime (`UniversalNativeCreatePage` / Detail + DocFlow), nicht zweites Formularframework.
- [ ] Browserkette: lesen → bearbeiten/anlegen → erlaubte Folgeaktion; Buchung nur wo `bucht`, mit Journal-/OP-Nachweis.
- [ ] Kein Funktionsverlust gegenüber abgenommener Legacy-Inventurliste (Sonderfelder dokumentiert oder geparkt).
- [ ] ProcessBand/Ribbon korrekt getrennt; keine internen Prozessschlüssel in der UI.
- [ ] Studio-Import der Ausgangsfassung möglich; **aktive** Route zeigt freigegebene Runtime-Definition (nicht nur Draft).
- [ ] Vitest/API-Verträge grün; keine neue DB/Container; gemeinsamer Prüfstand.

### 4.3 Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Funktionsverlust bei Nav-Umhängen | Inventur vor Switch; Legacy-Rollback (UIX-057) |
| Doppelpflege Legacy + Native + Familie | Ein führender Detailpfad pro Belegart; Create getrennt bis Parität |
| Studio-Import als „fertig“ missverstanden | §5; `eligible_for_release=false` bis Nachweis |
| Deep-Merge-Illusion bei Patches | Ganze Root-Keys ersetzen; dokumentieren |
| Bestellung Dual-Pfad / parallele Agenten | Keine Überschreibung von Listen-Nav/Create-WIP ohne Handshake (MASK-BESTELLUNG-NAV abgeschlossen; Create weiter Legacy) |
| Codex STUDIO-BELEG-THEME | Theme/Register/Builder-Dateien nicht ohne Handshake anfassen |

---

## 5. Abgrenzung: Studio-Import ≠ Runtime-Verdrahtung

| Stufe | Bedeutet | Reicht nicht für |
|---|---|---|
| A — Native Familie im Register | 9 Varianten aus Builder, Versionsbindung | produktive Alt-Nav |
| B — Studio-Ausgangsimport | revisionsgebundener Draft, Historie | Aktivierung, Rechte, Fachwirkung |
| C — Runtime verdrahtet | Route → `UniversalNative*Page` → Screen-ID der Familie; Commands gebunden | — |
| D — Alt-Einstieg abgelöst | Listen/Shortcuts zeigen nur noch C; Legacy entfernt nach Abnahme | — |

„Made by Studio“ heißt: Definition und Freigabe laufen über Studio/Meridian-Governance — **aber** die Nutzerroute muss Stufe C erreichen. Import allein (B) ist kein Migrationsabschluss.

---

## 6. Empfohlene nächste Implementierungsschritte

1. Parent: ProcessBand-/Ribbon-Vertrag an Belegfamilie spezifizieren und in einer Basisversion verankern (ohne alle Children neu zu patchen).
2. Child `purchase_order`: Paritätslücken aus MASK-BESTELLUNG-NAV (DocumentCaseBand/Flow-Spine, Positionsallokation, Freigabe/Storno, Kommunikation) gegen Familie schließen — **Handshake**, Dateien der Listen-Nav nicht regressiv ändern.
3. Child `sales_invoice` / `purchase_invoice`: FormBuilder-/Finance-Zweitwege auf Familie + DocFlow bündeln (Masterplan BELEG-030/041).
4. Varianteneditor / unabhängige Variantenfreigabe (offen in STUDIO-BELEG-THEME) — Codex-Claim respektieren.
5. RFQ/Einkaufsangebot erst nach explizitem `Belegvariante`-Eintrag und Kettenprofil.

---

## 7. Slice-Vorschlag (offen, kein Codex-Konflikt)

Vorschlag: `UIX-BELEG-FAMILIE-VERERBUNG-20261022` — **nur Doku/Plan + Abnahmelisten**, Status `offen`.
**Nicht claimen** gegen `screen_definitions_beleg.py`, `document_screen_versions.json`, Theme/Compiler (STUDIO-BELEG-THEME / STUDIO-MODEL).
Implementierende Folgeslices erst nach Handshake mit Codex und nach Abschluss paralleler Bestellung-Create-Arbeiten.

Siehe Slice-YAML: `docs/agent-ops/slices/UIX-BELEG-FAMILIE-VERERBUNG-20261022.yaml`.
