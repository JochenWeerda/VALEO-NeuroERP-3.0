---
title: Handshake USTVA-WAHRHEIT-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Uebergabe Claude -> Codex fuer die Umsatzsteuer-Voranmeldung aus dem Hauptbuch mit gespeicherten Bearbeitern und Transferticket.
---

# Handshake USTVA-WAHRHEIT-20261027 (Claude Code → Codex)

## Basis und Reihenfolge

- Basis `claude/rls-domain-shared-20261027` (#79), Zweig `claude/ustva-wahrheit-20261027`; nach #79 integrieren.
- Alembic `rls_domain_shared_20261027 → vat_return_bearbeiter_20261027`, ein Head. Nur additive Spalten,
  eine Vorgabe und eine Pruefbedingung; live 0 Anmeldungen.

## Fuer dich

1. **API-Vertrag:** `POST /finance/vat-return/{id}/approve` ohne Rumpf (Freigebender aus dem Token);
   `POST /{id}/submit` verlangt `transferticket` statt `submitted_by`; `calculate` antwortet 422 mit `klaerungen`,
   wenn die Voranmeldung nicht eindeutig ist. `elster_reference` ist das Transferticket, sonst `null`.
2. **Live-relevant:** `/compliance/ustva` meldet `UEBERMITTELT` nur noch mit Transferticket; vorher `EINGEREICHT`
   ohne Uebermittlung. Die Zahlen sind nicht mehr 0, sondern die gebuchten Salden.
3. **Masken (dein Bereich):** Die Studio-Masken `finance/ustva` und `export/ustva` sind Listen ohne Ablauf; ihre
   Spalten passen nicht zur API. Bitte eine Ablaufmaske (berechnen, pruefen, freigeben, Ticket festhalten).
4. **Kasse auf dieser Basis:** `pos/terminal` und `pos/retoure` sind generische Listen (`pos/retoure` liest
   `/pos/dsfinvk/export`); kassieren und Retouren buchen geht auf dieser Basis nicht. Siehe PR #80.
5. **`closing_checklist_validation.py` TAX-001** zaehlt `approved` nicht mit (dein Closing-Bereich).
6. OpenAPI nur fuer meine Pfade; die vorbestehende Drift (closing-checklists, biostimulanzien, weighing-tickets) bleibt bei dir.
7. Nicht beruehrt: Freigabe-Engine, `ebilanz_elster.py`, Studio-Registry, Systemrollen, Live.
