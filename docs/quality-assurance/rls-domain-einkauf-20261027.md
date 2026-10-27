---
title: QA RLS-DOMAIN-EINKAUF-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: RLS-Domain einkauf (Bestellungen, Lieferanten, ERS, Rechnungspruefung, Lieferscheine, Waren- und Rechnungseingaenge mit Positionen) auf valeo_probe abgenommen; live blockiert die Migration absichtlich an zwei Demo-Bestellungen mit fremdem Lieferanten.
---

# QA RLS-DOMAIN-EINKAUF-20261027

**Basis:** `claude/rls-domain-inventory-20261027` (#77, getestet ffd126cb4).
Migration `rls_domain_einkauf_20261027` folgt auf `rls_domain_inventory_20261027`. `alembic heads` zeigt
einen einzigen Head.

**Status:** abgeschlossen auf dem Prüfstand, **live blockiert** (siehe „Gewachsene DB“). Prüfstandsfenster nach
Freigabe durch Codex. `valeo_probe` stand vorher und nachher auf `loading_stop_fk_20261023`, 0 fremde
Sitzungen. Die gewachsene Datenbank wurde nur lesend geprüft.

**Nicht enthalten:** `einkauf_anfragen`, `einkauf_angebote`, `einkauf_anlieferavis`,
`einkauf_auftragsbestaetigungen`, `einkauf_warengruppen`, `einkauf_zahlungslaeufe`, `kontrakte`,
`bestellvorschlaege`, `rfq_*` und `artikel_lager_parameter` stehen schon unter P5. Sie bekommen nur
Verbund-FKs bzw. die neue Vorgabe, ihre Policies bleiben unverändert.

## Analyse einkauf

| Tabelle | Befund | Entscheidung |
|---|---|---|
| `domain_einkauf.bestellungen`, `lieferanten` (B) | Schreiber tokengebunden; Statuswechsel in `proc_bestellung_lifecycle_service.py` las und änderte die Bestellung **ohne Mandantenfilter** | getrennt; Bestellung → Lieferant/Kontrakt/Vorschlag über `(id, tenant_id)` |
| `ers_invoices`, `ers_suppliers`, `invoice_verification`, `proc_purchase_orders`, `zahlungslauf_kreditoren` (A, nullable) | keine Zeile ohne Mandant | NOT NULL, getrennt |
| `einkauf_lieferscheine` (A) | Schreiber tokengebunden | getrennt |
| 7 Positionstabellen (C) | Mandant nur am Kopf | `tenant_id` vom Kopf, NOT NULL, Vorgabe aus dem Kontext, Verbund-FK (ON DELETE wie bisher) |
| `einkauf_rechnungseingaenge`, `einkauf_wareneingaenge`, `einkauf_abgleich_ergebnisse` (D, nur frisch) | Code filtert schon nach `tenant_id`, die Tabellen hatten die Spalte nicht | `tenant_id varchar` NOT NULL, Vorgabe aus dem Kontext; Positionen erben vom Kopf |
| `einkauf_angebote`, `_anlieferavis`, `_auftragsbestaetigungen`, `_warengruppen`, `_zahlungslaeufe` (P5) | Spaltenvorgabe `'default'` | Vorgabe `public.rls_current_tenant()`; Policies unverändert |
| `kontrakte.lieferant_id`, `artikel_lager_parameter.std_lieferant_id`, `rfq_quotes.rfq_id` (P5) | Einzel-FK | Verbund-FK (`rfq_quotes` CASCADE wie bisher) |

## Fachkorrekturen

- **`procurement_match.py`** (5 Wege unter `/api/v1/procurement/...`): Der Mandant kam aus dem Kopf
  `X-Tenant-ID`, ohne Kopf galt `"default"`. Jetzt kommt er aus dem Token (`Depends(get_tenant_id)`).
  Eingefrorene Rückfälle auf `"default"`: −5.
- **`proc_bestellung_lifecycle_service.py`**: `_fetch_bestellung` und das Status-UPDATE filtern nach dem
  Mandanten. Bisher konnte ein Nutzer eine fremde Bestellung über ihre ID freigeben oder stornieren.
- **`einkauf_compat_service.py`:**
  - `list_goods_receipts` verband auf die nirgends vorhandene Tabelle `docs_store`; die Wareneingangsliste
    war immer leer und hatte keinen Mandantenfilter. Jetzt eine Abfrage auf `einkauf_wareneingaenge` mit Mandant.
  - Rechnungseingänge: Liste, Statusabfrage, Prüfen/Freigeben (UPDATE) und Verbuchen lasen ohne
    Mandantenfilter. Eine fremde Rechnung ergibt jetzt 404.
  - Wareneingänge und ihre Positionen werden mit `tenant_id` angelegt.
- **`app/einkauf/router.py`**: Rechnungseingangspositionen werden mit `tenant_id` angelegt.

## Gewachsene DB (lesend) — Live-Blocker

- `DEMO-PO-001` und `DEMO-PO-002` (Mandant `00000000-0000-0000-0000-000000000001`) verweisen über
  `lieferant_id` auf den Lieferanten `019ca040-5090-79fd-95ea-f4d3e9b4ff26` des Mandanten `valeo`.
  Die Migration bricht dort **absichtlich** ab (Fremdprüfung vor dem Verbund-FK). Vor einem Live-Lauf muss
  geklärt werden, woher die Bestellungen stammen: umhängen auf einen eigenen Lieferanten oder als
  Demodaten entfernen. Diese Entscheidung trifft der Lead; die Migration korrigiert keine Daten selbst.
- `einkauf_rechnungseingaenge`, `einkauf_wareneingaenge` und `einkauf_abgleich_ergebnisse` fehlen in der
  gewachsenen DB ganz. Die Migration überspringt fehlende Tabellen.
- Sonst keine Zeile ohne Mandant oder mit Platzhalter, keine Kinder ohne Eltern.

## Nachweise

```
pytest tests/test_rls_domain_einkauf.py -rs    -> 50 passed, 0 skipped (valeo_app, zurueckgerollt)
Gegenprobe mit alten Einzel-FKs                -> 19 rot
Gegenprobe mit altem Code                      -> 7 rot (alle Fach- und Tokenvertraege)
RLS-Gesamtsuite + Fallback-Vertrag             -> 481 passed, 0 skipped
356 Bestandsmodule (conftest, Pruefstand, 9 Pakete nacheinander)
                                               -> 12454 passed; 41 rot wie auf der Basis #77 (0 neu rot)
Inventar/Rollout/Matrix/Systemlesen regeneriert, generate_code_inventories.py --check -> OK
```

| Abnahmekriterium | Test |
|---|---|
| Mandantengrenze je Tabelle (eigen ok; fremd und `system` SELECT/INSERT/UPDATE/DELETE gesperrt; kein `tenant_id`-Wechsel; fail-closed) | `test_mandantengrenze_je_tabelle` (20) |
| kein Verweis auf fremden Eltern, auch nicht umgehängt (auch aus P5-Tabellen) | `test_kein_verweis_auf_fremden_eltern` (18) |
| Positionen und D-Köpfe erben den Mandanten aus dem Kontext | `test_kind_und_beleg_erben_den_mandanten_vom_kontext` |
| P5-Vorgabe ist der Kontext, nicht `'default'` | `test_p5_vorgabe_ist_der_kontext_nicht_default` |
| Eltern mit Verweisen behalten ihren Mandanten | `test_eltern_mit_verweisen_behaelt_seinen_mandanten` |
| Kontextwechsel/Savepoint, Hintergrund, Pool | `test_kontextwechsel_savepoint_hintergrund_pool` |
| Waren- und Rechnungseingänge nur eigen, fremd 404 | `test_fachkette_waren_und_rechnungseingaenge_nur_eigener_mandant` |
| Bestellstatus nur an eigener Bestellung | `test_fachkette_bestellstatus_nur_eigene_bestellung` |
| Beschaffungswege nehmen den Mandanten aus dem Token | `test_beschaffungswege_nehmen_den_mandanten_aus_dem_token` (5) |

Die Fachketten laufen als Tabelleneigentümer (`RESET ROLE`), also ohne RLS: Sie prüfen den Code, nicht die
Policies. Mit `valeo_app` hätte RLS die fehlenden Mandantenfilter verdeckt.

Die 41 vorbestehenden Fehlschläge (Studio-/Masken-Generatorverträge, `test_document_screen_versions` 10,
`test_studio_listen_kommandos` 14, `test_mcp_local_action_classification` 5, `test_meridian_beleg_systemweit` 4
u. a.) sind mit und ohne diesen Slice gleich rot. Die 21 übersprungenen Bestandstests überspringen auch auf der
Basis und zählen nicht als Abnahme.

Inventar: 112 zurückgestellt (−15).

**Testhilfe** (`tests/rls_domain_support.py`): `probe` gewährt zusätzlich `USAGE` auf die Sequenzen der
Schemata (serielle Schlüssel wie `ers_invoices.id`).

## Verbleibend / vor Live-Aktivierung

- **DEMO-PO-001/002** klären (siehe oben); bis dahin bricht die Migration live ab.
- **Identitätsbefund:** `_write_rechnung_audit` trägt als Akteur einen beliebigen aktiven Nutzer des Mandanten
  ein, nicht den angemeldeten. Eigener Slice zur Identität im Prüfprotokoll.
- **`einkauf_retouren`** gibt es nicht; Lieferantenretouren haben keine eigene Tabelle.
- Die drei D-Tabellen fehlen in der gewachsenen DB; vor Live muss geklärt sein, ob sie angelegt werden
  (Migrationsstand) oder ob der Code dort auf andere Tabellen zeigt.
- **Masken:** Bestellung, Wareneingang, Rechnungseingang, Abgleich mit zwei Mandanten prüfen.
  Die Maskenabnahme liegt bei Codex.
