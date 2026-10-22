---
title: Maskenfamilien-Taxonomie (systemweit)
type: architecture
audience: [architect, agent, entwickler]
owner: Cursor Composer (Plan)
status: aktiv
last_reviewed: 2026-10-22
version: 1.0.0
description: Systemweite Parent/Child-Familien für Ein-/Ausgabemasken; Vererbungsregeln, reale Cluster aus Inventar und ScreenDefinitions, priorisierte Roadmap P0–P3; Belegfamilie als Spezialfall.
---

# Maskenfamilien-Taxonomie (systemweit)

Stand: 2026-10-22. **Planungsartefakt** (keine Groß-Migration von Pages).
Meridian-Regel: Qualität über `ScreenDefinition → RenderPlan → useUniversalMaskRuntime → UniversalMaskRenderer` — nicht Einzelmasken-Redesign. Studio-Import ≠ Runtime-Ablösung.

## Zweck und Querverweise

| Dokument | Rolle |
|---|---|
| **Dieses Dokument** | Systemweite Kategorien, Familienkandidaten, Parent-Verträge, Cluster-Roadmap P0–P3 |
| [beleg-maskenfamilie-vererbung.md](beleg-maskenfamilie-vererbung.md) | Spezialfall **Beleg** (9 Varianten, Ketten, ProcessBand/Ribbon) |
| [mask-route-migration-inventory.md](mask-route-migration-inventory.md) | Messbasis Routen/Seiten/Builder |
| [universal-mask-runtime-status.md](universal-mask-runtime-status.md) | Runtime-/Gate-Stand |
| [MASKEN.md](../../MASKEN.md) | Gewohnheits-Prinzip (Layout-Parität) |
| Skill Meridian Single Mask Builder | Floorplans, Density, Table Profiles, Readiness |

### Inventar-Anker (Messung 2026-10-22)

| Metrik | Zahl | Bedeutung für Familien |
|---|---:|---|
| Routen gesamt | **941** | Migrationsraum |
| `runtime_wired` | **61** | bereits Runtime-Pfad (Familie kann hier „andocken“) |
| `legacy_mask_pattern` (ObjectPage/ListReport) | **~115–122** | oft schon familienfähig, noch nicht Runtime |
| `hand_built` | **~757–764** | größter Block; nur Clusterweise angehen |
| Seiten TSX | **700** | davon ~54 `*-liste`, ~31 `*-stamm`, ~31 `*-native`, ~19 Dashboard/Cockpit |
| ScreenDefinition-Builder | **102** | Authoring-Kern; viele Near-Duplicates = Familienkandidaten |

Zahlen leicht driftfähig bei Re-Run von `scripts/mask_route_migration_inventory.py`; Roadmap hängt an **Größenordnung und Cluster**, nicht an einer Zeile Delta.

---

## 1. Prinzipien (verbindlich)

### 1.1 OOP-Analog

```
Parent (abstrakte Schablone / gemeinsame ScreenDefinition-Basis)
 └── Child (Variante) — nur echte fachliche Varianz überschreibt
```

- Ähnliche Masken → **Familie**, nicht Copy-Paste-Page.
- Override nur für echte Varianz (Felder, Commands, Kettenprofil, Table-Profile).
- **Familie nur wenn** eine Parent-Änderung ≥ **2–3 Children** mitzieht.
- Sonst: **Komposition** (gemeinsame Bausteine/Renderer), keine künstliche Vererbungshierarchie.

### 1.2 Kategorien (Taxonomie-Root)

| Kategorie | Floorplan (Meridian) | Typische Aufgabe |
|---|---|---|
| **Beleg** | `transaction` (+ Register) | Ein-/Ausgangsbelege, Ketten, Buchungswirkung |
| **Stamm** | `objectPage` | Partner, Artikel, Produktstamm, Konten |
| **Liste** | `worklist` (browse) | Stammdaten-/Beleg-Browse, Filter, Variants, Zeile → Detail |
| **Worklist** | `worklist` (queue) | Ausnahme-/Kontrollschlangen, Inbox, Leitstand |
| **Ausnahme** | `wizard` / `cockpit` / Sonder | Wizard, Dashboard, einmalige Prozessmasken, Godfiles |

