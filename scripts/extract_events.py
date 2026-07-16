"""Extrahiert NATS/Outbox-Event-IDs aus dem App-Code."""

import re
import json
from pathlib import Path

REPO = Path(__file__).parent.parent

events: dict[str, dict] = {}

# Pattern: outbox_event_type = "..."
P_OUTBOX = re.compile(r'outbox_event_type\s*=\s*["\']([^"\']+)["\']')
# Pattern: event_type = "..."  (nur sinnvolle dot-Namen)
P_EVENT = re.compile(r'event_type\s*=\s*["\']([a-z][a-z0-9_\.]+)["\']')
# Pattern: subject_pattern="tenant.*.xxx"
P_SUBJECT = re.compile(r'subject_pattern\s*=\s*f?["\']([^"\']+)["\']')

DOMAIN_MAP = {
    "inventory": "Lager / Materialfluss",
    "procurement": "Einkauf",
    "purchase_order": "Einkauf",
    "goods_receipt": "Einkauf",
    "service_entry_sheet": "Einkauf",
    "pos": "POS / Kasse",
    "portal_order": "Portal",
    "crm": "CRM",
    "lager": "Lager",
    "lkw": "Logistik",
    "route": "Logistik",
    "silo": "Agrar / Silo",
    "qs": "Qualitätssicherung",
    "qualitaets": "Qualitätssicherung",
    "ration": "Tierernährung",
    "feeding": "Tierernährung",
    "harvest": "Agrar",
    "agrar": "Agrar",
    "payment": "Finanzbuchhaltung",
    "docflow": "Dokumentenfluss",
    "field_service": "Außendienst",
    "tenant": "System",
    "workflow": "Workflow",
    "ap_invoice": "Finanzbuchhaltung",
    "audit": "Compliance",
    "sla": "Betrieb",
    "command": "System",
    "e2e_chain": "Qualitätssicherung",
    "agrar_settlement": "Agrar",
    "duenge_bilanz": "Agrar",
}


def get_domain(event_id: str) -> str:
    for prefix, domain in DOMAIN_MAP.items():
        if event_id.startswith(prefix) or event_id.replace(".", "_").startswith(prefix):
            return domain
    return "Sonstige"


def _py_files(root: Path):
    for d in ["app", "modules", "scripts"]:
        p = root / d
        if p.exists():
            yield from p.rglob("*.py")


for f in sorted(_py_files(REPO)):
    if "test" in f.parts or "__pycache__" in f.parts:
        continue
    try:
        src = f.read_text(encoding="utf-8", errors="replace")
        rel = str(f.relative_to(REPO)).replace("\\", "/")

        for m in P_OUTBOX.finditer(src):
            eid = m.group(1)
            if eid not in events:
                events[eid] = {
                    "id": eid,
                    "source": rel,
                    "domain": get_domain(eid),
                    "channel": "outbox",
                }

        for m in P_EVENT.finditer(src):
            eid = m.group(1)
            if "." in eid and eid not in events:
                events[eid] = {
                    "id": eid,
                    "source": rel,
                    "domain": get_domain(eid),
                    "channel": "outbox",
                }

        for m in P_SUBJECT.finditer(src):
            eid = m.group(1).strip()
            if eid and eid not in events:
                events[eid] = {
                    "id": eid,
                    "source": rel,
                    "domain": get_domain(eid),
                    "channel": "nats",
                }
    except Exception:
        pass

result = sorted(events.values(), key=lambda e: (e["domain"], e["id"]))
print(f"Gefunden: {len(result)} Events")
for e in result[:5]:
    print(f"  {e['domain']:30s} {e['id']}")
print("  ...")
out = REPO / "events_raw.json"
json.dump(result, out.open("w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Geschrieben: {out}")
