"""Export OpenAPI spec from FastAPI app to docs/api/openapi.json."""

from __future__ import annotations

import json
from pathlib import Path

from main import app


if __name__ == "__main__":
    out = Path("docs/api/openapi.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    spec = app.openapi()
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"openapi exported: {out}")
