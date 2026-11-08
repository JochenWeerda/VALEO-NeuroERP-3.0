# PORTAL-FELDBUCH-KUNDE-20261014: Portal-Feldbuch nur mit Kunde aus der Anmeldung

Stand: 2026-10-14 · Slice `PORTAL-FELDBUCH-KUNDE-20261014` · Folgeslice von `PORTAL-KUNDE-001`, Umsetzung
TENANT-DOC-001 Punkt 1 (Nutzerentscheidung 14.10.2026)

## Befund

`app/api/v1/endpoints/portal_feldbuch.py` (30 Wege: Schlaege, Massnahmen, Duenge-/Stoffstrombilanz, Ernte,
Pflanzenschutz, Import/Export, Offline-Sync, Jahreswechsel …) nahm den Kunden ueber `_get_customer_id` aus dem
Parameter `customer_id`, sonst aus der Anmeldekennung, sonst aus dem Rueckfall `dev-customer`. Wer eine fremde
Kunden-ID in die URL schrieb, las und aenderte Schlaege und Massnahmen dieses Kunden; jede Anmeldung ohne Kunden-
bezug schrieb in ein gemeinsames Feldbuch `dev-customer`.

## Aenderung

- `_get_customer_id` liefert das Kundenkonto nur noch aus `portal_kunde` (Anmeldung + gepruefte Zuordnung; interne
  Betreuung waehlt per `X-Kundenkonto` einen Kunden des Mandanten). Alle 30 Wege haengen an dieser einen Stelle;
  der Parameter `customer_id` ist aus dem Vertrag entfernt, mitgeschickt bleibt er wirkungslos.
- Interne Betreuung liest das Feldbuch mit einer Belegleserolle (wie das uebrige Portal); **aendern** (POST/PUT/
  DELETE) nur mit `AGRAR_BEARBEITEN`, `AGRAR_ADMIN` oder `admin`. Portalkunden schreiben in ihr eigenes Feldbuch wie
  bisher.
- OpenAPI: 30 Operationen der `/api/v1/portal/feldbuch/*`-Pfade, `customer_id` → Kopf `X-Kundenkonto`.

## Nachweis

- `tests/test_portal_kunde_trennung.py` (frische Datenbank `valeo_probe`), vier neue Faelle: `customer_id` in der URL
  wirkungslos beim Lesen und Anlegen; fremder Schlag lesen/aendern/loeschen 404; ohne Zuordnung 403 (auch mit
  `customer_id`), kein Ersatzkunde; Zuordnung aus Mandant B gilt in A nicht; interne Leserolle liest, schreibt und
  loescht nicht (403), Agrar-Bearbeiter legt an, fremder Mandant 404. Insgesamt 25 Faelle gruen.
- Regression: `test_portal_feldbuch_*`, `test_feldbuch_*` (50), `test_process_kernel_wave31_dq_import_edge_paths`,
  `test_portal_canonical_routes` gruen.

## Offen

- `scripts/seed_simulation_rations_acker.py` legte Schlaege ueber den Rueckfall `dev-customer` an; es braucht jetzt
  eine Zuordnung oder `X-Kundenkonto` mit Agrar-Bearbeiterrolle.
- `created_by` nennt weiter `portal:<kunde>` statt der handelnden Anmeldung.
- Interne Agrarberatung mit nur `AGRAR_LESEN` (ohne Belegleserolle) kommt nicht ins Kundenfeldbuch — die Liste der
  Betreuungsrollen in `portal_kunde` ist eine eigene Entscheidung.
- Lohndienste (`kunden_nr` aus Query), Empfehlungen (`/portal/empfehlungen/{kunden_nr}`); Rolle je Portalweg.
