# StammListenParent — Ergebnisnotiz 2026-10-22

Workstream: P1 StammListenParent und Dual-Pfad Listen (parallel zu StammObjectPageParent).

## Backend

- Neu: `app/core/stamm_list_parent.py` mit `build_stamm_list_screen`, Export/Neu-Hilfen, Status-Filter.
- `app/core/screen_definitions_listen.py` delegiert an den Parent (keine Duplikat-Shell mehr in `_liste`).

## Frontend (Dual-Pfad Detail → native Runtime)

| Seite | Detail (neu) | Create (unveraendert Legacy) |
|---|---|---|
| `finance/debitoren-liste.tsx` | `/finance/debitor/:id` | `/finance/debitoren/new` |
| `futtermittel/mischfuttermittel-liste.tsx` | `/futtermittel/mischfuttermittel/:id` | `/futtermittel/mischfuttermittel/stamm/new` |
| `einkauf/auftragsbestaetigungen-liste.tsx` | `/einkauf/auftragsbestaetigung/:id` | `/einkauf/auftragsbestaetigung/neu` |
| `artikel/liste.tsx` | `/lager/artikel/:id` | `/artikel/neu` |
| `crm/lieferanten-liste.tsx` | `/crm/lieferanten/:id` | `/crm/lieferanten/stamm/new` |
| `crm/kunden-liste.tsx` | `/crm/kunden/:id` (Entity-ID, Customer-360 native) | `/verkauf/kunde/neu` |
| `sales/auftraege-liste.tsx` | `/sales/sales-order/:id` | `/sales/order-editor` |
| `sales/lieferungen-liste.tsx` | `/sales/delivery-note/:id` (Auftrag: `/sales/sales-order/:id`) | `/sales/delivery-editor` |

Bereits erledigt / unveraendert (Detail schon native oder `NativeListPage`): `saatgut-liste`, `duenger-liste`, `einkauf/lieferanten-liste`, `bestellungen-liste`, `kreditoren-liste` (`NativeListPage`), `verkauf/kunden-liste` (Detail bereits `/crm/kunden/:id`), `kontakte-liste`, `anlieferavis-liste`, `futtermittel/einzelfuttermittel-liste`, Einkauf-`anfragen`/`angebote` (`NativeListPage`).

Offen (kein native Detail in `route-aliases.json`): u. a. `biostimulanzien-liste` (`/agrar/biostimulanzien-stamm/:id`), `rechnungseingaenge-liste` (nur Legacy `rechnungseingang`), `sales/angebote-liste` (Verkaufsangebot-Editor).

## Tests

- `tests/test_stamm_list_parent.py`
- `packages/frontend-web/src/__tests__/pages/mask-listen-family-nav.test.ts`

## Nicht angefasst (parallele Agenten)

- `app/core/stamm_object_page_parent.py`, `app/core/screen_definitions_stamm.py`
- `app/core/kontroll_worklist_parent.py`, `screen_definitions_kontrolle.py`
- `beleg_maske_parent.py`, `beleg_screen_builder.py`, `screen_definitions.py` (Beleg-Pfad)

Kein Git-Commit in diesem Workstream (index.lock / parallele Agenten).
