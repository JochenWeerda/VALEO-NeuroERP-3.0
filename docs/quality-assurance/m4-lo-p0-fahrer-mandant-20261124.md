---
title: M4-LO-P0 Fahrer-Mandantenleck
type: qa
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-11-24
version: 1.0.0
description: Nachweis Mandantenfilter ops_fahrer / transporte.py (LO-02).
---

# M4-LO-P0 — Fahrer Mandantenleck

## Befund

`domain_ops.ops_fahrer` hatte keine `tenant_id`. `GET/POST/PATCH/DELETE /api/v1/transporte/fahrer`
fragte `db.query(Fahrer)` ohne Filter ab — jeder Mandant sah und aenderte alle Fahrer
(personenbezogene Daten).

## Fix

- Migration `ops_fahrer_tenant_20261124`: Spalte `tenant_id`, Rueckfuellung aus Fahrzeug/Tour,
  Unique `(tenant_id, personalnummer)`, RLS.
- `FahrerRepository` verlangt Mandant und filtert immer.
- `transporte.py` nutzt `get_tenant_id` und das Repository.

## Abnahme

```bash
export PGAPPNAME=agent:cursor-m4-lo-p0
export TEST_DATABASE_URL=postgresql://…/valeo_probe
alembic upgrade head
pytest tests/test_m4_lo_p0_fahrer_mandant.py --no-cov -q
```

Erwartung: Liste nur eigener Mandant; Fremd-GET/PATCH/DELETE 404; Create setzt `tenant_id`.
