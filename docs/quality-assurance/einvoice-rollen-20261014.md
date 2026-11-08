# EINVOICE-ROLLEN: Die E-Rechnungswege pruefen die Belegrolle

Stand: 2026-10-14 · Slice `EINVOICE-ROLLEN-20261014` · Folge aus `DOC-EINZELABRUF-MANDANT-20261014`

## Befund

`POST /api/v1/sales/invoices/{nr}/einvoice/xrechnung`, `POST …/zugferd` und `GET …/xrechnung` verlangten nur eine
Anmeldung. Jede angemeldete Person des Mandanten — auch Lager, Fuhrpark oder Portalnutzer ohne Belegrecht — konnte
zu jeder eigenen Ausgangsrechnung eine E-Rechnung erzeugen und damit einen unloeschbaren Eintrag im GoBD-Archiv
(`domain_docflow.document_artifacts`) festschreiben.

## Was jetzt gilt

Wie bei `/finance/invoices` (`app/auth/finance_roles.py`):

| Weg | Rolle | Wirkung |
|---|---|---|
| `POST …/einvoice/xrechnung`, `POST …/einvoice/zugferd` | `beleg_write` (Sachbearbeitung Finanz/Verkauf/Einkauf, admin, manager) | erzeugt und archiviert |
| `GET …/einvoice/xrechnung` | `beleg_read` (Lesen Finanz/Verkauf/CRM/Einkauf und hoeher) | erzeugt ohne Archiveintrag |

Die Rolle wird vor dem ersten Datenbankzugriff geprueft; ohne sie 403 und kein Archiveintrag.

## Nachweis

- `tests/test_einvoice_rollen.py` (4, frische Datenbank): ohne Belegrolle alle drei Wege 403 und kein Archiveintrag;
  Leserolle (Verkauf, Finanz) ruft ab, erzeugt aber nicht; Sachbearbeitung Verkauf erzeugt und archiviert genau einen
  Eintrag.
- `tests/test_sales_invoice_einvoice_endpoints.py` (7) gruen — laeuft nur mit gesetztem `TEST_DATABASE_URL`, sonst
  uebersprungen; das gilt auch fuer den Nachweis in `DOC-EINZELABRUF-MANDANT` und ist hiermit nachgeholt.
- `test_einzelabruf_mandant`, `test_einvoice_generator`, `test_gobd_artefakt_bestell_altbeleg`,
  `test_spec_p0_05_belege_coverage` gruen.
- OpenAPI: keine Abweichung (die Pfade trugen die Bearer-Angabe schon).
