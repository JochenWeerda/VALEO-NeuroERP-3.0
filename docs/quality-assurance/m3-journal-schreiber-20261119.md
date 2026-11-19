# M3: Journal nur über den Buchungsdienst – erster Schnitt (19.11.2026)

Meilenstein M3 (vollständige Fibu), Integrität. `FinanceTransactionService` ist der kanonische Schreibweg ins
Journal: Periodensperre, buchbare Konten, exakte Beträge, Belegbezug, lückenlose Sequenz und Hash-Kette.

## Bestandsaufnahme

Neun Dateien schrieben roh per SQL in `domain_erp.journal_entries` / `journal_entry_lines`. Die neue Ratsche
`tests/test_journal_schreiber_ratsche.py` hält die Liste fest; sie darf nur schrumpfen. Stand nach diesem Schnitt: 6.

## Befunde und Änderungen

| Schreiber | Befund | Änderung |
|---|---|---|
| `accruals_provisions.py` `POST /{id}/post` | Kopf mit Status `posted`, **ohne Buchungszeile**, ohne Periodenprüfung, Sequenz und Hash – bewegte kein Konto | bucht über den Dienst (Soll `account_number`, Haben `counterpart_account`, Stichtag Periodenende, Bezug `ABGR-<id>`), mit der Kontrollprüfung der manuellen Hauptbuchbuchung (FIN-CONTROL-001) |
| `finance_closing_service.py` `run` | INSERT in die Spalten `closing_type`/`created_by`, die es weder frisch noch gewachsen gibt; `except` verschluckte den Fehler, PostgreSQL hatte die Transaktion aber schon abgebrochen → Sperre und Commit scheiterten, `/closing/run` gelang nie | kein Scheinkopf; der Monatsabschluss ist die Sperre. Saldenvortrag/Jahresabschlussbuchung bleiben eigene Fachaktionen |
| `storage_fees.py` `POST /run` | Forderung an Erlös direkt ins Journal: keine Umsatzsteuer, kein offener Posten, legte Konten 1200/8400 selbst an | Direktbuchung entfernt; `post_to_ledger=true` → 422. Der Lauf berechnet und protokolliert; gebucht wird über die Ausgangsrechnung an den Einlagerer |

## Prüfung

- `tests/test_abgrenzung_bucht_ueber_dienst.py` gegen frisches Schema (Prüfstand, zurückgerollt): Soll/Haben je
  Konto, Stichtag, Sequenz und Hash; keine Doppelbuchung; gesperrte Periode → 422 ohne Journal, Abgrenzung bleibt
  Entwurf; unbekanntes Konto → 422; Periode ohne Monat → 422.
- `tests/test_lagergeld_bucht_nicht_direkt.py`, `tests/test_finance_closing_service.py` (kein Journalkopf).
- Spaltenbestand `domain_erp.journal_entries` frisch (`valeo_s5_test`) und gewachsen (`valeo_neuro_erp`) geprüft:
  `closing_type`, `created_by` fehlen in beiden.

## Offen

Offene Posten (Zahlungsausgleich/Storno), Buchungsvorlagen, Massenimport, Konnektoren (Lohn/Anlagen),
Inventurbuchung, POS-Tagesabschluss in `compat.py`; Lagergeld-Abrechnung als Ausgangsrechnung.