### 1.3 ProcessBand ≠ ProcessRibbon

| Baustein | Aufgabe | Wo erlaubt |
|---|---|---|
| **ProcessBand** | Stand *eines* Vorgangs (Phasen, eine nächste Aktion, Blocker) | Beleg/Transaction, ggf. Workflow-Stamm |
| **ProcessRibbon** | Navigation der *Belegkette* | nur Belegfamilie / DocFlow-Kette |
| **DocumentCaseBand** | Legacy-/Übergang Flow-Spine | nicht kanonischer Parent; Paritätslücke dokumentieren |

Nie zusammenführen nur weil beide Chevrons zeichnen.

### 1.4 Studio-Qualität vs. Runtime

- „Made by studio“ = Qualitätsversprechen (Freigabe + CLI + Runtime + Browser), nicht Draft-Count.
  Verbindliche Checkliste: [made-by-studio-qualitaetsversprechen.md](made-by-studio-qualitaetsversprechen.md).
- Studio-Import eines Drafts **ersetzt nicht** `runtime_wired` (Route → UniversalNative* → freigegebene SD).
- Theme/Compiler: Codex-Claims respektieren (siehe §6 Handshake).

---

## 2. Familienkatalog (reale Cluster)

Jede Familie unten: Parent-Vertrag, Child-Beispiele aus dem Repo, Anti-Patterns.
Priorität in §4.

### 2.1 BelegMaskeParent — Kategorie Beleg

**Status:** Spezialdoku + Slice `UIX-BELEG-FAMILIE-VERERBUNG-20261022` (offen).
**Parent-Kern:** `app/core/screen_definitions_beleg.py` + `belegvertrag.BELEGARTEN` + `config/document_screen_versions.json`.

| Erbt vom Parent | Child-Override |
|---|---|
| Floorplan `transaction`, sticky Header/Footer, Reiter `kopf/positionen/kette/dokumente/historie` | Bezeichner, `mit_preisen` / `bucht`, Folgekette |
| Partner-Slot, Positionsgerüst, DocFlow Create/Update | Partnerrolle Kunde/Lieferant, Positions-Spalten |
| Actions aus Belegkommandos | erlaubte Commands / Converts |
| Meridian/Theme global | **kein** Masken-Sonder-Theme |

**Children (Beispiele):** `beleg/sales-order`, `beleg/purchase-order`, …; Runtime u. a. `/belege/:belegart/:id`, `/einkauf/bestellung/:id`, `/sales/sales-order/:id`.
**Details / Migration:** [beleg-maskenfamilie-vererbung.md](beleg-maskenfamilie-vererbung.md).

**Anti-Patterns:** Parallel-SD pro Belegart ohne Builder; FormBuilder-Zweitweg als „neue Maske“; ProcessBand-Phasen nur in einem Child; RFQ still als `sales_offer` aliasen.

---

### 2.2 StammObjectPageParent — Kategorie Stamm

**Befund:** Near-Duplicate-Builder in `screen_definitions.py` — gleiches Gerüst `mode: detail`, Tab `kopf` + Lazy-Tabs, `noWorkflowReason` bei reinen Referenzdaten, Action `edit`.

| Erbt vom Parent | Child-Override |
|---|---|
| Floorplan `objectPage`, Density compact/expertDense, Identity-Header, Tab-Gerüst (`kopf` + lazy Tables) | Fachfelder, Tab-Keys, Endpoints |
| Summary-Zeile, Action-Hierarchie (primär Bearbeiten), Context-Rail optional | Permissions, Summary-KPIs |
| Adapter native, Readiness/agentContract-Muster | Texte, testIds, sensitiveFields |
| Create-Parität getrennt (UIX-057: Detail native, Create oft Legacy) | Create erst nach Paritätsnachweis |

**Children (Beispiele, Screen-IDs / Routen):**

