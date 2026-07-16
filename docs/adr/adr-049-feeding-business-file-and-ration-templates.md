---
title: "ADR-049 Betriebsakte und unveraenderliche Rationsvorlagen"
type: adr
audience: [architektur, domain, entwickler, qa]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-16
version: 1.0.0
---

# ADR-049 Betriebsakte und unveraenderliche Rationsvorlagen

**Status:** Accepted

**Datum:** 2026-07-16

## Kontext

Betrieb, Gruppen, Rationen, Bewertungen und Analysereife existierten als getrennte
Journeys. `based_on_version_id` dokumentierte nur Kopien innerhalb einer Ration;
ein persistenter, grant-sicherer Vorlagenkatalog fehlte.

## Entscheidung

- Eine Vorlage speichert Metadaten und den Verweis auf genau eine unveraenderliche
  `ration_version`; Futter-, Analyse- und Ergebnisdaten werden nicht dupliziert.
- Vorlagen sind append-only. Aendern oder Loeschen wird per Trigger verhindert.
- Anwenden erzeugt ueber den Lifecycle-Service eine neue Draft-Version. Snapshot,
  `based_on_version_id`, Auditgrund und `expected_latest_version_no` sind eindeutig.
- Kopieren ist nur zwischen Rationen derselben Fuetterungsgruppe und desselben
  Tenants erlaubt. Damit bleibt das Bedarfsprofil fachlich vergleichbar.
- Die Betriebsakte ist ein grant-sicheres Read-Model. Fehlende Reife wird als
  `not_checked`/`incomplete` und nie als gesunde Null-KPI dargestellt.
- Die UI verwendet die zentrale Meridian-Kette; nur die zwei Commands sind
  schmale Domain-Overlays.

## Konsequenzen

Vorlagen bewahren reproduzierbare Herkunft ohne eine zweite Rationswahrheit.
Aufgaben, Berichte und direkte Analysenlisten koennen als weitere Projektionen
in dieselbe ObjectPage aufgenommen werden.
