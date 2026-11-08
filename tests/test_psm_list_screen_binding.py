"""The routed PSM list must request a real definition and its BVL read source."""
import json
import re
from pathlib import Path
from app.core.screen_definitions import get_screen_definition

def test_routed_psm_list_uses_registered_bvl_definition():
    page = Path(__file__).resolve().parents[1] / "packages/frontend-web/src/pages/agrar/psm/liste.tsx"
    source = page.read_text(encoding="utf-8")
    match = re.search(r'<NativeListPage\s+screenId="([^"]+)"', source)
    assert match is not None
    definition = get_screen_definition(match.group(1))
    assert definition is not None, "Routed PSM list requests a missing ScreenDefinition"
    assert definition["id"] == "agrar/psm-liste"
    assert "source=bvl" in json.dumps(definition.get("dataSources"), ensure_ascii=False)