| Child | Screen-ID | Runtime-Route (soweit verdrahtet) | Legacy-Parallel |
|---|---|---|---|
| Dünger | `agrar/duenger` | `/agrar/duenger/:id` | `duenger-stamm`, `duenger/stamm` |
| Saatgut | `agrar/saatgut` | `/agrar/saatgut/:id` | `saatgut-stamm`, … |
| Lieferant | `einkauf/supplier` | `/einkauf/lieferanten/:id` | `lieferanten-liste` → früher Plural-Stamm |
| Debitor | `finance/debitor` | `/finance/debitor/:id` | `debitoren-liste` / FIBU-Stämme |
| Kreditor | `finance/kreditor` | `/finance/kreditor/:id` | analog |
| Bankkonto | `finance/bankkonto` | `/finance/bankkonto/:id` | analog |
| Artikelbestand | `lager/article-stock` | `/lager/artikel/:id` | Artikel-Stämme handgebaut |
| Fahrzeug | `fuhrpark/fahrzeug-stamm` | `/fuhrpark/fahrzeug/:id` | — |
| Opportunity | `crm/opportunity` | `/crm/opportunity/:id` | `opportunities-liste` |
| Mischfutter | `futtermittel/mischfuttermittel` | `/futtermittel/mischfuttermittel/:id` | Listen ObjectPage |

Weitere Kandidaten ohne gemeinsamen Parent-Builder (noch Copy-Paste): Biostimulanzien (`legacy_mask_pattern`), Einzelfuttermittel, Kontrakt (`agrar/kontrakte` — fachlich näher Beleg/Vertrag, eigener Unterast).

**Anti-Patterns:** Pro Produkt eine handgeschriebene Page mit eigenem Layout; Floorplan/Density nur in einem Child setzen; CRM 360 in diese Familie pressen (Ausnahme/Cockpit).

**Familientauglichkeit:** Parent-Änderung an Layout/Actions zieht sofort ≥6–10 Children — **Ja, Familie**.

---

### 2.3 StammListenParent — Kategorie Liste

**Befund:** ~54 `*-liste.tsx`; Dual-Pfad nach MASK-PRIMARY / MASK-BESTELLUNG: Listen öffnen native Detailrouten, Create bleibt Legacy.

| Erbt vom Parent | Child-Override |
|---|---|
| Floorplan `worklist`, Suche/Filter/Chips/Variants, Tabellen-Toolbar, Statusfilter | Spalten, Filterfelder, DataSource |
| Primäraktion „Neu“ (bis Create-Parität oft Legacy-Ziel) | Zielroute Neu / Permission |
| Zeilenklick → kanonische Detail-Route (native Screen-ID) | `flow_route` / path template |
| Table profile `standard` (default) | `inventory` / `financial` wo Mengen/Beträge |

**Children (Beispiele):**

- NativeList-nahe: `einkauf/bestellungen-liste`, `anfragen-liste`, `angebote-liste`
- ObjectPage/ListReport-Legacy: `agrar/saatgut-liste`, `duenger-liste`, `crm/kunden-liste`, `biostimulanzien-liste`, Futtermittel-Listen
- Worklist-ähnlich aber Beleg-Browse: `verkauf/rechnungen-worklist` → SD `sales/invoices`

**Anti-Patterns:** Liste baut eigenes Detail-Layout inline; Zeilenklick auf toten Legacy-Stamm obwohl `*-native` existiert; eine globale `loading`-Boolean für alle Zeilen-Mutationen.

**Familientauglichkeit:** Ja — gemeinsamer Listen-Shell + Spalten-Patches; Umsetzung oft über deklarative List-SD / NativeListPage, nicht über neue React-Pages.

---

### 2.4 KontrollWorklistParent — Kategorie Worklist

**Befund:** Im Code **bereits Vererbung**: `_build_document_control_variant` klont Parent `auswertungen/beleg-kontrolle` und überschreibt nur ID/Titel/Endpoint-Filter. Analog `_build_sanctions_scope_screen_definition`.

