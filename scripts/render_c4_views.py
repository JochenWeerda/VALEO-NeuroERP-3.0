#!/usr/bin/env python3
"""Render C4 Context/Container Markdown from Structurizr workspace.dsl.

Ausgabe:
  - docs/architecture/views/c4-01-system-context.md
  - docs/architecture/views/c4-02-containers.md

Verwendung:
    python scripts/render_c4_views.py
    python scripts/render_c4_views.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DSL_PATH = REPO_ROOT / "docs" / "architecture" / "c4" / "workspace.dsl"
OUTPUTS = {
    "context": REPO_ROOT / "docs" / "architecture" / "views" / "c4-01-system-context.md",
    "containers": REPO_ROOT / "docs" / "architecture" / "views" / "c4-02-containers.md",
}

GENERATED_BANNER = (
    "> **Generierte View** — Quelle: [`docs/architecture/c4/workspace.dsl`]"
    " · Renderer: `python scripts/render_c4_views.py` · **Nicht manuell editieren.**"
)

PRODUCTION_MERMAID = """```mermaid
C4Container
  title Container — VALEO NeuroERP (Production)

  Person(user, "Nutzer", "Browser")

  Container_Boundary(prod, "Production") {
    Container(fe_prod, "frontend", "Nginx/React", "Static + Proxy")
    Container(app, "valeo-app", "FastAPI", "Monolith API")
    Container(inv_p, "inventory-service", "FastAPI", "Lager MS")
  }

  Container_Boundary(infra_p, "Infrastruktur") {
    ContainerDb(pg_p, "postgres", "PostgreSQL", "ERP DB")
    Container(redis_p, "redis", "Redis", "Cache")
    Container(nats_p, "nats", "NATS", "Events")
    Container(kc_p, "keycloak", "Keycloak", "OIDC")
    Container(prom, "prometheus", "Prometheus", "Metriken")
    Container(graf, "grafana", "Grafana", "Dashboards")
    Container(loki_p, "loki", "Loki", "Logs")
  }

  Rel(user, fe_prod, "HTTPS")
  Rel(fe_prod, app, "Proxy /api")
  Rel(app, pg_p, "SQL")
  Rel(app, redis_p, "Cache")
  Rel(app, nats_p, "Events")
  Rel(app, inv_p, "HTTP")
  Rel(app, kc_p, "JWT")
  Rel(prom, app, "Scrape")
  Rel(graf, prom, "Query")
  Rel(loki_p, app, "Logs")
```"""


@dataclass
class Element:
    var_id: str
    kind: str
    name: str
    description: str = ""
    technology: str = ""
    tags: set[str] = field(default_factory=set)
    parent: str | None = None


@dataclass
class Relationship:
    source: str
    target: str
    label: str


@dataclass
class DslModel:
    elements: dict[str, Element] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)
    root_system: str | None = None


def _sanitize_mermaid_id(var_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", var_id)


def parse_dsl(text: str) -> DslModel:
    model = DslModel()
    lines = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("!"):
            continue
        lines.append(raw)

    block = "\n".join(lines)
    block = re.sub(r"//.*", "", block)
    block = re.sub(r"/\*.*?\*/", "", block, flags=re.DOTALL)

    stack: list[str] = []
    tag_re = re.compile(r'tags\s+"([^"]+)"')
    assign_re = re.compile(
        r"^(\w+)\s*=\s*(person|softwareSystem|container)\s+"
        r'"([^"]*)"(?:\s+"([^"]*)")?(?:\s+"([^"]*)")?\s*\{?\s*$'
    )
    rel_re = re.compile(r"^(\w+)\s*->\s*(\w+)\s+" r'"([^"]*)"\s*$')

    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped in {"workspace", "model", "views", "}"}:
            continue
        if stripped.startswith("workspace ") or stripped.startswith("systemContext ") or stripped.startswith("container "):
            continue
        if stripped.startswith("include ") or stripped.startswith("autolayout "):
            continue

        if stripped == "{":
            continue
        if stripped.startswith("}"):
            if stack:
                stack.pop()
            continue

        tag_match = tag_re.match(stripped)
        if tag_match and stack:
            parent_id = stack[-1]
            if parent_id in model.elements:
                model.elements[parent_id].tags.add(tag_match.group(1))
            continue

        assign_match = assign_re.match(stripped)
        if assign_match:
            var_id, kind, name, second, third = assign_match.groups()
            desc = ""
            tech = ""
            if kind == "container":
                tech = second or ""
                desc = third or ""
            else:
                desc = second or ""
            parent = stack[-1] if stack else None
            opens_block = stripped.endswith("{")
            model.elements[var_id] = Element(
                var_id=var_id,
                kind=kind,
                name=name,
                description=desc,
                technology=tech,
                parent=parent,
            )
            if kind == "softwareSystem" and parent is None and "External" not in model.elements[var_id].tags:
                if model.root_system is None or name.startswith("VALEO"):
                    model.root_system = var_id
            if opens_block:
                stack.append(var_id)
            continue

        rel_match = rel_re.match(stripped)
        if rel_match:
            model.relationships.append(
                Relationship(rel_match.group(1), rel_match.group(2), rel_match.group(3))
            )

    return model


def _is_external(el: Element) -> bool:
    return "External" in el.tags or (
        el.kind == "softwareSystem" and el.parent is None and el.var_id != "valeo"
    )


def render_context_mermaid(model: DslModel) -> str:
    root = model.root_system or "valeo"
    lines = [
        "```mermaid",
        "C4Context",
        "  title System Context — VALEO NeuroERP 3.0",
        "",
    ]

    for el in model.elements.values():
        if el.kind != "person":
            continue
        mid = _sanitize_mermaid_id(el.var_id)
        lines.append(f'  Person({mid}, "{el.name}", "{el.description}")')

    root_el = model.elements.get(root)
    if root_el:
        lines.append(f'  System({root}, "{root_el.name}", "{root_el.description}")')

    for el in model.elements.values():
        if el.kind != "softwareSystem" or el.var_id == root:
            continue
        if not _is_external(el):
            continue
        mid = _sanitize_mermaid_id(el.var_id)
        lines.append(f'  System_Ext({mid}, "{el.name}", "{el.description}")')

    lines.append("")
    for rel in model.relationships:
        src = model.elements.get(rel.source)
        tgt = model.elements.get(rel.target)
        if not src or not tgt:
            continue
        if src.kind == "container" or tgt.kind == "container":
            continue
        lines.append(f'  Rel({rel.source}, {rel.target}, "{rel.label}")')

    lines.append("```")
    return "\n".join(lines)


def render_container_mermaid(model: DslModel) -> str:
    root = model.root_system or "valeo"
    root_el = model.elements.get(root)
    title_name = root_el.name if root_el else "VALEO NeuroERP"

    app_containers: list[Element] = []
    infra_containers: list[Element] = []

    infra_names = {"postgres", "redis", "nats", "keycloak", "paperless"}

    for el in model.elements.values():
        if el.kind != "container" or el.parent != root:
            continue
        if "Database" in el.tags or el.name in infra_names or "PostgreSQL" in el.technology:
            infra_containers.append(el)
        else:
            app_containers.append(el)

    lines = [
        "```mermaid",
        "C4Container",
        f"  title Container — {title_name} (docker-compose dev)",
        "",
        '  Person(user, "Nutzer", "Browser / Mobile")',
        "",
        f'  Container_Boundary({root}, "{title_name}") {{',
    ]

    for el in app_containers:
        mid = _sanitize_mermaid_id(el.var_id)
        tech = el.technology or "—"
        lines.append(f'    Container({mid}, "{el.name}", "{tech}", "{el.description}")')

    lines.append("  }")
    lines.append("")
    lines.append('  Container_Boundary(infra, "Infrastruktur") {')

    for el in infra_containers:
        mid = _sanitize_mermaid_id(el.var_id)
        tech = el.technology or "—"
        kind = "ContainerDb" if "PostgreSQL" in tech or "Database" in el.tags else "Container"
        lines.append(f'    {kind}({mid}, "{el.name}", "{tech}", "{el.description}")')

    lines.append("  }")
    lines.append("")
    lines.append('  System_Ext(ext, "Externe Systeme", "DATEV, ELSTER, L3, …")')
    lines.append("")

    for rel in model.relationships:
        src = model.elements.get(rel.source)
        tgt = model.elements.get(rel.target)
        if not src or not tgt:
            continue
        if src.kind == "person" and tgt.kind == "container":
            lines.append(f'  Rel({rel.source}, {rel.target}, "{rel.label}")')
        elif src.kind == "container" and tgt.kind == "container":
            lines.append(f'  Rel({rel.source}, {rel.target}, "{rel.label}")')
        elif src.kind == "container" and tgt.kind == "softwareSystem" and _is_external(tgt):
            lines.append(f'  Rel({rel.source}, ext, "{rel.label}")')

    if not any("Rel(user," in ln for ln in lines) and app_containers:
        first = _sanitize_mermaid_id(app_containers[0].var_id)
        lines.append(f'  Rel(user, {first}, "HTTPS")')

    if not any("Rel(backend, ext" in ln for ln in lines):
        if any(e.var_id == "backend" for e in app_containers):
            lines.append('  Rel(backend, ext, "Integrationen")')

    lines.append("```")
    return "\n".join(lines)


def build_context_doc(mermaid: str) -> str:
    today = date.today().isoformat()
    return f"""---
