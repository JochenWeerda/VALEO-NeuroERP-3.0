import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tools.apply_batch12_kontrolle_migration as m  # noqa: E402

print("const BATCH12: Array<[string, string, string]> = [")
for p in m.PAGES_LIST:
    sid = m.page_to_screen_id(p)
    comp = "UniversalNativeCockpitPage" if sid in m.COCKPIT_SCREENS else "NativeListPage"
    print(f"  ['{p}', '{sid}', '{comp}'],")
print("]")
