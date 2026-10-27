---
title: QA RLS-DOMAIN-CRM-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: RLS-Domain CRM (Geschäftspartner und Details, Kontakte, Segmente, Chancen, Protokolle) ohne Dienst-Tabellen auf valeo_probe abgenommen.
---

# QA RLS-DOMAIN-CRM-20261027

**Basis:** `claude/rls-domain-sales-20261027` (#75, getestet 6c6ee52f0).
Migration `rls_domain_crm_20261027` folgt auf `rls_domain_sales_20261027`. `alembic heads` zeigt
einen einzigen Head.

**Status:** abgeschlossen. Codex hatte das Prüfstandsfenster freigegeben
(RLS-GESAMTABNAHME-20261027). `valeo_probe` stand vorher und nachher auf
`loading_stop_fk_20261023`, 0 fremde Sitzungen.

**Nicht enthalten:** die Tabellen der Dienste unter `services/*` (activities, customers, farm_profiles,
leads, crm_activities, crm_leads, crm_opportunities). Diese Dienste prüfen das Token noch nicht selbst.
Ihre Tabellen kommen nach der Token-Prüfung (Nutzerentscheidung Option A,
`docs/architecture/rls-dienste-identitaet-vorschlag.md`).

## Analyse CRM

| Tabelle | Befund | Entscheidung |
|---|---|---|
| `domain_crm.business_partners` (A) | live 7 Zeilen, alle mit eigenem Mandanten; Schreiber tokengebunden; einziger Standardmandant in `customer_service._adapt_customer` (nur Antwortfeld) | getrennt, kein `system`; `UNIQUE (partner_id, tenant_id)` |
| 15 `business_partner_*` (C) | Mandant nur am Partner; live 0 Zeilen | `tenant_id` vom Partner, NOT NULL, Default aus dem Kontext, Verbund-FK, ON DELETE wie bisher |
| `domain_crm.supplier_tax_profiles` (P5) | schon unter RLS, einfacher FK auf den Partner | nur Verbund-FK, Policies unverändert |
| `domain_crm.credit_limits`, `crm_segments` (A) | Schreiber tokengebunden (`credit_management.py`, `app/crm/router.py` nach Korrektur) | getrennt |
| `crm_segment_members`, `crm_contact_consent_history` (C) | Mandant am Segment bzw. an der Einwilligung (`crm_contact_consents`, P5) | `tenant_id` vom Eltern, Verbund-FK (CASCADE wie bisher) |
| `public.crm_contacts`, `crm_betriebsprofile` (A) | **Fachbefund:** `app/crm/router.py` (live über `main.py`) nahm den Mandanten aus dem Kopf `X-Tenant`, ohne Kopf `"default"`. 39 Wege, darunter Kontakte, Betriebsprofile, Chancen, Einwilligungen, Segmente | Router nutzt `app.core.tenant.get_tenant_id`; Verbund-FK Betriebsprofil → Kontakt |
| `domain_crm.cancellation_reason`, `opportunity` (B, nur frisch) | ohne Schreiber; Verweis Chance → Absagegrund einfach | NOT NULL, getrennt, Verbund-FK |
| `public.crm_merge_log`, `crm_ownership_log`, `opportunities` (B) | live 0 Zeilen; Merge/Ownership fielen ohne Mandant auf die Standard-UUID zurück, die Historie las mandantenübergreifend | NOT NULL, getrennt; Dienste verlangen den Mandanten, Historie mit Mandantenfilter |

## Fachkorrekturen

- **`app/crm/router.py`:** eigener `get_tenant_id` (Kopf `X-Tenant`, Rückfall `"default"`) entfernt, ersetzt durch
  den Token-Mandanten. Ohne Token antwortet der Router mit 401/403. Der Vertragstest
  `test_system_tenant_fallback_contract.py` erfasst jetzt auch Parameter namens `x_tenant`; die alte Fassung macht ihn rot.
- **DSGVO-Auskunft `/crm/gdpr/data-export`** las `domain_shared.business_partners`. Diese Tabelle gibt es in keiner
  Datenbank, die Auskunft endete mit 500. Jetzt liest sie `domain_crm.business_partners` mit Mandantenfilter (fremd 404).
  Optionale Quellen laufen im Savepoint.
- **DSGVO-Kurzweg `/crm/gdpr/anonymize`** schrieb in dieselbe fehlende Tabelle ohne Mandanten. Er schluckte den Fehler,
  die Transaktion war tot, und die Antwort meldete „anonymisiert“, ohne dass ein Datensatz geändert war. Jetzt antwortet
  er mit 409 und verweist auf den protokollierten Löschantrag `POST /api/v1/compliance/dsgvo/erasure-requests`.
  Kein Frontend ruft den Kurzweg auf.
- **`crm_merge_service.py`, `crm_ownership_service.py`:** kein Rückfall auf die Standard-UUID; ohne Mandant `ValueError`.
  Die Ownership-Historie filtert nach Mandant.
- **`customer_service._adapt_customer`:** Mandant des Aufrufers statt `settings.DEFAULT_TENANT_ID`.
- **`app/crm/seed.py`, `scripts/seed-all-domains.py`:** keine Vorgabe `"default"`; das Skript verlangt `SEED_TENANT_ID`.
  Eingefrorene Rückfälle auf `"default"`: −1 (`app/crm/seed.py` aus der Baseline).

## Nachweise

```
pytest tests/test_rls_domain_crm.py -rs    -> 58 passed, 0 skipped (valeo_app, zurückgerollt)
Gegenprobe mit alten Einzel-FKs             -> 21 rot
Vertrag x_tenant mit alter router.py        -> rot ({'app/crm/router.py': (1, 0)})
RLS-Gesamtsuite + Fallback-Vertrag          -> 331 passed, 0 skipped
100 CRM-/Partner-/Kunden-/OpenAPI-Bestandsmodule (conftest, Prüfstand)
                                             -> 2788 passed; 22 rot wie auf der Basis #75 (0 neu rot)
Inventar/Rollout/Matrix regeneriert, generate_code_inventories.py --check -> OK
```

| Abnahmekriterium | Test |
|---|---|
| Mandantengrenze je Tabelle (eigen ok; fremd und `system` SELECT/INSERT/UPDATE/DELETE gesperrt; kein `tenant_id`-Wechsel; fail-closed) | `test_mandantengrenze_je_tabelle` (28) |
| kein Kind unter fremdem Eltern, auch nicht umgehängt | `test_kein_kind_unter_fremdem_eltern` (20) |
| Kind erbt den Mandanten aus dem Kontext | `test_kind_erbt_den_mandanten_vom_kontext` |
| Eltern mit Kindern behalten ihren Mandanten | `test_eltern_mit_kindern_behaelt_seinen_mandanten` |
| Kontextwechsel/Savepoint, Hintergrund, Pool | `test_kontextwechsel_savepoint_hintergrund_pool` |
| Fachkette: Kontakte nur eigen, fremder Kontakt 404, DSGVO-Auskunft eigen ja / fremd 404 | `test_fachkette_crm_router_nur_eigener_mandant` |
| Router ohne Token: Kopf `X-Tenant` genügt nicht | `test_crm_router_nimmt_den_mandanten_aus_dem_token` |
| DSGVO-Kurzweg meldet keinen Schein-Erfolg | `test_dsgvo_kurzweg_meldet_keinen_schein_erfolg` |
| Merge/Ownership ohne Standardmandant | `test_crm_dienste_ohne_standardmandant` (4) |
| Policy-Formen | `test_policy_formen` |

Die 22 vorbestehenden Fehlschläge liegen in Studio-, Masken- und Meridian-Verträgen
(`test_studio_listen_kommandos` 14, `test_meridian_beleg_systemweit` 4, `test_mask_studio_inventory` 2,
je 1 in `test_neuro_tool_execution` und `test_stammdaten_bearbeiten`). Sie sind mit und ohne diesen Slice gleich rot.

Inventar: 154 zurückgestellt (−27).

## Verbleibend / vor Live-Aktivierung

- **Kundenstamm `public.kunden`, `kunden_crm360`, `kunden_adressen` (Klasse D, ohne Mandant):** Merge und Ownership lesen und
  ändern ihn mandantenübergreifend. Er braucht eine eigene Mandantenentscheidung.
- **DSGVO-Löschantrag** (`compliance_dsgvo._anonymize_subject`) anonymisiert `domain_crm.customers` und `crm_customers`,
  aber nicht `domain_crm.business_partners`. Das ist ein eigener Fachslice.
- **Weitere Verweise auf `business_partners`:** `domain_inventory.harvest_acceptances` (Spediteur, Zwischenhändler) und
  `article_suppliers` haben einfache FKs. Sie folgen mit der Domain inventory.
- **`cancellation_reason.cancel_reason_id`** ist systemweit eindeutig, nicht je Mandant. Der Verbund-FK greift trotzdem.
  Umstellung erst, wenn es einen Schreiber gibt.
- **`business_partner_communities`** (Klasse D, 0 Zeilen, kein Schreiber) bleibt mandantenlos.
- **Masken:** Geschäftspartner, Kontakte, Segmente und Einwilligungen mit zwei Mandanten prüfen.
  Die Maskenabnahme liegt bei Codex.
