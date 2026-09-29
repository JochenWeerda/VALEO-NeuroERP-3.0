---
title: Kontenrahmen und GoBD
type: reference
audience: [buchhaltung, entwickler, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-29
version: 1.0.0
description: Welche Konten gebucht werden, warum drei davon getrennt wurden, und was davon noch eine Entscheidung braucht.
---

# Kontenrahmen und GoBD

## Ausgangslage

`domain_erp.chart_of_accounts` hatte drei Einträge. Gebucht wurde gegen mehr als
zwanzig Konten. Jede Buchung gegen ein fehlendes Konto scheitert — die
Bestellfreigabe blieb an `Active chart-of-accounts entry not found: 6000`
hängen, und dasselbe hätte Wareneingang, Kasse, Fracht und Lohn getroffen.

Inzwischen stehen 29 Konten (`erp_kontenrahmen_skr03_20260927`,
`erp_gutscheinkonto_20260928`). Die Namen sind nicht erfunden, sondern aus dem
Haus eingesammelt:

- `app/services/pos_accounting_service.ACCOUNT_DEFINITIONS` — die einzige
  bereits strukturierte Kontentabelle.
- `app/finance/router.py` — das SKR03-Regelwerk für Agrar und Handel.
- Die Buchungsdienste, wo der Zweck als Kommentar am Konto steht.

Jeder Eintrag trägt seine Herkunft in der Beschreibung und den Vermerk, dass
die Buchhaltung ihn bestätigen muss.

## Drei Konten, die zwei Dinge trugen — aufgelöst

Die GoBD verlangen Nachvollziehbarkeit und Klarheit (Rz. 30 ff.): Ein
sachverständiger Dritter muss die Geschäftsvorfälle in angemessener Zeit
nachvollziehen können. Bei einem Konto, das zwei Dinge trägt, kann er das
nicht — und keiner der beiden Salden stimmt.

| Konto | trug zusätzlich | jetzt | Grund |
|---|---|---|---|
| **1200** Bank | Forderungen (`sales_posting_service`) | Forderungen → **1400** | Richtigkeit: Eine Forderung auf dem Bankkonto behauptet Geld, das noch nicht da ist |
| **6000** Löhne und Gehälter | Wareneinkauf (`procurement_service`) | Wareneinkauf → **5100** | Klarheit: Personal- und Materialaufwand vermischt machen die GuV unbrauchbar |
| **1600** Verbindlichkeiten aus L+L | Gutscheine (`pos_accounting_service`) | Gutscheine → **1700** | Klarheit: Ein Gutschein ist eine Leistungsverpflichtung gegenüber dem Kunden, keine Lieferantenschuld |

Bei 5100 wurde nichts erfunden: Das ist das Konto, das `finance/router.py`
ohnehin für die Eingangsrechnung vorsieht (ER → 5100 / 1600). Bei 1700 ist die
Nummer eine Verabredung mit der Buchhaltung — die Trennung ist es nicht.

## Was ausdrücklich **nicht** geschehen ist

Die GoBD fordern Unveränderbarkeit (Rz. 107 ff.). Auf 6000 stehen 94,50 und auf
1200 stehen 20,00 aus früheren Läufen. **Diese Sätze bleiben, wo sie sind.**

Eine Umbuchung ist ein Buchungsvorgang mit eigenem Beleg und Gegenbuchung, kein
Datenbankupdate. Ob die Altbestände korrigiert werden, entscheidet die
Buchhaltung; technisch ist dafür nichts vorbereitet und soll es auch nicht
sein.

`tests/test_gobd_kontentrennung.py` hält beides fest. Der
Unveränderbarkeits-Test unterscheidet dabei bewusst:

- Eine Migration, die eine **neue** Spalte aus dem vorhandenen Wert füllt
  (`WHERE ... IS NULL`), ändert am Geschäftsvorfall nichts und bleibt erlaubt.
  Genau das tut `add_missing_domain_erp_finance_tables_20260304`, als sie
  `debit_amount` aus `debit` und `period` aus `entry_date` ableitet.
- Ein `UPDATE` ohne diese Bedingung oder ein `DELETE` schreibt Gebuchtes um und
  ist ein Verstoß.

## Offen — Entscheidungen, keine Aufgaben

**Der Kontenlookup filtert nicht nach Mandant.**
`FinanceTransactionService._resolve_account_id` sucht die Kontonummer ohne
Mandantenbezug. Für einen gemeinsamen Rahmen ist das vertretbar; ein Konto, das
ein Mandant selbst anlegt, kann damit aber in der Buchung eines anderen landen.
Die Leseseite (`/api/v1/finance/chart-of-accounts`) zeigt seit dem 29.09. den
eigenen **und** den gemeinsamen Rahmen, damit sichtbar ist, was gilt.

**Die Nummer 1700.** SKR03-Bereich der sonstigen Verbindlichkeiten. Wenn die
Buchhaltung eine andere will, ist es eine Zeile in
`pos_accounting_service.ACCOUNT_DEFINITIONS` plus eine Migration — die Trennung
selbst bleibt.

**Die Altbestände auf 6000 und 1200** (siehe oben).

## Für die nächste Migration

Die Kontensaat lief lokal und brach in CI: `chart_of_accounts.tenant_id` zeigt
per Fremdschlüssel auf `tenants`, und den Mandanten `system` gibt es nur in
einer gewachsenen Datenbank, nicht in einer frischen. `alembic upgrade head`
bricht dann an dieser Stelle ab — und damit kommt auch nichts danach mehr
durch.

**Eine Migration gegen die eigene gewachsene Datenbank zu prüfen sagt nichts
darüber, ob sie auf einer leeren läuft.** Der Weg dafür ist kurz:

```bash
createdb valeo_probe
DATABASE_URL="postgresql://…/valeo_probe" python -m alembic upgrade head
dropdb valeo_probe
```
