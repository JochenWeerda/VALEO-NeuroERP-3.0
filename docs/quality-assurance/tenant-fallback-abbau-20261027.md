---
title: QA TENANT-FALLBACK-ABBAU-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Alle 43 eingefrorenen Rueckfaelle auf den Mandanten 'default' abgebaut; Operations-Router mit Mandant aus dem Token und Filter je Abfrage; Service-Anfragen in der Datenbank statt im Prozessspeicher.
---

# QA TENANT-FALLBACK-ABBAU-20261027

**Basis:** `claude/ustva-wahrheit-20261027` (wegen der Alembic-Kette). Migration `service_anfragen_20261027` folgt auf
`vat_return_bearbeiter_20261027`; `alembic heads` zeigt einen Head.

## Befunde

| Stelle | Befund | Korrektur |
|---|---|---|
| `tankstelle.py`, `wartung.py`, `versicherungen.py`, `projekte.py`, `ernte_planung.py` | **Kein Mandantenfilter** in Liste, Abruf, Aenderung, Loeschen; Mandant der Anlage aus dem Rumpf mit `"default"` als Vorgabe. Eine Zapfung minderte den **Tankbestand des ersten Treffers** zu diesem Artikel, gleich welcher Mandant | Mandant aus dem Token, jede Abfrage im eigenen Mandanten, Anlage setzt den Mandanten selbst |
| `verladung.py` | Anlage mit `"default"` aus dem Rumpf, Frachtbrief mit dem Token-Mandanten: zwei verschiedene Mandanten fuer einen Vorgang; Abruf/Loeschen ohne Filter | wie oben |
| `edi_api.py` | Nachricht mit `"default"` aus dem Rumpf, Partner mit Mandant aus dem Rumpf, offene Nachrichten ohne Filter | wie oben |
| Operations-Router (5) | `created_by`/`updated_by` existieren, wurden nie gefuellt | Bearbeiter aus dem Token |
| `controlling_actions.py` (6), `finance_actions.py` (7) | `x_tenant_id or "default"` | `Depends(get_tenant_id)` |
| `service_anfragen.py` | Daten in einem **Woerterbuch des Prozesses**, vorbelegt mit zwei erfundenen Anfragen des Mandanten `default`; Kopf mit `"default"` als Vorgabe; jeder Neustart verlor alle Anfragen, jeder Worker hatte einen eigenen Stand | Tabellen `domain_ops.service_anfragen` und `service_anfrage_rueckmeldungen` (getrennte Policies, Verbund-FK, Nummernkreis je Mandant, Status als Pruefbedingung, Abschluss nur ueber `/abschluss`), Bearbeiter aus dem Token |
| `external_agent_integrations.py` (5 + Monitoring) | `Query(default="default")`; `superglue/monitoring` ohne Mandant lieferte die Journaleintraege **aller** Mandanten an jeden angemeldeten Nutzer | Token |
| `numbering_router.py`, `numbering_service_pg.py` (7) | `"default"` als Vorgabe in Modell, Query und Dienst; `init-year` legte Nummernkreise fuer `default` an | Token; der Dienst verlangt den Mandanten |
| `atlas_customs_service.py`, `agents_schemas.py` | Vorgabe `"default"` (die Schema-Kopie ist unbenutzt) | Pflichtangabe bzw. Feld entfernt |
| ORM-Modelle der Operations-Router (9) | `default="default"` | entfernt; der Weg setzt den Mandanten |

**Ratsche:** `DEFAULT_BASELINE` in `tests/test_system_tenant_fallback_contract.py` 43 -> **0** (leer).

## Gewachsene Datenbank (lesend)

Alle betroffenen `domain_ops`-Tabellen sind live leer, ausser `domain_ops.edi_nachrichten`: **31 Zeilen, alle mit
Mandant `default`**. Sie sind fuer jeden echten Mandanten ab jetzt unsichtbar. Herkunft und Zuordnung sind eine
Datenentscheidung (Codex); nichts geaendert.

## Nachweise

```
pytest tests/test_tenant_fallback_abbau.py tests/test_system_tenant_fallback_contract.py -rs
                                                   -> 17 passed, 0 skipped (valeo_probe, Migrationen zurueckgerollt)
Gegenprobe alte Router/Modelle                     -> 9 rot (die 4 uebrigen pruefen nur die neue Migration)
68 betroffene Bestandsmodule (Pakete zu 20)        -> 1902 passed, 11 rot; 9 davon vorbestehend
                                                      (test_mcp_local_action_classification 5, test_meridian_beleg_systemweit 4,
                                                      auf der Basis #81 gleich rot), 2 durch diesen Slice -> Tests nachgezogen, 11 passed
RLS-Suite + Fallback- + Identitaetsvertrag (--noconftest) -> 549 passed
alembic heads 1; Code-Inventare, rls_inventory, rls_domain_matrix, rls_system_read, rls_rollout aktuell
OpenAPI: eigene Pfade und Schemas; vorbestehende Drift (closing-checklists, biostimulanzien, weighing-tickets) unveraendert
ruff: keine neuen Befunde
```

Nebenbefund behoben: Loeschen einer Wartungsanlage mit Protokollen und eines Projekts mit Aufgaben scheiterte (500): das
ORM setzte den Verweis der Kinder auf NULL, statt das `ON DELETE CASCADE` der Datenbank wirken zu lassen
(`passive_deletes=True`).

Die beiden Superglue-Routentests bauen eine App nur mit dem Router; sie setzen jetzt den geprueften Mandanten ueber
`dependency_overrides[get_tenant_id]` statt ueber `?tenant_id=`.

## Offen (eigener Slice RLS-DOMAIN-OPS)

- **Eindeutig systemweit statt je Mandant:** `ops_tank_bestand.artikel`, `ops_versicherungen.vertragsnummer`,
  `edi_partner.partner_id`/`gln`, `edi_nachrichten.nachricht_id`. Ein zweiter Mandant mit demselben Artikel scheitert
  an der Datenbank.
- **Server-Vorgabe `'default'`** an `tenant_id` dieser Tabellen und keine Policies; `ops_fahrer`, `ops_waagen`,
  `ops_wiegungen` und weitere `domain_ops`-Tabellen haben gar keinen Mandanten.
- **Verweise ohne Mandant:** `ops_zapfungen.fahrer_id` -> `ops_fahrer` (ohne Mandant), Fahrzeugverweise ohne Verbund-FK.
