---
title: ADR-069 Gegatete L3-Standard- und Unimet-Adapter
type: adr
audience: [architektur, entwickler, product, qa, betrieb]
owner: domain/integration
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-069 Gegatete L3-Standard- und Unimet-Adapter

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

Die L3-Inventur nennt Standard-Schnittstelle und Unimet, liefert aber keine
verlaesslichen Kundenformate, Feldlayouts oder produktiven Zielbuchungen. Eine
scheinbar fertige Parserimplementierung ohne diese Evidenz waere riskant.

## Entscheidung

- `l3_standard` und `unimet` sind feste, standardmaessig inaktive Profile.
- Ein Profil wird erst `ready`, wenn der versionierte Formatvertrag alle
  profilspezifischen Angaben, einen Echtdaten-Sample-Hash und eine nicht leere
  deklarative Source-Target-Map enthaelt. `pilot` kann nicht per Konfiguration
  vorgetaeuscht werden.
- Intake ist durch Tenant, Profil und externe ID idempotent; SHA-256 erkennt
  abweichende Wiederverwendung. Nicht bereite Profile fuehren in Quarantaene.
- Mapping erzeugt ausschliesslich kanonische Staging-Records. Fehlerzeilen,
  Mengenabweichungen, Retry-/Freigabeaktionen und Gruende sind auditierbar.
- Nur ein abweichungsfrei reconciliierter Batch kann fuer einen Pilot
  freigegeben werden. Auch danach bleibt `execution_enabled=false`.
- `schnittstelle/legacy-adapter-monitor` ist die native Operator-Worklist.

## Konsequenzen

Der repo-seitig verantwortbare Teil von `L3-GAP-IFACE-014` ist geschlossen.
Reale Formatmuster, Mappingabnahme, Zieladapter und Produktivpilot bleiben
explizite externe Aktivierungs-Gates.
