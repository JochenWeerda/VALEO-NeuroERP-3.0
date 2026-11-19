---
title: Kundenprofil innerhalb des bestehenden Partneraggregats
status: proposed
owner: Codex
type: adr
last_reviewed: 2026-11-17
---

# Kundenkopf als Studio-Projektion

**Status:** Proposed
**Datum:** 2026-11-17

## Kontext

Entscheidungsstufe: Significant (neuer interner Endpointcluster/Event im bestehenden
CRM-Kontext). Vorgeschlagen: vorhandene skalare BusinessPartner-Daten ueber dieselbe
Studio-Kundenakte lesbar und als atomaren, teilweisen Domain-Command pflegbar machen.
Kein neuer Bounded Context, keine konkurrierende Kundentabelle, kein Rollenmodell.
Die Kundengrunddatenprojektion und Einwilligungsnachweise bleiben in ihren
bestehenden Fachprozessen. Sechs bestehende Untertabellenwege werden erhalten.

## Entscheidung

Die Metadatenquelle config/customer_master_profile.json speist Sichtfelder und
Eingabefelder; serverseitig gelten zusaetzlich die vorhandenen DTO-Typen und
ORM-Nullability. UI, MCP und CLI adressieren dieselbe deklarierte Aktion;
schreibende MCP-Freischaltung bleibt der vorhandenen Capability-Policy unterworfen.

## Konsequenzen

Freigabegrundlage: [Feldinventar und Abnahmestand](../quality-assurance/customer-master-field-parity-20261117.md).
Vollstaendige Untertabellen- und Browserparitaet ist noch kein angenommener Stand.
