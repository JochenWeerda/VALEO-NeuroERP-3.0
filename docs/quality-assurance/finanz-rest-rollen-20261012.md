# Übrige Finanzwege: Rollen vor der Datenbank

Stand: 2026-10-12 · Slice `FINANZ-REST-ROLLEN-20261012` · Auftrag: „bewusst Ausgelassenes und Offenes
delegiere ich an dich" · vierter Schnitt nach
[Zahlungsverkehr und Stammdaten](zahlung-stammdaten-rollen-20261012.md)

## Befund

45 Wege prüften keine Rolle. Darunter drei **Umgehungswege**, die an den Rollen der eigentlichen Wege
vorbeiführten:

| Umgehungsweg (`mask_frontend_bridges.py`, `compat.py`) | eigentlicher Weg verlangt |
|---|---|
| `POST /finance/direct-debits/{id}/approve` und `/execute` – Lastschriftlauf freigeben, ausführen | Finanzleitung |
| `POST /finance/periods/{id}/close` – Buchungsperiode abschließen | Finanzleitung |
| `POST /finance/import/debitoren` – Debitoren in Masse einspielen | (kein eigentlicher Weg) |

Wer angemeldet war, konnte über die Brücke eine Periode abschließen, obwohl `/finance/periods` das
seit dem Hauptbuch-Slice nur der Finanzleitung erlaubt.

## Entscheidung

| Gruppe | Lesen | Bearbeiten | Leitung |
|---|---|---|---|
| Kontoauszugsimport, Zahlungsabgleich (`bank_statement_import`, `payment_matching`) | `finance_read` | `finance_write`: importieren, zuordnen, automatisch abgleichen | – |
| Finanz-Lesemodelle (`finance_read_models`) | `finance_read` | – | Projektionen neu aufbauen |
| Belege mehrerer Bereiche: Ausgangsrechnung (`finance_invoices`), Belegkontrolle (`document_control`), Eingangsrechnung über die Brücke | `beleg_read` = Finanz, Verkauf, Vertrieb, Einkauf | `beleg_write` = Sachbearbeitung von Finanz, Verkauf, Einkauf | löschen |
| Finanzwege der Brücke: Anlagen, DATEV-Ausgabe, Kennzahlen, Cockpit | `finance_read` | Anlage anlegen | Lastschrift freigeben und ausführen, Periode abschließen |
| Debitorenimport (`compat`) | – | – | importieren |

**Warum eine gemeinsame Belegrolle:** Der Verkauf fakturiert und schreibt Gutschriften, der Einkauf
erfasst Eingangsrechnungen, die Belegkontrolle führt offene Bestellungen, fehlende Eingangsbelege und
gesperrte Lieferscheine – daran arbeiten alle drei. Eine Rolle je Belegart wäre genauer, aber drei
weitere Rollen, die niemand auseinanderhält. Löschen bleibt in jedem Fall bei der Finanzleitung.

**Ausgenommen:** `settlement-cockpit` und `position-exposure` liegen im Finanzrouter, sind aber
Lesemodelle für Abrechnung und Positionen aus Agrar und Kontrakt. Eine Finanzrolle hätte deren Leser
ausgesperrt; ihre Rolle ist dort zu klären.

## Zurückgestellt: Debitoren und Kreditoren lesen

Geplant war, das Lesen von Debitoren und Kreditoren auf Finanz, Verkauf, Vertrieb und Einkauf zu
begrenzen. Dafür muss `tests/test_zahlung_stammdaten_rollen_vertrag.py` geändert werden – die Datei
trägt im geteilten Arbeitsbaum gerade nicht committete Änderungen eines anderen Agenten
(Identitätsgrenze der Tests). Die Änderung folgt, sobald die committet sind.

## Geänderte Dateien

- `app/auth/finance_roles.py` – `beleg_read`, `beleg_write` (additiv)
- nur Dekoratoren und ein Import in `payment_matching.py`, `bank_statement_import.py`,
  `finance_read_models.py`, `finance_invoices.py`, `document_control.py`; in
  `mask_frontend_bridges.py` (15 Wege) und `compat.py` (1 Weg) nur die genannten Finanzwege