| Erbt vom Parent | Child-Override |
|---|---|
| Worklist-Shell, Summary, Exception-Tabelle, rowActions (öffnen/klären), Audit-Rail | `exception_type` / `scope`, Titel, testId |
| Density `expertDense`, tableProfile audit/financial | Domain-Labels |
| Drilldown auf Quellbeleg-Route | erlaubte Quelltypen |

**Children:**

| Screen-ID | Ausnahme-Filter |
|---|---|
| `auswertungen/beleg-kontrolle` | Parent |
| `auswertungen/auftrags-kontrolle` | `open_purchase_order` |
| `auswertungen/lieferschein-kontrolle` | `uninvoiced_delivery_note` |
| `abrechnung/eb-lieferschein-kontrolle` | `missing_inbound_document` |
| `auswertungen/sanktionspruefung-*` | scope personal/kunden (Schwesterfamilie) |

**Weitere Cluster-Kandidaten (Komposition oder spätere Subfamilie):** `lager/leitstand`, `produktion/produktionsleitstand`, `produktion/chargen-bearbeiten`, `schnittstelle/mde-inbox`, `tankstelle/adapter-inbox`, `finance/rechnungstapel`, `docflow/dokumenten-ruecklauf`, `lager/fremdware`.

**Anti-Patterns:** Vier getrennte Full-SDs kopieren; Kontroll-UI als Dashboard ohne Queue-Vertrag; ProcessRibbon in Worklist.

**Familientauglichkeit:** Ja — Muster schon produktiv; ausweiten statt neu erfinden.

---

### 2.5 FinanceObjektParent — Kategorie Stamm / Transaction-hybrid

**Befund:** Runtime-verdrahtet: `finance/ap-invoice`, `finance/ar-open-item`, `finance/payment-run`, Debitor/Kreditor/Bankkonto. AP-Rechnung ist Zweitweg zur Belegfamilie `purchase_invoice`.

| Erbt vom Parent | Child-Override |
|---|---|
| Financial table profile, Betragsausrichtung, Perioden-/Statusfelder | Buchungscommands, OP-Bezug |
| Context-Rail audit, Danger-Actions mit Confirm | Zahlauf vs. Einzelbeleg |
| Read-only vs. buchende Actions klar getrennt | Permissions |

**Children:** AP-Invoice, AR-OP, Payment-Run, Steuerschlüssel (Listen-nah), Rechnungstapel (Worklist-nah).

**Anti-Patterns:** Warenbeleg und reine Finanzrechnung still zusammenlegen; Belegfamilie umgehen zugunsten FormBuilder (`finance/ap-invoice-form`).

**Familientauglichkeit:** Teilweise — Debitor/Kreditor → eher **StammObjectPage**; AP/AR/Payment → eigene **FinanceTransaction**-Subfamilie oder Beleg-Child. Nicht alles unter einen Parent zwingen.

---

### 2.6 WorkspaceCockpitParent — Kategorie Ausnahme (Cockpit)

**Befund:** SD-Serie `workspace/einkauf|verkauf|lager|fibu|leitung` — gleiches Cockpit-Muster, unterschiedliche Domänen-Kacheln.

| Erbt vom Parent | Child-Override |
|---|---|
| Floorplan `cockpit`, dichte Arbeitsfläche, Nav-Kacheln | Domain-Links, KPIs |
| Kein Beleg-ProcessRibbon | optional ProcessBand nur wenn echter Vorgang |

**Anti-Patterns:** Cockpit als Ersatz für fehlende Listenfamilie; Godfile-Page statt deklarativer Kacheln.

**Familientauglichkeit:** Ja für Shell; Inhalt bleibt Domain-Komposition. **P3**, weil geringer Migrationshebel auf die 757 hand_built Fachmasken.

---

### 2.7 Personal / Fuhrpark / Feeding — Domänencluster

Kleine, bereits native Cluster (Runtime-Liste im Inventar): Personal (Qualifikationen, Onboarding, Schulungen, Bewerbungen, Einwilligungen), Fuhrpark (Fahrzeuge, Rechnungen, Dokumente), Agrar Feeding/Rations (`agrar/feeding-*`, `agrar/ration`).

