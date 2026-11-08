# Journal: vollständige Kontosperren-Zusammenfassung

Stand: 2026-10-12. Slice `JOURNAL-BLOCK-SUMMARY-20261012`.

Die manuelle Buchung materialisierte eine Liste gesperrter Kontonummern nur,
um daraus einen Meldungstext zu bilden. PostgreSQL liefert diesen Text jetzt
mit `string_agg` in einer einzigen Ergebniszeile. Alle ausgewählten gesperrten
Konten bleiben enthalten und nach Kontonummer sortiert. Ein `LIMIT`, das
Sperren abschneiden könnte, wird nicht verwendet. Die Datenbanktrigger bleiben
die verbindliche Buchungssperre; Rollen und Buchungstransaktionen sind unverändert.

Drei echte PostgreSQL-Verträge über den Endpoint bestehen: mehrere Sperrkonten
mit wiederholter Konto-ID, Mischung aus offenem und gesperrtem Konto und nur
offene Konten. Bei offenen Konten wird die nachgelagerte Repository-Grenze
erreicht; eine tatsächliche Buchung wird in diesem begrenzten Vertrag nicht
behauptet. Ergebnis: drei bestanden, eine Warnung, 22,86 Sekunden.

Vorheriger Status des gemeinsamen Prüfstands: `vat_codes_entfernt_20261012`.
Eigene Testkonten und Mandanten werden durch die äußere Transaktion verworfen.
Keine neue Datenbank, kein Container, kein Reset und keine Migration.

Die unveränderte Pagination-Ratsche besteht: 280 Abfragen in 253 Funktionen.
Weitere Dateigrößen-, Katalog-, Audit- und GitHub-Gesamtbefunde bleiben offen.
