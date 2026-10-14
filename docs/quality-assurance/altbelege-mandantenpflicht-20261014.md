# ALTBELEG-MANDANTENPFLICHT-20261014: mandantenlose Altbelege entfernt, neue ausgeschlossen

Stand: 2026-10-14 · Slice `ALTBELEG-QUARANTAENE-20261014` (Claim) · TENANT-DOC-001 Punkt 2, PORTAL-CONTEXT-001

## Inventar (gewachsene Datenbank `valeo_neuro_erp`, vor jeder Aenderung)

`documents` enthielt 11 Belege, davon 7 ohne `tenantId`/`tenant_id`:

| Nummer | Art | Kunde/Lieferant | angelegt |
| --- | --- | --- | --- |
| INV-Q-05CCCD2F, INV-Q-2AA3BA6A, INV-Q-578FE3BA | sales_invoice | C-QUALITY-1 | 14.09.2026 12:46 |
| INV-Q-0A1EA945, INV-Q-159E381A, INV-Q-CC492256 | sales_invoice | C-QUALITY-1 | 14.09.2026 12:49 |
| AP-TEST-001 | ap_invoice (ENTWURF) | supplier-1 | 14.09.2026 12:46 |

- **Herkunft:** `INV-Q-…` aus `tests/test_sales_invoice_einvoice_endpoints.py::_seed_invoice` (bis Commit `109146416`
  am 14.10.2026 ohne `tenantId`); `AP-TEST-001` aus `tests/test_ap_invoices_api.py::test_create_ap_invoice_minimal`
  (feste Nummer bis Commit `42f8fe6c3` am 07.10.2026). Testlaeufe gegen die Entwicklungsdatenbank.
- **Bezuege:** Volltextsuche nach allen sieben Nummern und IDs in allen 780 uebrigen Tabellen (alle lesbar) — kein
  Treffer: keine Positionen ausserhalb des Belegs, keine Buchung, kein offener Posten, keine Zahlung, kein Anhang,
  keine Historie, kein Archiveintrag.
- **Klassifikation:** Testdaten ohne Relevanz — Code-Befund und Aussage des Nutzers vom 14.10.2026 („die Altbelege
  sind saemtlich erfundene Testdaten ohne Relevanz").

## Sicherung

Vor jeder Aenderung (`pg_dump -Fc` im Container `valeo-neuro-erp-postgres`), abgelegt ausserhalb des Repos unter
`C:/Users/Jochen/valeo-backups/`:

- `valeo_neuro_erp-full-20261014-altbelege.dump` — sha256 `5eaa005b9f7c83d6ef44922d070d8c0a4b2c10cf1a61177688416057f810e958`
- `documents-20261014-altbelege.dump` — sha256 `67aaba75a1f2132466bca9ff6de2bc4ee64f2984a97746e1d2ccc8a9b6de3ad7`

Wiederherstellbarkeit geprueft: Vollsicherung in eine Wegwerfdatenbank zurueckgespielt — 783 Tabellen, Pruefsumme
ueber `documents` identisch (`d4d0e102…`); Wegwerfdatenbank danach entfernt.

## Bereinigung

Der Nutzer hat am 14.10.2026 das Loeschen ausdruecklich freigegeben („kann alles weg (Altbelege loeschen)") — das
ersetzt fuer diese sieben Testbelege die zuvor beschlossene Quarantaene. Ausgefuehrt in einer Transaktion: Abgleich
der sieben Datensaetze mit der zurueckgespielten Sicherung, dann `DELETE` nur per ID **und** nur, wenn weiterhin ohne
Mandant **und** Nummer `INV-Q-%`/`AP-TEST-001`; genau 7 Zeilen. Danach: 4 Belege, keiner ohne Mandant.

Die zunaechst gebaute Quarantaene (Register, Schutztrigger, Skript) ist damit gegenstandslos und **nicht** im Repo;
sie lief nur auf dem Pruefstand, der danach frisch aufgebaut wurde.

## Ausschluss neuer Belege ohne Mandant

`app/documents/repository.py`: `DocumentRepository.save_document` — der einzige Schreibweg der Anwendung in
`documents` — weist einen Beleg ohne nicht-leeres `tenantId` mit `BelegOhneMandant` (ValueError) ab, auch beim
Aendern (ein Aendern kann den Mandanten nicht entfernen). Alle Schreibaufrufe der Anwendung (80 Stellen) setzen
`tenantId` oder schreiben einen ueber `eigener_beleg` geladenen Beleg zurueck. Bewusst **keine** Datenbank-CHECK:
mehrere Tests legen per SQL mandantenlose Altbelege an, um deren Unsichtbarkeit zu pruefen.

## Nachweis

- `tests/test_beleg_mandantenpflicht.py` (frische Datenbank): fuenf Varianten ohne Mandant abgewiesen, nichts
  geschrieben; Aendern ohne Mandant abgewiesen, Bestand unveraendert. 6 gruen.
- Regression: alle 74 Testdateien rund um den Belegspeicher — 1232 gruen, 2 uebersprungen, 60 rot; davon 58 × 401
  (alter Dev-Token, vorbestehend: `test_coverage_ratchet_erp_core_001`, `test_gap_fixes_batch3/6`,
  `test_sales_delivery_notes_api`) und 2 auch ohne diese Aenderung rot
  (`test_process_kernel_wave1_contracts::test_payment_run_approve…`, `test_meridian_beleg_systemweit::test_lagerbewegung…`).
  Kein Fehler durch `BelegOhneMandant`.

## Offen

- `documents.doc_number` ist systemweit eindeutig (`documents_doc_number_key`), nicht je Mandant.
- Testlaeufe gegen die Entwicklungsdatenbank haben die Altbelege erzeugt — Tests mit Schreibzugriff nur gegen den
  Pruefstand (`valeo_probe`).
