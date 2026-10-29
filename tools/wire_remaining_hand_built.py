"""Wire remaining hand_built pages to runtime wrappers (completion audit)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.mask_route_migration_inventory import classify_source  # noqa: E402

PAGES = ROOT / "packages" / "frontend-web" / "src" / "pages"
FE = ROOT / "packages" / "frontend-web"

RUNTIME_EXEMPT = {
    PAGES / "errors" / "NotFound.tsx",
    FE / "src" / "app" / "FibuSuiteRuntime.tsx",
}

SCREEN_BY_REL: dict[str, tuple[str, str]] = {
    "agrar/aussaat/liste.tsx": ("list", "agrar/aussaat-liste"),
    "schichtplan/liste.tsx": ("list", "schichtplan/liste"),
    "lager/bestandsuebersicht.tsx": ("list", "lager/bestandsuebersicht-liste"),
    "energie/verbrauch.tsx": ("cockpit", "energie/verbrauch"),
    "einkauf/lieferschein-erfassung.tsx": ("detail", "einkauf/lieferschein-erfassung"),
    "verkauf/lieferschein-erfassung.tsx": ("detail", "sales/delivery-note-capture"),
    "futtermittel/rationsoptimierung.tsx": ("cockpit", "futtermittel/rationsoptimierung"),
    "produktion/mischfutter-produktion.tsx": ("cockpit", "produktion/mischfutter-produktion"),
    "workflow/mask-rollout/MaskRolloutRoute.tsx": ("rollout", ""),
}


def _list_tsx(screen_id: str) -> str:
    return (
        "import { NativeListPage } from '@/components/mask-builder/NativeListPage'\n\n"
        "export default function Page(): JSX.Element {\n"
        f'  return <NativeListPage screenId="{screen_id}" testId="screen-{screen_id}" />\n'
        "}\n"
    )


def _cockpit_tsx(screen_id: str) -> str:
    tid = screen_id.replace("/", "-")
    return (
        "import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'\n\n"
        "export default function Page(): JSX.Element {\n"
        f'  return <UniversalNativeCockpitPage screenId="{screen_id}" testId="{tid}" />\n'
        "}\n"
    )


def _detail_tsx(screen_id: str) -> str:
    tid = screen_id.replace("/", "-")
    return (
        "import { useParams } from '@/app/routing/typed-router'\n"
        "import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'\n\n"
        "export default function Page(): JSX.Element {\n"
        "  const { id } = useParams<{ id?: string }>()\n"
        f'  return <UniversalNativeDetailPage screenId="{screen_id}" entityId={{id ?? \'new\'}} testId="{tid}" />\n'
        "}\n"
    )


def _legacy_wrap(page: Path, text: str) -> None:
    legacy = page.with_name(page.stem + "-legacy.tsx")
    if not legacy.exists():
        legacy.write_text(text, encoding="utf-8")
    rel_import = "./" + legacy.name.removesuffix(".tsx")
    wrapper = (
        "import { createLegacyMaskPage } from '@/components/mask-builder'\n\n"
        f"export default createLegacyMaskPage(() => import('{rel_import}'))\n"
    )
    page.write_text(wrapper, encoding="utf-8")


def _rollout_tsx() -> str:
    return (
        "import { lazy, Suspense } from 'react'\n"
        "import { Navigate, useParams } from '@/app/routing/typed-router'\n"
        "import { isRolloutPilotEnabled } from '@/features/mask-rollouts/rollout-registry'\n"
        "import { UniversalMaskRolloutPilotPage } from '@/pages/workflow/mask-rollout/UniversalMaskRolloutPilotPage'\n\n"
        "export default function MaskRolloutRoute(): JSX.Element {\n"
        "  const { screenId, entityId } = useParams() as { screenId?: string; entityId?: string }\n"
        "  const normalizedScreenId = screenId?.replace(/__/g, '/')\n"
        "  if (!normalizedScreenId || !entityId) return <Navigate to=\"/\" replace />\n"
        "  if (!isRolloutPilotEnabled(normalizedScreenId)) {\n"
        "    return <div className=\"p-6 text-sm text-muted-foreground\">Rollout Pilot deaktiviert.</div>\n"
        "  }\n"
        "  return (\n"
        "    <Suspense fallback={null}>\n"
        "      <UniversalMaskRolloutPilotPage screenId={normalizedScreenId} entityId={entityId} />\n"
        "    </Suspense>\n"
        "  )\n"
        "}\n"
    )


def main() -> None:
    changed = 0
    for page in sorted(PAGES.rglob("*.tsx")):
        if "__tests__" in str(page) or ".test." in page.name or page.name.endswith("-legacy.tsx"):
            continue
        if page in RUNTIME_EXEMPT:
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        if classify_source(text, filename=page.name) != "hand_built":
            continue
        rel = page.relative_to(PAGES).as_posix()
        spec = SCREEN_BY_REL.get(rel)
        if spec:
            kind, sid = spec
            if kind == "rollout":
                page.write_text(_rollout_tsx(), encoding="utf-8")
            elif kind == "list":
                page.write_text(_list_tsx(sid), encoding="utf-8")
            elif kind == "cockpit":
                page.write_text(_cockpit_tsx(sid), encoding="utf-8")
            elif kind == "detail":
                page.write_text(_detail_tsx(sid), encoding="utf-8")
            changed += 1
            print("mapped", rel)
            continue
        if "export default" in text and len(text) > 200:
            _legacy_wrap(page, text)
            changed += 1
            print("legacy", rel)
    print("changed", changed)


if __name__ == "__main__":
    main()
