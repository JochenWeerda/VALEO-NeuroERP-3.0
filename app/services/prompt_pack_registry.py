"""
Prompt Pack Registry -- NC-G5
In-memory registry for versioned prompt packs with A/B traffic split.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from app.agents.neuroassist_contracts import PromptPack

_IN_MEMORY_PROMPT_PACKS: dict[str, list[dict]] = {}


def register_prompt_pack(
    prompt_pack: PromptPack,
    version: str = "1.0",
    tenant_id: str = "system",
    variant_key: str | None = None,
    traffic_weight: float | None = None,
) -> dict:
    entry = {
        "id": str(uuid4()),
        "prompt_pack_key": prompt_pack.prompt_pack_key,
        "role_key": prompt_pack.role_key,
        "version": version,
        "prompt_pack": prompt_pack.model_dump(mode="json"),
        "tenant_id": tenant_id,
        "active": True,
        "variant_key": variant_key,
        "traffic_weight": traffic_weight,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if prompt_pack.prompt_pack_key not in _IN_MEMORY_PROMPT_PACKS:
        _IN_MEMORY_PROMPT_PACKS[prompt_pack.prompt_pack_key] = []

    if variant_key:
        for p in _IN_MEMORY_PROMPT_PACKS[prompt_pack.prompt_pack_key]:
            if p.get("variant_key") == variant_key and p.get("tenant_id") == tenant_id:
                p["active"] = False
    else:
        for p in _IN_MEMORY_PROMPT_PACKS[prompt_pack.prompt_pack_key]:
            if p.get("tenant_id") == tenant_id:
                p["active"] = False

    _IN_MEMORY_PROMPT_PACKS[prompt_pack.prompt_pack_key].append(entry)
    return entry


def list_prompt_packs(tenant_id: str = "system") -> list[dict]:
    result = []
    for versions in _IN_MEMORY_PROMPT_PACKS.values():
        for v in versions:
            if v.get("tenant_id") == tenant_id:
                result.append(v)
    return result


def get_active_prompt_pack(prompt_pack_key: str, tenant_id: str = "system") -> Optional[dict]:
    versions = _IN_MEMORY_PROMPT_PACKS.get(prompt_pack_key, [])
    for v in reversed(versions):
        if v.get("active") and v.get("tenant_id") == tenant_id:
            return v
    return None


def list_active_variants(prompt_pack_key: str, tenant_id: str = "system") -> list[dict]:
    versions = _IN_MEMORY_PROMPT_PACKS.get(prompt_pack_key, [])
    return [
        v for v in versions
        if v.get("active") and v.get("tenant_id") == tenant_id
    ]


def select_prompt_pack_variant(
    prompt_pack_key: str,
    tenant_id: str = "system",
    seed: str | None = None,
) -> Optional[dict]:
    variants = list_active_variants(prompt_pack_key, tenant_id)
    if not variants:
        return None

    weighted = []
    for variant in variants:
        weight = variant.get("traffic_weight")
        if weight is None:
            weight = 1.0
        weighted.append((variant, max(0.0, float(weight))))

    total = sum(w for _, w in weighted)
    if total <= 0:
        return variants[0]

    if seed:
        digest = hashlib.sha256(seed.encode()).hexdigest()
        roll = int(digest, 16) / float(2**256)
    else:
        from random import random

        roll = random()

    threshold = roll * total
    running = 0.0
    for variant, weight in weighted:
        running += weight
        if threshold <= running:
            return variant
    return weighted[-1][0]


def rollback_prompt_pack(prompt_pack_key: str, tenant_id: str = "system") -> Optional[dict]:
    versions = _IN_MEMORY_PROMPT_PACKS.get(prompt_pack_key, [])
    tenant_versions = [v for v in versions if v.get("tenant_id") == tenant_id]
    if len(tenant_versions) < 2:
        return None

    for v in tenant_versions:
        v["active"] = False
    tenant_versions[-2]["active"] = True
    return tenant_versions[-2]
