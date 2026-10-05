---
title: ADR-059 Produktionsleitstand als Projektion kanonischer ERP-Quellen
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/agrar
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-059 Produktionsleitstand als Projektion kanonischer ERP-Quellen

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

VALEO besitzt Mischfutterauftraege mit Bestands-, Chargen- und FIBU-Kette sowie
Ruestlisten und Lagerbewegungen. Fuer den aus L3 gewohnten Tagesablauf fehlt
eine gemeinsame Produktionsliste fuer Muehle, Umbuchung, Stapelbuchung und
Nachbearbeitung.

## Entscheidung

- Der Leitstand fuehrt keine zweite Produktionsbuchhaltung. Er projiziert
  kanonische Quellobjekte ueber tenantgebundene `source_type/source_ref`-Paare.
- Allgemeine Muehlen-, Umbuchungs-, Stapel- und Nachbearbeitungsvorgaenge
  verwenden einen geschlossenen Operations-Lifecycle. Jeder Statuswechsel
  verlangt einen Grund und erzeugt append-only Audit.
- Mischfutterauftraege werden idempotent in das Read-Model synchronisiert;
  Bestandsabzug, Charge und FIBU bleiben in ihrer bestehenden Fachlogik.
- `produktion/produktionsleitstand` ist eine native, serverseitig paginierte
  Meridian-Worklist mit Quell-Deep-Link und bestehendem Produktionsdruckpfad.
- Physische SPS-/Muehlenbefehle bleiben ausserhalb des ERP-Lifecycles und
  benoetigen einen freigegebenen Adapter.

## Konsequenzen

`L3-GAP-PROD-003` ist repo-seitig geschlossen. Anlagenadapter, reale
Schichtdaten und Pilotabnahme bleiben externe Rollout-Gates.