- `tests/test_finanz_rest_rollen_vertrag.py` (neu)
- `tests/test_process_kernel_wave2_read_models.py` – Nutzer mit Finanzrolle

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_finanz_rest_rollen_vertrag.py` – 14 Rollen × 45 Wege, ohne Anmeldung, Umgehungswege bei der Leitung, kein Löschen durch die Belegrolle, Vollständigkeit der Finanzwege je Datei | 684 bestanden |
| `test_process_kernel_wave2_read_models.py`, `…wave19_read_model_contracts.py` | wie ohne die Änderung: 42 bestanden, 2 rot (siehe unten) |
| Ruff auf den geänderten Dateien | keine neue Meldung |

### Die Nachbartests sind nicht aussagekräftig – und warum

Seit `840b78e30` („enforce provider tenant binding", Identitätsarbeit eines anderen Agenten) verlangt
`get_tenant_id` einen geprüften Mandanten. 38 Testdateien rund um diese Wege enden deshalb schon
**ohne** diese Änderung mit 170 Fehlschlägen (gemessen am selben Stand, in einem zweiten Arbeitsbaum,
mit der dort vorbereiteten, noch nicht committeten Korrektur der `conftest.py`). Mit dieser Änderung
sind es dieselben Dateien mit denselben Zahlen.

Das heißt nicht, dass die Rollen dort nichts brechen: Sobald die Mandantengrenze der Tests repariert
ist, antworten **67 Fälle** an den jetzt geschützten Wegen mit „Not authenticated" statt mit ihrem
Ergebnis, weil ihre Testanwendung keinen Nutzer setzt. Betroffen sind:

- Mini-Anwendungen ohne Nutzer: `test_bank_import_account_replay.py`,
  `test_bank_payment_matching_integrity.py`, `test_bank_statement_import_integrity.py`,
  `test_payment_csv_import_integrity.py`, dazu `test_bank_camt_parser_integrity.py`,
  `test_bank_mt940_parser_integrity.py`, `test_bank_statement_date.py`
- Hauptanwendung ohne `Authorization`-Kopf: `test_document_control.py`,
  `test_document_control_projection.py`, `test_finance_p0_endpoints.py`,
  `test_finance_read_models_api.py`, `test_gap_fixes_batch1.py`, `test_mask_entity_backends.py`,
  `test_mask_frontend_bridges.py`, `test_process_kernel_wave7_read_models.py`,
  `test_small_endpoints_wave54.py`

Diese Dateien sind hier **nicht** angefasst: Sie sind aus dem anderen Grund rot und werden gerade von
dem anderen Agenten repariert; ein zweiter Eingriff in dieselben Dateien hätte sich überschnitten.
Sie bekommen ihren Nutzer, sobald dessen Korrektur committet ist.

Keine Sichtprüfung: Das Entwicklungs-Backend nimmt den Dev-Token nicht mehr an; ein Provider-Konto
für die Sichtprüfung liegt noch nicht vor.

## Betrieb

- Verkauf und Einkauf brauchen für Rechnungen und Belegkontrolle ihre Bearbeiterrolle
  (`SALES_BEARBEITEN`, `EINKAUF_BEARBEITEN`); eine Leserolle reicht zum Ansehen.
- Lastschrift freigeben und ausführen sowie Periode abschließen gehen auch über die Brückenwege nur
  noch mit `FINANCE_ADMIN`.

## Offen

- **67 Tests** brauchen einen Nutzer, sobald die Mandantengrenze der Tests repariert ist (oben).
- **Debitoren und Kreditoren lesen** (oben, zurückgestellt).
- **`mask_frontend_bridges.py` hat 28 weitere Wege anderer Bereiche ohne Rolle** – darunter
  schreibende: Saatgutbestellung, Segment neu berechnen, Anfrage senden, Waagenvorlage,
  Dienstplan-Zuweisung, EPCIS-Ereignis, Futtermittel sammeln löschen. Nicht Finanz, deshalb hier nicht
  entschieden; die Datei ist als Ganzes ein Umgehungsweg.
- **`crm_account_hierarchy.py`** (Kundenhierarchie setzen) und **`iban_lookup.py`** prüfen keine Rolle.
- **Abrechnungs- und Positions-Lesemodell** (oben, ausgenommen).
