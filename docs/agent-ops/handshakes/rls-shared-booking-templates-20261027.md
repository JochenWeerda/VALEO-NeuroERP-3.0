---
title: Handshake RLS-SHARED-BOOKING-TEMPLATES-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex: gemeinsame System-Buchungsvorlagen (Nutzerentscheidung) und offene Maskenanpassung.
---

# Handshake RLS-SHARED-BOOKING-TEMPLATES-20261027 (Claude Code → Codex)

Kette: `… → #69 systemweit → dieser PR`; Alembic
`rls_system_read_justified_20261027 → rls_booking_templates_shared_20261027`.

## Für dich (Leadbesitz, nicht von mir geändert)

`build_finance_buchungsvorlagen_liste` in `app/core/screen_definitions_listen.py`:

- Spalte `{"key": "shared", "label": "Gemeinsam", "renderKind": "boolean"}`.
- Zeilenaktion „Loeschen“ nur bei `shared = false` anzeigen, per `visibleWhen`.

Dazu die abhängigen generierten Artefakte, also Studio-Versionen und Handbuch.
`BookingTemplateResponse.shared` ist im OpenAPI nachgezogen.

## Fachlich

Gemeinsame Vorlagen kann jeder Mandant lesen und anwenden. Ändern geht nur zentral über
`valeo_system`. Beim Anwenden hat das eigene Konto Vorrang vor dem gemeinsamen
Kontenrahmen.
