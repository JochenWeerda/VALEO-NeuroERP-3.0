# PKP-06 Finance Cash Snapshot Read Contract

## Ziel
- `finance/kasse` nicht als zweiten Abschluss- oder Buchungspfad bauen
- lesende Finanzsicht auf produktive POS-Kassenabschluesse vorbereiten

## Fachliche Abgrenzung
- `POS/Kasse`
  - Tagesabschluss
  - Kassenzaehlung
  - Zahlartenabgleich
  - Differenzermittlung
  - operative Buchung/Abschlussausloesung
- `Finance/Kasse`
  - lesende Abstimmung
  - Snapshot fuer Reporting
  - Journal- und Importkontrolle
  - kein eigener CRUD fuer Abschluss oder Bewegungen

## Empfohlener Read-Endpoint
- `GET /api/v1/finance/cash-closings`
- optional spaeter `GET /api/v1/finance/cash-closings/{closing_id}`

## Snapshot-Felder Liste
- `id`
- `closing_date`
- `location_id`
- `location_name`
- `cash_register_id`
- `cash_register_name`
- `operator_name`
- `source`
  - `POS`
  - `IMPORT`
- `workflow_status`
  - `draft`
  - `booked`
  - `posted`
  - `reconciled`
  - `exception`
- `currency`
- `totals`
  - `cash_expected`
  - `cash_counted`
  - `cash_difference`
  - `card_expected`
  - `card_counted`
  - `card_difference`
  - `paypal_expected`
  - `paypal_counted`
  - `paypal_difference`
  - `b2b_expected`
  - `gross_total`
- `posting`
  - `journal_entry_id`
  - `journal_entry_number`
  - `posted_at`
  - `posting_status`
- `import_context`
  - `import_batch_id`
  - `import_source_label`
  - `imported_at`
- `reference_context`
  - `tse_transaction_count`
  - `source_document_refs`
- `exception_flags`
  - `has_difference`
  - `has_import_gap`
  - `has_missing_posting`

## Beispielantwort
```json
{
  "items": [
    {
      "id": "cash-close-2026-03-11-001",
      "closing_date": "2026-03-11",
      "location_id": "store-1",
      "location_name": "Hauptstandort",
      "cash_register_id": "pos-1",
      "cash_register_name": "POS 1",
      "operator_name": "M. Muster",
      "source": "POS",
      "workflow_status": "posted",
      "currency": "EUR",
      "totals": {
        "cash_expected": 2450.0,
        "cash_counted": 2450.0,
        "cash_difference": 0.0,
        "card_expected": 3200.0,
        "card_counted": 3200.0,
        "card_difference": 0.0,
        "paypal_expected": 400.0,
        "paypal_counted": 400.0,
        "paypal_difference": 0.0,
        "b2b_expected": 150.0,
        "gross_total": 6200.0
      },
      "posting": {
        "journal_entry_id": "je-1",
        "journal_entry_number": "KA-2026-03-11",
        "posted_at": "2026-03-11T18:15:00Z",
        "posting_status": "posted"
      },
      "import_context": {
        "import_batch_id": null,
        "import_source_label": null,
        "imported_at": null
      },
      "reference_context": {
        "tse_transaction_count": 42,
        "source_document_refs": [
          "tse-journal:2026-03-11",
          "abschluss_checklisten:cash-close-2026-03-11-001"
        ]
      },
      "exception_flags": {
        "has_difference": false,
        "has_import_gap": false,
        "has_missing_posting": false
      }
    }
  ]
}
```

## Ableitungsquellen im aktuellen Bestand
- `app/api/v1/endpoints/compat.py:/pos/tagesabschluss`
- `abschluss_checklisten`
- `domain_erp.journal_entries`
- `domain_erp.cash_movements`
- `app/api/v1/endpoints/admin_pos.py:/pos/uebernahme-kasse`

## Nicht Ziel dieses Contracts
- kein `POST /api/v1/finance/cash`
- kein eigenes `approve` fuer Kassenabschluss in Finance
- kein zweiter Kassensturz neben POS

## Naechster Implementierungsschritt
- Backend-Read-Model fuer `finance/cash-closings` aufsetzen
- `packages/frontend-web/src/pages/finance/kasse.tsx` spaeter von Bridge auf Snapshot-Liste umstellen
