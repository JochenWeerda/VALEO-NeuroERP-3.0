#!/usr/bin/env python3
"""Generate Batch-15 domain ScreenDefinitions and wire frontend pages (einkauf/preisspiegel..end)."""
from __future__ import annotations

import json
import re
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages" / "frontend-web" / "src" / "pages"
OPENAPI = ROOT / "docs" / "schnittstellen" / "openapi.json"
INV = ROOT / "packages" / "frontend-web" / "src" / "app" / "routing" / "route-inventory.gen.json"
ANALYSIS = ROOT / ".cursor" / "hand_built_analysis.json"
OUT_PY = ROOT / "app" / "core" / "screen_definitions_domain_batch15.py"
SCREEN_DEF = ROOT / "app" / "core" / "screen_definitions.py"
START = "einkauf/preisspiegel.tsx"

API_RE = re.compile(r"""['"](/api/v1[^'"]+)['"]""")


def _write_page(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    try:
        tmp.replace(path)
    except OSError:
        path.write_text(content, encoding="utf-8")
        if tmp.exists():
            tmp.unlink(missing_ok=True)
COL_RE = re.compile(r"""key:\s*['"](\w+)['"]""")
TITLE_RE = re.compile(r"""<CardTitle[^>]*>([^<]+)</CardTitle>|title:\s*['"]([^'"]+)['"]""")


def classify_source(text: str) -> str:
    if any(
        x in text
        for x in (
            "useUniversalMaskRuntime",
            "UniversalMaskRenderer",
            "UniversalNativeDetailPage",
            "NativeListPage",
            "UniversalNativeCockpitPage",
            "createStammNativeDetailPage",
        )
    ):
        return "runtime_wired"
    if re.search(r"\bObjectPage\b", text) or re.search(r"\bListReport\b", text):
        return "legacy"
    return "hand_built"


def load_get_paths() -> set[str]:
    oa = json.loads(OPENAPI.read_text(encoding="utf-8"))
    out: set[str] = set()
    for path, spec in oa.get("paths", {}).items():
        if "get" in spec:
            norm = re.sub(r"\{[^}]+\}", "{}", path).rstrip("/")
            out.add(norm)
            out.add(path.rstrip("/"))
    return out


def route_key(endpoint: str) -> str:
    base = endpoint.split("?", 1)[0]
    return re.sub(r"\{[^}]+\}", "{}", base).rstrip("/")


def in_openapi(endpoint: str, get_paths: set[str]) -> bool:
    return route_key(endpoint) in get_paths


def pick_list_endpoint(candidates: list[str], get_paths: set[str]) -> str | None:
    scored: list[tuple[int, str]] = []
    for ep in candidates:
        if not ep.startswith("/api/v1/"):
            continue
        if not in_openapi(ep, get_paths):
            continue
        score = 0
        if "{" not in ep.split("?", 1)[0]:
            score += 10
        if ep.endswith("/list") or "/export/list" in ep:
            score += 5
        if "/stats" in ep or "/summary" in ep:
            score -= 2
        scored.append((score, ep))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], len(x[1])))
    return scored[0][1]


def pick_entity_endpoint(candidates: list[str], get_paths: set[str]) -> str | None:
    for ep in candidates:
        if "{entity_id}" in ep or "{id}" in ep:
            fixed = ep.replace("{id}", "{entity_id}")
            if in_openapi(fixed, get_paths):
                return fixed
    for ep in candidates:
        if "{" in ep and in_openapi(ep.replace("{id}", "{entity_id}"), get_paths):
            return ep.replace("{id}", "{entity_id}")
    return None


def pick_cockpit_endpoint(candidates: list[str], get_paths: set[str], domain: str) -> str | None:
    for ep in candidates:
        if not in_openapi(ep, get_paths):
            continue
        if any(x in ep for x in ("/stats", "/summary", "/overview", "/dashboard", "/read-model")):
            return ep
    return pick_list_endpoint(candidates, get_paths)


