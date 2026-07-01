"""
UIX-051: Legacy-Routen auf native ScreenDefinitions umgehängt.

Prüft:
- Alle 26 SDs haben eine /:id-Route in route-aliases.json
- Neue native Wrapper-Pages vorhanden (customer-360, supplier, opportunity, article-stock)
- Routen zeigen auf *-native.tsx oder UniversalNativeDetailPage-Wrapper
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).parent.parent
ROUTE_ALIASES = ROOT / "packages/frontend-web/src/app/route-aliases.json"
PAGES_DIR = ROOT / "packages/frontend-web/src/pages"


def _load_aliases() -> list[dict]:
    with ROUTE_ALIASES.open(encoding="utf-8") as f:
        data = json.load(f)
    return data.get("aliases", [])


def _native_modules(aliases: list[dict]) -> set[str]:
    return {a["module"] for a in aliases if "native" in a.get("module", "")}


class TestUIX051NativeWrapperPages:
    """Die 4 neuen native Wrapper-Pages müssen existieren."""

    @pytest.mark.parametrize("rel_path", [
        "crm/customer-360-native.tsx",
        "einkauf/supplier-native.tsx",
        "crm/opportunity-native.tsx",
        "lager/article-stock-native.tsx",
        "sales/sales-order-native.tsx",
        "agrar/kontrakt-native.tsx",
    ])
    def test_native_page_file_exists(self, rel_path: str):
        page = PAGES_DIR / rel_path
        assert page.exists(), f"Native-Page fehlt: {page}"

    @pytest.mark.parametrize("rel_path,expected_screen_id", [
        ("crm/customer-360-native.tsx", "crm/customer-360"),
        ("einkauf/supplier-native.tsx", "einkauf/supplier"),
        ("crm/opportunity-native.tsx", "crm/opportunity"),
        ("lager/article-stock-native.tsx", "lager/article-stock"),
        ("sales/sales-order-native.tsx", "sales/sales-order"),
        ("agrar/kontrakt-native.tsx", "agrar/kontrakte"),
    ])
    def test_native_page_uses_correct_screen_id(self, rel_path: str, expected_screen_id: str):
        content = (PAGES_DIR / rel_path).read_text(encoding="utf-8")
        assert "UniversalNativeDetailPage" in content, f"{rel_path}: muss UniversalNativeDetailPage verwenden"
        assert f'screenId="{expected_screen_id}"' in content, (
            f"{rel_path}: screenId='{expected_screen_id}' fehlt"
        )


class TestUIX051RouteAliases:
    """Alle 4 neuen /:id-Routen müssen in route-aliases.json eingetragen sein."""

    @pytest.mark.parametrize("path,expected_module_fragment", [
        ("crm/customer-360/:id", "customer-360-native"),
        ("crm/kunden/:id", "customer-360-native"),
        ("einkauf/supplier/:id", "supplier-native"),
        ("einkauf/lieferanten/:id", "supplier-native"),
        ("crm/opportunity/:id", "opportunity-native"),
        ("lager/article-stock/:id", "article-stock-native"),
        ("lager/artikel/:id", "article-stock-native"),
        ("sales/sales-order/:id", "sales-order-native"),
        ("agrar/kontrakt/:id", "kontrakt-native"),
        ("agrar/kontrakte/:id", "kontrakt-native"),
    ])
    def test_route_alias_registered(self, path: str, expected_module_fragment: str):
        aliases = _load_aliases()
        matching = [a for a in aliases if a.get("path") == path]
        assert matching, f"Route '{path}' nicht in route-aliases.json gefunden"
        modules = [a.get("module", "") for a in matching]
        assert any(expected_module_fragment in m for m in modules), (
            f"Route '{path}' zeigt nicht auf '{expected_module_fragment}': {modules}"
        )


class TestUIX051AllSDs26Routes:
    """Alle 26 nativen SDs haben mindestens eine /:id-Route."""

    EXPECTED_ROUTES = [
        ("crm/customer-360", "crm/customer-360/:id"),
        ("crm/lead", "crm/lead/:id"),
        ("crm/opportunity", "crm/opportunity/:id"),
        ("einkauf/supplier", "einkauf/supplier/:id"),
        ("einkauf/purchase-order", "einkauf/bestellung/:id"),
        ("einkauf/anfrage", "einkauf/anfrage/:id"),
        ("einkauf/angebot", "einkauf/angebot/:id"),
        ("einkauf/anlieferavis", "einkauf/anlieferavis/:id"),
        ("einkauf/auftragsbestaetigung", "einkauf/auftragsbestaetigung/:id"),
        ("finance/ap-invoice", "finance/ap-invoice/:id"),
        ("finance/ar-open-item", "finance/ar-open-item/:id"),
        ("finance/payment-run", "finance/payment-run/:id"),
        ("finance/debitor", "finance/debitor/:id"),
        ("finance/kreditor", "finance/kreditor/:id"),
        ("finance/bankkonto", "finance/bankkonto/:id"),
        ("lager/article-stock", "lager/article-stock/:id"),
        ("lager/stock-movement", "lager/stock-movement/:id"),
        ("sales/delivery-note", "sales/delivery-note/:id"),
        ("agrar/harvest-settlement", "agrar/harvest-settlement/:id"),
        ("agrar/kontrakte", "agrar/kontrakt/:id"),
        ("agrar/duenger", "agrar/duenger/:id"),
        ("agrar/saatgut", "agrar/saatgut/:id"),
        ("sales/sales-order", "sales/sales-order/:id"),
        ("qualitaet/reklamation", "qualitaet/reklamation/:id"),
        ("futtermittel/einzelfuttermittel", "futtermittel/einzelfuttermittel/:id"),
        ("futtermittel/mischfuttermittel", "futtermittel/mischfuttermittel/:id"),
    ]

    @pytest.mark.parametrize("screen_id,expected_path", EXPECTED_ROUTES)
    def test_sd_has_id_route(self, screen_id: str, expected_path: str):
        aliases = _load_aliases()
        paths = {a.get("path") for a in aliases}
        assert expected_path in paths, (
            f"ScreenDefinition '{screen_id}': Route '{expected_path}' fehlt in route-aliases.json"
        )

    def test_total_native_module_count(self):
        """Mindestens 26 verschiedene *-native Module registriert (alle 26 SDs)."""
        aliases = _load_aliases()
        native = _native_modules(aliases)
        assert len(native) >= 26, f"Erwartet ≥26 native Module, gefunden: {len(native)}: {sorted(native)}"
