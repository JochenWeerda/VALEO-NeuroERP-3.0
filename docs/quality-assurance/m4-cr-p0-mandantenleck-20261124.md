---
title: M4-CR-P0 Mandantenleck CRM
type: qa
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-11-24
version: 1.0.0
description: Abnahme der P0-Mandantenlecks an public.kunden, KIM, Lookup, 360-Fallback und Merge.
---

# M4-CR-P0 Mandantenleck CRM (2026-11-24)

## Befund

`public.kunden` und Satelliten (`kunden_lookup`, `kunden_crm360`, `kunden_ansprechpartner`)
haben keine `tenant_id`. Lookup, KIM und Merge lasen bzw. schrieben ueber `kunden_nr`
ohne Pruefung gegen den Token-Mandanten.

## Fix

Zentraler Helfer `app/core/public_kunden_mandant.py`: Zugehoerigkeit ueber
`business_partners.tenant_id` oder `domain_crm.customers.tenant_id`.

| Weg | Aenderung |
|-----|-----------|
| `BusinessPartnerService.search_lookup` | Filter `KUNDE_GEHOERT_MANDANT` |
| `crm_kim` Liste/Get/Update/Kontakte | Filter bzw. 404 vor Schreibweg |
| `crm_360_sql._kunde_finden` Fallback | nur mandantengeprueft; `tenant_id` Pflicht |
| `CrmMergeService._kunde` | nur mandantengeprueft |
| `CustomerService.get_from_db_any_key` Altbestand | nur mandantengeprueft |

## Abnahme

`tests/test_m4_cr_p0_mandantenleck.py` gegen valeo_probe: Lookup/KIM nur eigener Mandant;
Fremdmandant 404 bei Update/Kontakt/Merge; unverknuepfter Bestandskunde 404.
