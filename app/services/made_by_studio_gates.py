"""Made-by-Studio Qualitätsgates A–C und E für registrierte ScreenDefinitions.

Reine Analyse (keine DB, keine Netzwerkaufrufe). Gate D (Browser/Image) wird nur als
Metrik aus Readiness-Advisories abgeleitet, nicht als harter Pass/Fail.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]

CANONICAL_LAYOUT_KINDS = frozenset({"objectPage", "listReport", "worklist", "wizard", "overviewPage"})

_RAW_COLOR_PATTERN = re.compile(
    r"\b(text|bg|border|ring|fill|stroke)-(green|red|blue|yellow|orange|purple|pink|emerald|lime|amber|sky|indigo|violet|fuchsia|rose|teal|cyan)-[0-9]{2,3}\b"
    r"|\btext-\[[0-9]+px\]"
)

_RUNTIME_MARKERS = re.compile(
    r"\b(useUniversalMaskRuntime|UniversalMaskRenderer|UniversalNativeDetailPage|"
    r"UniversalNativeCreatePage|UniversalNativeCockpitPage|NativeListPage|NativeAuditListPage|CaptureScreenHost|"
    r"createStammNativeDetailPage|MadeByStudioListRuntimeWire|MadeByStudioDetailRuntimeWire|"
    r"MadeByStudioCockpitRuntimeWire|DocumentControlScopePage|SanktionsScopePage)\b"
)
_SCREEN_ID_IN_SOURCE = re.compile(
    r"""screenId\s*=\s*(?:\{\s*)?[`'"]([^`'"]+)[`'"]|useScreenDefinition\(\s*[`'"]([^`'"]+)[`'"]"""
)
_RUNTIME_WRAPPER = re.compile(
    r"\b(UniversalNativeCockpitPage|UniversalNativeDetailPage|NativeListPage|NativeAuditListPage|"
    r"DocumentControlScopePage|SanktionsScopePage|UniversalMaskRolloutPilotPage|"
    r"createStammNativeDetailPage|MadeByStudioListRuntimeWire|MadeByStudioDetailRuntimeWire|"
    r"MadeByStudioCockpitRuntimeWire|CaptureScreenHost)\b"
)

# Legacy-Worklist-IDs, deren Runtime bereits auf StammListenParent-*-liste verdrahtet ist.
_RUNTIME_LIST_WIRE_ALIASES: dict[str, str] = {
    "fuhrpark/uebersicht": "fuhrpark/fahrzeuge-liste",
    "fuhrpark/rechnungen": "fuhrpark/rechnungen-liste",
    "logistik/verladung": "verladung/liste",
    "transporte/fahrer": "transporte/fahrer-liste",
    "waage/liste": "waage/waagen-liste",
    "dashboard/verkauf": "dashboard/sales-dashboard",
    "strecke/vorlaeufig": "strecke/vorlaeufige-streckengeschaefte",
    "start-dashboard": "workspace/start-dashboard",
    "finance/offene-posten": "finance/offene-posten-cockpit",
    "logistik/frachtbrief": "logistik/frachtbriefe",
    "workflow/process-mining": "workflow/process-mining-analytics",
    "crm/campaign-performance": "crm/campaign-performance-dashboard",
    "fuhrpark/auswertungen-menu": "fuhrpark/fuhrpark-auswertungen-menu",
    "fuhrpark/auswertung-kosten": "fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug",
    "lager/leitstand": "lager/materialfluss-visualisierung",
    "lager/lagerbewegungen-liste": "lager/stock-movement",
    "sales/invoices": "sales/invoice",
    "fibu/kostenstellenrechnung": "fibu/kostenstellen-liste",
    "finance/bookings/new": "fibu/buchungsjournal-liste",
    "transporte/fahrer/neu": "transporte/fahrer",
    "kontrakte/liste": "kontrakte/LstKontraktUebersicht",
    "agrar/feldbuch-massnahmen-liste": "agrar/feldbuch/massnahmen",
    "agrar/saatzucht-partien-liste": "agrar/saatzucht",
    "finance/ap/invoices": "finance/ap-invoices-liste",
    "finance/payments": "finance/payment-matching-liste",
}


def _screen_id_path_variants(screen_id: str) -> set[str]:
    """Listen-Registry (-liste) vs. Frontend-Routen (/liste) und Kurzformen."""
    variants = {screen_id}
    if screen_id.endswith("-liste"):
        base = screen_id[: -len("-liste")]
        variants.add(base)
        variants.add(f"{base}/liste")
    elif screen_id.endswith("/liste"):
        parent = screen_id[: -len("/liste")]
        variants.add(parent)
        variants.add(f"{parent}-liste")
    else:
        variants.add(f"{screen_id}-liste")
        if "/" in screen_id:
            variants.add(f"{screen_id}/liste")
    return variants


@lru_cache(maxsize=1)
def _route_path_to_screen_ids() -> dict[str, set[str]]:
    path_map: dict[str, set[str]] = {}
    try:
        from app.core.screen_definitions_listen import LISTEN_ROUTEN
    except ImportError:
        LISTEN_ROUTEN = {}
    for sid, route in (LISTEN_ROUTEN or {}).items():
        if isinstance(route, str) and route.strip():
            path_map.setdefault(route.lstrip("/"), set()).add(sid)
    try:
        from app.core import screen_definitions as sd_mod

        for attr in ("_SCREEN_LIST_ROUTE", "_AGENT_NAV"):
            routes = getattr(sd_mod, attr, {}) or {}
            for sid, route in routes.items():
                if isinstance(route, str) and route.strip():
                    path_map.setdefault(route.lstrip("/"), set()).add(sid)
    except Exception:
        pass
    return path_map


def _source_has_runtime_marker(text: str) -> bool:
    from app.core.mask_runtime_evidence import has_visible_runtime
    return has_visible_runtime(text)


def _screen_ids_from_runtime_routes() -> set[str]:
    """Screen-IDs deren Routenmodul runtime-markiert ist (NativeListPage, Cockpit, …)."""
    inv_path = ROOT / "packages" / "frontend-web" / "src" / "app" / "routing" / "route-inventory.gen.json"
    if not inv_path.is_file():
        return set()
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    path_to_sids = _route_path_to_screen_ids()
    wired: set[str] = set()
    for route in inv.get("routes") or []:
        module = route.get("module", "")
        src = _resolve_page_module(module)
        if src is None or not src.is_file():
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        if not _source_has_runtime_marker(text):
            continue
        wired |= _screen_ids_from_source(text)
        path = str(route.get("path", "")).lstrip("/")
        wired |= path_to_sids.get(path, set())
        for sid in list(wired):
            wired |= _screen_id_path_variants(sid)
    return wired


def _gate_e_runtime_candidates(screen_id: str) -> set[str]:
    candidates = _screen_id_path_variants(screen_id)
    mapped = _RUNTIME_LIST_WIRE_ALIASES.get(screen_id)
    if mapped:
        candidates.add(mapped)
        candidates |= _screen_id_path_variants(mapped)
    for legacy_id, wired_list_id in _RUNTIME_LIST_WIRE_ALIASES.items():
        if wired_list_id == screen_id:
            candidates.add(legacy_id)
            candidates |= _screen_id_path_variants(legacy_id)
    return candidates


FLOORPLAN_TO_LAYOUT_KIND: dict[str, str] = {
    "worklist": "worklist",
    "analyticalList": "listReport",
    "objectPage": "objectPage",
    "transaction": "objectPage",
    "wizard": "wizard",
    "cockpit": "overviewPage",
}


@dataclass
class GateResult:
    gate: str
    passed: bool
    issues: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScreenGateReport:
    screen_id: str
    gates: dict[str, GateResult]
    layout_kind: str | None = None
    studio_draft_violations: list[str] = field(default_factory=list)


def resolve_layout_kind(definition: dict[str, Any]) -> str | None:
    layout = definition.get("layout") or {}
    floorplan = layout.get("floorplan")
    if isinstance(floorplan, str) and floorplan in FLOORPLAN_TO_LAYOUT_KIND:
        return FLOORPLAN_TO_LAYOUT_KIND[floorplan]
    mode = definition.get("mode")
    if mode == "list":
        return "worklist"
    if mode == "wizard":
        return "wizard"
    if mode == "cockpit":
        return "overviewPage"
    if mode in ("detail", "transaction"):
        return "objectPage"
    return None


def _walk_strings(value: Any, found: list[str]) -> None:
    if isinstance(value, str):
        if _RAW_COLOR_PATTERN.search(value):
            found.append(value[:120])
    elif isinstance(value, dict):
        for child in value.values():
            _walk_strings(child, found)
    elif isinstance(value, list):
        for child in value:
            _walk_strings(child, found)


def _collect_tables(definition: dict[str, Any]) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = list(definition.get("tables") or [])
    for tab in definition.get("tabs") or []:
        if isinstance(tab, dict):
            tables.extend(tab.get("tables") or [])
    return tables


def _is_mutating_action(action: dict[str, Any]) -> bool:
    if not isinstance(action, dict) or not action.get("key"):
        return False
    if action.get("stubReason"):
        return False
    flow = action.get("inputFlow") if isinstance(action.get("inputFlow"), dict) else {}
    rest = action.get("commandEndpoint") or flow.get("submitEndpoint") or action.get("command")
    navigation = (bool(action.get("navigationRoute")) or bool(action.get("localEffect"))) and not rest
    if navigation:
        return False
    if rest:
        return True
    danger = str(action.get("dangerLevel") or "safe")
    return danger not in ("safe",) and not action.get("readOnly")


def check_gate_a(definition: dict[str, Any]) -> GateResult:
    issues: list[str] = []
    layout_kind = resolve_layout_kind(definition)
    if layout_kind is None or layout_kind not in CANONICAL_LAYOUT_KINDS:
        issues.append(f"layout_kind_unbekannt:{layout_kind!r}")

    layout = definition.get("layout") or {}
    floorplan = layout.get("floorplan")
    section_nav = layout.get("sectionNavigation")
    if floorplan == "worklist" and section_nav == "anchors":
        issues.append("register_tabs:worklist_darf_keine_sectionNavigation_anchors")
    tabs = definition.get("tabs") or []
    if len(tabs) > 1 and section_nav not in (None, "tabs") and floorplan in ("worklist", "analyticalList"):
        issues.append("register_tabs:mehrere_register_erwarten_sectionNavigation_tabs")

    title = str(definition.get("title") or "").strip()
    if not title:
        issues.append("h1_identitaet:title_fehlt")

    detail_floorplans = {"objectPage", "transaction"}
    if floorplan in detail_floorplans or layout_kind == "objectPage":
        identity = definition.get("identityField")
        if not identity:
            from app.core.screen_definitions import infer_identity_field

            if not infer_identity_field(definition):
                issues.append("h1_identitaet:identityField_fehlt_auf_objectPage")

    raw_hits: list[str] = []
    _walk_strings(definition, raw_hits)
    if raw_hits:
        issues.append(f"meridian_rohe_farbklassen:{len(raw_hits)}")

    from app.api.v1.endpoints.mask_screen_definition import _check_readiness

    readiness = _check_readiness(definition)
    schema_blockers = [e for e in readiness.get("errors") or [] if e.startswith("[schema_valid]")]
    layout_blockers = [
        e for e in readiness.get("errors") or []
        if e.startswith("[layout_metadata]") or e.startswith("[table_profile]")
    ]
    for item in schema_blockers + layout_blockers:
        issues.append(f"readiness:{item}")

    return GateResult(
        gate="A",
        passed=not issues,
        issues=issues,
        metrics={"layout_kind": layout_kind, "generator_ready": readiness.get("generatorReady")},
    )


def check_gate_b(definition: dict[str, Any]) -> GateResult:
    from app.services.studio_validation import _iter_actions

    issues: list[str] = []
    mutating = 0
    for action in _iter_actions(definition):
        if not isinstance(action, dict):
            continue
        if not _is_mutating_action(action):
            continue
        mutating += 1
        if not action.get("permission"):
            issues.append(f"aktion_ohne_permission:{action.get('key')}")

    unclassified = [
        a.get("key")
        for a in (definition.get("actions") or [])
        if isinstance(a, dict) and a.get("key")
        and (not a.get("dangerLevel") or (not a.get("permission") and not a.get("stubReason")))
    ]
    for key in unclassified:
        issues.append(f"header_aktion_unklassifiziert:{key}")

    return GateResult(
        gate="B",
        passed=not issues,
        issues=issues,
        metrics={"mutating_actions": mutating},
    )


@lru_cache(maxsize=8)
def _openapi_route_keys(method: str = "GET") -> set[str]:
    """Match the declared method; concrete variants need an explicit path enum.

    An arbitrary parameter route cannot prove that a named operation exists
    (e.g. /finance/{id} does not establish /finance/datev-export).
    """
    from itertools import product

    path = ROOT / "docs" / "schnittstellen" / "openapi.json"
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    routes: set[str] = set()
    for endpoint, item in data.get("paths", {}).items():
        operation = item.get(method.lower())
        if not isinstance(operation, dict):
            continue
        routes.add(_route_key(endpoint))
        parameters = {
            parameter.get("name"): parameter
            for parameter in [*(item.get("parameters") or []), *(operation.get("parameters") or [])]
            if isinstance(parameter, dict) and parameter.get("in") == "path"
        }
        variants: list[list[str]] = []
        has_enum = False
        for segment in endpoint.split("/"):
            parameter = parameters.get(segment[1:-1]) if re.fullmatch(r"\{[^{}]+\}", segment) else None
            schema = (parameter or {}).get("schema") or {}
            if "$ref" in schema and schema["$ref"].startswith("#/components/schemas/"):
                schema = data.get("components", {}).get("schemas", {}).get(schema["$ref"].rsplit("/", 1)[-1], {})
            values = schema.get("enum")
            if isinstance(values, list) and values:
                # Only complete safe segments can describe concrete routes.
                concrete = [str(value) for value in values if isinstance(value, (str, int))
                            and not isinstance(value, bool) and re.fullmatch(r"[A-Za-z0-9_.~-]+", str(value))]
                variants.append(concrete or [segment])
                has_enum = has_enum or bool(concrete)
            else:
                variants.append([segment])
        if has_enum:
            routes.update(_route_key("/".join(parts)) for parts in product(*variants))
    return routes


def _route_key(path: str) -> str:
    import re as _re

    base = path.split("?", 1)[0]
    return _re.sub(r"\{[^}]+\}", "{}", base).rstrip("/")


def _openapi_endpoint_candidates(endpoint: str) -> list[str]:
    keys = [_route_key(endpoint)]
    base = endpoint.split("?", 1)[0]
    if "/api/v1/belege/" in base:
        from app.core.belegvertrag import BELEGARTEN

        normalized = base.replace("{entity_id}", "{beleg_id}")
        for art in BELEGARTEN:
            normalized = normalized.replace(f"/belege/{art}/", "/belege/{belegart}/")
        normalized = re.sub(
            r"/tabs/(positionen|kette|dokumente|historie)(?=/|$)",
            "/tabs/{reiter}",
            normalized,
        )
        keys.append(_route_key(normalized))
    return keys


def _endpoint_in_openapi(endpoint: str, routes: set[str]) -> bool:
    return bool(routes) and any(key in routes for key in _openapi_endpoint_candidates(endpoint))


def _entity_source(definition: dict[str, Any]) -> dict[str, Any] | None:
    for source in definition.get("dataSources") or []:
        if isinstance(source, dict) and source.get("key") == "entity":
            return source
    return None


def check_gate_c(definition: dict[str, Any], *, screen_id: str) -> GateResult:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness

    issues: list[str] = []
    readiness = _check_readiness(definition)
    if not readiness.get("generatorReady"):
        for err in readiness.get("errors") or []:
            issues.append(f"compiler:{err}")

    missing_endpoints: list[str] = []
    for source in definition.get("dataSources") or []:
        if not isinstance(source, dict):
            continue
        endpoint = source.get("endpoint")
        if isinstance(endpoint, str) and endpoint.startswith("/api/"):
            method = source.get("method", "GET")
            routes = _openapi_route_keys(method) if isinstance(method, str) else set()
            if not _endpoint_in_openapi(endpoint, routes):
                missing_endpoints.append(endpoint)
    for endpoint in missing_endpoints:
        issues.append(f"api_bindung:endpoint_nicht_in_openapi:{endpoint}")

    layout_kind = resolve_layout_kind(definition)
    entity = _entity_source(definition)
    if layout_kind == "objectPage" and not entity:
        issues.append("entity_source:objectPage_ohne_dataSources.entity")
    elif entity and layout_kind == "objectPage":
        endpoint = entity.get("endpoint")
        if not isinstance(endpoint, str) or "{entity_id}" not in endpoint:
            issues.append("entity_source:entity_endpoint_ohne_entity_id_platzholder")

    return GateResult(
        gate="C",
        passed=not issues,
        issues=issues,
        metrics={
            "advisory_score": readiness.get("advisoryScore"),
            "warnings": len(readiness.get("warnings") or []),
        },
    )


def _resolve_page_module(module: str) -> Path | None:
    fe = ROOT / "packages" / "frontend-web"
    pages = fe / "src" / "pages"
    if not module.startswith("@/pages/"):
        return None
    rel = module[len("@/pages/") :]
    base = pages / Path(*rel.split("/"))
    for ext in (".tsx", ".ts", "/index.tsx", "/index.ts"):
        cand = Path(str(base) + ext) if not ext.startswith("/") else base / ext[1:]
        if cand.is_file():
            return cand
    return None


def _screen_ids_from_source(text: str) -> set[str]:
    ids: set[str] = set()
    consts: dict[str, str] = {}
    for match in re.finditer(r"const\s+(SCREEN_ID|[A-Z_]+)\s*=\s*['\"]([^'\"]+)['\"]", text):
        consts[match.group(1)] = match.group(2)
    for match in _SCREEN_ID_IN_SOURCE.finditer(text):
        sid = match.group(1) or match.group(2)
        if sid:
            ids.add(sid)
    for match in re.finditer(r"""screenId:\s*['"]([^'"]+)['"]""", text):
        ids.add(match.group(1))
    for match in re.finditer(
        r"""createStammNativeDetailPage\s*\(\s*['"]([^'"]+)['"]""", text
    ):
        ids.add(match.group(1))
    for match in re.finditer(
        r"""MadeByStudio(?:List|Detail|Cockpit)RuntimeWire[^>]*screenId=\{?['"]([^'"]+)['"]""",
        text,
    ):
        ids.add(match.group(1))
    for match in re.finditer(
        r"""createStammNativeDetailPage\s*\(\s*['"]([^'"]+)['"]""",
        text,
    ):
        ids.add(match.group(1))
    # Generierte Cockpit-Pages (Rollout) setzen screenId teils ohne JSX-Quotes.
    for match in re.finditer(r"screenId=([a-z][a-zA-Z0-9_./-]+)", text):
        ids.add(match.group(1))
    if re.search(r"screenId=\{SCREEN_ID\}", text) and "SCREEN_ID" in consts:
        ids.add(consts["SCREEN_ID"])
    # Ein gerenderter Runtime-Host kann zwischen zwei echten Studio-Definitionen
    # wechseln (z. B. Historie und Diff). Beide Zweige laden die jeweilige SD.
    if re.search(r"\buseScreenDefinition\(\s*screenId\s*\)", text) and re.search(
        r"\buseUniversalMaskRuntime\(\s*\{\s*screenId\b", text
    ):
        for match in re.finditer(
            r"\bconst\s+screenId\s*=\s*[^?;\n]+\?\s*['\"]([^'\"]+)['\"]\s*:\s*['\"]([^'\"]+)['\"]",
            text,
        ):
            ids.update(match.groups())
    if "sanktionspruefung-" in text and "SanktionsScopePage" in text:
        ids.update({"auswertungen/sanktionspruefung-kunden", "auswertungen/sanktionspruefung-personal"})
    if re.search(r"screenId=\{`beleg/\$\{", text) or "beleg/${variante}" in text:
        from app.core.belegvertrag import BELEGARTEN
        from app.core.screen_definitions_beleg import screen_id as beleg_screen_id

        ids.update(beleg_screen_id(art) for art in BELEGARTEN)
    return ids


def _iter_runtime_source_files() -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    inv_path = ROOT / "packages" / "frontend-web" / "src" / "app" / "routing" / "route-inventory.gen.json"
    if inv_path.is_file():
        inv = json.loads(inv_path.read_text(encoding="utf-8"))
        for route in inv.get("routes") or []:
            src = _resolve_page_module(route.get("module", ""))
            if src is not None and src not in seen:
                seen.add(src)
                files.append(src)
    aliases_path = ROOT / "packages" / "frontend-web" / "src" / "app" / "route-aliases.json"
    if aliases_path.is_file():
        aliases = json.loads(aliases_path.read_text(encoding="utf-8"))
        for entry in aliases.get("aliases") or []:
            src = _resolve_page_module(entry.get("module", ""))
            if src is not None and src not in seen:
                seen.add(src)
                files.append(src)
    for root in (
        ROOT / "packages" / "frontend-web" / "src" / "pages",
        ROOT / "packages" / "frontend-web" / "src" / "features",
    ):
        if not root.is_dir():
            continue
        for src in root.rglob("*.tsx"):
            if "__tests__" in str(src) or src in seen:
                continue
            seen.add(src)
            files.append(src)
    return files


@lru_cache(maxsize=1)
def runtime_wired_screen_ids() -> frozenset[str]:
    wired: set[str] = set()
    for src in _iter_runtime_source_files():
        text = src.read_text(encoding="utf-8", errors="replace")
        if not _source_has_runtime_marker(text):
            continue
        wired |= _screen_ids_from_source(text)
    wired |= _screen_ids_from_runtime_routes()
    expanded: set[str] = set()
    for sid in wired:
        expanded |= _screen_id_path_variants(sid)
        expanded.add(sid)
    return frozenset(expanded)


def check_gate_e(screen_id: str) -> GateResult:
    wired = runtime_wired_screen_ids()
    passed = any(candidate in wired for candidate in _gate_e_runtime_candidates(screen_id))
    issues = [] if passed else ["runtime:screen_id_nicht_runtime_wired"]
    return GateResult(gate="E", passed=passed, issues=issues, metrics={"runtime_wired_routes": len(wired)})


def studio_draft_projection_violations(definition: dict[str, Any], screen_id: str) -> list[str]:
    """Wie Native-Import: tenant-Draft ableiten und Server-Validierung prüfen."""
    from hashlib import sha256

    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
    from app.core.studio_release import definition_hash
    from app.services.studio_validation import validate_studio_draft

    canonical = get_screen_definition(screen_id) or definition
    tenant_id = "tenant/native-" + sha256(screen_id.encode()).hexdigest()
    projected = {
        **canonical,
        "id": tenant_id,
        "baseScreenId": screen_id,
        "nativeBaseline": {"sourceHash": definition_hash(canonical)},
        "adapter": {"type": "native", "sourceId": tenant_id, "temporary": True},
    }
    return validate_studio_draft(projected, native_screen_ids=set(SCREEN_DEFINITION_BUILDERS))


def evaluate_screen(screen_id: str, definition: dict[str, Any]) -> ScreenGateReport:
    draft_violations = studio_draft_projection_violations(definition, screen_id)
    gates = {
        "A": check_gate_a(definition),
        "B": check_gate_b(definition),
        "C": check_gate_c(definition, screen_id=screen_id),
        "E": check_gate_e(screen_id),
    }
    return ScreenGateReport(
        screen_id=screen_id,
        gates=gates,
        layout_kind=resolve_layout_kind(definition),
        studio_draft_violations=draft_violations,
    )


def load_registered_definitions() -> dict[str, dict[str, Any]]:
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
    from app.core.screen_definitions_beleg import BELEGARTEN, build_beleg_screen_definition, screen_id as beleg_screen_id
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry

    # Der Gate-Lauf muss unabhaengig von der Import-Reihenfolge denselben
    # kanonischen Bestand sehen wie Studio-Katalog, CLI und Agent-Handbuch.
    ensure_stamm_screen_registry()
    ids = list(SCREEN_DEFINITION_BUILDERS)
    defs = {sid: get_screen_definition(sid) or {} for sid in ids}
    for art in BELEGARTEN:
        defs[beleg_screen_id(art)] = build_beleg_screen_definition(art)
    return defs


def evaluate_all() -> list[ScreenGateReport]:
    return [
        evaluate_screen(sid, definition)
        for sid, definition in sorted(load_registered_definitions().items())
        if definition
    ]


def summarize(reports: list[ScreenGateReport]) -> dict[str, Any]:
    total = len(reports)
    by_gate = {g: sum(1 for r in reports if r.gates[g].passed) for g in ("A", "B", "C", "E")}
    failed: dict[str, list[str]] = {g: [] for g in ("A", "B", "C", "E")}
    for report in reports:
        for gate, result in report.gates.items():
            if not result.passed:
                failed[gate].append(report.screen_id)
    draft_ready = sum(1 for r in reports if not r.studio_draft_violations)
    advisory_avg = round(
        sum(r.gates["C"].metrics.get("advisory_score", 0) for r in reports) / max(total, 1),
        2,
    )
    return {
        "total": total,
        "passed": by_gate,
        "failed_ids": failed,
        "studio_draft_clean": draft_ready,
        "advisory_score_avg": advisory_avg,
        "runtime_wired_screens": len(runtime_wired_screen_ids()),
    }


def markdown_report(reports: list[ScreenGateReport], *, stand: str) -> str:
    summary = summarize(reports)
    lines = [
        "# Made-by-Studio Gate-Report",
        "",
        f"Stand: {stand} (erzeugt mit `python scripts/verify_made_by_studio_gates.py`).",
        "",
        "Bezug: [Made by Studio — Qualitätsversprechen](made-by-studio-qualitaetsversprechen.md).",
        "",
        "## Zusammenfassung",
        "",
        f"| Metrik | Wert |",
        f"|--------|------|",
        f"| Registrierte ScreenDefinitions | {summary['total']} |",
        f"| Gate A (Meridian & Struktur) grün | {summary['passed']['A']} |",
        f"| Gate B (Rechte & Aktionen) grün | {summary['passed']['B']} |",
        f"| Gate C (Compiler & Kanal) grün | {summary['passed']['C']} |",
        f"| Gate E (Runtime-Verdrahtung) grün | {summary['passed']['E']} |",
        f"| Studio-Draft-Projektion ohne Violations | {summary['studio_draft_clean']} |",
        f"| Ø Advisory-Score (Gate-C-Metrik) | {summary['advisory_score_avg']} |",
        f"| Screen-IDs in runtime_wired-Routen (gesamt) | {summary['runtime_wired_screens']} |",
        "",
        "Gate D (Browser/Image) wird hier nicht automatisiert geprüft.",
        "",
    ]
    for gate in ("A", "B", "C", "E"):
        lines += [f"## Gate {gate} — offene Screen-IDs ({len(summary['failed_ids'][gate])})", ""]
        ids = sorted(summary["failed_ids"][gate])
        if not ids:
            lines.append("Keine — alle grün.")
        else:
            for sid in ids:
                report = next(r for r in reports if r.screen_id == sid)
                sample = report.gates[gate].issues[:3]
                extra = f" (+{len(report.gates[gate].issues) - 3})" if len(report.gates[gate].issues) > 3 else ""
                lines.append(f"- `{sid}`: {', '.join(sample)}{extra}")
        lines.append("")
    lines += ["## Studio-Draft-Projektion (Auszug)", ""]
    draft_fail = [r for r in reports if r.studio_draft_violations][:25]
    if not draft_fail:
        lines.append("Alle Projektionen ohne Violations.")
    else:
        for r in draft_fail:
            lines.append(f"- `{r.screen_id}`: {', '.join(r.studio_draft_violations[:4])}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
