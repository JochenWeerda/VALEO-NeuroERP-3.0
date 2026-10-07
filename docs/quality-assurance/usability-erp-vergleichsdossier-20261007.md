---
title: Usability- und ERP-Vergleichsdossier VALEO NeuroERP
type: reference
audience: [produkt, management, qa, agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-10-07
version: 1.0.0
description: Systemweites Stufe-1 Usability-Audit plus Capability-/Zukunftsvergleich gegen Tier-1-ERPs, Light (light.inc) und AI-native Peers ERPClaw OpenLedger TaxHacker OpenAccountants.
---

# Usability- und ERP-Vergleichsdossier — VALEO NeuroERP 3.0

**Datum:** 2026-10-07
**Auditstufe:** 1 (Experten-Systemaudit)
**Protokoll:** [usability-erp-audit-protocol-20261007.md](usability-erp-audit-protocol-20261007.md)
**Matrix:** [../gap/usability-systemaudit-matrix-20261007.csv](../gap/usability-systemaudit-matrix-20261007.csv) · [Findings](../gap/usability-systemaudit-findings-20261007.csv)

---

## 1. Executive Summary

VALEO NeuroERP ist als **Landhandel-/Agrar-Vollsuite** mit Meridian-Maskenkette,
Flow-Spine und wachsender Voice-/MCP-Schicht positioniert — nicht als Finance-only
AI-Ledger. Die Gebrauchstauglichkeit ist im **Operations-/Handelskern** (Ernte,
Waage-Touch, CRM-360, Belegketten-Muster) klar über dem Niveau typischer
gewachsener Branchensoftware; die größten Usability- und Zukunftslücken liegen
im **Finance-Agenten-Modell**, in der **einheitlichen Action-Dichte**
(UI = Voice = MCP) und in der **Abschmelzung paralleler Masken-Frameworks**.

| Kennzahl (Stufe 1) | Wert |
|---|---|
| Domänencluster bewertet | 10 |
| SUS-Experten-Schnitt (ungewichtet) | ~66 (±8) |
| Blocker-Befunde | 3 (alle Finance-/Close-/Ledger-Agentik) |
| Major-Befunde | 11 |
| Native Maskenaktionen ohne Weg (`BEKANNTE_LUECKEN`) | 0 |
| Vergleichsanker | SAP/Oracle/Dynamics/Odoo/NetSuite/L3 + Light + 4 Peers |

**Strategische Lage in einem Satz:** VALEO gewinnt gegen Light/OpenLedger auf
**Ops und Branchenprozessen**, verliert auf **agentischem Finance unter Policy**;
gegen SAP/Dynamics gewinnt es auf **Landhandel-Gewohnheit und Time-to-Value**,
verliert auf **Ökosystembreite und Incumbent-Copilot-Reife**; gegen ERPClaw
verliert es auf **Action-/Agent-First-Dichte**, gewinnt auf **produktionsreifem
Meridian-UI, Mandanten-/GoBD-Tiefe und DE-Agrar-Compliance**.

Die Archiv-Zahl „~38 % Maturity“ (2025) ist **ersetzt** durch
[Gap-Hub Executive Summary 2026-10](../gap/executive-summary-20261007.md) und
[domain-maturity-matrix-20261007.csv](../gap/domain-maturity-matrix-20261007.csv).
Dieses Dossier liefert Usability-Cluster-Scores und AI-/Tier-1-Vergleich;
Capability-Reife steuert der Gap-Hub.

---

## 2. Methodik und Grenzen

Siehe Protokoll. Kurz:

- ISO 9241-11/110 + Singh/Wesson ERP-Heuristiken + Meridian/WCAG/Flow-Spine.
- Evidenz: Navigation, ScreenDefinitions, Design-Audits, Open Gaps, QA vom
  07.10.2026, Action-Registry, L3-Inventur — **kein** Live-Lab.
- Vendor-Angaben (Light-Matrix, Peer-READMEs) sind **öffentlich dokumentierte
  Claims**, im Dossier als solche gekennzeichnet.
- Stufe 2 (SUS mit Landhandel-Rollen) ist vorbereitet, nicht durchgeführt.

---

## 3. Systemweiter Usability-Befund

### 3.1 Heatmap (Heuristik 0–5, SUS Experten)

| Cluster | Nav | Pres | Learn | Task | Cust | ISO | SUS≈ |
|---|---:|---:|---:|---:|---:|---:|---:|
| C01 Start / Voice / Shell | 4 | 4 | 3 | 4 | 3 | 4 | 72 |
| C02 CRM / Verkauf / O2C | 4 | 4 | 3 | 4 | 2 | 4 | 70 |
| C03 Einkauf / S2P | 3 | 3 | 3 | 3 | 2 | 3 | 62 |
| C04 Lager / Logistik | 4 | 4 | 3 | 4 | 2 | 4 | 71 |
| C05 Agrar / Ernte / Waage | 4 | 4 | 3 | 4 | 2 | 4 | 74 |
| C06 Finance / FiBu / Bank | 3 | 3 | 2 | 3 | 2 | 3 | 58 |
| C07 Personal | 4 | 3 | 3 | 4 | 2 | 4 | 68 |
| C08 Compliance / ESG | 3 | 3 | 2 | 3 | 2 | 3 | 60 |
| C09 Portal / POS | 3 | 3 | 3 | 3 | 2 | 3 | 64 |
| C10 Admin / Agent / Docflow | 4 | 3 | 3 | 3 | 3 | 3 | 66 |

**Lesart:** Agrar/Waage und Start/Shell sind die UX-Leuchttürme. Finance und
Compliance ziehen SUS und Task Support nach unten — dort treffen fragmentierte
IA (`finance` vs. `fibu`), offene Journal-/Close-Integrität und fehlende
agentische Policy-Ausführung zusammen.

### 3.2 Stärken (belegt)

1. **Meridian-Fundament:** Tokens, Density, 44-px-Touch, Register-Tabs, Mask-
   Builder/UniversalMaskRuntime — Designsystem reifer als typische ERP-Altfrontends
   ([frontend-design-skill-audit.md](../design/frontend-design-skill-audit.md)).
2. **Landhandel-Gewohnheit:** Belegketten-Layout, ProcessBand/ProcessRibbon,
   L3-Parität ohne P0-Funktionsgap ([l3-full-mask-functional-gap-inventory.md](../design/l3-full-mask-functional-gap-inventory.md)).
3. **Ehrliche Aktionen:** `BEKANNTE_LUECKEN` leer; Schein-`success: true` aus
   Mask-Aktionen-Welle adressiert (QA 2026-10-07).
4. **Multi-Kanal-Ansatz:** Command Palette, Shortcuts, Voice/`ki-usability`
   (~78 Action-IDs), Launchpad-Spaces — Richtung „ein Eingabefeld“.
5. **Rollen-Touch:** Außendienst/Waage explizit in Bedienwegen dokumentiert und
   teilweise umgesetzt (44 px, Queue, Suche).

### 3.3 Schwächen (Top)

| ID | Sev | Befund |
|---|---|---|
| U-C06-01 | Blocker | Kein agentisches Finance unter Policy (Close/Matching/AP) |
| U-C06-02 | Blocker | Kein OpenLedger-artiges „LLM darf Intent, Ledger-Invarianten blocken“ als durchgängiges Agent-Muster |
| U-C06-04 | Blocker | Kassenabschluss maskenseitig ohne fachlich fertigen Close |
| U-C02-01 | Major | Parallele Masken-Frameworks → Lern-/Konsistenzkosten |
| U-C02-02 / U-C10-01 | Major | MCP/Voice-Schreibdichte << UI-Oberfläche / << ERPClaw |
| U-C08-01 | Major | Kein zitierbarer Steuer-/Compliance-Skill-MCP |
| U-C10-02 | Major | OCR nicht local-LLM-first (TaxHacker/Ollama-Muster) |
| U-C03-01 | Major | Restliche API-Doppelgruppen → Erwartungsbruch |
| U-C06-03 | Major | Finance-IA fragmentiert |
| U-C09-01 | Major | Portal/POS außerhalb Kern-Gewohnheit |

### 3.4 Tiefen-Tasks (Kurzbewertung)

| Task | Wirksamkeit | Effizienz | Zufriedenheit (Experte) | Kommentar |
|---|---|---|---|---|
| T-O2C Belegkette | hoch | mittel–hoch | gut | Ribbon/Band vorhanden; Framework-Doppelung kostet |
| T-S2P Einkauf | mittel | mittel | mittel | Nach Mandanten-/Aktionsfixes besser; Compat-Rest |
| T-ERNTE | hoch | hoch (Touch) | gut–sehr gut | Branchenstärke; PDF-Archiv laut ADR-078 adressiert |
| T-FIN Close/Zahlung | niedrig–mittel | niedrig | schwach | Größte Lücke vs. Light/OpenLedger |
| T-CRM Lead/KIM | hoch | mittel–hoch | gut | Kanon-Lead; MCP-Schreiben Rest |
| T-VOICE | mittel | hoch wo verdrahtet | mittel | Gut für Nav/Shortcuts; Mutation/Waage unvollständig |

---

## 4. Vergleich zu führenden ERPs (klassisch / UX)

Bewertung relativ zu VALEO-Zielgruppe **DE-Landhandel / Genossenschaft /
Handels-ERP**, nicht „Fortune-500 All Domains“.

| Dimension | VALEO | SAP S/4 + Fiori | Oracle Fusion | Dynamics 365 / BC | Odoo | zvoove/L3 (Referenz) |
|---|---|---|---|---|---|---|
| Branchen-Agrar/Waage/Ernte | stark | schwach ohne Partner | schwach | mittel (Add-ons) | schwach–mittel | stark (Ist-Referenz) |
| Belegketten-UX Gewohnheit | stark (Meridian+L3) | stark (Fiori Elements) | stark | stark | gut | stark (Desktop-RDP) |
| Launchpad / Rollenstart | gut (Spaces) | sehr stark | stark | stark | gut | Ribbon-Menüs |
| Accessibility / Touch | gut (44 px Ziel) | gut (Fiori Mobile) | gut | gut | mittel | schwach (klassisch) |
| Implementierungsaufwand | niedrig–mittel | sehr hoch | sehr hoch | mittel–hoch | niedrig–mittel | Migrationsthema |
| Ökosystem / Partner | klein | sehr groß | groß | groß | groß | Nische DE |
| Assistive Copilots | Voice/Intent vorhanden | Joule | Fusion AI | Copilot | Odoo AI | — |
| Agentic Finance | schwach | assistiv→agentisch (Cloud) | assistiv→agentisch | assistiv (reif Sales) | leichtgewichtig | — |

### Was gegenüber Tier-1 noch fehlt (UX + Capability, priorisiert)

**P0 / P1 (nächste Wellen)**

1. **Finance-Close-Wahrheit:** echter Kassen-/Periodenabschluss, atomare
   Journal-/Audit-Pfade — ohne Scheinerfolg (bereits in Open Gaps).
2. **Eine Maskenkette:** keine neuen Parallel-Frameworks; Legacy sichtbarmachen
   und abschmelzen.
3. **UI = MCP = Voice:** jede mutationsfähige Fachaktion über dieselbe
   Action-ID / denselben Guard (Dynamics-MCP-Idee aus Bedienwegen).
4. **IA Finance:** `finance`/`fibu` konsolidieren; eine FiBu-Sprache.
5. **Router-Kanon:** Rest-Doppelgruppen entfernen (Erwartungskonformität).

**P2 (Differenzierung)**

6. Rollen-Cockpits / Floorplans (UIX-Zukunft M1).
7. Omnibox Intent-Compiler mit Vorschau vor Ausführung.
8. Table-Profile/Customization je Rolle/Terminal.
9. Portal/POS an Gewohnheitsprinzip oder klaren Channel-Kontext binden.

**Nicht als Gap umetikettieren:** fehlende SAP-Modulbreite (IS-Oil, globale
HR-Payroll in 80 Ländern) — außerhalb der Landhandel-SoR-Strategie.

---

## 5. Future / AI-ERP — Light als kommerzielle Leitreferenz

Quelle: [light.inc/versus/erp](https://light.inc/versus/erp) (Vendor-Self-
Darstellung Mid-2026).

### 5.1 Zwei Lager

| Lager | Vertreter | Charakter |
|---|---|---|
| A Incumbent + assistive KI | SAP, Workday, NetSuite, Dynamics | Copilot auf alter Architektur; Mensch erledigt Arbeit |
| B AI-native | Light (Finance), ERPClaw (Voll-ERP), OpenLedger (GL) | Agents/Actions sind Designprämisse |

VALEO liegt heute näher an **A mit starker Ops-UI** plus einer wachsenden
**Intent-/Voice-Schicht** — noch nicht an B für Finance.

### 5.2 Vier Light-Trennfragen × VALEO

| Frage | Light (Claim) | VALEO IST | Gap |
|---|---|---|---|
| 1. Echtes Multi-Entity-GL / SoR? | Ja, ein Ledger | Ja, multi-tenant PostgreSQL-SoR für Ops+Finance | Multi-Entity-Konsolidierung/Intercompany nicht Light-Niveau |
| 2. AP/Cards/Expenses/Procurement nativ? | Ja (Spend nativ) | AP/Procurement nativ; Cards/Expense-Stack nicht Light-artig | Spend/Cards/Subscription-Billing |
| 3. Agentic vs assistive? | Agentic unter Policy | Assistiv (Voice→Action, Copilot-ähnlich) | Policy-Agents die Close/Match/AP ausführen |
| 4. Global vs Regional? | 80+ Länder Claim | DE/EU Landhandel-fokussiert | Kein Global-Bill-Pay-Zielbild nötig; DE-Tiefe halten |

### 5.3 Light Vendor-Dimensionen × VALEO

| Dimension | Light Claim | VALEO | Kommentar |
|---|---|---|---|
| Multi-entity GL | Yes | Teilweise (Tenant/Filiale; keine Light-Konsolidierung) | Ops-SoR ja |
| Subscription management | Yes | Nein / Rand | Nicht Kern Landhandel |
| Spend management | Yes | Teilweise (Einkauf/AP, keine Card-Native) | |
| Agents | Yes | Intent/Voice, nicht Finance-Agent | Kernlücke |
| Global bill pay | Yes | Nein (SEPA/DE Fokus) | Bewusst |
| Self-learning | Yes | Schwach / Muster in UIX-Zukunft | |
| Adaptive | Yes | Density/Rollen ansatzweise | |
| **Inventory / Waage / Agrar** | Nein (Finance-only) | **Ja — VALEO-Stärke** | Fairness |

**Fazit Light:** Als **Finance-Zukunftsspiegel** unverzichtbar; als
**Ersatzprodukt** für VALEO ungeeignet. Ableitung: agentische Finance-Schicht
*auf* dem VALEO-SoR, nicht SoR-Austausch.

---

## 6. AI-native Peer-Stack (User-Vorgabe)

| Peer | Fokus | Stack (Vorgabe) | Öffentlicher Anker | VALEO-Ableitung |
|---|---|---|---|---|
| **ERPClaw** | Gesamtes ERP agent-first | Python / AI-Native | [erpclaw.ai](https://www.erpclaw.ai/), `avansaber/erpclaw` | Action-Router + Skills; Chat primär; deterministische Buchungsregeln hinter dem Agent |
| **OpenLedger** | Manipulationssicheres HB | Go / SQLite / MCP* | MCP-first Ledger-Familie (u. a. Attri open-ledger öffentlich Python/SQLite — Stack-Varianten im Audit notieren) | Immutable Tx + Contra; Audit in derselben DB-Tx; LLM halluziniert nicht ins Journal |
| **TaxHacker** | Dokumente & OCR | Next.js / PostgreSQL / Ollama | [vas3k/TaxHacker](https://github.com/vas3k/TaxHacker) | Lokale Vision-LLMs für Belege; On-Prem-Pflichtpfad |
| **OpenAccountants** | Compliance & Steuer | Python / MCP | [openaccountants.com/docs/mcp](https://www.openaccountants.com/docs/mcp) | Zitierbare Steuer-Skills statt Modellraten |

\*User-Stack Go; öffentlich auch Python/SQLite/MCP-Varianten — im Folge-Slice
exakte Repo-Wahl festnageln.

### 6.1 Peer-Matrix vs VALEO `ki-usability`

| Kriterium | ERPClaw | OpenLedger | TaxHacker | OpenAccountants | VALEO heute |
|---|---|---|---|---|---|
| Scope | Voll-ERP | Nur GL | Docs/OCR/Expenses | Tax Knowledge | Landhandel-Vollsuite |
| Primär-UI | Chat/Skills | MCP Tools | Web App | MCP | Meridian Masken + Voice |
| Agent-Tiefe | hoch (hundert Actions) | mittel (Ledger-Tools) | mittel (Extraktion) | beratend | mittel-niedrig (~78 Actions) |
| Ledger-Schutz | Validierung vor Post | Immutable + Audit-Tx | n/a (kein HB) | n/a | Journal-Guards wachsend, Agent-Muster fehlt |
| Lokale KI | modellagnostisch | n/a | Ollama-first | Cloud-MCP | Ollama in Voice-Stack; OCR nicht first-class |
| Tax/Compliance | Module | nein | schwach | sehr stark Guides | DE Meldewesen/ELSTER stark; kein Guide-MCP |
| Agrar/Waage/Ops | generisch möglich | nein | nein | nein | **Kernstärke** |

### 6.2 Kompositionsbild (empfohlen)

```text
┌─────────────────────────────────────────────────────────────┐
│  Intent: Voice / MCP / Omnibox / Agent                      │
├─────────────────────────────────────────────────────────────┤
│  Action Registry (eine ID = UI = Voice = MCP)               │
├─────────────────────────────────────────────────────────────┤
│  Domain Guards: Journal-Invarianten · Mandant · Rollen      │  ← OpenLedger-Muster
├─────────────────────────────────────────────────────────────┤
│  VALEO System of Record (Ops + Finance PostgreSQL)          │
├──────────────┬──────────────┬───────────────────────────────┤
│ OCR local    │ Tax Skills   │ Meridian Masken (Mensch)      │
│ (TaxHacker)  │ (OpenAcct.)  │ + ERPClaw-Dichte Actions      │
└──────────────┴──────────────┴───────────────────────────────┘
```

VALEO bleibt SoR für Landhandel. Peers liefern **Muster**, keine Drop-in-
Ersetzung der Suite.

---

## 7. Was fehlt — konsolidierte Gap-Liste (Usability + Future)

| Prio | ID | Gap | Vergleich | Nächster Schritt |
|---|---|---|---|---|
| P0 | U-C06-01 | Agentic Finance unter Policy | Light, Joule-Agents | Slice: Policy-Agent Close/Match/AP |
| P0 | U-C06-02 | Immutable Agent-Ledger-Vertrag | OpenLedger, ERPClaw | Slice: Contra-only + Audit-Tx für Agent-Pfade |
| P0 | U-C06-04 | Echter Kassenabschluss | Tier-1 Finance | bestehender Open-Gap Close |
| P1 | U-C10-01 | Action-Dichte generieren | ERPClaw | SD→Action-Registry Compiler |
| P1 | U-C02-02 | MCP Schreibparität | Dynamics MCP | restliche Write-Tools |
| P1 | U-C10-02 | Local OCR Provider | TaxHacker | Ollama-Vision an Docflow |
| P1 | U-C08-01 | Tax/Compliance MCP Skills | OpenAccountants | DE-Guides als Skills |
| P1 | U-C02-01 | Framework-Abschmelzung | Fiori Elements Einheit | nur Meridian-Kette |
| P1 | U-C06-03 | Finance-IA | BC/NetSuite Klarheit | Nav-Konsolidierung |
| P1 | U-C03-01 | API-Doppelgruppen Rest | — | CI-RUN Folge |
| P1 | U-C09-01 | Portal/POS Gewohnheit | Odoo POS | Channel-UX |
| P2 | U-C01-01 | Omnibox Intent-Compiler | Light conversational | UIX-Zukunft |
| P2 | U-SYS-02 | Rollen-Cockpits | Fiori Spaces | M1 Roadmap |
| P2 | U-C01-02 | Voice-Wiegen | — | UIX-072 |

---

## 8. Roadmap-Empfehlungen

### 90 Tage

1. P0 Finance-Wahrheit (Close/Journal/Agent-Guards) — keine UI-Kosmetik ohne SoR.
2. Action-Registry aus ScreenDefinitions ableiten (Messzahl: Actions ≥ 200).
3. MCP-Schreiben für Top-10 FiBu/CRM-Mutationen.
4. Finance-IA Konsolidierungsentwurf (ohne Big-Bang-Rewrite).

### 12 Monate

5. Policy-Agents für Matching, Accruals, Close-Memo (Light-Muster, VALEO-SoR).
6. Local OCR-Pipeline (TaxHacker-Muster) optional cloud.
7. DE-Steuer/Melde-Skills MCP (OpenAccountants-Muster).
8. Legacy-Masken-Abschmelzung ≥ 80 % Meridian.
9. Stufe-2 SUS mit Folkerts-/Landhandel-Rollen; Ziel SUS ≥ 68 Schnitt.

### Strategisch

10. Bleibe **Ops-SoR**; integriere agentische Finance-Schicht.
11. Kein Versuch, Light auf Waage/Ernte zu schlagen — und kein Versuch,
    Light nur mit Masken zu kopieren.
12. ERPClaw-Idee „AI entscheidet Intent, Code entscheidet Bücher“ als
    verbindliche Architekturregel in ADR festhalten.

---

## 9. Stufe-2 SUS — Kurzprotokoll

Siehe [Protokoll §8](usability-erp-audit-protocol-20261007.md). Minimal-Set:

- 5 Rollen × 3 Tasks × SUS-10 + 3 qualitative Fragen.
- Blocker aus diesem Dossier müssen vor Stufe 2 geschlossen oder als
  bekannte Einschränkung kommuniziert sein.

---

## 10. Quellen (Auswahl)

**Intern:**
`docs/design/frontend-design-skill-audit.md`, `uix-anwender-bedienwege.md`,
`uix-zukunft-masterplan.md`, `l3-full-mask-functional-gap-inventory.md`,
`docs/project-context/open-gaps-and-known-issues.md`, QA 2026-10-07
(Mask-Aktionen, Lead/PDF, Logistik-Deklarationen), `services/ki-usability`,
`packages/frontend-web` Navigation + pages.

**Extern:**
[ISO 9241-11 Überblick](https://www.softwareevaluation.de/en/foundations/iso-9241-11-simply-explained/),
Singh & Wesson ERP-Heuristiken (SAICSIT),
[Light AI ERP comparison](https://light.inc/versus/erp),
[ERPClaw](https://www.erpclaw.ai/),
[TaxHacker](https://github.com/vas3k/TaxHacker),
[OpenAccountants MCP](https://www.openaccountants.com/docs/mcp),
Agentic AI ERP Vergleiche 2026 (Joule/Copilot/Oracle/Odoo).

---

## 11. Abnahme dieses Audits

| Kriterium | Status |
|---|---|
| 10 Cluster gescored | ja |
| Tiefen-Tasks bewertet | ja |
| Tier-1 + Light + 4 Peers | ja |
| Matrix CSV | ja |
| Stufe-2 Protokoll | ja |
| Produktcode geändert | nein (Doku-only) |
| Fremde Claims angefasst | nein |
