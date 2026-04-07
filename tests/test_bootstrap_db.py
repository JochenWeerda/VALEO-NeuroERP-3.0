from __future__ import annotations

from pathlib import Path

import pytest

from scripts.bootstrap_db import (
    confirmation_token_for_env,
    export_superglue_onboarding_bundle,
    validate_force_request,
)


def test_confirmation_token_for_environment():
    assert confirmation_token_for_env("development") == "DELETE-DEVELOPMENT"
    assert confirmation_token_for_env("production") == "DELETE-PRODUCTION"


def test_validate_force_request_rejects_nonempty_db_without_force():
    args = type(
        "Args",
        (),
        {"force": False, "confirm": None, "allow_prod_force": False},
    )()

    with pytest.raises(SystemExit) as exc:
        validate_force_request(args, "development", 3)

    assert exc.value.code == 1


def test_validate_force_request_rejects_production_without_override():
    args = type(
        "Args",
        (),
        {"force": True, "confirm": "DELETE-PRODUCTION", "allow_prod_force": False},
    )()

    with pytest.raises(SystemExit) as exc:
        validate_force_request(args, "production", 1)

    assert exc.value.code == 1


def test_export_superglue_onboarding_bundle_writes_expected_artifacts(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "scripts.bootstrap_db.render_superglue_onboarding_pack_json",
        lambda tenant_id: f'{{"tenant":"{tenant_id}"}}\n',
    )
    monkeypatch.setattr(
        "scripts.bootstrap_db.render_superglue_onboarding_env_template",
        lambda tenant_id: f"TENANT={tenant_id}\n",
    )
    monkeypatch.setattr(
        "scripts.bootstrap_db.render_superglue_onboarding_vault_template",
        lambda tenant_id: f"[tenant:{tenant_id}]\n",
    )

    artifacts = export_superglue_onboarding_bundle("tenant-a", tmp_path)

    assert set(artifacts) == {"json", "env", "vault"}
    assert (tmp_path / "superglue-onboarding.json").read_text(encoding="utf-8") == '{"tenant":"tenant-a"}\n'
    assert (tmp_path / "superglue-onboarding.env").read_text(encoding="utf-8") == "TENANT=tenant-a\n"
    assert (tmp_path / "superglue-onboarding.vault").read_text(encoding="utf-8") == "[tenant:tenant-a]\n"
