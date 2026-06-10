# POS-Fiskalisierung Operations UAT

Stand: 2026-06-10

## Abgedeckter Vertrag

- Typed Route `/admin-suite/pos-fiscalization` oeffnet ohne 404.
- Bestehende tenantbezogene Konfiguration wird geladen.
- TSE-Provider kann zwischen fiskaly, Swissbit Cloud, Swissbit Gateway und
  expliziter Simulation gewaehlt werden.
- Swissbit als TSE und fiskaly als DSFinV-K-Provider bleiben getrennt.
- Der Browser sendet keine Provider-Secrets.
- SUBMIT DE, RECEIPT und SAFE zeigen fehlende Produktvertraege als Blocker.
- Ein Tagesabschluss mit unvollstaendiger Fiskaltransaktion kann nicht in die
  Fibu gebucht werden.

## Automatisierter Nachweis

```text
npx playwright test playwright-tests/specs/pos/fiscalization-admin.spec.ts --project=full --workers=1
2 passed
```

Der Lauf erzeugt zuvor einen Produktions-Build und prueft die echte
TanStack-Route. Backend-Vertraege:

```text
python -m pytest -o "addopts=" tests/test_pos_fiscalization_providers.py tests/test_pos_fiscalization_security_contract.py -q
11 passed
```

## Externer-Pruefer-Simulation: Beleg und FiBu

Die automatisierte Simulation verwendet den expliziten virtuellen
`VirtualPdfPrinter` (PDF-Erzeugung via ReportLab, atomarer Druckauftrag auf
ein `.pdf`-Ziel) und ein eindeutig gekennzeichnetes Mock-TSE-Zertifikat.
Nicht-PDF-Druckauftraege und Inhalte ohne PDF-Signatur werden abgewiesen.

Fall 1 - Kassenbon:

- fiktiver Verkauf ueber `357,00 EUR`;
- Zahlung `119,00 EUR` bar und `238,00 EUR` EC/Karte;
- PDF-Pruefung auf Belegnummer, TSE-Transaktionsnummer, Start/Ende,
  Signaturzaehler, Signatur, QR-Daten, Gesamtbetrag, Zahlungsarten,
  Zertifikatseriennummer und SHA-256-Fingerprint.

Fall 2 - Tagesabschluss und FiBu:

- Barverkauf `119,00 EUR`;
- EC-/Kartenzahlung `238,00 EUR`;
- Gutscheinannahme `50,00 EUR`;
- Gutscheinausgabe `100,00 EUR`;
- Barentnahme `80,00 EUR`;
- steuerbarer POS-Umsatz `407,00 EUR`;
- Abschlussbeleg als PDF mit Zahlungsarten, Gutscheinbewegungen,
  Barentnahme, FiBu-Belegnummer und Buchungszeilen;
- Endpoint-Nachweis, dass genau die erwarteten sieben Buchungszeilen an
  `domain_erp.journal_entry_lines` uebergeben werden;
- Soll und Haben jeweils `587,00 EUR`.

Ausfuehrung:

```text
python -m pytest tests/test_pos_fiscal_documents_accounting.py \
  tests/test_pos_fiscalization_providers.py \
  tests/test_process_kernel_wave1_contracts.py -q --no-cov
46 passed
```

Die PDFs werden im jeweiligen Pytest-Temporaerverzeichnis geschrieben und
anschliessend mit `pdfplumber` wie ein gedrucktes Dokument wieder eingelesen.
Der Test akzeptiert keine reine Byte-Erzeugung ohne inhaltliche
Dokumentenpruefung.

## Externe Gates

- fiskaly Sandbox-/Live-Credentials und lizenzierte OpenAPI-Vertraege
- Swissbit Cloud- oder SDK-Partnervertrag
- DSFinV-K-Pruefwerkzeug und KassenSichV-/GoBD-Fachabnahme
- reale Kasse, Drucker, Offlinebetrieb und Wiederanlauf
- visueller Ausdruck- und Lesbarkeitstest auf dem freigegebenen
  Produktions-PDF-/Thermodruckertreiber