def module_to_screen_id(rel: str) -> str:
    inv = json.loads(INV.read_text(encoding="utf-8"))
    mod = rel.replace(".tsx", "")
    paths = []
    for r in inv.get("routes", []):
        m = r.get("module", "")
        if m == f"@/pages/{mod}" or m == f"@/pages/{mod}/index":
            paths.append(r.get("path", mod))
    if paths:
        return paths[0].lstrip("/") or mod
    return mod


def fn_name(screen_id: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", screen_id).strip("_").lower()
    return f"build_{slug}_screen_definition"


def test_id(screen_id: str) -> str:
    return screen_id.replace("/", "-")


def title_from_rel(rel: str, text: str) -> str:
    m = TITLE_RE.search(text)
    if m:
        return (m.group(1) or m.group(2) or "").strip()
    base = Path(rel).stem.replace("-", " ").replace("_", " ")
    return base[:1].upper() + base[1:]


def columns_from_text(text: str) -> list[tuple[str, str]]:
    keys = []
    for k in COL_RE.findall(text):
        if k in keys or k in ("key", "label", "render"):
            continue
        keys.append(k)
    if not keys:
        keys = ["id", "name", "status", "updated_at"]
    keys = keys[:8]
    return [(k, k.replace("_", " ").title()) for k in keys]


def std_cols(pairs: list[tuple[str, str]]) -> str:
    parts = []
    for k, label in pairs:
        parts.append(
            f'{{"key": "{k}", "label": "{label}", "sortable": True, "filterable": True, "width": 160}}'
        )
    return "[" + ", ".join(parts) + "]"


def permission_read(domain: str) -> str:
    return f"{domain.replace('-', '_')}.read"


def permission_write(domain: str) -> str:
    return f"{domain.replace('-', '_')}.write"


def in_batch15_rel(rel: str) -> bool:
    if "-legacy" in rel or ".test." in rel:
        return False
    if "/" not in rel:
        return rel >= "Home.tsx"
    return rel >= START


def routable_batch15() -> dict[str, str]:
    """Map page rel (tsx) -> canonical screen_id (route path)."""
    inv = json.loads(INV.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for route in inv.get("routes") or []:
        mod = route.get("module", "")
        if not mod.startswith("@/pages/"):
            continue
        mod_rel = mod[len("@/pages/") :]
        if mod_rel.endswith("/index"):
            rel = f"{mod_rel}.tsx".replace("/index.tsx", "/index.tsx")
        else:
            rel = f"{mod_rel}.tsx" if not mod_rel.endswith(".tsx") else mod_rel
        if not in_batch15_rel(rel):
            continue
        screen_id = (route.get("path") or mod_rel).lstrip("/") or mod_rel
        if ":" in screen_id:
            continue
        out[rel] = screen_id
    return out


def page_source_text(rel: str) -> str:
    path = PAGES / rel
    text = path.read_text(encoding="utf-8", errors="replace")
    legacy = path.with_name(path.stem + "-legacy.tsx")
    if classify_source(text) != "hand_built" and legacy.is_file():
        return legacy.read_text(encoding="utf-8", errors="replace")
    return text


def has_named_exports(text: str) -> bool:
    return bool(re.search(r"^export (function|const|class|type|interface)", text, re.M))


def write_list_tsx(rel: str, screen_id: str) -> None:
    tid = test_id(screen_id)
    content = textwrap.dedent(
        f"""\
        import {{ NativeListPage }} from '@/components/mask-builder/NativeListPage'

        export default function Page(): JSX.Element {{
          return (
            <NativeListPage screenId="{screen_id}" testId="screen-{screen_id}" />
          )
        }}
        """
    )
    _write_page(PAGES / rel, content)


def write_cockpit_tsx(rel: str, screen_id: str) -> None:
    tid = test_id(screen_id)
    content = textwrap.dedent(
        f"""\
        import {{ UniversalNativeCockpitPage }} from '@/components/mask-builder/UniversalNativeCockpitPage'

        export default function Page(): JSX.Element {{
          return (
            <UniversalNativeCockpitPage
              screenId="{screen_id}"
              testId="{tid}"
            />
          )
        }}
        """
    )
    _write_page(PAGES / rel, content)


def write_object_tsx(rel: str, screen_id: str, text: str) -> None:
    legacy_rel = rel.replace(".tsx", "-legacy.tsx")
    legacy_path = PAGES / legacy_rel
    if not legacy_path.exists():
        _write_page(legacy_path, text)
    import_path = "./" + legacy_rel.replace(".tsx", "")
    tid = test_id(screen_id)
    content = textwrap.dedent(
        f"""\
        import {{ createStammNativeDetailPage }} from '@/components/mask-builder'

        export default createStammNativeDetailPage(
          '{screen_id}',
          '{tid}',
          () => import('{import_path}'),
        )
        """
    )
    _write_page(PAGES / rel, content)


def write_runtime_tsx(rel: str, screen_id: str, mode: str) -> None:
    tid = test_id(screen_id)
    if mode == "cockpit":
        write_cockpit_tsx(rel, screen_id)
        return
    if mode == "detail":
        content = textwrap.dedent(
            f"""\
            import {{ useParams }} from '@/app/routing/typed-router'
            import {{ UniversalNativeDetailPage }} from '@/components/mask-builder/UniversalNativeDetailPage'

            export default function Page(): JSX.Element {{
              const {{ id }} = useParams<{{ id?: string }}>()
              return (
                <UniversalNativeDetailPage screenId="{screen_id}" entityId={{id}} testId="{tid}" />
              )
            }}
            """
        )
        _write_page(PAGES / rel, content)
        return
    write_list_tsx(rel, screen_id)


def build_py_function(
    *,
    screen_id: str,
    family: str,
    domain: str,
    title: str,
    endpoint: str,
    cols: list[tuple[str, str]],
    perm_read: str,
) -> str:
    fn = fn_name(screen_id)
    col_expr = std_cols(cols)
    subtitle = domain
    no_wf = "Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken."

    if family in ("d_cockpit_dashboard",) or family == "e_wizard_terminal" and "cockpit" in screen_id:
        body = f"""
def {fn}() -> dict[str, Any]:
    cols = {col_expr}
    return build_cockpit_overview_screen(
        screen_id="{screen_id}",
        domain="{domain}",
        title="{title}",
        subtitle="{subtitle}",
        business_purpose="{title} mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige {title}.", "Aktualisiere die Kennzahlen."],
        test_id="{test_id(screen_id)}",
        data_sources=[cockpit_entity_source("{endpoint}")],
        tables=[cockpit_summary_table(table_key="list", label="{title}", columns=cols)],
        actions=[cockpit_refresh_action(permission="{perm_read}")],
        context_rail="combined",
    )
"""
    elif family == "c_stamm_object":
        ent = endpoint if "{entity_id}" in endpoint else endpoint.rstrip("/") + "/{entity_id}"
        if "{entity_id}" not in ent:
            ent = endpoint
        fields = ", ".join(
            f'{{"key": "{k}", "label": "{lab}", "type": "text"}}' for k, lab in cols[:6]
        )
        body = f"""
def {fn}() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="{screen_id}",
        domain="{domain}",
        title="{title}",
        subtitle="{subtitle}",
        identity_field="{cols[0][0]}",
        data_sources=[stamm_entity_source("{ent}")],
        tabs=[stamm_kopf_tab([{fields}])],
        edit_permission="{permission_write(domain)}",
        no_workflow_reason="{no_wf}",
        business_purpose="{title} als Stammblatt pflegen.",
        example_prompts=["Oeffne {title}.", "Bearbeite Stammdaten."],
        test_id="{test_id(screen_id)}",
    )
"""
    elif family == "b_kontroll_worklist":
        summary_ep = endpoint
        queue_ep = endpoint
        body = f"""
def {fn}() -> dict[str, Any]:
    cols = {col_expr}
    return build_kontroll_worklist_screen(
        screen_id="{screen_id}",
        domain="{domain}",
        title="{title}",
        subtitle="{subtitle}",
        data_sources=kontroll_entity_and_queue_sources(
            summary_endpoint="{summary_ep}",
            queue_endpoint="{queue_ep}",
        ),
        summary=[{{"key": "total", "label": "Offen", "tone": "warning"}}],
        tables=[kontroll_queue_table(table_key="exceptions", label="{title}", columns=cols, row_actions=[])],
        business_purpose="{title} als Kontroll-Worklist bearbeiten.",
        example_prompts=["Zeige offene Ausnahmen.", "Was ist ueberfaellig?"],
        test_id="{test_id(screen_id)}",
        no_workflow_reason="{no_wf}",
    )
"""
    else:
        body = f"""
def {fn}() -> dict[str, Any]:
    columns = {col_expr}
    return build_stamm_list_screen(
        screen_id="{screen_id}",
        domain="{domain}",
        title="{title}",
        subtitle="{subtitle}",
        endpoint="{endpoint}",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="{title} im {domain}-Bereich finden und auswerten.",
        prompts=["Zeige {title}.", "Filtere die Liste."],
        bundle="{domain}",
        no_workflow="{no_wf}",
    )
"""
    return body


def main() -> None:
    get_paths = load_get_paths()
    analysis = {e["file"].replace("src/pages/", ""): e for e in json.loads(ANALYSIS.read_text(encoding="utf-8"))}

    sys_path_insert = False
    import sys

    sys.path.insert(0, str(ROOT))
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS

    routes = routable_batch15()
    builders: dict[str, str] = {}
    skipped_existing = 0
    skipped_no_api = 0
    migrated = 0
    family_counts: Counter[str] = Counter()

    for rel, screen_id in sorted(routes.items()):
        entry = analysis.get(rel) or {
            "family": "other_mixed",
            "oa_hits": [],
        }
        family = entry["family"]
        if family == "e_wizard_terminal":
            family = "a_stamm_listen"
        path = PAGES / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        source_text = page_source_text(rel)
        needs_builder = screen_id not in SCREEN_DEFINITION_BUILDERS and screen_id not in builders
        if not needs_builder:
            skipped_existing += 1
        if not needs_builder and classify_source(text) != "hand_built":
            continue

        candidates = list(dict.fromkeys(entry.get("oa_hits") or []))
        candidates.extend(API_RE.findall(source_text))

        domain = screen_id.split("/")[0] if "/" in screen_id else "workspace"
        title = title_from_rel(rel, source_text).replace('"', "'")
        cols = columns_from_text(source_text)

        if not needs_builder:
            if classify_source(text) == "hand_built" and not has_named_exports(text):
                try:
                    if family == "c_stamm_object":
                        write_object_tsx(rel, screen_id, text)
                    elif family == "d_cockpit_dashboard":
                        write_cockpit_tsx(rel, screen_id)
                    else:
                        write_list_tsx(rel, screen_id)
                    migrated += 1
                except OSError as exc:
                    print(f"WARN skip write {rel}: {exc}")
            continue

        endpoint: str | None = None
        if family == "c_stamm_object":
            endpoint = pick_entity_endpoint(candidates, get_paths)
        elif family == "d_cockpit_dashboard":
            endpoint = pick_cockpit_endpoint(candidates, get_paths, domain)
        else:
            endpoint = pick_list_endpoint(candidates, get_paths)

        if not endpoint:
            prefixes = (
                f"/api/v1/{domain.replace('-', '_')}",
                f"/api/v1/{domain}",
            )
            for prefix in prefixes:
                for p in sorted(get_paths):
                    if p.startswith(prefix) and "{" not in p:
                        endpoint = p
                        break
                if endpoint:
                    break
        if not endpoint:
            tail = screen_id.split("/")[-1].replace("-", "_")
            for p in sorted(get_paths):
                if tail and tail in p.lower() and "{" not in p:
                    endpoint = p
                    break
        if not endpoint:
            skipped_no_api += 1
            continue

        perm = permission_read(domain)
        fn_body = build_py_function(
            screen_id=screen_id,
            family=family,
            domain=domain,
            title=title,
            endpoint=endpoint,
            cols=cols,
            perm_read=perm,
        )
        builders[screen_id] = fn_body
        family_counts[family] += 1

        if has_named_exports(text):
            continue
        try:
            if family == "c_stamm_object":
                write_object_tsx(rel, screen_id, text)
            elif family == "d_cockpit_dashboard":
                write_cockpit_tsx(rel, screen_id)
            else:
                write_list_tsx(rel, screen_id)
            migrated += 1
        except OSError as exc:
            print(f"WARN skip write {rel}: {exc}")

    header = textwrap.dedent(
        '''\
        """Domain ScreenDefinitions — Batch 15 (einkauf/preisspiegel .. workflow, auto-generated)."""
        from __future__ import annotations

        from typing import Any

        from app.core.cockpit_overview_parent import (
            build_cockpit_overview_screen,
            cockpit_entity_source,
            cockpit_refresh_action,
            cockpit_summary_table,
        )
        from app.core.kontroll_worklist_parent import (
            build_kontroll_worklist_screen,
            kontroll_entity_and_queue_sources,
            kontroll_queue_table,
        )
        from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action
        from app.core.stamm_object_page_parent import (
            build_stamm_object_page,
            stamm_entity_source,
            stamm_kopf_tab,
        )

        '''
    )

    parts = [header]
    for sid in sorted(builders):
        parts.append(builders[sid])
        parts.append("\n")

    registry = "BATCH15_SCREEN_BUILDERS: dict[str, Any] = {\n"
    for sid in sorted(builders):
        registry += f'    "{sid}": {fn_name(sid)},\n'
    registry += "}\n"
    parts.append(registry)
    parts.append(
        textwrap.dedent(
            """\

            def _register_batch15_via_finisher() -> None:
                from app.core import screen_definitions_finisher as finisher

                for key, builder in BATCH15_SCREEN_BUILDERS.items():
                    finisher.FINISHER_SCREEN_BUILDERS.setdefault(key, builder)


            _register_batch15_via_finisher()
            """
        )
    )

    OUT_PY.write_text("".join(parts), encoding="utf-8")

    sd_text = SCREEN_DEF.read_text(encoding="utf-8")
    if "screen_definitions_domain_batch15" not in sd_text:
        sd_text = sd_text.replace(
            "from app.core.screen_definitions_cockpit import COCKPIT_SCREEN_BUILDERS\n",
            "from app.core.screen_definitions_cockpit import COCKPIT_SCREEN_BUILDERS\n"
            "from app.core.screen_definitions_domain_batch15 import BATCH15_SCREEN_BUILDERS\n",
        )
        sd_text = sd_text.replace(
            "    **COCKPIT_SCREEN_BUILDERS,\n}",
            "    **COCKPIT_SCREEN_BUILDERS,\n    **BATCH15_SCREEN_BUILDERS,\n}",
        )
        SCREEN_DEF.write_text(sd_text, encoding="utf-8")

    print(
        json.dumps(
            {
                "routable_batch15": len(routes),
                "new_builders": len(builders),
                "tsx_migrated": migrated,
                "skipped_existing_registry": skipped_existing,
                "skipped_no_openapi_get": skipped_no_api,
                "families": dict(family_counts),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
