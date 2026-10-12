# Abschluss, Auswertung, Kostenrechnung: Rollen vor der Datenbank

Stand: 2026-10-12 · Slice `ABSCHLUSS-ROLLEN-20261012` · zweiter Schnitt nach
[Hauptbuch: Rollen](hauptbuch-rollen-20261011.md)

## Befund

Keiner der 74 Wege in elf Dateien prüfte eine Rolle. Wer angemeldet war, konnte eine
Umsatzsteuer-Voranmeldung genehmigen und einreichen, einen Abschreibungslauf starten, Anlagen
ausbuchen, Budgets und Abschluss-Checklisten genehmigen und Kostenbuchungen löschen.

## Entscheidung

Dieselbe Regel wie am Hauptbuch, ohne Sonderfall beim Lesen – diese Wege benutzen nur Finanzmasken:

| Zugang | Rollen | Wege |
|---|---|---|
| Lesen (`finance_read`) | `FINANCE_LESEN`, `FINANCE_BEARBEITEN`, `FINANCE_ADMIN`, `admin`, `manager` | alle `GET`: Checklisten, Abgrenzungen, Anlagen, Budgets, Liquidität, Finanzberichte, Nebenbuchabstimmung, UStVA, DATEV-Ausgabe, Kostenstellen, Kostenarten, Kostenbuchungen |
| Bearbeiten (`finance_write`) | `FINANCE_BEARBEITEN`, `FINANCE_ADMIN`, `admin`, `manager` | Checkliste und Vorlage anlegen, Punkt erledigen, prüfen; Abgrenzung anlegen, ändern, buchen; Anlage anlegen und ändern; Budget anlegen, Zeilen pflegen; Liquiditätsszenario; UStVA berechnen und prüfen; Kostenstelle, Kostenart, Kostenbuchung, Umlage anlegen |
| Leitung (`finance_admin`) | `FINANCE_ADMIN`, `admin` | alles Löschen; Checkliste genehmigen; Budget genehmigen; UStVA genehmigen und einreichen; Anlagenabgang; Abschreibungslauf |

**Was der Leitung bleibt:** Genehmigungen (sie sind die zweite Unterschrift), die Einreichung beim
Finanzamt (geht nach außen), der Anlagenabgang und der Abschreibungslauf (Massenbuchung), dazu jedes
Löschen.

## Geänderte Dateien

- nur Dekoratoren und ein Import in `closing_checklists.py`, `accruals_provisions.py`,
  `asset_accounting.py`, `budget_planning.py`, `liquidity_planning.py`, `liquidity.py`,
  `financial_reports.py`, `subsidiary_ledger_reconciliation.py`, `vat_return_export.py`,
  `finance_datev.py`, `kostenrechnung.py`
- `tests/test_abschluss_rollen_vertrag.py` (neu)

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_abschluss_rollen_vertrag.py` – 13 Rollen × 74 Wege, ohne Anmeldung, Vollständigkeit je Datei | 1048 bestanden |
| 28 Testdateien, die diese Wege oder Module berühren (Prüfstand `valeo_probe`) | 2135 bestanden, 1 rot |
| Ruff auf den elf Dateien | keine neue Meldung gegenüber dem Stand davor |

Der eine rote Test ist `test_parallel_installation_endpoints::test_schaeden_and_etiketten_endpoints_work`:
Ein Etikettendrucker aus einem früheren Lauf liegt noch im Prüfstand (`ux_drucker_name`). Er berührt
keinen der geänderten Wege und war schon vor diesem Slice rot.

Keine Sichtprüfung: Der Entwicklungsnutzer trägt alle Rollen.

## Betrieb

Buchhaltung `FINANCE_BEARBEITEN`, Finanzleitung `FINANCE_ADMIN`, Prüfer und Steuerberater
`FINANCE_LESEN`. Wer bisher ohne Finanzrolle eine Voranmeldung eingereicht oder ein Budget genehmigt
hat, bekommt nach dem Einspielen 403.

## Offen

- **229 Finanzwege ohne Rolle** bleiben. Größte Blöcke: `finance_actions` (teils Codex),
  `fibu_connectors`, `finance_stammdaten`, `fibu_stammdaten`, `auto_matching`, `billing_batch`,
  Zahlungsabgleich, Lastschriften, Stammdaten mit Lesern aus anderen Bereichen (Steuerschlüssel,
  Zahlungsbedingungen, Debitoren, Kreditoren).
- **Die Masken sagen bei 403 nicht, dass die Rolle fehlt.** Am Mahnlauf ist das gelöst
  („Für das Mahnwesen fehlt die Finanzrolle."), an Abschluss, UStVA und Kostenrechnung nicht geprüft.
