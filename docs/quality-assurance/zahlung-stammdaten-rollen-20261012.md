# Zahlungsverkehr, Schnittstellen, Finanzstammdaten: Rollen vor der Datenbank

Stand: 2026-10-12 · Slice `ZAHLUNG-STAMMDATEN-ROLLEN-20261012` · dritter Schnitt nach
[Hauptbuch](hauptbuch-rollen-20261011.md) und [Abschluss](abschluss-rollen-20261012.md)

## Befund

137 Wege in 22 Dateien prüften keine Rolle. Wer angemeldet war, konnte eine Lastschriftdatei ausgeben,
einen Rechnungsstapel freigeben und ausführen, einen Lohnimport auslösen, Schnittstellen umstellen
und Steuerschlüssel oder Zahlungsbedingungen ändern.

## Entscheidung

### Zahlungsverkehr und Schnittstellen (zwölf Dateien)

`auto_matching`, `direct_debits`, `op_skonto_auszifferung`, `fibu_zahlungsmeldungen`,
`finance_clearing`, `finance_op`, `finance_followup`, `billing_batch`, `fibu_connectors`,
`lohn_connector`, `quadriga_connector`, `asset_ledger_connector`

| Zugang | Wege |
|---|---|
| Lesen (`finance_read`) | alle `GET` |
| Bearbeiten (`finance_write`) | Abgleichsregel anlegen und ändern, abgleichen, Zuordnung übernehmen; Lastschriftlauf anlegen; Skonto berechnen, ausziffern, Auszifferung stornieren; Zahlungsmeldung anlegen, verarbeiten, abweisen; Zahlungseingang erfassen; Mahn- und Kassenexport; Rechnungsstapel anlegen, prüfen, Zeile wiederholen; Importlauf anlegen, prüfen, abbrechen |
| Leitung (`finance_admin`) | jedes Löschen; **Lastschrift ausgeben** (beide Wege); **Rechnungsstapel freigeben und ausführen**; **Importlauf buchen und zurücknehmen**; Schnittstellenprofil anlegen und ändern; Lohnimport anlegen und auslösen; Quadriga- und Anlagenbuch-Konfiguration und -Abgleich |

Bei der Leitung liegt, was Geld einzieht, in Masse bucht, nach außen geht oder eine Schnittstelle
umstellt.

### Stammdaten (zehn Dateien)

`finance_stammdaten`, `fibu_stammdaten`, `vat_codes`, `tax_keys`, `exchange_rates`,
`zahlungsbedingungen`, `forderungsgruppen`, `erloeskennziffern`, `debtors`, `creditors`

| Zugang | Wege |
|---|---|
| **Lesen bleibt offen** für jeden Angemeldeten | 31 `GET` |
| Bearbeiten (`finance_write`) | anlegen, ändern |
| Leitung (`finance_admin`) | löschen |

**Warum das Lesen offen bleibt:** Zahlungsbedingungen lesen Kundenstamm, Lieferantenstamm, Angebot,
Bestellung und Rechnungseingang; Steuerschlüssel und Wechselkurse stehen in Belegen. Eine
Finanz-Leserolle hätte diese Masken still geleert. Es ändert sich also nichts am Lesen – das ist kein
neuer Schutz, sondern der bewusste Verzicht darauf. Auch Debitoren- und Kreditorenlisten bleiben damit
für jeden Angemeldeten lesbar.

## Bewusst nicht Teil

- **`bank_statement_import.py`, `payment_matching.py`:** Erst mit umgestellt, dann zurückgenommen –
  93 Fälle in sechs Testdateien eines anderen Agenten bauen dort eigene Mini-Anwendungen ohne Nutzer.
  Die Wege gehören in dessen Bank-Slice.
- **`finance_invoices.py`, `document_control.py`:** Dort schreiben auch Verkauf (Gutschrift),
  CRM und die Belegkontrolle. Die Rollenzuordnung ist eine eigene Entscheidung.

## Geänderte Dateien

- nur Dekoratoren und ein Import in den 22 Dateien
- `tests/test_zahlung_stammdaten_rollen_vertrag.py` (neu)
- Nutzer mit Finanzrolle in `test_fibu_connectors_api.py`, `test_finance_exchange_rates_api.py`,
  `test_finance_followup_api.py`, `test_process_kernel_wave31_dq_connector_imports.py`

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_zahlung_stammdaten_rollen_vertrag.py` – 13 Rollen × 137 Wege, ohne Anmeldung an den 106 geschützten Wegen, Vollständigkeit je Datei, „offen nur beim Lesen von Stammdaten" | 1910 bestanden |
| 53 Testdateien, die diese Wege berühren (`valeo_probe`) | 2683 bestanden, 2 übersprungen, 3 rot |
| Ruff auf den 22 Dateien | keine neue Meldung gegenüber dem Stand davor |

Die drei roten Tests liegen in `tests/test_config_service.py` (`/api/v1/config/…`, kein geänderter
Weg): Beim zweiten Lauf gegen denselben Prüfstand stoßen sie auf ihre eigenen Zeilen aus dem ersten
(`ix_reporting_units_tenant_key`, `ix_schedules_tenant_key`). Im ersten Lauf dieses Slices waren sie
grün.

Keine Sichtprüfung: Das Entwicklungs-Backend lehnt den Dev-Token derzeit ab (nicht committete Arbeit
eines anderen Agenten im geteilten Baum, siehe [Kontosperre](konto-sperre-20261012.md)).

## Betrieb

Buchhaltung `FINANCE_BEARBEITEN`, Finanzleitung `FINANCE_ADMIN`, Prüfer `FINANCE_LESEN`. Wer bisher
ohne Finanzleitung eine Lastschrift ausgegeben, einen Rechnungsstapel ausgeführt oder einen Lohnimport
ausgelöst hat, bekommt nach dem Einspielen 403.

## Offen

- **19 schreibende Finanzwege ohne Rolle** (321 von 413 Finanzwegen prüfen jetzt eine) – im Kern die vier oben ausgenommenen Dateien, dazu Wege,
  die nur wegen ihres Schlagworts mitgezählt werden (Masken-Brücken, Process Mining, IBAN-Prüfung).
- **Debitoren und Kreditoren lesen** kann jeder Angemeldete. Ob das so bleiben soll, ist eine
  fachliche Entscheidung (Datenschutz, Kreditlimits).
- **Masken melden 403 nicht als fehlende Rolle** – außer Mahnlauf und Kontenplan.
