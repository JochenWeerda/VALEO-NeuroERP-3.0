import json
import runpy
from pathlib import Path

m = runpy.run_path("tools/apply_batch11_listen_migration.py")
BATCH11 = m["BATCH11"]
openapi = json.loads(Path("docs/schnittstellen/openapi.json").read_text(encoding="utf-8"))
GET_PATHS = {p for p, spec in openapi.get("paths", {}).items() if "get" in spec}
for page, screen_id, route_path, spec in BATCH11:
    base = spec["endpoint"].split("?", 1)[0]
    if base not in GET_PATHS:
        alt = base.rstrip("/") + "/" if not base.endswith("/") else base.rstrip("/")
        if alt not in GET_PATHS:
            print("FAIL", page, spec["endpoint"])
print("done")
