"""UIX-091: Prozessketten-Katalog an ScreenDefinitions haengen.

Liest config/process_chains.yaml unveraendert. Keine zweite Kette, kein
Instanzfortschritt. Routen kommen aus der bestehenden Listen-Bruecke.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONFIG = _REPO_ROOT / "config" / "process_chains.yaml"

PROCESS_CHAIN_DOMAINS = frozenset({"sales", "einkauf", "finance", "agrar"})
PROCESS_CHAIN_MODES = frozenset({"detail", "transaction"})

RouteResolver = Callable[[str], str | None]


@lru_cache(maxsize=1)
def load_process_chains() -> dict[str, Any]:
    return yaml.safe_load(_CONFIG.read_text(encoding="utf-8")) or {}


def membership_for(screen_id: str) -> dict[str, str] | None:
    chains = load_process_chains().get("chains") or {}
    for chain_id, chain in chains.items():
        for step in (chain or {}).get("steps") or []:
            if step.get("screenId") == screen_id:
                key = str(step.get("key") or "").strip()
                if key:
                    return {"chainId": str(chain_id), "stepKey": key}
    return None


def build_catalog(resolve_route: RouteResolver) -> dict[str, Any]:
    chains = load_process_chains().get("chains") or {}
    catalog: dict[str, Any] = {}
    for chain_id, chain in chains.items():
        steps: list[dict[str, str]] = []
        for step in (chain or {}).get("steps") or []:
            screen_id = str(step.get("screenId") or "")
            item: dict[str, str] = {
                "key": str(step.get("key") or ""),
                "label": str(step.get("label") or ""),
                "screenId": screen_id,
            }
            route = resolve_route(screen_id) if screen_id else None
            if route:
                item["routePath"] = route
            steps.append(item)
        catalog[str(chain_id)] = {
            "label": str((chain or {}).get("label") or chain_id),
            "steps": steps,
        }
    return catalog


def needs_process_chain(definition: dict[str, Any]) -> bool:
    return (
        str(definition.get("domain") or "") in PROCESS_CHAIN_DOMAINS
        and str(definition.get("mode") or "") in PROCESS_CHAIN_MODES
    )


def attach_process_chain(definition: dict[str, Any], resolve_route: RouteResolver) -> None:
    """Additives Anreichern — vorhandene processChain-Felder bleiben stehen."""
    definition["processChains"] = build_catalog(resolve_route)
    hit = membership_for(str(definition.get("id") or ""))
    if hit:
        definition.setdefault("processChain", hit)
