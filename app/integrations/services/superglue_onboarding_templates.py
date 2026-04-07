"""Render human-usable onboarding artifacts from the Superglue onboarding pack."""

from __future__ import annotations

import json

from app.integrations.services.superglue_onboarding_pack import build_superglue_onboarding_pack


def render_superglue_onboarding_pack_json(tenant_id: str) -> str:
    return json.dumps(build_superglue_onboarding_pack(tenant_id), indent=2, ensure_ascii=True) + "\n"


def render_superglue_onboarding_env_template(tenant_id: str) -> str:
    pack = build_superglue_onboarding_pack(tenant_id)
    lines = [
        f"# Superglue onboarding env template for tenant {tenant_id}",
        f"# Environment: {pack['environment']}",
        "",
    ]
    for key in pack["platform_secret_keys"]["AUTH_TOKEN"]:
        lines.append(f"{key}=")
    lines.append("")
    for connector in pack["connectors"]:
        lines.append(f"# {connector['display_name']} ({connector['connector_key']})")
        for field, candidates in connector["secret_keys"].items():
            if not candidates:
                continue
            lines.append(f"{candidates[0]}=")
        lines.append("")
    for key, value in pack["policy_keys"].items():
        lines.append(f"{key}={value}")
    return "\n".join(lines).rstrip() + "\n"


def render_superglue_onboarding_vault_template(tenant_id: str) -> str:
    pack = build_superglue_onboarding_pack(tenant_id)
    lines = [
        f"# Superglue onboarding vault mapping for tenant {tenant_id}",
        f"# Prefix: {pack['vault_path_prefix']}",
        "",
        f"[tenant:{tenant_id}]",
    ]
    for key, candidates in pack["platform_secret_keys"].items():
        lines.append(f"{key}={','.join(candidates)}")
    lines.append("")
    for connector in pack["connectors"]:
        lines.append(f"[connector:{connector['connector_key']}]")
        for field, candidates in connector["secret_keys"].items():
            lines.append(f"{field}={','.join(candidates)}")
        lines.append("")
    for key, value in pack["policy_keys"].items():
        lines.append(f"{key}={value}")
    return "\n".join(lines).rstrip() + "\n"
