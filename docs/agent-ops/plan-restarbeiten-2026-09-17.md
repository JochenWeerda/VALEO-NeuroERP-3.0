---
title: Plan Restarbeiten
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-17
version: 2.0.0
description: Was nach Feldvertrag und Adressgate noch offen war — abgearbeitet, mit dem Rest, der eine Entscheidung braucht.
---

# Plan: der Rest

Die Adressen stimmen (`check_frontend_api_calls` = 0), die Maskenköpfe sprechen
die Sprache ihrer Endpunkte (`check_field_contracts` = 0 Abweichungen). Was
bleibt, ist **eine Ebene tiefer**: Endpunkte, die Tabellen lesen, die es nicht
gibt.

## Der Kassensturz

Stand nach Abarbeitung (17.09.2026 abends). Die Klammerwerte sind der
Ausgangsstand vom Vormittag.

| Messung | Stand |
|---|---|
| Frontend-Aufrufe ohne Route | 0 |
| Maskenfelder gegen deklarierte Antwort | **431** geprüft (379), **0** Abweichungen |
| Maskenköpfe ohne deklarierte Antwort | 0 |
| Tabellenquellen ohne Zeilenform | **17** (27) — alle generische Stubs, Cursor |
| Endpunkte, die fehlende Tabellen lesen | **28 lebend** (31), **19 ruhend** (23) |

Die 431 gegenüber 379 geprüften Feldern sind der eigentliche Gewinn: Nicht die
Abweichungen wurden weggeräumt, sondern **52 Felder mehr sind überhaupt
prüfbar** geworden. 28 davon meldeten beim ersten Blick sofort einen Fehler
(18 in der Kunden-360, 10 in den Kontrakten).

## R1 — Falsche Schemaverweise (abgeschlossen bis auf eine Entscheidung)

Neun Fälle mit **exaktem** Namensdoppelgänger in einem anderen Schema. Je Fall
prüfen, ob die Spalten passen, dann den Verweis ziehen — sonst benennen.

| Verweis | Wirklich unter | Stand |
|---|---|---|
| `domain_erp.sales_invoices` / `_lines` (xrechnung) | `domain_sales.*` | **erledigt** |
| `domain_erp.business_partners.name` (xrechnung) | Spalte heißt `partner_name` | **erledigt** |
| `domain_finance.journal_entries` (budget_planning) | `domain_erp` **und** `domain_shared` — zwei Kandidaten | **erledigt** — `domain_erp.journal_entry_lines` JOIN Kopf; ein `amount` gibt es nirgends, nur debit/credit |
| `domain_agrar.agrar_contracts` (crm_360) | `domain_inventory.agrar_contracts` | **erledigt** — auch Spalten und Statuswerte (`open`, nicht `AKTIV`) |
| `domain_agrar.kontrakte` (price_calculation) | `domain_einkauf.kontrakte` | **erledigt** — der Preis steht an der Position, nicht im Kopf |
| `domain_finance.open_items` | `domain_erp.open_items` | **erledigt** (mit der Liquiditätssicht) |
| `domain_finance.bank_accounts` | `domain_erp.bank_accounts` | **erledigt** |
| `domain_pos.pos_transactions` | `domain_erp.pos_transactions` | **offen, Entscheidung**: `domain_erp.pos_transactions` hat vier Spalten (id, tenant_id, source, created_at) — keine `payment_method`, kein `amount`. Umhängen tauschte eine fehlende Tabelle gegen fehlende Spalten. |
| `domain_shared.business_partners` (finance_invoices) | `domain_erp.business_partners` | **erledigt** — `domain_crm.business_partners.name_1` |
| `domain_crm.sales_order_lines` (compat) | `domain_crm.sales_order_items` | **erledigt** |

## R2 — Gate: kein Endpunkt liest eine Tabelle, die es nicht gibt

Wie bei Adressen und Feldern: messen, Schwelle setzen, Zahl darf nur sinken.
Getrennt nach **lebend** (von Maske oder Frontend erreichbar) und **ruhend**.
Ohne dieses Gate wächst der Bestand beim nächsten Endpunkt wieder.

## R3 — Fachliche Zeilenformen (10) — **abgeschlossen**

Dasselbe Muster wie bei Auftrag und Rechnung: Zeilenmodell deklarieren, dann
meldet das Gate die leeren Spalten von selbst. Es meldete 28.

| Maske | Register | Befund |
|---|---|---|
| `crm/customer-360` | 4 | **alle vier** zeigten an der Antwort vorbei (18 Spalten) |
| `agrar/kontrakte` | 2 | **beide** zeigten vollständig vorbei (10 Spalten) |
| Fütterung | 4 | Spalten waren in Ordnung — jetzt gemessen statt geglaubt |

