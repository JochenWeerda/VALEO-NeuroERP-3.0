---
title: Finance Domain Pack
type: explanation
audience: [entwickler, architect]
owner: domain/finance
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Finance / FiBu — Domain Pack

**Owner:** `domain/finance`

Finanzbuchhaltung, AP/AR, Abschluss, DATEV-Export, UStVA/ELSTER, POS/TSE.

## Navigation

| Thema | Datei |
|---|---|
| API | [api.md](api.md) |
| Workflows | [workflows.md](workflows.md) |
| Tests | [tests.md](tests.md) |
| Entscheidungen | [decisions.md](decisions.md) |

## Sichten

- [C4 Component Finance](../../views/components/c4-finance.md)
- [fin-001 Workflow](../../../workflows/fin-001-finance-to-reporting.md)
- Index: `config/architecture-index.yaml` → `domains.finance`

## UIX / Universal Mask Generator

Finance wird nicht als erster Pilot umgestellt, bleibt aber ein harter
Interferenzbereich fuer GoBD, Audit, Freigabe und Export. Generatorfaehige
Finance-Masken muessen Audit-/Evidence-Anforderungen im `ScreenDefinition`-
Vertrag ausdruecken und duerfen keine schema-getriebenen Actions ohne
Permission- und Tenant-Pruefung ausfuehren.

## Sicheres Abfrage-Center

`auswertungen/abfrage-center` stellt ausschliesslich freigegebene
Read-Model-Datenprodukte, Felder, Filter und Aggregationen bereit. Vorschau,
persoenliche Favoriten sowie signierter Definitionsaustausch laufen ueber die
zentrale Runtime; beliebiges SQL ist nicht Bestandteil des Vertrags.

## Priorisierter L3-Berichtskatalog

`auswertungen/l3-berichtskatalog` stellt 30 feste, tenantgebundene
Berichtssichten mit gemeinsamer Summen-, Export- und Drilldown-Semantik bereit.
Die Finance-Domaene konsumiert die freigegebene Reporting-Projektion, ohne
freie SQL- oder domaenenfremde Schreiblogik einzufuehren.

`auswertungen/bonus-berechnung` speichert unveraenderbare Periodenlaeufe und
Zeilen. Korrekturen referenzieren den Ursprung als eigener Lauf; Exporte sind
mit Akteur, Grund und Parameterhash auditiert. Auftrags-, Lieferschein- und
EB-Kontrollen sind gespeicherte Sichten derselben Belegkontroll-Funktion.

## L3 Standard und Unimet

Der zentrale Legacy-Adapterrahmen nimmt `l3_standard`- und `unimet`-Payloads
hashgebunden auf und fuehrt sie nur bis in ein kanonisches, abgestimmtes
Staging. Finance-Zielbuchungen bleiben gesperrt, bis Kundenformat, Mapping und
fachliche Pilotfreigabe vorliegen.