title: C4 — System Context
type: explanation
audience: [entwickler, integrator, architect]
owner: Cursor
status: aktiv
last_reviewed: {today}
version: 1.1.0
description: C4 Level 1 — VALEO NeuroERP im Zusammenspiel mit Nutzern und externen Systemen.
---

# C4 — System Context (Level 1)

{GENERATED_BANNER}

VALEO NeuroERP als **Software-System** in seiner Umgebung. Stand: Dev-Stack + dokumentierte Integrationen.

{mermaid}

## Externe Systeme — Detailreferenzen

| System | Dokumentation |
|---|---|
| DATEV | [process-map § FiBu](../process-map.md), [fin-001 Workflow](../../workflows/fin-001-finance-to-reporting.md) |
| ELSTER | [Open Gaps VALEO-FIBU-006](../../project-context/open-gaps-and-known-issues.md) |
| Fiskaly/TSE | [POS Fiscalization](../pos-fiscalization-providers.md) |
| Paperless/DMS | [dms-paperless-integration.md](../dms-paperless-integration.md) |
| Keycloak | [Deployment](../../admin/deployment.md), [ADR-032](../../adr/adr-032-auth-enforcement-router-global-dependency.md) |
| L3 | [Open Gaps L3-*](../../project-context/open-gaps-and-known-issues.md) |
| Superglue | [superglue-integration-bewertung.md](../superglue-integration-bewertung.md) |
| Integration allgemein | [ADR-014](../../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md) |

