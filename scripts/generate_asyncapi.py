"""Generiert AsyncAPI 2.6 Spec + MkDocs-Seite aus extrahierten Events.

Verwendung:
    python scripts/generate_asyncapi.py

Liest events_raw.json aus dem Repo-Root (erzeugt von scripts/extract_events.py).
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import date

REPO = Path(__file__).parent.parent
events_file = REPO / "events_raw.json"

# Automatisch extrahieren wenn nicht vorhanden
if not events_file.exists():
    subprocess.run(
        [sys.executable, str(REPO / "scripts" / "extract_events.py")], check=True
    )

events = json.loads(events_file.read_text(encoding="utf-8"))


# ── AsyncAPI 2.6 YAML ─────────────────────────────────────────────────────────
def yaml_str(s: str) -> str:
    if any(c in s for c in [":", "#", "{", "}"]):
        return f'"{s}"'
    return s


lines = [
    "asyncapi: '2.6.0'",
    "info:",
    "  title: VALEO NeuroERP Event-Katalog",
    "  version: '3.0.0'",
    "  description: >",
    "    NATS JetStream / Transactional-Outbox Events für VALEO NeuroERP 3.0.",
    "    Generiert via scripts/generate_asyncapi.py.",
    f"  x-generated: '{date.today().isoformat()}'",
    "",
    "servers:",
    "  production:",
    "    url: nats://nats:4222",
    "    protocol: nats",
    "    description: NATS JetStream (Production)",
    "  development:",
    "    url: nats://localhost:4222",
    "    protocol: nats",
    "    description: NATS JetStream (Development)",
    "",
    "defaultContentType: application/json",
    "",
    "channels:",
]

for ev in events:
    eid = ev["id"]
    domain = ev["domain"]
    channel = ev.get("channel", "outbox")
    # NATS subject: tenant.{tenantId}.<event_id> oder direkt <event_id>
    if channel == "nats" and "*" in eid:
        subject = eid
    else:
        subject = f"tenant.{{tenantId}}.{eid}"

    lines += [
        f"  {yaml_str(subject)}:",
        "    description: >",
        f"      [{domain}] {eid.replace('.', ' ').replace('_', ' ').title()}",
        "    subscribe:",
        f"      summary: {yaml_str(eid)}",
        f"      operationId: on_{eid.replace('.', '_').replace('-', '_').replace('*', 'any')}",
        "      message:",
        f"        $ref: '#/components/messages/{eid.replace('.', '_').replace('-', '_').replace('*', 'any').replace('{', '').replace('}', '')}Event'",
        "",
    ]

lines += [
    "components:",
    "  messages:",
]
for ev in events:
    eid = ev["id"]
    key = (
        eid.replace(".", "_")
        .replace("-", "_")
        .replace("*", "any")
        .replace("{", "")
        .replace("}", "")
    )
    message_lines = [
        f"  {key}Event:",
        f"    name: {yaml_str(eid)}",
        f"    title: {eid.replace('.', ' ').replace('_', ' ').title()}",
        "    contentType: application/json",
        "    payload:",
        "      type: object",
    ]
    if eid.startswith("feeding."):
        message_lines += [
            "      required: [schema_version, event_id, event_type, aggregate_id, timestamp, payload]",
            "      properties:",
            "        schema_version:",
            "          type: string",
            "          const: '1.0'",
            "        event_id:",
            "          type: string",
            "          format: uuid",
            "        event_type:",
            "          type: string",
            f"          const: {eid}",
            "        aggregate_id:",
            "          type: string",
            "        timestamp:",
            "          type: string",
            "          format: date-time",
            "        payload:",
            "          type: object",
            "          description: Referenzorientierte fachliche Nutzdaten",
            "",
        ]
    else:
        message_lines += [
            "      required: [event_id, tenant_id, occurred_at, payload]",
            "      properties:",
            "        event_id:",
            "          type: string",
            "          format: uuid",
            "        tenant_id:",
            "          type: string",
            "        occurred_at:",
            "          type: string",
            "          format: date-time",
            "        correlation_id:",
            "          type: string",
            "        payload:",
            "          type: object",
            "          description: Fachliche Nutzdaten je Event-Typ",
            "",
        ]
    lines += message_lines

asyncapi_path = REPO / "docs/schnittstellen/asyncapi.yaml"
asyncapi_path.write_text("\n".join(line.rstrip() for line in lines), encoding="utf-8")
print(f"Geschrieben: {asyncapi_path} ({len(events)} Channels)")

# ── MkDocs-Seite ──────────────────────────────────────────────────────────────
by_domain: dict[str, list] = {}
for ev in events:
    by_domain.setdefault(ev["domain"], []).append(ev)

md_lines = [
    "---",
    "title: Event-Katalog (NATS / Outbox) — generiert",
    "description: Maschinenlesbar generierter AsyncAPI-Event-Katalog für VALEO NeuroERP 3.0.",
    "type: reference",
    "audience: [integrator, entwickler]",
    "owner: Claude Code",
    "status: aktiv",
    f"last_reviewed: {date.today().isoformat()}",
    "version: 3.0.0",
    "---",
    "",
    "# Event-Katalog (NATS / Outbox)",
    "",
    "> Maschinenlesbare Quelle: [`docs/schnittstellen/asyncapi.yaml`](asyncapi.yaml)  ",
    "> Generiert via `scripts/generate_asyncapi.py`",
    "",
    "VALEO NeuroERP publiziert fachliche Domänen-Events über das **Transactional Outbox Pattern**:",
    "Events werden atomar mit der fachlichen Änderung persistiert und über **NATS JetStream** ausgeliefert.",
    "",
    "## Namenskonvention",
    "",
    "```",
    "tenant.{tenantId}.<domäne>.<aggregat>.<aktion>",
    "```",
    "",
    "## Zustellgarantien",
    "",
    "| Eigenschaft | Wert |",
    "|---|---|",
    "| Zustellung | At-least-once (Konsumenten müssen idempotent sein) |",
    "| Transaktionalität | Outbox-Pattern: Event + Datenänderung atomar |",
    "| Mandantentrennung | Jedes Event trägt `tenant_id` |",
    "| Korrelation | `correlation_id` für verteiltes Tracing |",
    "",
]

for domain in sorted(by_domain):
    md_lines += [f"## {domain}", "", "| Event | Kanal | Quelle |", "|---|---|---|"]
    for ev in sorted(by_domain[domain], key=lambda e: e["id"]):
        src = ev["source"].replace("app/", "")
        md_lines.append(f"| `{ev['id']}` | {ev['channel']} | `{src}` |")
    md_lines.append("")

md_lines += [
    "## AsyncAPI-Spec",
    "",
    "Die maschinenlesbare Spec im AsyncAPI 2.6 Format:",
    "",
    "```yaml",
    "# docs/schnittstellen/asyncapi.yaml",
    "asyncapi: '2.6.0'",
    "info:",
    "  title: VALEO NeuroERP Event-Katalog",
    "  version: '3.0.0'",
    "# ... (vollständige Spec in asyncapi.yaml)",
    "```",
    "",
    f"*Stand: {date.today().isoformat()} · {len(events)} Events · Slice: DOC-ASYNCAPI-001*",
]

events_md_path = REPO / "docs" / "schnittstellen" / "events.md"
events_md_path.write_text("\n".join(line.rstrip() for line in md_lines), encoding="utf-8")
print(f"Geschrieben: {events_md_path}")
