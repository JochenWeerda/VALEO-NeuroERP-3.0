# PORTAL-SHOP-KUNDE-20261014: Portalshop nur mit Mandant und Kunde aus der Anmeldung

Stand: 2026-10-14 · Slice `PORTAL-SHOP-KUNDE-20261014` · Folgeslice von `PORTAL-KUNDE-001`, Umsetzung TENANT-DOC-001
Punkt 1 (Nutzerentscheidung 14.10.2026)

## Befund

- `app/api/v1/endpoints/portal_shop.py` nahm den **Mandanten aus dem Parameter `tenant_id`** und den Kunden aus
  `customer_id`, aus der Anmeldekennung oder dem Rueckfall `customer-demo-001`. Wer `tenant_id` und `customer_id`
  in die URL schrieb, sah Katalog, Bestellungen, Kontrakte und Vorkaeufe jedes Kunden jedes Mandanten und konnte in
  dessen Namen bestellen.
- Die internen Wege (`PATCH /portal/orders/{id}/status`, `/orders/reconciliation`, `/orders/observability`) prueften
  keine Rolle und nahmen den Mandanten ebenfalls aus der URL.
- Das Modell `CustomerOrder` kennt seit C3 die Spalte `idempotency_key`, **keine Migration legte sie an** — weder die
  frische noch die gewachsene Datenbank (`valeo_neuro_erp`) hat sie. Alle Bestellwege des Shops antworteten dort 500.
  Zudem war der Schluessel systemweit eindeutig, obwohl ihn der Client waehlt.

## Aenderung

- Kundenwege `products`, `orders` (GET/POST), `orders/{id}`, `contracts`, `pre-purchases`: Mandant und Kunde nur aus
  `portal_kunde` (Anmeldung + gepruefte Zuordnung; interne Betreuung waehlt per `X-Kundenkonto`). Die Parameter
  `tenant_id`/`customer_id` sind entfernt; mitgeschickt bleiben sie wirkungslos.
- Interne Wege: Mandant aus `get_tenant_id`, Rechte wie bei Auftraegen (`app/auth/beleg_roles.py`, `sales_order`):
  Abgleich und Beobachtung `lesen`, Statusaenderung `bearbeiten`.
- Migration `portal_order_idempotency_20261014`: Spalte `idempotency_key`, eindeutig je Mandant, Kunde und Schluessel
  (`ux_customer_orders_idempotency`); das Modell entsprechend.
- Frontend `lib/services/portal-service.ts`: kein `VITE_TENANT_ID`/`tenant_id` mehr.
- OpenAPI: nur die acht Shop-Pfade; Tabellenkatalog nur `domain_portal.customer_orders` (Spalte), Migrationsinventar.

## Nachweis

- `tests/test_portal_kunde_trennung.py` (frische Datenbank `valeo_probe`): vier neue Faelle — `tenant_id`/`customer_id`
  in der URL wirkungslos (nur eigene Kontrakte); Bestellliste und -detail nur des eigenen Kontos (fremde Bestellung
  404); ohne Zuordnung 403 auf allen vier Kundenwegen; interne Wege: Portalkunde 403, Leserolle darf Abgleich, aber
  keine Statusaenderung, fremder Mandant 404 trotz `tenant_id` in der URL, Bearbeiterrolle 200. Dazu die 17
  bestehenden Faelle gruen.
- `tests/test_portal_canonical_routes.py` umgestellt: der veroeffentlichte Vertrag enthaelt **keinen** `tenant_id`-
  oder `customer_id`-Parameter mehr (vorher als Pflicht festgeschrieben). 9 gruen.
- `tests/test_portal_shop_business_time.py`, `tests/test_canonical_router_mounts.py` gruen.
- Migration: frische Datenbank auf/ab/auf, ein Head. Gewachsene Datenbank nicht migriert.

## Nebenbefund

`domain_portal.customer_orders.order_number` ist systemweit eindeutig (`customer_orders_order_number_key`), nicht je
Mandant — Muster wie `domain_crm.customers.customer_number`.

## Offen

- `portal_feldbuch` (31 Wege), Lohndienste (`kunden_nr` aus Query), Empfehlungen (`/portal/empfehlungen/{kunden_nr}`).
- Kontowahl `X-Kundenkonto` im Frontend; Rolle je Portalweg (welche Betriebsrolle bestellen darf) nicht entschieden.
- Gewachsene Datenbank: Migration noch nicht angewandt (Shop-Bestellwege dort bis dahin 500).