## Nächste Zoom-Stufe

→ [C4 Container (Level 2)](c4-02-containers.md)
"""


def build_containers_doc(mermaid: str) -> str:
    today = date.today().isoformat()
    return f"""---
title: C4 — Container
type: explanation
audience: [entwickler, betrieb]
owner: Cursor
status: aktiv
last_reviewed: {today}
version: 1.1.0
description: C4 Level 2 — Deploybare Container aus docker-compose.yml (Dev) und docker-compose.production.yml (Prod/Observability).
---

# C4 — Container (Level 2)

{GENERATED_BANNER}

Deploybare Anwendungs- und Infrastruktur-Container. **Quelle der Wahrheit (Modell):** [`workspace.dsl`](../c4/workspace.dsl) · **Compose:** [`docker-compose.yml`](../../../docker-compose.yml) — abgeglichen via [Container-Inventar](../../entwickler/container-inventory.md).

{mermaid}

## Container-Gruppen

| Gruppe | Services | Rolle |
|---|---|---|
| Presentation | `frontend-web`, `mobile-app` (Repo) | UI |
| Edge | `bff-web`, `dev-sse`, `logistics-bff` (Repo) | BFF, SSE |
| Core API | `backend` | FastAPI Monolith, Process Kernel |
| Domain MS | `crm-core`, `crm-sales`, `crm-service`, `crm-workflow`, `crm-analytics`, `crm-communication`, `crm-multichannel`, `crm-security`, `crm-ai` (profile) | CRM Bounded Context |
| Domain MS | `inventory-service`, `rations-optimization`, `ki-usability`, `ai` | Spezialdomänen |
| Integration | `dms-adapter` | DMS |
| DMS Stack | `paperless`, `paperless-db`, `paperless-redis` | Dokumentenarchiv |
| Data/Event | `postgres`, `redis`, `nats` | Persistenz, Cache, Events |
| Identity | `keycloak` | OIDC |
| Ops (optional) | `pgadmin`, `redis-commander` | Dev-Tools |