Zwei Register waren nicht nur falsch beschriftet, sondern leer: Die Kunden-360
las `domain_crm.activities` mit `activity_type`, `subject`, `customer_id` —
die Tabelle hat `type`, `title`, `date` und kennt ihren Kunden **nur beim
Namen** (`customer` ist ein String, keine Referenz). Die Kontraktumsätze hatten
gar keinen Betrag; Menge und Preis stehen da, also rechnet ihn jetzt der
Endpunkt aus.

## R4 — Fehlende Tabellen an lebenden Wegen — **abgeschlossen, soweit die Fachlichkeit trägt**

| Tabelle | Stand |
|---|---|
| `domain_audit.attestations` | **gebaut**. Der INSERT steht ungeschützt im Druckpfad — jeder Nachdruck eines gebuchten Lieferscheins lief in einen 500, der Lieferschein blieb ungedruckt. Die Governance war nicht streng, sondern kaputt. |
| `domain_compliance.data_erasure_requests` | **gebaut** (kam unterwegs dazu, siehe unten) |
| `domain_erp.accounting_periods` | **kein Fund**: Kanonisch ist `public.finance_accounting_periods`; `domain_erp` ist ein ausdrücklicher Legacy-Fallback im `except`. So gewollt. |
| `domain_shared.sepa_mandates` | **offen, Entscheidung**: Ein Mandatsstamm ist reguliert (Mandatsreferenz, Unterschriftsdatum, Sequenztyp CORE/B2B, Erst-/Folgelastschrift, Widerruf). Das wird entschieden, nicht geraten. Der Lastschriftlauf liest außerdem `domain_shared.open_items` statt `domain_erp.offene_posten` — beides gehört in denselben Schritt. |

## Was unterwegs auftauchte

Zwei Funde, die nicht im Plan standen und schwerer wogen als das Geplante:

**Die Kunden-360 filterte nicht nach Mandant.** Der Mandant kam aus einem
Query-Parameter `?tenant_id=`, den kein Aufrufer setzt — weder die Maske noch
das Frontend. Damit war `:tid IS NULL OR ...` in jeder Abfrage dauerhaft offen
und jeder Aufruf sah Kunden, Aufträge und Kontrakte **aller** Mandanten.
Aufgefallen ist das nur, weil ein Regressionstest den Fremdmandanten prüfte.

**Ein Löschantrag nach Art. 17 DSGVO löschte nichts.** Jede einzelne Anweisung
zeigte auf Tabellen oder Spalten, die es nicht gibt; jeder Fehlschlag landete
im Protokoll — und der Antrag wurde **trotzdem** auf ABGESCHLOSSEN gesetzt.
Eine gesetzliche Pflicht galt als erfüllt, während kein Datensatz angefasst
worden war. Dazu: die Tabelle der Anträge gab es nie (jeder Antrag scheiterte
mit 503), und das Protokoll fiel beim Serialisieren weg, weil der Endpunkt mit
`IDResponse` antwortete. Der Abschluss hängt jetzt am Protokoll.

Beide gehören zur selben Familie wie der Rest: ein gefangener Fehler, der in
der Maske zu einer Null wird. Nur ist die Null hier einmal eine Fremdauskunft
und einmal eine falsche Zusage.

## R5 — Nicht bauen, entscheiden lassen

- **19 ruhende Tabellen**: Code ohne Weg dorthin. Löschen oder bauen ist eine
  Produktentscheidung, keine Aufräumarbeit.
- **`domain_shared.sepa_mandates`** (siehe R4).
- **`domain_pos.pos_transactions`**: die Zieltabelle ist eine Hülle mit vier
  Spalten. Kassenumsätze sind ein Modell, kein Verweis.
- **Das Budgetmodul ist hohl**: `domain_finance.budget_plans` und
  `budget_lines` gibt es nicht, daneben steht ein leeres
  `domain_controlling.controlling_budgets` mit anderem Modell.
- **Kein Personalstamm**: `domain_hr.employees` existiert nicht — ein
  Löschantrag für EMPLOYEE hat kein Ziel.
- **`lager/leitstand`**: Cockpit ohne Inhalt und ohne Seite. Was soll es zeigen?
- **Docflow-Rechnung neben `domain_sales.sales_invoices`**: zwei Welten für
  denselben Beleg.
- **GoBD-Nummernkreis**: `_ersatznummer()` ist eindeutig, aber nicht
  fortlaufend.
- **20 handgeschriebene Listenmasken**: das nächste Programm, kein Fehler.

## Zuständigkeit

Die generischen `/masks/.../tabs/`- und `/mask-rollouts/`-Stubs nimmt Cursor —
sie sind jetzt alles, was von den 27 Zeilenformen übrig ist (17). Alles hier
Aufgeführte lag bei Claude Code und ist abgearbeitet, außer den unter R5
genannten Entscheidungen.

Die Schwelle in `tests/test_mask_field_contracts.py` steht bei 27 (Cursors
Stand); gemessen sind 17. Sie darf beim nächsten Durchgang nachgezogen werden —
die Datei liegt in Cursors Arbeitsbaum, deshalb nicht von hier aus.
