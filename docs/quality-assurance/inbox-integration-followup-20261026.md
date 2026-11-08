# Inbox integration follow-up 2026-10-26

Scope: delegated PENDING-INTEGRATION ownership in `artifacts/migration-repair-source` only. No root source, index, commit, database schema, migration or container changes.

## Verified

- Existing connector `app/integrations/dms_client.py:get_client` returns `httpx.Client`; it has no `get_bytes` method. Previous PDF helper guessed file-list routes absent from repository evidence.
- PDF retrieval now consumes only optional `download_url` advertised by the existing versions response. Uses `get`, `raise_for_status`, `Response.content`; accepts PDF signature only, rejects foreign origins and redirects, preserves OCR-text extraction on absent/error/non-PDF download. This is a transport contract, not live Mayan acceptance or a claim that every Mayan deployment advertises this field.
- Four actual httpx.MockTransport cases cover success, unavailable link, foreign origin, redirect/403/non-PDF and retained OCR table extraction.
- Original OCR training fixtures were not tracked in Git HEAD and absent from the delivery view. Self-contained synthetic fixtures in `tests/fixtures/dms_inbox` replace that private filesystem dependency. They establish parser contracts, not real supplier-document accuracy.
- Shared PostgreSQL status: existing `valeo_probe`, revision `loading_stop_fk_20261023`. Sandbox TCP restriction required approved execution outside sandbox. Tests use own rows and cleanup; no reset/DDL/database/container creation.
- Focused tenant/PDF run: 8 passed (4 tenant contracts, 4 PDF cases). Tenant checks cover both inbox adapters, read/write roles, connector tenant binding, retry status preservation and cross-tenant identity collision without overwrite.
- Existing queue/router contracts: 29 passed with normal conftest. Queue/prepare/approve remain preparation/blocking contracts, with no booking or processed mutation.

## Limits

No browser acceptance, live Mayan download acceptance or full CI/coverage claim. A first diagnostic narrow invocation used --noconftest together with repository-wide coverage defaults: 43 passed, five missing private-fixture failures and five missing require_db errors, then coverage below the global threshold. Follow-up runs explicitly select focused tests without claiming global coverage; the normal conftest router run passes all29.

## Generic parser completion

Lead explicitly extended ownership to `app/integrations/dms_parser.py` for generic deterministic positions. It now calls the existing shared table extractor (local import, no extractor-to-parser dependency). Optional LLM/PDF behavior stays in the inbox pipeline; the existing early return preserves parsed rows rather than extracting twice. No supplier rules, sample positions or private training data added. Regression checks empty document text does not create positions and subsequent inbox enrichment does not re-extract existing rows.

Final focused run before the two additional negative regressions: 48/48 passed (20 position cases including four PDF cases,24 contract cases,4 PostgreSQL tenant cases). Queue/router 5/5 separately passed as part of29/29 normal-conftest run. Final negative-regression rerun recorded below.

Final rerun: **50/50 passed**, including both new negative regressions; four tenant tests use PostgreSQL, remaining46 are isolated contracts/transport/parser cases. One existing Starlette/httpx deprecation warning. No tests removed/skipped; no global coverage/CI waiver claimed.
