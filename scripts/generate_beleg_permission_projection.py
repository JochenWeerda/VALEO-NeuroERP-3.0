"""Generate mask permission metadata from the authoritative document role policy."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "packages/frontend-web/src/components/mask-builder/runtime/beleg-permissions.generated.json"


def render() -> str:
    from app.auth.beleg_roles import RECHTE, rollen_fuer
    from app.core.belegvertrag import BELEGARTEN
    return json.dumps({
        "schemaVersion": 1, "source": "app/auth/beleg_roles.py",
        "screens": {"beleg/" + art.replace("_", "-"): {
            "belege." + right: sorted(rollen_fuer(right, art)) for right in RECHTE
        } for art in sorted(BELEGARTEN)},
    }, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != expected:
            print("Document mask permission projection drift; regenerate it.")
            return 1
        print("Document mask permission projection current.")
    else:
        OUT.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
