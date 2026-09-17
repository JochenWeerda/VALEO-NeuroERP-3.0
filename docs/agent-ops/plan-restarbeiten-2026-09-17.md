---
title: Plan Restarbeiten
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Was nach Feldvertrag und Adressgate noch offen ist — gemessen, priorisiert und mit Zuständigkeit.
---

# Plan: der Rest

Die Adressen stimmen (`check_frontend_api_calls` = 0), die Maskenköpfe sprechen
die Sprache ihrer Endpunkte (`check_field_contracts` = 0 Abweichungen). Was
bleibt, ist **eine Ebene tiefer**: Endpunkte, die Tabellen lesen, die es nicht
gibt.

## Der Kassensturz

| Messung | Stand |
|---|---|
| Frontend-Aufrufe ohne Route | 0 |
| Maskenfelder gegen deklarierte Antwort | 379 geprüft, 0 Abweichungen |
| Maskenköpfe ohne deklarierte Antwort | 0 |
| Tabellenquellen ohne Zeilenform | 27 (17 generisch, **10 fachlich**) |
| **Endpunkte, die fehlende Tabellen lesen** | **58 Tabellen**, davon **31 an lebenden Wegen** |

Von den 58 haben **24 einen Doppelgänger** — die Tabelle gibt es, nur unter
einem anderen Namen oder Schema. Das ist dieselbe Klasse wie `invoice_id` statt
`invoice_number`: kein fehlendes Stück Software, sondern ein falscher Verweis.

## R1 — Falsche Schemaverweise (läuft)

Neun Fälle mit **exaktem** Namensdoppelgänger in einem anderen Schema. Je Fall
prüfen, ob die Spalten passen, dann den Verweis ziehen — sonst benennen.

| Verweis | Wirklich unter | Stand |
|---|---|---|
| `domain_erp.sales_invoices` / `_lines` (xrechnung) | `domain_sales.*` | **erledigt** |
| `domain_erp.business_partners.name` (xrechnung) | Spalte heißt `partner_name` | **erledigt** |
| `domain_finance.journal_entries` (budget_planning) | `domain_erp` **und** `domain_shared` — zwei Kandidaten | offen, Entscheidung nötig |
| `domain_agrar.agrar_contracts` (crm_360) | `domain_inventory.agrar_contracts` | offen |
| `domain_agrar.kontrakte` (price_calculation) | `domain_einkauf.kontrakte` | offen |
| `domain_finance.open_items` | `domain_erp.open_items` | offen |
| `domain_finance.bank_accounts` | `domain_erp.bank_accounts` | offen |
| `domain_pos.pos_transactions` | `domain_erp.pos_transactions` | offen |
| `domain_shared.business_partners` (finance_invoices) | `domain_erp.business_partners` | offen |
| `domain_crm.sales_order_lines` (compat) | `domain_crm.sales_order_items` | offen |

## R2 — Gate: kein Endpunkt liest eine Tabelle, die es nicht gibt

Wie bei Adressen und Feldern: messen, Schwelle setzen, Zahl darf nur sinken.
Getrennt nach **lebend** (von Maske oder Frontend erreichbar) und **ruhend**.
Ohne dieses Gate wächst der Bestand beim nächsten Endpunkt wieder.

## R3 — Fachliche Zeilenformen (10)

`crm/customer-360` (4 Register), `agrar/kontrakte` (2), Fütterung (4). Dasselbe
Muster wie bei Auftrag und Rechnung: Zeilenmodell deklarieren, dann meldet das
Gate die leeren Spalten von selbst.

## R4 — Fehlende Tabellen an lebenden Wegen

Nur wo die Fachlichkeit klar ist. Kandidaten mit Belegbezug zuerst:
`domain_audit.attestations` (der Lieferscheindruck schreibt dorthin),
`domain_shared.sepa_mandates` (Lastschrift), `domain_erp.accounting_periods`
(Periodenabschluss). Der Rest wird benannt, nicht geraten.

## R5 — Nicht bauen, entscheiden lassen

- **27 ruhende Tabellen**: Code ohne Weg dorthin. Löschen oder bauen ist eine
  Produktentscheidung, keine Aufräumarbeit.
- **`lager/leitstand`**: Cockpit ohne Inhalt und ohne Seite. Was soll es zeigen?
- **Docflow-Rechnung neben `domain_sales.sales_invoices`**: zwei Welten für
  denselben Beleg.
- **GoBD-Nummernkreis**: `_ersatznummer()` ist eindeutig, aber nicht
  fortlaufend.
- **20 handgeschriebene Listenmasken**: das nächste Programm, kein Fehler.

## Zuständigkeit

Die generischen `/masks/.../tabs/`-Stubs (17 der 27 Zeilenformen) nimmt Cursor.
Alles hier Aufgeführte liegt bei Claude Code, außer den unter R5 genannten
Entscheidungen.
