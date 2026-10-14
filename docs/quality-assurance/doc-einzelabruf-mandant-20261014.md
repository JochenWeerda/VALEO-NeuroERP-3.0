# DOC-EINZELABRUF-MANDANT: Einzelabrufe des Dokumentspeichers nur im eigenen Mandanten

Stand: 2026-10-14 · Slice `DOC-EINZELABRUF-MANDANT-20261014` · Folge aus `DOC-ROUTER-MANDANT-20261014`

## Befund

Die Belegnummer ist im Dokumentspeicher systemweit eindeutig. Wer per Nummer liest, ohne den Mandanten des Belegs
zu pruefen, trifft auch den Beleg eines anderen Mandanten. Bis 14.10.2026:

| Stelle | Wirkung |
|---|---|
| E-Rechnung (`/sales/invoices/{nr}/einvoice/xrechnung`, `/zugferd`, GET) | erzeugte aus einer **fremden Ausgangsrechnung** XRechnung/ZUGFeRD mit den eigenen Absenderdaten und schrieb sie ins eigene GoBD-Archiv |
| Gutschrift und Retoure (`sales_credit_notes`) | setzten die per `invoice_reference` angegebene Rechnung auf GUTGESCHRIEBEN — auch eine fremde |
| Verrechnung Lieferantengutschrift/-belastung (`/einkauf/credit-memos/{id}/settle`, `/debit-memos/…`) | pruefte die Rechnungen ohne Mandant, aenderte ihren offenen Betrag und minderte die offenen Posten **im Mandanten der Rechnung** |
| Anlage Gutschrift/Belastung | las Lieferantenname und Rechnungsnummer mandantenlos |
| Kopfdaten und Positionen der Eingangsrechnungsmaske (`MaskRolloutSummaryService`, `finance/ap-invoice`) | zeigten fremde Eingangsrechnungen |
| Zahlungseingang (`finance_clearing`), Skonto-Auszifferung, Storno Ausgangsrechnung | setzten einen fremden Beleg gleicher Nummer auf BEZAHLT bzw. STORNIERT |
| Zahlungslauf | setzte eine mandantenlose Eingangsrechnung gleicher Nummer auf BEZAHLT |
| AP-Freigabe (Abschluss) | aktualisierte den Rechnungsstatus ohne Mandantenpruefung |
| AP-Buchung (`ap_invoice_kernel_posting`) | behandelte eine mandantenlose Rechnung als Rechnung des Mandanten `system` |
| Korrekturentwurf Agrarabrechnung | las den Lieferantennamen mandantenlos |

## Was jetzt gilt

- Neuer Helfer `eigener_beleg(doc_type, nummer, tenant_id, repo)` in `app/documents/router_helpers.py`: der Beleg
  nur, wenn er dem Mandanten gehoert; fremd, mandantenlos oder ohne Mandant in der Anfrage → `None`.
- Alle oben genannten Stellen lesen ueber ihn. Lesewege antworten 404; Statusnachtraege lassen den fremden Beleg
  unberuehrt; die Memo-Verrechnung antwortet 404 fuer eine fremde Rechnung und mindert offene Posten nur im
  eigenen Mandanten.
- Bereits korrekt und unveraendert: `ap_invoices`, `finance_invoices` (Lesen/Anlegen), `credit_debit_memos`
  (`_memo_des_mandanten`), `finance_freigabe`, `mcp_execution_service`, AP-Freigabe-Anforderung/-Status.

## Nachweis

- `tests/test_einzelabruf_mandant.py` (7): Helfer (eigen/fremd/mandantenlos/ohne Mandant), E-Rechnung gegen die
  echte Datenbank (eigen 200, fremd und mandantenlos 404), Eingangsrechnungsmaske (eigen, fremd 404, mandantenlos
  404), Gutschrift und Zahlungseingang lassen fremde und mandantenlose Rechnungen unberuehrt.
- Angepasst: Mock-Tests patchen den Speicher jetzt an der Grenze (`router_helpers.get_from_store`) und tragen den
  Mandanten im Testbeleg; `test_sales_invoice_einvoice_endpoints` legt die Rechnung mit Mandant an (von dort
  stammten die sechs mandantenlosen `INV-Q-…` der gewachsenen Datenbank). `test_sales_cn_inv_001` scheiterte schon
  vorher am Antwortmodell (MagicMock als `correction_type`) und setzt das Feld jetzt.
- Regression (frische Datenbank, 48 Dateien): gruen bis auf vorbestehend rot —
  `test_agrar_settlements_api.py` (5, Dev-Token → 401) und
  `test_process_kernel_wave1_contracts.py::test_payment_run_approve_…`.
- Keine Migration, keine Aenderung an Pfaden oder Schemas (OpenAPI unveraendert).

## Offen

- Die E-Rechnungswege (`/sales/invoices/{nr}/einvoice/*`) haben keine Rollenpruefung — jede angemeldete Person
  des Mandanten kann E-Rechnungen erzeugen und archivieren.
- Bestandsbelege ohne Mandant (gewachsene DB: 6 `sales_invoice`, 1 `ap_invoice`) sind jetzt fuer niemanden
  erreichbar; Zuordnung oder Loeschung ist eine fachliche Entscheidung.