**Empfehlung:** Zuerst **Komposition** (gemeinsame Tabellen-/Consent-Bausteine). Familie nur wenn ≥3 Screens denselben Parent-Patch brauchen — Feeding-Lifecycle ist Kandidat für eigenen Slice, nicht P0 der Taxonomie.

---

### 2.8 Explizite Ausnahmen (keine Familie erzwingen)

| Masken / Cluster | Warum Ausnahme |
|---|---|
| **CRM Customer 360** (`crm/customer-360`) | Cockpit mit eigener Paritätsmatrix (UIX-034); nicht StammObjectPage |
| **Tourenplanung / Tour-Fracht-Arbeitsraum** | Godfile-/Prozessmaske; Codex-/Agent-Claim-Schutz |
| **Bestellvorschlag**, **Training**-Flows | Sonderprozesse; nicht Beleg-Child |
| **Start-/Admin-Dashboards**, Gap-Pipeline, Control-Center | Reporting/Ops, kein Ein-/Ausgabe-Gewohnheitslayout |
| **Wizards** (DATEV, Periodenabschluss, Inventur-geführt) | Floorplan `wizard`; selten, eigene Gates |
| **Studio Run / Preview** (`studio/run/:screenId`) | Authoring, nicht Produktivfamilie |
| **Harvest Rule Store / Semantic Preview** | Fachliche Sonderabnahme; Studio-Claims |

Ausnahmen nutzen weiter Meridian-Bausteine (Renderer, Density, Rails) — nur **keine** Parent/Child-Zwangsvererbung.

---

## 3. Entscheidungsbaum: Familie vs. Komposition

```
Ähnliche UX/Layout (≥2–3 Masken)?
  ├─ Nein → Einzel-SD oder bestehende Renderer-Bausteine
  └─ Ja → Parent-Änderung würde alle Children verbessern?
        ├─ Ja → Familie (Base + Variant-Patch / Builder-Helper)
        └─ Nein → Komposition (shared tab/table/action blocks)
Fachlich Belegkette / bucht / Positionen?
  └─ Ja → Belegfamilie (nicht Stamm/Worklist vermischen)
Nur Queue/Ausnahmen?
  └─ Ja → KontrollWorklistParent oder Inbox-Komposition
Einmaliger Leitstand / 360 / Wizard?
  └─ Ja → Ausnahme + Meridian-Floorplan, kein künstlicher Parent
```

---

## 4. Priorisierte Cluster-Roadmap (P0–P3)

Abhängig von Inventar: Hebel = (Anzahl Children × Dual-Pfad-Schmerz) / Claim-Konflikt.

### P0 — Fundament (jetzt / parallel Plan)

| Cluster | Abhängigkeit Inventar | Abnahmekriterien |
|---|---|---|
| **BelegMaskeParent** (bestehender Slice) | ~9 Varianten + ~14 Alt-Einstiege; Teilmenge der 61 runtime_wired | siehe beleg-maskenfamilie-vererbung.md §4.2; ProcessBand≠Ribbon; Studio≠Runtime |
| **Taxonomie + Handshake** (dieser Slice) | 941/61/~120/~760 als Baseline | Doku + Workboard offen; keine Page-Migration |

### P1 — Höchster Hebel nach Beleg

| Cluster | Abhängigkeit Inventar | Abnahmekriterien |
|---|---|---|
| **StammObjectPageParent** | ≥8 native Stamm-SDs; Dutzend Legacy-`*-stamm` / ObjectPage; Listen bereits teils auf native Detail | Ein Parent-Builder oder shared factory; Duenger/Saatgut/Supplier/Debitor/Kreditor aus Parent+Patch; Layout/Meridian-Felder einmal; Create weiter Legacy bis Parität; Vitest je Child-Smoke |
| **KontrollWorklistParent ausweiten** | 4 Varianten schon vererbt; weitere hand_built Kontroll-/Inbox-Seiten | Neue Kontroll-Views nur über `_build_*_variant`; keine Full-SD-Kopien; Inventar: betroffene Routen → runtime_wired oder bewusst geparkt |
| **StammListenParent (Nav-Parität)** | ~54 Listen-Seiten; Dual-Pfad-Rest | Zeilenklick → native Detail-Screen-ID; Inventar-Delta dokumentiert; kein Create-Switch ohne Parität |

