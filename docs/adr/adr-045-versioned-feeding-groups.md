---
title: "ADR-045 Versionierte Fuetterungsgruppen und betrieblicher Zugriffsscope"
type: adr
audience: [architektur, domain, entwickler, qa]
owner: domain/agrar
status: proposed
last_reviewed: 2026-07-15
version: 1.0.0
---

# ADR-045 Versionierte Fuetterungsgruppen und betrieblicher Zugriffsscope

**Status:** Proposed

**Datum:** 2026-07-15

## Kontext

`feeding_groups` enthielt operative Basiswerte, aber weder typisierte
Gruppenprofile, Traechtigkeit/Milchinhaltsstoffe, zeitliche Gueltigkeit noch eine
unveraenderliche Parameterhistorie. Die Lifecycle-API war nur tenant- und
rollenbezogen; damit konnten externe Berater ohne Betriebs-Grant Gruppenlisten
des Tenants sehen. Eine freie Spezialseite haette zudem die Meridian-Runtime
umgangen.

## Entscheidung

- Der bestehende Agrar-/Rations-Optimization-Kontext bleibt verantwortlich.
- Der Gruppenkopf traegt den aktuellen, optimistisch versionierten Stand.
- Jede Anlage/Aenderung schreibt einen append-only Snapshot nach
  `feeding_group_revisions`; Update verlangt `expected_revision` und Grund.
- Profile, Schwangerschaft, Inhaltsstoffe, Risiko und Gueltigkeit sind zentral
  typisiert und durch API plus DB-Checks geschuetzt.
- Listen und Einzelzugriffe kombinieren Domainrolle mit Ersteller oder aktivem
  Business-Grant; verweigerte Einzelzugriffe liefern 404 ohne Existenzsignal.
- Die ObjectPage ist die native ScreenDefinition `agrar/feeding-group`; nur der
  fachliche Revisionsdialog bleibt ein schmales Domain-Overlay.

## Konsequenzen

Rationsversionen koennen weiterhin auf die stabile Gruppen-ID verweisen; der
verwendete Parameterstand bleibt ueber Revision/Snapshot nachvollziehbar.
Legacygruppen erhalten Profil `custom`, Risiko `low`, Gueltigkeit ab Migration
und Revision 1. Businesslose Gruppen sind nur fuer Ersteller oder Admin sichtbar,
bis der kontrollierte Backfill abgeschlossen ist.

## Verworfene Alternativen

- Gruppenwerte in jeder Rationsversion duplizieren: keine pflegbare Stammsicht.
- In-place Update ohne Historie: Beratung und Wirkung nicht auditierbar.
- Tier-Level-Vollmodell: fuer FEED-CORE-016 unnoetig; Provider bleibt Quelle.
- Handgebaute Gruppen-Spezialseite: verletzt den zentralen Meridian-Vertrag.
