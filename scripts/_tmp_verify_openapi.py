import json
from pathlib import Path

paths = json.loads((Path("docs/schnittstellen/openapi.json")).read_text(encoding="utf-8"))["paths"]
GET = {p for p, s in paths.items() if "get" in s}

candidates = [
    "/api/v1/dms/inbox",
    "/api/v1/crm/bestell-inbox",
    "/api/v1/crm/kim/capture-inbox",
    "/api/v1/finance/ap/invoices/",
    "/api/v1/operations/exceptions",
    "/api/v1/audit/logs",
    "/api/v1/audit/stats",
    "/api/v1/compliance/sanctions/eintraege",
    "/api/v1/compliance/pcn-meldungen",
    "/api/v1/annahme/warteschlange",
    "/api/v1/workflow/executions",
    "/api/v1/docflow/evidence/wiedervorlagen",
    "/api/v1/docflow/evidence/gobd-export",
    "/api/v1/docflow/evidence/documents",
    "/api/v1/docflow/evidence/artifacts",
    "/api/v1/jobs",
    "/api/v1/agrar/quality-protocols",
    "/api/v1/sales/credit-check/customers",
    "/api/v1/export/list",
    "/api/v1/process/background-jobs/queue",
    "/api/v1/process/approval-density/overview",
    "/api/v1/futtermittel/qs/kontrollen",
    "/api/v1/compliance/export/lot-trace",
    "/api/v1/procurement/audit-trail",
    "/api/v1/mobile/sync-summary",
]

for c in candidates:
    ok = c in GET or (c.rstrip("/") + "/") in GET or c.rstrip("/") in GET
    print("OK" if ok else "MISS", c)
