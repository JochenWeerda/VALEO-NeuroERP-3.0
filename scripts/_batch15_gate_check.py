import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.screen_definitions import get_screen_definition
from app.core.screen_definitions_domain_batch15 import BATCH15_SCREEN_BUILDERS
from app.services.made_by_studio_gates import (
    check_gate_a,
    check_gate_b,
    check_gate_c,
    check_gate_e,
)

failed: dict[str, list[str]] = {}
for sid in sorted(BATCH15_SCREEN_BUILDERS):
    defn = get_screen_definition(sid)
    if defn is None:
        failed.setdefault(sid, []).append("no_definition")
        continue
    for gate, fn in (
        ("A", lambda d: check_gate_a(d)),
        ("B", lambda d: check_gate_b(d)),
        ("C", lambda d: check_gate_c(d, screen_id=sid)),
        ("E", lambda d: check_gate_e(sid)),
    ):
        res = fn(defn)
        if not res.passed:
            failed.setdefault(sid, []).extend([f"{gate}:{i}" for i in res.issues])

print("batch15 screens", len(BATCH15_SCREEN_BUILDERS))
print("gate failures", len(failed))
for sid, issues in list(failed.items())[:15]:
    print(sid, issues[:4])
