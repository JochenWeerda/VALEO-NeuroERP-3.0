import json
from pathlib import Path

m = json.loads(Path("docs/benutzerhandbuch/screenshot-manifest.json").read_text(encoding="utf-8"))
img = Path("docs/benutzerhandbuch/img")
pending = [e for e in m["entries"] if e.get("approval") == "pending"]
missing = []
rejected_no_file = []
for e in m["entries"]:
    slug = e["slug"]
    has = (img / f"{slug}.webp").exists() or (img / f"{slug}.png").exists()
    if not has:
        missing.append(e)
        if e.get("approval") == "rejected":
            rejected_no_file.append(e)
print(f"pending={len(pending)} missing_file={len(missing)} rejected_no_file={len(rejected_no_file)}")
for e in missing:
    print(f"  MISSING {e['slug']} approval={e.get('approval')} path={e.get('path')}")
