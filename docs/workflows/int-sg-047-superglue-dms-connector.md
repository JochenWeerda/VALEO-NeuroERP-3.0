# INT-SG-047 - Superglue DMS Connector

## Ziel

Den bisherigen Pilot-Dokumentpfad auf tenant-gebundene echte Connector-Bindings ziehen.

## Umgesetzt

- `document_adapter.py` loest Tool-ID und Runtime-Credentials pro Tenant ueber den Connector-Registry-Pfad auf.
- DMS-Suchen laufen jetzt ueber den tenant-spezifischen Superglue-Tool-Run statt ueber eine harte Pilot-ID.
- Dokument-Metadaten werden weiterhin ueber den stabilen VALEO-Port `DocumentPort` bereitgestellt.

## Verifikation

- `pytest tests/test_superglue_document_adapter.py -q --no-cov`

