# DOC-ROUTER-ROLLEN: Der generische Belegrouter schreibt keine Finanzbelege mehr

Stand: 2026-10-14 · Slice `DOC-ROUTER-ROLLEN-20261014` · Folge aus `DOC-ROUTER-MANDANT-20261014`

## Entscheidung

Nutzerentscheidung vom 14.10.2026: `PUT`/`DELETE /{doc_type}/…` des Belegrouters nur fuer die Belegarten, die allein
ueber ihn gefuehrt werden. Finanzbelege laufen ausschliesslich ueber ihre Fachwege mit Rollenpruefung.

## Befund

`/api/mcp/documents/*` verlangte nur eine Anmeldung. Jede angemeldete Person des Mandanten konnte darueber eigene
Ausgangs- und Eingangsrechnungen, Zahlungseingaenge, Lieferantengutschriften und -belastungen aendern (etwa den Status
auf BEZAHLT setzen) und loeschen sowie Rechnungen und Zahlungseingaenge anlegen — an `finance_write`, `beleg_write`,
der Freigabe einer zweiten Person und der Buchung vorbei.

## Was jetzt gilt

- `ROUTER_BELEGARTEN` in `app/documents/router.py`: Anfrage, Angebot, Auftrag, Lieferschein, Bedarfsmeldung,
  Lieferantenangebot, Bestellung — die sieben Arten, die der Router selbst anlegt.
- `PUT /{doc_type}/{nr}`, `DELETE /{doc_type}/{nr}` und `DELETE /{doc_type}?numbers=` antworten fuer jede andere
  Belegart 403 mit Verweis auf den Fachweg, ohne zu lesen oder zu schreiben.
- `POST /sales_invoice` und `POST /payment_received` sind geschlossen (403). Aufrufer gab es keine: das Frontend
  schreibt ueber diesen Router nur Angebote und Auftraege; Rechnungen entstehen ueber `/api/v1/finance/invoices`.
- Lesen (Einzelbeleg, Liste) bleibt fuer alle Belegarten im eigenen Mandanten moeglich.

## Nachweis

- `tests/test_belegrouter_rollen.py` (19, frische Datenbank): je Finanzbelegart (Ausgangs-/Eingangsrechnung,
  Zahlungseingang, Gutschrift, Belastung) Aendern 403 und Beleg unveraendert, Loeschen und Sammelloeschung 403 und
  Beleg vorhanden; Rechnung und Zahlungseingang werden nicht angelegt; die sieben Router-Belegarten bleiben aenderbar;
  die Positivliste enthaelt keinen Finanzbeleg.
- `tests/test_belegrouter_mandant.py` nutzt fuer Aendern/Loeschen/Anlegen jetzt Router-Belegarten (vorher
  Gutschrift und Rechnung); Lesen fremder Rechnungen und Gutschriften bleibt geprueft.
- Regression: alle Testdateien, die den Router oder seine Helfer beruehren — gruen bis auf vorbestehend rot
  `test_process_kernel_wave1_contracts.py::test_payment_run_approve_…`.
- OpenAPI: nur die Beschreibungen der vier POST-Pfade (mit und ohne `/api/v1`) geaendert und nachgezogen.

## Offen

- Die sieben Router-Belegarten selbst haben weiterhin keine Rollenpruefung (jede angemeldete Person des Mandanten
  darf Angebote, Auftraege, Bestellungen … anlegen, aendern, loeschen). Das entspricht dem bisherigen Fachstand
  dieser Belege, ist aber keine bewusste Rechtevergabe.
