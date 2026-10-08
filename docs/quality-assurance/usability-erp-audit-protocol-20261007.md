---
title: ERP-Usability-Auditprotokoll VALEO NeuroERP
type: reference
audience: [qa, produkt, agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-10-07
version: 1.0.0
description: Methodik und Durchführung Stufe-1 Experten-Usability-Audit systemweit; Grundlage für Vergleichsdossier und Stufe-2 SUS.
---

# ERP-Usability-Auditprotokoll — 2026-10-07

**Slice:** `USABILITY-SYSTEMAUDIT-20261007`
**Stufe:** 1 — Experten-Audit (systemweit)
**Ergebnisartefakte:**

- Cluster-Matrix: [docs/gap/usability-systemaudit-matrix-20261007.csv](../gap/usability-systemaudit-matrix-20261007.csv)
- Befunde: [docs/gap/usability-systemaudit-findings-20261007.csv](../gap/usability-systemaudit-findings-20261007.csv)
- Dossier: [usability-erp-vergleichsdossier-20261007.md](usability-erp-vergleichsdossier-20261007.md)

## 1. Zweck

Bewertung der Gebrauchstauglichkeit von VALEO NeuroERP über alle Domänencluster
und Kernprozessketten, mit anschließendem Capability-/Zukunftsvergleich gegen
führende Suites und AI-native Finance-/Agent-Peers (Light, ERPClaw, OpenLedger,
TaxHacker, OpenAccountants).

## 2. Methodik

| Schicht | Quelle | Anwendung |
|---|---|---|
| ISO 9241-11 | Wirksamkeit, Effizienz, Zufriedenheit im Kontext | Task-Erfolg, Schrittzahl, Feedback |
| ISO 9241-110 | Dialogprinzipien | Cluster-Kurzscore 0–5 |
| Singh & Wesson ERP-Heuristiken | Navigation, Presentation, Learnability, Task Support, Customization | Cluster-Score 0–5 je Heuristik |
| WCAG 2.2 AA + Meridian | Touch 44 px, Register, h1, Tokens | Pflichtlayer |
| VALEO Flow-Spine / MASKEN | ProcessBand vs. ProcessRibbon, Belegketten-Layout | Fach-UX |
| SUS | Bangor et al. | Stufe 1: Experten-Schätzung pro Cluster; Stufe 2: echte Nutzer |

### Schweregrade

| Stufe | Bedeutung |
|---|---|
| Blocker | Kernaufgabe nicht zuverlässig erledigbar oder Scheinerfolg |
| Major | Deutliche Reibung / Fehlergefahr / Inkonsistenz |
| Minor | Lokal störend, Workaround vorhanden |
| Nice | Zukunfts-/Differenzierungsverbesserung |

## 3. Nutzungskontext (Rollen)

Aus [uix-anwender-bedienwege.md](../design/uix-anwender-bedienwege.md):

| Rolle | Gerät | Erster Weg |
|---|---|---|
| Außendienst | Handy/Tablet | Start → Handel → Kunden / Suche / Stimme |
| Annahme / Waage | Tablet, Handschuhe, Lärm | Start → Ernte → Warteschlange |
| Disposition | Desktop + Tablet | Start → Lager / Leitstand |
| Buchhaltung | Desktop, Tastatur | Start → Finanzen; Kürzel |
| Leitung | Desktop | Start-KPIs, Drilldown |

## 4. Inventur-Basis (Stand Audit)

| Metrik | Wert | Quelle |
|---|---:|---|
| Seitenordner unter `pages/` | ~90 Domänenordner | Dateisystem |
| TSX/TS-Seiten (rekursiv) | ~697 | Dateisystem |
| Nav-Labels (domains/*.tsx) | ~439 | Grep |
| Native ScreenDefinitions (`"type":"native"`) | ~90–99 | screen_definitions*; Workboard 99 |
| `BEKANNTE_LUECKEN` Maskenaktionen | 0 | `check_mask_command_endpoint_inventory.py` |
| KI-Usability ActionOut-Einträge | ~78 | `action_registry.py` |
| Nav-Packs | 4 (core, commercial, finance, operations) | `manifest.tsx` |

## 5. Cluster (systemweit)

1. Start / Launchpad / AppShell / Command Palette / Voice
2. CRM / Verkauf / Belegkette O2C
3. Einkauf / S2P
4. Lager / Logistik / Fuhrpark
5. Agrar / Ernte / Waage / NaWaRo / Kontrakte
6. Finance / FiBu / Bank / Kasse / Zahlungslauf
7. Personal / Bewerbungen
8. Compliance / Meldewesen / ESG
9. Portal / POS / Shop
10. Admin / Agent Ops / Masken-Studio / Docflow

## 6. Tiefen-Tasks

| ID | Kette | Erfolgskriterium |
|---|---|---|
| T-O2C | Angebot → Auftrag → Lieferschein → Rechnung | ProcessRibbon + echte Mutation + Pending-Guard |
| T-S2P | Anfrage → Bestellung → Avis/WE → Eingangsrechnung | Kein Scheinerfolg; Mandant/Rollen |
| T-ERNTE | Annahme → Wiegen → Abrechnung/PDF | Touch 44 px; PDF archivierbar |
| T-FIN | Zahlungslauf / Bankabgleich / Journal | Vier-Augen; keine Scheinfreigabe |
| T-CRM | Lead → Opportunity / KIM-360 | Kanonisches `crm_leads`; Aktivität im Reiter |
| T-VOICE | Intent → Action-ID → Handler | Gleiche ID wie Toolbar/Palette |

## 7. Grenzen Stufe 1

- Keine moderierte Lab-Session mit Landhandel-Endnutzern.
- Keine Stoppuhr-Messung produktiver Schichten.
- SUS-Werte sind **Experten-Schätzungen** mit Unsicherheitsband (±8).
- Vendor-Matrizen (Light u. a.) sind öffentlich dokumentierte Claims, keine
  unabhängigen Lab-Messungen.
- Fremde aktive Code-Claims (CI-RUN-REPAIR, MANDANT-FINANZ, BANK-RECONCILIATION)
  wurden nicht überschrieben.

## 8. Stufe-2-SUS-Protokoll (Folge)

1. 5–8 Nutzer je Rolle (Außendienst, Waage, Disposition, FiBu, Leitung).
2. Je Rolle 3 Tasks aus Abschnitt 6.
3. Nach Tasks SUS-10 (deutsch validierte Fassung).
4. Severity-Rating mit Beobachter; Video nur mit Einwilligung.
5. Ziel: SUS ≥ 68 Domänenschnitt; Blocker = 0 vor Rollout-Welle.

## 9. Durchführung

| Schritt | Status | Nachweis |
|---|---|---|
| Claim Workboard | erledigt | `USABILITY-SYSTEMAUDIT-20261007` |
| Inventur Cluster | erledigt | Matrix CSV |
| Heuristik-Scoring | erledigt | Matrix CSV |
| Tiefen-Tasks | erledigt | Dossier §3 |
| Vergleich Tier-1 + Light + Peer-Stack | erledigt | Dossier §4–6; Peer-CSV |
| Open-Gaps-Verweis | erledigt | open-gaps-and-known-issues.md |
| Gap-Hub / Archiv-Banner | erledigt | `docs/gap/`, `docs/_internal/archive/gap/` |
| ACTION-DEN Nachzug | erledigt | 85 mask:*; Generator `--check`; QA 20261008 |
