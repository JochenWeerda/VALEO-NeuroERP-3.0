#!/usr/bin/env python3
"""Generiert config/architecture-index.yaml aus Code-Inventaren.

Quellen:
  - config/architecture-domain-prefixes.yaml (Prefix-Regeln — Single Source of Truth)
  - packages/frontend-web/src/app/routing/route-inventory.gen.json
  - docs/schnittstellen/endpoint-inventory.md
  - docs/entwickler/service-inventory.md
  - docs/entwickler/container-inventory.md
  - config/architecture-index.overrides.yaml (optional)

Verwendung:
    python scripts/generate_architecture_index.py
    python scripts/generate_architecture_index.py --check
    python scripts/generate_architecture_index.py --require-complete
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "config" / "architecture-index.yaml"
OVERRIDES = REPO_ROOT / "config" / "architecture-index.overrides.yaml"
PREFIX_CONFIG = REPO_ROOT / "config" / "architecture-domain-prefixes.yaml"
ROUTE_INVENTORY = REPO_ROOT / "packages/frontend-web/src/app/routing/route-inventory.gen.json"
ENDPOINT_INVENTORY = REPO_ROOT / "docs" / "schnittstellen" / "endpoint-inventory.md"
SERVICE_INVENTORY = REPO_ROOT / "docs" / "entwickler" / "service-inventory.md"
CONTAINER_INVENTORY = REPO_ROOT / "docs" / "entwickler" / "container-inventory.md"
ADR_DIR = REPO_ROOT / "docs" / "adr"
EVENTS_DOC = REPO_ROOT / "docs" / "schnittstellen" / "events.md"

DOMAIN_META: dict[str, dict[str, object]] = {
    "crm": {
        "owner": "domain/crm",
        "frontend_route_prefixes": ["/crm", "/verkauf", "/sales", "/portal"],
        "service_prefixes": ["crm_", "business_partner_", "sales_"],
        "containers": [
            "crm-core", "crm-sales", "crm-service", "crm-workflow", "crm-analytics",
            "crm-communication", "crm-multichannel", "crm-security", "crm-ai",
        ],
        "architecture_docs": [
            "docs/architecture/domains/crm/README.md",
            "docs/architecture/views/components/c4-crm.md",
        ],
        "database_schemas": ["domain_crm", "domain_shared"],
    },
    "finance": {
        "owner": "domain/finance",
        "frontend_route_prefixes": ["/finance", "/finanz", "/fibu", "/meldewesen", "/pos"],
        "service_prefixes": ["finance_", "accounting_", "closing_", "ap_invoice"],
        "containers": ["backend"],
        "architecture_docs": [
            "docs/architecture/domains/finance/README.md",
            "docs/architecture/views/components/c4-finance.md",
        ],
        "database_schemas": ["domain_finance", "domain_shared"],
    },
    "agrar": {
        "owner": "domain/agrar",
        "frontend_route_prefixes": ["/agrar", "/agribusiness", "/annahme", "/kontrakte"],
        "service_prefixes": ["agrar_", "agri_", "kontrakt_"],
        "containers": ["backend", "rations-optimization"],
        "architecture_docs": [
            "docs/architecture/domains/agrar/README.md",
            "docs/architecture/views/components/c4-agrar.md",
        ],
        "database_schemas": ["domain_agrar", "domain_shared"],
    },
    "inventory": {
        "owner": "domain/inventory",
        "frontend_route_prefixes": ["/lager", "/inventory", "/artikel", "/stammdaten"],
        "service_prefixes": ["inventory_", "warehouse_", "articles_"],
        "containers": ["inventory-service", "backend"],
        "architecture_docs": [
            "docs/architecture/domains/inventory/README.md",
            "docs/architecture/views/components/c4-procurement-inventory.md",
        ],
        "database_schemas": ["domain_inventory", "domain_shared"],
    },
    "procurement": {
        "owner": "domain/procurement",
        "frontend_route_prefixes": ["/einkauf", "/procurement"],
        "service_prefixes": ["procurement_", "proc_", "purchase_order_"],
        "containers": ["backend"],
        "architecture_docs": [
            "docs/architecture/views/components/c4-procurement-inventory.md",
        ],
        "database_schemas": ["domain_procurement", "domain_shared"],
    },
    "logistics": {
        "owner": "domain/logistics",
        "frontend_route_prefixes": ["/logistik", "/transporte", "/strecke", "/fuhrpark"],
        "service_prefixes": ["logistics_", "logistik_"],
        "containers": ["backend", "bff-web"],
        "architecture_docs": [
            "docs/architecture/views/components/c4-procurement-inventory.md",
        ],
        "database_schemas": ["domain_shared"],
    },
    "dms-compliance": {
        "owner": "domain/dms-compliance",
        "frontend_route_prefixes": ["/compliance", "/dms", "/docflow", "/qualitaet"],
        "service_prefixes": ["compliance_", "docflow_", "dms_"],
        "containers": ["dms-adapter", "paperless", "paperless-db", "paperless-redis"],
        "architecture_docs": [
            "docs/architecture/domains/dms-compliance/README.md",
            "docs/architecture/views/components/c4-dms-compliance.md",
        ],
        "database_schemas": ["domain_compliance", "domain_shared"],
    },
    "hr": {
        "owner": "domain/hr",
        "frontend_route_prefixes": ["/personal", "/schichtplan"],
        "service_prefixes": ["hrm_", "personal_", "lohn_"],
        "containers": ["backend"],
        "architecture_docs": [],
        "database_schemas": ["domain_shared"],
    },
    "platform": {
        "owner": "platform",
        "frontend_route_prefixes": ["/admin", "/admin-suite", "/workflow", "/auth"],
        "service_prefixes": ["admin_", "ai_", "mcp_", "workflow_"],
        "containers": ["backend", "keycloak", "bff-web", "ki-usability"],
        "architecture_docs": [],
        "database_schemas": ["domain_shared"],
    },
}


@dataclass
class PrefixRules:
    default_route_domain: str = "platform"
    route_segment_to_domain: dict[str, str] = field(default_factory=dict)
    service_prefixes: list[tuple[str, str]] = field(default_factory=list)
    endpoint_prefixes: list[tuple[str, str]] = field(default_factory=list)
    exact_service: dict[str, str] = field(default_factory=dict)
    exact_endpoint: dict[str, str] = field(default_factory=dict)


def _match_stem(stem: str, prefix: str) -> bool:
    if prefix.endswith("_"):
        base = prefix.rstrip("_")
        return stem.startswith(prefix) or stem == base
    return stem == prefix or stem.startswith(f"{prefix}_") or stem.startswith(prefix)


def load_prefix_rules() -> PrefixRules:
    if yaml is None or not PREFIX_CONFIG.exists():
        return PrefixRules()
    raw = yaml.safe_load(PREFIX_CONFIG.read_text(encoding="utf-8")) or {}
    rules = PrefixRules(default_route_domain=raw.get("default_route_domain", "platform"))

    for domain_id, cfg in (raw.get("domains") or {}).items():
        for seg in cfg.get("route_segments") or []:
            rules.route_segment_to_domain[seg] = domain_id
        for pfx in cfg.get("service_prefixes") or []:
            rules.service_prefixes.append((pfx, domain_id))
        for pfx in cfg.get("endpoint_prefixes") or []:
            rules.endpoint_prefixes.append((pfx, domain_id))

    rules.service_prefixes.sort(key=lambda x: len(x[0]), reverse=True)
    rules.endpoint_prefixes.sort(key=lambda x: len(x[0]), reverse=True)
    rules.exact_service = raw.get("exact_service_stems") or {}
    rules.exact_endpoint = raw.get("exact_endpoint_stems") or {}
    return rules


_RULES: PrefixRules | None = None


def get_rules() -> PrefixRules:
    global _RULES
    if _RULES is None:
        _RULES = load_prefix_rules()
    return _RULES


def route_domain(path: str, module: str = "") -> str | None:
    rules = get_rules()
    if not path:
        return rules.default_route_domain
    first = path.split("/")[0]
    if first in rules.route_segment_to_domain:
        return rules.route_segment_to_domain[first]
    if "/pages/" in module:
        folder = module.split("/pages/")[1].split("/")[0]
        if folder in rules.route_segment_to_domain:
            return rules.route_segment_to_domain[folder]
    return None


def service_domain(stem: str) -> str | None:
    rules = get_rules()
    if stem in rules.exact_service:
        return rules.exact_service[stem]
    for prefix, domain in rules.service_prefixes:
        if _match_stem(stem, prefix):
            return domain
    return None


def endpoint_domain(stem: str) -> str | None:
    rules = get_rules()
    if stem in rules.exact_endpoint:
        return rules.exact_endpoint[stem]
    for prefix, domain in rules.endpoint_prefixes:
        if _match_stem(stem, prefix):
            return domain
    return None


def all_domain_ids() -> list[str]:
    ids = set(DOMAIN_META) | set(get_rules().route_segment_to_domain.values())
    return sorted(ids)


def load_routes() -> list[dict[str, str]]:
    if not ROUTE_INVENTORY.exists():
        return []
    data = json.loads(ROUTE_INVENTORY.read_text(encoding="utf-8"))
    return data.get("routes", [])


def parse_inventory_table(path: Path) -> list[str]:
    if not path.exists():
        return []
    stems: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| `([^`]+)` \|", line)
        if m:
            stems.append(m.group(1))
    return stems


def parse_containers(path: Path) -> list[str]:
    if not path.exists():
        return []
    names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| `([^`]+)` \|", line)
        if m and m.group(1) not in {"Service", "Container"}:
            names.append(m.group(1))
    return sorted(set(names))


def collect_adrs() -> dict[str, list[str]]:
    domain_ids = all_domain_ids()
    clusters: dict[str, list[str]] = {d: [] for d in domain_ids}
    clusters["architecture"] = []
    if not ADR_DIR.exists():
        return clusters
    adr_keywords: dict[str, list[str]] = {
        "crm": ["crm", "business partner", "kunde", "vertrieb", "sales"],
        "finance": ["finance", "fibu", "datev", "elster", "ustva", "accounting"],
        "agrar": ["agrar", "agri", "ernte", "trocknung", "kontrakt"],
        "inventory": ["inventory", "lager", "warehouse", "silo"],
        "logistics": ["logistik", "logistics", "transport", "fuhrpark"],
        "dms-compliance": ["dms", "paperless", "compliance", "vvvo"],
        "procurement": ["einkauf", "procurement", "purchase"],
        "hr": ["hrm", "personal", "lohn", "zeiterfassung"],
        "architecture": ["architecture", "structurizr", "c4", "arc42", "multiten"],
    }
    adr_paths = (path for path in ADR_DIR.glob("*.md") if path.stem.lower().startswith("adr-"))
    for adr_path in sorted(adr_paths, key=lambda path: path.name.lower()):
        name = adr_path.stem
        text = adr_path.read_text(encoding="utf-8").lower()
        for domain, keywords in adr_keywords.items():
            if any(kw in text or kw in name for kw in keywords):
                clusters.setdefault(domain, []).append(f"docs/adr/{adr_path.name}")
    return clusters


def load_overrides() -> dict:
    if not OVERRIDES.exists() or yaml is None:
        return {}
    return yaml.safe_load(OVERRIDES.read_text(encoding="utf-8")) or {}


def build_index() -> dict:
    routes = load_routes()
    services = parse_inventory_table(SERVICE_INVENTORY)
    endpoints = parse_inventory_table(ENDPOINT_INVENTORY)
    containers = parse_containers(CONTAINER_INVENTORY)
    adrs = collect_adrs()
    overrides = load_overrides()
    domain_ids = all_domain_ids()

    domain_routes: dict[str, list[str]] = {k: [] for k in domain_ids}
    unmapped_routes: list[str] = []

    for r in routes:
        path = r.get("path", "")
        module = r.get("module", "")
        url = f"/{path}" if path else "/"
        domain = route_domain(path, module)
        if domain and domain in domain_routes:
            if url not in domain_routes[domain]:
                domain_routes[domain].append(url)
        else:
            unmapped_routes.append(url)

    domain_services: dict[str, list[str]] = {k: [] for k in domain_ids}
    unmapped_services: list[str] = []
    for svc in services:
        domain = service_domain(svc)
        if domain and domain in domain_services:
            domain_services[domain].append(svc)
        else:
            unmapped_services.append(svc)

    domain_endpoints: dict[str, list[str]] = {k: [] for k in domain_ids}
    unmapped_endpoints: list[str] = []
    for ep in endpoints:
        domain = endpoint_domain(ep)
        if domain and domain in domain_endpoints:
            domain_endpoints[domain].append(ep)
        else:
            unmapped_endpoints.append(ep)

    domains_out: dict[str, dict] = {}
    for domain_id in domain_ids:
        meta = DOMAIN_META.get(domain_id, {})
        entry: dict = {
            "owner": meta.get("owner", domain_id),
            "frontend_route_prefixes": meta.get("frontend_route_prefixes", []),
            "service_prefixes": meta.get("service_prefixes", []),
            "containers": meta.get("containers", []),
            "architecture_docs": meta.get("architecture_docs", []),
            "database_schemas": meta.get("database_schemas", []),
            "frontend_routes": sorted(domain_routes.get(domain_id, [])),
            "backend_services": sorted(domain_services.get(domain_id, [])),
            "backend_endpoints": sorted(domain_endpoints.get(domain_id, [])),
            "decisions": sorted(set(adrs.get(domain_id, []))),
        }
        if overrides.get("domains", {}).get(domain_id):
            entry.update(overrides["domains"][domain_id])
        domains_out[domain_id] = entry

    rules = get_rules()
    index = {
        "schema_version": "1.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/generate_architecture_index.py",
        "prefix_rules": str(PREFIX_CONFIG.relative_to(REPO_ROOT)).replace("\\", "/"),
        "delivery_ref": "docs/architecture/process-kernel/STATUS.md",
        "c4_source": "docs/architecture/c4/workspace.dsl",
        "architecture_protocol": "docs/architecture/agents/architecture-protocol.md",
        "containers": containers,
        "events_doc": "docs/schnittstellen/events.md" if EVENTS_DOC.exists() else None,
        "domains": domains_out,
        "mapping_stats": {
            "frontend_routes_total": len(routes),
            "frontend_routes_mapped": len(routes) - len(unmapped_routes),
            "backend_services_total": len(services),
            "backend_services_mapped": len(services) - len(unmapped_services),
            "backend_endpoints_total": len(endpoints),
            "backend_endpoints_mapped": len(endpoints) - len(unmapped_endpoints),
        },
        "unmapped": {
            "frontend_routes": sorted(unmapped_routes),
            "backend_services": sorted(unmapped_services),
            "backend_endpoints": sorted(unmapped_endpoints),
        },
    }

    if overrides.get("status"):
        index["status"] = overrides["status"]

    return index


def validate_complete(index: dict) -> list[str]:
    errors: list[str] = []
    unmapped = index.get("unmapped", {})
    for key, label in (
        ("frontend_routes", "Frontend-Routen"),
        ("backend_services", "Backend-Services"),
        ("backend_endpoints", "Backend-Endpoints"),
    ):
        items = unmapped.get(key, [])
        if items:
            errors.append(f"{len(items)} {label} ohne Domain-Mapping: {items[:5]}")
    return errors


def serialize_index(data: dict) -> str:
    if yaml is None:
        raise RuntimeError("PyYAML fehlt — pip install pyyaml")
    header = (
        f"# Architecture Index — generiert {date.today().isoformat()}\n"
        f"# Nicht manuell bearbeiten. Prefix-Regeln: config/architecture-domain-prefixes.yaml\n"
    )
    body = yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return header + body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Fehler wenn unmapped routes/services/endpoints > 0",
    )
    args = parser.parse_args()

    if yaml is None:
        print("FEHLER: PyYAML nicht installiert", file=sys.stderr)
        return 1

    if not PREFIX_CONFIG.exists():
        print(f"FEHLER: {PREFIX_CONFIG} fehlt", file=sys.stderr)
        return 1

    index = build_index()
    if args.require_complete:
        mapping_errors = validate_complete(index)
        for err in mapping_errors:
            print(f"FEHLER: {err}", file=sys.stderr)
        if mapping_errors:
            return 1

    content = serialize_index(index)

    if args.check:
        if not OUTPUT.exists():
            print(f"DRIFT: {OUTPUT} fehlt", file=sys.stderr)
            return 1
        existing = OUTPUT.read_text(encoding="utf-8")

        def normalize(s: str) -> str:
            s = re.sub(r"^# Architecture Index .*generiert \d{4}-\d{2}-\d{2}$", "# Architecture Index -- generiert X", s, flags=re.MULTILINE)
            return re.sub(r"^generated_at:.*$", "generated_at: X", s, flags=re.MULTILINE)

        if normalize(existing) != normalize(content):
            print(f"DRIFT: {OUTPUT} weicht ab — python scripts/generate_architecture_index.py ausführen", file=sys.stderr)
            return 1
        stats = index.get("mapping_stats", {})
        print(f"OK: {OUTPUT} (routes {stats.get('frontend_routes_mapped')}/{stats.get('frontend_routes_total')})")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    stats = index.get("mapping_stats", {})
    print(f"Geschrieben: {OUTPUT}")
    print(
        f"Mapping: routes {stats.get('frontend_routes_mapped')}/{stats.get('frontend_routes_total')}, "
        f"services {stats.get('backend_services_mapped')}/{stats.get('backend_services_total')}, "
        f"endpoints {stats.get('backend_endpoints_mapped')}/{stats.get('backend_endpoints_total')}"
    )
    unmapped = index.get("unmapped", {})
    if any(unmapped.get(k) for k in ("frontend_routes", "backend_services", "backend_endpoints")):
        print(
            f"WARNUNG: unmapped routes={len(unmapped.get('frontend_routes', []))}, "
            f"services={len(unmapped.get('backend_services', []))}, "
            f"endpoints={len(unmapped.get('backend_endpoints', []))}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
