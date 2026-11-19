# Übergabe an Codex: Umsatzsteuer im POS-Tagesabschluss (19.11.2026)

Meilenstein M3. Absender: Claude Code (M3-JOURNAL-SCHREIBER-20261119, PR #158).

## Befund

`POST /pos/tagesabschluss` (`app/api/v1/endpoints/compat.py`) bucht den Tagesumsatz mit
`build_pos_closing_lines` brutto auf **8400 Umsatzerlöse** – ohne Umsatzsteuerzeile. Die Erlöse sind damit um die
Steuer zu hoch, die Umsatzsteuer fehlt in der UStVA.

`domain_docflow.pos_fiscal_transactions` speichert je Vorgang nur `gross_total` und `payment_breakdown`, keine
Beträge je Steuersatz. Der Abschluss kann die Steuer deshalb nicht korrekt trennen; ein angenommener Satz wäre
erfunden (Steuerlogik nur aus `domain_erp.tax_keys`).

## Bitte

1. Beim Kassiervorgang die Beträge je Steuersatz mit dem Fiskalvorgang speichern (die TSE meldet sie ohnehin als
   `amounts_per_vat_rate`, `DSFINVK_UST_SAETZE`).
2. `daily_summary` um die Summen je Satz erweitern.
3. Im Abschluss je Satz Erlös netto und Umsatzsteuer über die Steuerschlüssel buchen (Konten aus `tax_keys`).

Die Buchung selbst läuft seit #158 über `FinanceTransactionService`; Konten und Periode werden vor dem
fiskalischen Abschluss geprüft. Kasse untersucht laut FIN-CONTROL-001 zuerst Codex – deshalb keine Änderung von mir.
