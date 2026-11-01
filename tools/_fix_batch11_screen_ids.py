import runpy
from pathlib import Path

m = runpy.run_path("tools/apply_batch11_listen_migration.py")
BATCH11 = m["BATCH11"]
root = Path("packages/frontend-web/src/pages")

# ackerschlag uses schlagkartei screen id
ALIASES = {
    "agrar/feldbuch/ackerschlagkartei.tsx": "agrar/feldbuch-schlagkartei-liste",
}

for page, screen_id, route_path, spec in BATCH11:
    screen_id = ALIASES.get(page, screen_id)
    rel = root / page
    if not rel.exists():
        continue
    title = spec["title"]
    comp_hint = page.replace(".tsx", "").split("/")[-1]
    content = (
        "import { NativeListPage } from '@/components/mask-builder/NativeListPage'\n\n"
        f"/** {title} aus der ScreenDefinition `{screen_id}`. */\n"
        f"export default function Batch11ListPage(): JSX.Element {{\n"
        "  return (\n"
        f'    <NativeListPage screenId="{screen_id}" testId="screen-{screen_id}" />\n'
        "  )\n"
        "}\n"
    )
    rel.write_text(content, encoding="utf-8")

print("rewrote batch11 pages")
