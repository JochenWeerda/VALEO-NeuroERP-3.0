"""
UIX-054: Finale Route-Wahrheit nach UIX-051 prüfen.

Nicht nur route-aliases.json, sondern das generierte Ergebnis:
  - route-inventory.gen.json (deduplizierte Gewinner-Routen)
  - route-tree.gen.tsx (TanStack-Modul-Verdrahtung)

Abnahme-Pfade müssen auf *-native Module zeigen; bei doppelten Alias-Einträgen
gewinnt native (candidatePriority in generate-tanstack-routes.mjs).
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).parent.parent
ROUTE_ALIASES = ROOT / "packages/frontend-web/src/app/route-aliases.json"
ROUTE_INVENTORY = ROOT / "packages/frontend-web/src/app/routing/route-inventory.gen.json"
ROUTE_TREE = ROOT / "packages/frontend-web/src/app/routing/route-tree.gen.tsx"

# screen_id, inventory path, erwarteter Modul-Fragment (*-native)
EXPECTED_SD_ROUTES: list[tuple[str, str, str]] = [
    ("crm/customer-360", "crm/customer-360/:id", "customer-360-native"),
    ("crm/customer-360", "crm/kunden/:id", "customer-360-native"),
    ("crm/lead", "crm/lead/:id", "lead-native"),
    ("crm/opportunity", "crm/opportunity/:id", "opportunity-native"),
    ("einkauf/supplier", "einkauf/supplier/:id", "supplier-native"),
    ("einkauf/supplier", "einkauf/lieferanten/:id", "supplier-native"),
    ("einkauf/purchase-order", "einkauf/bestellung/:id", "bestellung-native"),
    ("einkauf/anfrage", "einkauf/anfrage/:id", "anfrage-native"),
    ("einkauf/angebot", "einkauf/angebot/:id", "angebot-native"),
    ("einkauf/anlieferavis", "einkauf/anlieferavis/:id", "anlieferavis-native"),
    ("einkauf/auftragsbestaetigung", "einkauf/auftragsbestaetigung/:id", "auftragsbestaetigung-native"),
    ("finance/ap-invoice", "finance/ap-invoice/:id", "ap-invoice-native"),
    ("finance/ar-open-item", "finance/ar-open-item/:id", "ar-open-item-native"),
    ("finance/payment-run", "finance/payment-run/:id", "payment-run-native"),
    ("finance/debitor", "finance/debitor/:id", "debitor-native"),
    ("finance/kreditor", "finance/kreditor/:id", "kreditor-native"),
    ("finance/bankkonto", "finance/bankkonto/:id", "bankkonto-native"),
    ("lager/article-stock", "lager/article-stock/:id", "article-stock-native"),
    ("lager/article-stock", "lager/artikel/:id", "article-stock-native"),
    ("lager/stock-movement", "lager/stock-movement/:id", "lagerbewegung-native"),
    ("sales/delivery-note", "sales/delivery-note/:id", "lieferschein-native"),
    ("agrar/harvest-settlement", "agrar/harvest-settlement/:id", "ernte-abrechnung-native"),
    ("agrar/kontrakte", "agrar/kontrakt/:id", "kontrakt-native"),
    ("agrar/kontrakte", "agrar/kontrakte/:id", "kontrakt-native"),
    ("agrar/duenger", "agrar/duenger/:id", "duenger-native"),
    ("agrar/saatgut", "agrar/saatgut/:id", "saatgut-native"),
    ("sales/sales-order", "sales/sales-order/:id", "sales-order-native"),
    ("qualitaet/reklamation", "qualitaet/reklamation/:id", "reklamation-native"),
    ("futtermittel/einzelfuttermittel", "futtermittel/einzelfuttermittel/:id", "einzelfuttermittel-native"),
    ("futtermittel/mischfuttermittel", "futtermittel/mischfuttermittel/:id", "mischfuttermittel-native"),
]

ACCEPTANCE_ROUTES: list[tuple[str, str]] = [
    ("crm/kunden/:id", "customer-360-native"),
    ("einkauf/lieferanten/:id", "supplier-native"),
    ("crm/opportunity/:id", "opportunity-native"),
    ("sales/sales-order/:id", "sales-order-native"),
    ("agrar/kontrakt/:id", "kontrakt-native"),
]


def _load_aliases() -> list[dict]:
    with ROUTE_ALIASES.open(encoding="utf-8") as f:
        return json.load(f).get("aliases", [])


def _inventory_by_path() -> dict[str, dict]:
    data = json.loads(ROUTE_INVENTORY.read_text(encoding="utf-8"))
    return {r["path"]: r for r in data.get("routes", [])}


def _is_native_module(module: str) -> bool:
    return module.endswith("-native") or "-native" in module.split("/")[-1]


class TestUIX054RouteInventoryExists:
    def test_generated_inventory_file_present(self):
        assert ROUTE_INVENTORY.is_file(), "route-inventory.gen.json fehlt — npm run routes:generate ausführen"

    def test_generated_route_tree_present(self):
        assert ROUTE_TREE.is_file(), "route-tree.gen.tsx fehlt — npm run routes:generate ausführen"

    def test_inventory_paths_are_unique(self):
        paths = [r["path"] for r in json.loads(ROUTE_INVENTORY.read_text(encoding="utf-8")).get("routes", [])]
        dupes = [p for p, c in Counter(paths).items() if c > 1]
        assert not dupes, f"Doppelte Pfade in route-inventory.gen.json: {dupes[:10]}"


class TestUIX054AcceptanceRoutes:
    @pytest.mark.parametrize("path,fragment", ACCEPTANCE_ROUTES)
    def test_inventory_resolves_to_native(self, path: str, fragment: str):
        inv = _inventory_by_path()
        assert path in inv, f"Pfad '{path}' fehlt in route-inventory.gen.json"
        module = inv[path]["module"]
        assert fragment in module, f"{path} → {module}, erwartet Fragment '{fragment}'"
        assert _is_native_module(module)

    @pytest.mark.parametrize("path,fragment", ACCEPTANCE_ROUTES)
    def test_route_tree_wires_native_module(self, path: str, fragment: str):
        tree = ROUTE_TREE.read_text(encoding="utf-8")
        legacy_snippet = f'"legacyPath":"/{path}"'
        assert legacy_snippet in tree, f"route-tree.gen.tsx: {legacy_snippet} fehlt"
        idx = tree.index(legacy_snippet)
        window = tree[max(0, idx - 120) : idx + 120]
        assert fragment in window, f"route-tree.gen.tsx: Modul '{fragment}' fehlt bei /{path}"


class TestUIX054All26ScreenDefinitions:
    @pytest.mark.parametrize("screen_id,path,fragment", EXPECTED_SD_ROUTES)
    def test_sd_route_in_inventory_is_native(self, screen_id: str, path: str, fragment: str):
        inv = _inventory_by_path()
        assert path in inv, f"SD '{screen_id}': Pfad '{path}' fehlt in route-inventory.gen.json"
        module = inv[path]["module"]
        assert fragment in module, (
            f"SD '{screen_id}' / '{path}': inventory module '{module}' enthält nicht '{fragment}'"
        )
        assert _is_native_module(module), f"SD '{screen_id}': kein natives Modul: {module}"

    def test_at_least_26_distinct_native_detail_paths(self):
        inv = _inventory_by_path()
        native_detail = {
            p
            for p, r in inv.items()
            if ":id" in p and _is_native_module(r.get("module", ""))
        }
        assert len(native_detail) >= 26, f"Erwartet ≥26 native /:id-Routen, gefunden: {len(native_detail)}"


class TestUIX054DuplicateAliasPrioritization:
    def test_duplicate_alias_paths_resolve_native_in_inventory(self):
        aliases = _load_aliases()
        by_path: dict[str, list[str]] = defaultdict(list)
        for entry in aliases:
            path = entry.get("path")
            module = entry.get("module", "")
            if path and ":id" in path:
                by_path[path].append(module)

        duplicates = {p: mods for p, mods in by_path.items() if len(mods) > 1}
        assert duplicates, "Keine doppelten /:id-Alias-Pfade gefunden — Test unvollständig"

        inv = _inventory_by_path()
        failures: list[str] = []
        for path, modules in sorted(duplicates.items()):
            if path not in inv:
                failures.append(f"{path}: fehlt in inventory (Alias-Module: {modules})")
                continue
            winner = inv[path]["module"]
            has_native_alias = any("native" in m for m in modules)
            has_legacy_alias = any("native" not in m for m in modules)
            if has_native_alias and has_legacy_alias and not _is_native_module(winner):
                failures.append(
                    f"{path}: inventory='{winner}' gewinnt vor native Alias {modules}"
                )

        assert not failures, "Native-Priorisierung fehlgeschlagen:\n" + "\n".join(failures[:20])

    def test_known_legacy_competitors_lose(self):
        """Explizite Regression: lead-detail / opportunity-detail vs *-native."""
        inv = _inventory_by_path()
        checks = [
            ("crm/lead/:id", "lead-native", "lead-detail"),
            ("crm/opportunity/:id", "opportunity-native", "opportunity-detail"),
            ("crm/kunden/:id", "customer-360-native", "kunden-stamm"),
        ]
        for path, native_frag, legacy_frag in checks:
            module = inv[path]["module"]
            assert native_frag in module
            assert legacy_frag not in module


class TestUIX054InventoryMatchesGeneratorExport:
    def test_route_tree_embeds_inventory_count(self):
        inv_count = len(json.loads(ROUTE_INVENTORY.read_text(encoding="utf-8")).get("routes", []))
        tree = ROUTE_TREE.read_text(encoding="utf-8")
        match = re.search(r"generatedRouteInventory = (\[[\s\S]*?\]) as const", tree)
        assert match, "generatedRouteInventory fehlt in route-tree.gen.tsx"
        embedded = json.loads(match.group(1))
        assert len(embedded) == inv_count