## CRM-Cluster (Ports)

| Container | Port | Fokus |
|---|---|---|
| crm-core | 5600 | Stammdaten, Kern |
| crm-sales | 5700 | Vertrieb |
| crm-service | 5800 | Servicefälle |
| crm-workflow | 5900 | CRM-Workflows |
| crm-analytics | 6000 | Auswertung |
| crm-communication | 6100 | E-Mail, Benachrichtigung |
| crm-ai | 6200 | KI (profile ai) |
| crm-multichannel | 6300 | Social, Webhooks |
| crm-security | 6400 | CRM Security Layer |

## Production-Stack (`docker-compose.production.yml`)

Observability und vereinfachtes Deployment ohne CRM-Microservice-Cluster:

{PRODUCTION_MERMAID}

## Wartung

```bash
python scripts/render_c4_views.py
python scripts/render_c4_views.py --check
python scripts/generate_container_inventory.py --check
```

→ [C4 Component CRM](components/c4-crm.md) | [Enterprise-Landkarte](enterprise-landscape.md)
"""


def render_all() -> dict[Path, str]:
    dsl_text = DSL_PATH.read_text(encoding="utf-8")
    model = parse_dsl(dsl_text)
    if not model.elements:
        raise RuntimeError(f"Keine Elemente in {DSL_PATH} geparst — DSL-Syntax prüfen.")

    return {
        OUTPUTS["context"]: build_context_doc(render_context_mermaid(model)),
        OUTPUTS["containers"]: build_containers_doc(render_container_mermaid(model)),
    }


def dsl_fingerprint() -> str:
    return hashlib.sha256(DSL_PATH.read_bytes()).hexdigest()[:12]


def normalize_for_check(content: str) -> str:
    lines = [line for line in content.splitlines() if not line.startswith("last_reviewed:")]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render C4 views from Structurizr DSL")
    parser.add_argument("--check", action="store_true", help="Drift-Check ohne Schreiben")
    args = parser.parse_args()

    if not DSL_PATH.exists():
        print(f"FEHLER: {DSL_PATH} fehlt", file=sys.stderr)
        return 1

    outputs = render_all()
    drift = False
    for path, content in outputs.items():
        if args.check:
            if not path.exists():
                print(f"DRIFT: {path} fehlt (DSL fp={dsl_fingerprint()})", file=sys.stderr)
                drift = True
                continue
            existing = normalize_for_check(path.read_text(encoding="utf-8"))
            expected = normalize_for_check(content)
            if existing != expected:
                print(f"DRIFT: {path} weicht von Generator ab", file=sys.stderr)
                drift = True
            else:
                print(f"OK: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Geschrieben: {path}")

    if drift:
        print("render_c4_views --check fehlgeschlagen.", file=sys.stderr)
        return 1

    if not args.check:
        print(f"DSL fingerprint: {dsl_fingerprint()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
