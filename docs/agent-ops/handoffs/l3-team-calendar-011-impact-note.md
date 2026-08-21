---
title: Architecture Impact Note L3-TEAM-CALENDAR-011
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-TEAM-CALENDAR-011

- **Domains:** Platform, CRM, HRM
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-064](../../adr/adr-064-team-calendar-privacy-projection.md)
- **Containeraenderung:** keine
- **Datenmodell:** additive Owner-/Team-/Privacy-Spalten und Memberships
- **UI-Kette:** bestehende native `planung/kalender`-ScreenDefinition

## Datenschutzgrenze

Teamzugriff wird serverseitig aus aktiven Mitgliedschaften ermittelt. Private
Fremdtermine werden unabhaengig von Detailrechten auf Frei/Belegt reduziert.

## Checks

Zehn Kalender-/Teamkalender-Backendtests, TypeScript und Ruff sind gruen.
Alembic hat mit `team_calendar_20260821` genau einen Head. OpenAPI (2.719
Pfade), Route-Inventar (912/912), Agent-Handbuch (54 Masken), ADR-Navigation
(69) und Architekturindex sind aktuell; `arch:validate` und `arch:drift
--strict` sind gruen.
