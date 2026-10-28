---
title: QA RLS-DOMAIN-LOGISTICS-20261028
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-28
version: 1.0.0
description: RLS-Domain logistics auf valeo_probe abgenommen - sieben Tabellen getrennt, Mandant Pflicht, Verbundschluessel Tour/Stopp; Touren-, Fracht-, ePOD- und Dispositionswege mit Mandant aus dem Token; Spediteur-Rechnung ohne Schein-Buchung.
---

# QA RLS-DOMAIN-LOGISTICS-20261028

**Basis:** `claude/rls-domain-ops-20261028` (#84). Migration `rls_domain_logistics_20261028` folgt auf
`rls_domain_ops_20261028`; `alembic heads` zeigt einen Head.

## Befunde und Korrekturen

| Stelle | Befund | Korrektur |
|---|---|---|
| `GET /logistik/tours` | ohne `X-Tenant-ID` **alle Touren aller Mandanten** | Mandant aus dem Token, Filter je Abfrage (auch Stopps) |
| `GET /tours/{id}`, `/live-status`, `/tracking/{id}`, `/optimize`, `GET …/pod` | **gar kein Mandantenfilter**; Tracking nahm `share_token` an und pruefte ihn nie (jeder angemeldete Nutzer sah die GPS-Position jeder Tour) | Tour muss dem Mandanten gehoeren (sonst 404); `share_token` entfernt — ein oeffentlicher Link ist nicht gebaut |
| `POST …/stops`, `…/events` | an **fremde Touren** anlegbar | Tour im Mandanten (404) |
| `PATCH …/stops/{id}`, `…/pod`, Stornos | nur nach ID; Touren/Stopps ohne Mandant fuer jeden stornierbar | Tour, Stopp und Mandant im WHERE; fremd 404 |
| ePOD-Abrechnung, Dispositions-Check (Dienste) | Stopps nur nach ID gelesen und geaendert; Stopp ohne Tourbezug abrechenbar | Mandant und Tour Pflicht; Gewichtsabfrage in eigenem Savepoint (tote Transaktion) |
| `POST …/pod` | Lieferschein-Fehler mit `pass` verschluckt, Sitzung blieb in abgebrochener Transaktion | `rollback` |
| Frachttarife | Mandant aus dem Kopf, `tenant_id IS NULL` als „global“ fuer alle | Token; nur eigene Tarife (globale gab es live nicht, per API nicht anlegbar) |
| `POST /freight-cost/carrier-invoice` | doppelte Nummer still verworfen (`ON CONFLICT DO NOTHING`), **trotzdem gebucht** und eine nicht vorhandene Rechnung gemeldet; Tour nicht geprueft; Buchungsfehler liess die Transaktion abgebrochen; Status **„gebucht“ fuer einen Buchungsentwurf** | Tour im Mandanten (404), Nummer vorhanden 409, Buchungsentwurf im Savepoint, Status `entwurf` bzw. `offen` mit `buchungsfehler` |

## Schema

`domain_logistics.tours`, `tour_stops`, `tour_events`, `tour_disposition_checks`, `epod_settlements`, `freight_tariffs`,
`carrier_invoices`: getrennte Policies (kein `system`-Lesen), `tenant_id NOT NULL`, Vorgabe aus dem Kontext. Es gab
**keinen** Fremdschluessel zwischen Touren und ihren Kindern; jetzt Verbund-FKs Tour -> Stopps/Ereignisse/Checks
(CASCADE), Tour/Stopp -> ePOD-Abrechnung, Tour -> Spediteur-Rechnung (NO ACTION). Verwaiste oder fremde Verweise und
Zeilen ohne Mandant (bei Tarifen: „globale“) brechen ab. **Gewachsene DB:** 2 Touren, 2 Stopps, ein Mandant, keine
Waisen — kein Abbruchgrund.

## Nachweise

```
pytest tests/test_rls_domain_logistics.py -rs              -> 20 passed, 0 skipped
Gegenprobe alter Code + ohne Migration                      -> 20 rot
RLS-Suite + Fallback- + Identitaetsvertrag                 -> 588 passed
12 betroffene Bestandsmodule                               -> 106 passed, 1 rot (test_tourenplanung_definition, auf der Basis gleich rot)
   15 Tests schrieben das alte Verhalten fest (Kopf Pflicht -> 422, globale Tarife, 403 fuer fremde Tarife, x_tenant_id-Aufrufe)
   und sind auf Token-Mandant und 404 umgestellt
Inventar/Matrix/Systemlesen/Rollout regeneriert; Ausnahmen 84 -> 77; OpenAPI nur Logistik-Pfade
```

## Offen

- **Spediteur-Rechnung fachlich:** Konten (Aufwand, Kreditor, Vorsteuer) und Steuer kommen vom Client, nicht aus den
  Steuerschluesseln; gebucht wird sie nicht (Entwurf). Eigentlich ist sie eine Eingangsrechnung und gehoert ueber den
  Einkauf/Eingangsrechnungsweg mit Freigaberegeln (APPROVAL-001) gebucht.
- **Gemeinsame Frachttarife** (Mandant `system`) nur nach fachlicher Entscheidung.
- `domain_log.*` (Verladung) gehoert zu LOADING-ATOMIC-ACTOR.