### P2 — Domänen nachziehen

| Cluster | Abhängigkeit | Abnahme |
|---|---|---|
| **FinanceTransaction / AP-AR-Bündelung** | runtime finance/* + Legacy FormBuilder | Mapping auf Beleg-Child oder klarer Finance-Parent; kein stiller Doppelweg |
| **Agrar-Produktstamm Rest** (Biostimulanzien, PSM, …) | noch `legacy_mask_pattern` | Anschluss an StammObjectPageParent |
| **Einkauf Nebenbelege** (Anfrage/Angebot/Avis/AB) | bereits native Details; Listen NativeList | Kettenprofil vs. Belegfamilie klären (kein stiller BELEGARTEN-Eintrag) |

### P3 — Shells & Domänencluster

| Cluster | Abhängigkeit | Abnahme |
|---|---|---|
| WorkspaceCockpitParent | 5 SD-Workspaces | gemeinsame Shell-Metadaten |
| Personal / Fuhrpark Feinschliff | bereits runtime_wired | nur Overrides/Dokumentation |
| Feeding/Rations Subfamilie | viele `agrar/feeding-*` SDs | eigener Slice, nicht Taxonomie-Blocker |

---

## 5. Was bewusst Ausnahme bleibt

- CRM 360, Tourenplanung, Bestellvorschlag, Training, Admin-Dashboards, Wizards, Studio-Preview.
- Godfiles unter aktivem Claim: **nicht** „in Familie refactoren“ ohne Handshake.
- ProcessBand/Ribbon-Semantik: global verbindlich, aber Implementierung zuerst am **Beleg-Parent**.

---

## 6. Konflikte / Handshakes (Codex & Parallel)

| Claim / Bereich | Haltung dieses Plans |
|---|---|
| **STUDIO-BELEG-THEME** | Theme, Beleg-Builder, `document_screen_versions.json` — **nicht anfassen**; Beleg-Vererbung nur spezifizieren |
| **STUDIO-MODEL / STUDIO-SEMANTIC** | Semantic/LLM-Studio — außerhalb |
| **CI-GRUEN / develop-Identität** | keine CI-Skript-/Hook-Änderungen |
| **Tourenplanung / Training / Bestellvorschlag** | Dateibesitz fremd; Ausnahmen-Liste |
| **UIX-BELEG-FAMILIE-VERERBUNG-20261022** | **nicht überschreiben**; bleibt eigener offener Plan-Slice |
| **MASK-BESTELLUNG Create/Listen-WIP** | Create Legacy; Listen-Nav abgeschlossen — Regression vermeiden |
| **screen_definitions.py Massenrefactor** | erst nach Claim eines Implementierungs-Slices; Taxonomie allein ändert keine Builder |

Handshake-Notiz: `docs/agent-ops/handshakes/maskenfamilien-taxonomie-20261022.md`.

---

## 7. Slice

- Plan-Slice: **`UIX-MASKENFAMILIEN-TAXONOMIE-20261022`** — Status **offen**, nicht reserviert (nur Doku/Roadmap).
- YAML: `docs/agent-ops/slices/UIX-MASKENFAMILIEN-TAXONOMIE-20261022.yaml`
- Implementierende Folgeslices (Stamm-Parent-Factory, Worklist-Ausbau, …) **getrennt claimen**.

---

## 8. Nächste sinnvolle Implementierungsschritte (nicht Teil dieses Plans)

1. Beleg-Parent ProcessBand/Ribbon-Vertrag (Handshake Codex) — Slice Beleg.
2. `build_stamm_object_page_parent(...)` + Migration Duenger/Saatgut/Supplier als Pilot (3 Children-Regel erfüllt).
3. Weitere Document-Control-/Inbox-Children nur als Variant-Helper.
4. Listen-Rest Dual-Pfad gegen Inventar abarbeiten (niedrig-riskant wie MASK-PRIMARY).
