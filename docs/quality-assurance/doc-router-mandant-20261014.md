# DOC-ROUTER-MANDANT: Der generische Belegrouter arbeitet nur im eigenen Mandanten

Stand: 2026-10-14 · Slice `DOC-ROUTER-MANDANT-20261014` · Folge aus `DOC-STORE-MANDANT-20261014`

## Befund

`/api/mcp/documents/*` (`app/documents/router.py`, eingehängt in `main.py` und unter `/api/v1/api/mcp/documents`)
verlangte eine Anmeldung, kannte aber keinen Mandanten und keine Rolle:

| Weg | Zustand bis 14.10.2026 |
|---|---|
| `GET /{doc_type}/{nr}` | lieferte **jede Belegart jedes Mandanten** per Nummer — auch Lieferantengutschriften (`credit_memo`) und Rechnungen, an den seit 13.10. abgesicherten Finanzwegen vorbei |
| `PUT /{doc_type}/{nr}` | änderte fremde Belege; der Mandant im Beleg ließ sich per Anfrage umsetzen |
| `DELETE /{doc_type}/{nr}` | löschte fremde Belege |
| `POST /customer_inquiry`, `/sales_offer`, `/sales_order`, `/sales_delivery`, `/sales_invoice`, `/payment_received`, `/purchase_request`, `/purchase_offer`, `/purchase_order` | legten Belege **ohne Mandant** an und **überschrieben** unter einer vergebenen Nummer den Beleg eines anderen Mandanten (Nummer systemweit eindeutig) |
| `GET /{doc_type}` | las nur den Prozessspeicher — bei konfigurierter Datenbank also nichts (Portal-Lieferscheinliste, Bestellauswahl im Rechnungseingang waren leer) |
| `DELETE /{doc_type}?numbers=` | löschte nur im Prozessspeicher, ohne Mandant |
| `GET /analytics/sales-delivery-sustainability/export.csv` und `/export.pdf` (Portal) | rechneten N/P₂O₅/CO₂e über die Lieferscheine **aller Mandanten** und gaben sie als Datei aus |
| `delete_from_store` | fiel bei einem Datenbankfehler still auf den Prozessspeicher zurück und meldete dann „nicht gefunden“ |

## Was jetzt gilt

- Lesen, Ändern, Löschen und Sammellöschen treffen nur Belege des Mandanten der Anmeldung; ein fremder oder
  mandantenloser Beleg ist „nicht vorhanden“ (404).
- Anlegen setzt den Mandanten. Gehört die Nummer einem anderen oder keinem Mandanten: 409, nichts wird geschrieben.
- Ändern kann den Mandanten nicht umsetzen.
- Die Liste kommt aus der Datenbank, je Mandant (Antwortform unverändert: `ok`, `data`, `total`, `skip`, `limit`).
- Die Nachhaltigkeitsauswertung (JSON, CSV, PDF) rechnet nur über eigene Lieferscheine.
- Löschen ohne stillen Rückfall.

## Nachweis

- `tests/test_belegrouter_mandant.py` (16, frische Datenbank; vor der Änderung 15 rot): Lesen je Belegart
  (Bestellung, Gutschrift, Rechnung) — eigen, fremd, ohne Mandant; Liste; fremd nicht änderbar (Beleg danach
  unverändert); Mandant nicht umsetzbar; fremd nicht löschbar, eigen löschbar; Sammellöschung; Anlage trägt den
  Mandanten (drei Belegarten); Anlage unter fremder Nummer 409 und fremder Beleg unverändert (drei Belegarten); CSV-Export zählt einen von drei
  Lieferscheinen (eigen/fremd/ohne Mandant).
- Regression: alle Testdateien, die Router, Speicherhelfer, Compat-Dienste oder Portal berühren (11 Dateien) — 127 grün, 7 übersprungen,
  1 rot: `test_process_kernel_wave1_contracts.py::test_payment_run_approve_…`, vorbestehend (in DOC-STORE-MANDANT
  auf HEAD gegengeprüft).
- OpenAPI: die fünfzehn Pfade des Routers tragen jetzt die Bearer-Angabe (`security`); die committete Spezifikation
  ist für genau diese Pfade nachgezogen.

## Offen (nicht in diesem Slice)

- **Keine Rollenprüfung:** Jede angemeldete Person des Mandanten kann über diesen Router Rechnungen,
  Gutschriften und Zahlungseingänge anlegen, ändern und löschen. Die Fachwege (`/einkauf/credit-memos`,
  `/finance/invoices`, …) prüfen Rollen; dieser Router umgeht sie. Empfehlung: die generischen Wege
  `PUT`/`DELETE /{doc_type}/…` auf die Belegarten begrenzen, die nur hier geführt werden, oder Rollen je Belegart.
- **Tote Wege:** `GET /customers/search`, `/articles/search` und sechs `GET /analytics/…`-Wege werden von
  `GET /{doc_type}/{doc_number}` verdeckt und sind nie erreichbar (das Frontend nutzt sie nicht). Die
  Auswertungen lesen nur den Prozessspeicher und mandantenlos — sie freizuschalten, ohne das zu ändern, wäre
  schlechter als der heutige Zustand. Bewusst nicht angefasst.
- **Weitere Einzelabrufe** des Dokumentspeichers außerhalb dieses Routers und der Finanzwege
  (`ap_approval_workflow`, `finance_clearing`, `op_skonto_auszifferung`, `sales_credit_notes`,
  `sales_invoice_einvoice`, `mcp_execution_service`, `agrar_settlement_service`, `payment_runs`,
  `mask_rollout_summary_service`, `ap_invoice_kernel_posting`, `finance_freigabe`) sind nicht geprüft.
