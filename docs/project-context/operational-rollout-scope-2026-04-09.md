---
title: Operational Rollout Scope 2026-04-09
type: reference
audience: [entwickler, product]
owner: Claude Code
status: umgesetzt
last_reviewed: 2026-06-27
version: 3.0.0
description: Rollout-Scope und Arbeitsmodell fuer operative Erstausrollung — Vorgang, Objekt, Ressourcenlage, Wirtschaftslage, Governance und Naechste-Aktion-Struktur (Stand 2026-04-09).
---

# Operational Rollout Scope 2026-04-09

## Ziel

Das gemeinsame Arbeitsmodell aus:

- Vorgang
- Objekt
- Ressourcenlage
- Wirtschaftslage
- Governance
- Naechste Aktion

wird nur dort ausgerollt, wo ein echter operativer Mehrwert entsteht.

Es ist ausdruecklich **kein** Ziel, jede Liste oder jede Detailmaske mit denselben Leitstandselementen zu ueberziehen.

## Ausgerollte Fachmasken

Diese Masken haben jetzt einen kompakten Fallkopf, einen knappen Kontextblock und eine kurze Timeline, jeweils nur aus bereits geladenen Daten:

- Einkauf:
  - `angebote-liste.tsx`
  - `anfragen-liste.tsx`
  - `angebot-stamm.tsx`
  - `anfrage-stamm.tsx`
  - `bestellung-stamm.tsx`
  - `rechnungseingang.tsx`
- Annahme / Physische Kette:
  - `lkw-registrierung.tsx`
  - `rohware.tsx`
  - `qualitaets-check.tsx`
  - `wiegeschein-detail.tsx`
- Qualitaet:
  - `reklamation-detail.tsx`
- Finance:
  - `abschluss.tsx`
  - `buchungserfassung.tsx`
  - `mahnwesen.tsx`
  - `op-debitoren.tsx`
  - `op-kreditoren.tsx`
  - `finance/bank-abgleich.tsx`
  - `finance/payment-matching.tsx`
  - `finance/ap-invoices-list.tsx`
  - `finance/ap-invoice-form.tsx`
  - `fibu/kreditoren.tsx`
  - `fibu/zahlungslaeufe.tsx`
  - `fibu/offene-posten.tsx`
  - `fibu/zahlungseingaenge.tsx`
  - `fibu/zahlungsvorschlaege.tsx`
  - `finance/ustva.tsx`
  - `fibu/elster-online.tsx`
  - `fibu/schnittstellen-center.tsx`
  - `fibu/schnittstelle-fibu.tsx`
  - `fibu/monatswerte.tsx`
  - `fibu/buchungsjournal.tsx`
  - `fibu/abschluss-checklist-detail.tsx`
  - `fibu/bwa.tsx`
  - `fibu/bilanz.tsx`
  - `finance/zahlungslauf-kreditoren.tsx`
  - `finance/lastschriften-debitoren.tsx`
  - `fibu/buchhaltungsuebersicht.tsx`
- Service / CRM:
  - `service/anfrage-detail.tsx`
  - `crm/opportunity-detail.tsx`
- Weitere Sammel-/Follow-up-Masken:
  - `annahme/abrechnung.tsx`
  - `annahme/warteschlange.tsx`
  - `charge/rueckverfolgung.tsx`
  - `charge/wareneingang.tsx`
  - `einkauf/rechnungseingaenge-liste.tsx`
  - `einkauf/anlieferavis.tsx`
  - `einkauf/anlieferavis-liste.tsx`
  - `einkauf/auftragsbestaetigung.tsx`
  - `einkauf/auftragsbestaetigungen-liste.tsx`
  - `labor/proben-liste.tsx`
  - `qualitaet/labor-liste.tsx`
  - `fuhrpark/fahrzeug-stamm.tsx`
  - `futtermittel/charge-verfolgung.tsx`
  - `einkauf/lieferanten-stamm.tsx`
  - `logistik/tourenplanung.tsx`
  - `waage/liste.tsx`

## Mehrwertkriterien

Das Modell wird eingesetzt, wenn mindestens drei dieser Punkte gleichzeitig gelten:

- echte Statusuebergaenge oder Freigaben
- sichtbare Risiken oder Blocker
- ein benoetigter Owner oder Eskalationspfad
- ein Folgeobjekt oder naechster Prozessschritt
- fachlich relevante Ressourcen-, Finanz- oder Governance-Lage

## Bewusst schlank gelassene Masken

Schlanke Register, reine Such-/Listenraeume und einfache Nachschlageflaechen bleiben bewusst ohne Leitstandskopf, wenn sonst nur Informationsduplikate entstehen wuerden.

Typische Beispiele:

- Register mit Fokus auf Suche, Filter und Export
- reine Stammdatentabellen ohne akuten Vorgangscharakter
- Listenraeume ohne Owner-, Eskalations- oder Blockerlogik
- einfache Report-/Cockpit-Seiten, deren Kernaussage bereits durch KPI oder Segmentierung getragen wird

## Performance-Regel

Der Rollout darf keine zusaetzlichen API-Requests erzwingen.

Die neuen UI-Bausteine duerfen nur:

- bereits geladene Query-Daten
- bestehende Router-/Workflow-Kontexte
- lokal berechnete Verdichtung

verwenden.

## Gestaltungsregel

Der Kopfbereich bleibt bewusst leicht:

- 1 Fallkopf
- 1 kurze Timeline
- 1 kompakter Kontextblock

Wenn eine Maske mehr erklaeren muss, gehoert die Tiefe in bestehende Fachkarten oder Tabs, nicht in den Leitstandskopf.
