---
title: ADR-067 Governed L3-Berichtskatalog
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/reporting
status: proposed
last_reviewed: 2026-08-22
version: 1.1.0
---

# ADR-067 Governed L3-Berichtskatalog

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

VALEO besass domaenenspezifische Berichte, aber keinen einheitlichen, gegen die
L3-Screenshot-Inventur priorisierten Katalog mit gleicher Parameter-, Summen-,
Export- und Drilldown-Semantik.

## Entscheidung

- Der Katalog enthaelt 30 feste Berichte fuer Vertreter, Kunde, Artikel/-gruppe,
  Charge, Ernte, Strecke, Meldungen, Disposition und Bonus; freie SQL-
  Ausfuehrung ist ausgeschlossen.
- Domaenen liefern idempotente, tenantgebundene Facts mit stabiler interner
  Quellenroute. Die Reporting-Projektion ist kein neues Schreibmodell der
  Quellaggregate.
- Listen- und Gesamtsummen, CSV und Drilldown verwenden denselben
  freigegebenen Zeitraum-/Filtervertrag.
- Exporte verlangen einen Grund und werden mit Akteur und Parameterhash
  append-only auditiert.
- `auswertungen/l3-berichtskatalog` bleibt eine native Meridian-Worklist ueber
  der zentralen Runtime-Kette.
- Bonusberechnungen werden als unveraenderliche Periodenlaeufe mit Zeilen,
  Korrekturbezug und auditierter Ausgabe gespeichert. Eine Korrektur veraendert
  nie den Ursprungslauf.

## Konsequenzen

`L3-GAP-REPORT-012` sowie die Artikel-, Kunden-, Chargen- und Bonus-Leaf-Gaps
sind repo-seitig geschlossen. Fachliche Summenabnahme mit
produktiven L3-/VALEO-Echtdaten bleibt ein externes UAT-Gate.
