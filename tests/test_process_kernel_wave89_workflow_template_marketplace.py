from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import workflow_template_marketplace

pytestmark = pytest.mark.usefixtures("require_db")
TEST_TENANT_ID = "system"
from app.core.database import SessionLocal
from app.core.workflow_template_marketplace import (
    build_workflow_template_marketplace_catalog,
    clone_workflow_template,
    install_workflow_template,
    preview_workflow_template_installation,
)


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(workflow_template_marketplace.router)
    app.dependency_overrides[workflow_template_marketplace.get_tenant_id] = lambda: TEST_TENANT_ID

    def _override_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[workflow_template_marketplace.get_db] = _override_db
    return TestClient(app)


def _tenant_settings(tenant_id: str = TEST_TENANT_ID) -> dict:
    with SessionLocal() as db:
        row = db.execute(
            text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
            {"tenant_id": tenant_id},
        ).first()
        if not row or not row[0]:
            return {}
        raw = row[0]
        if isinstance(raw, dict):
            return raw
        return json.loads(raw)


def _snapshot_tenant_settings(tenant_id: str = TEST_TENANT_ID) -> dict:
    return json.loads(json.dumps(_tenant_settings(tenant_id)))


def _restore_tenant_settings(snapshot: dict, tenant_id: str = TEST_TENANT_ID) -> None:
    with SessionLocal() as db:
        db.execute(
            text(
                """
                UPDATE domain_shared.tenants
                SET settings = CAST(:settings AS jsonb),
                    updated_at = NOW()
                WHERE id = :tenant_id
                """
            ),
            {"tenant_id": tenant_id, "settings": json.dumps(snapshot)},
        )
        db.commit()


def test_workflow_template_marketplace_catalog_lists_curated_templates():
    catalog = build_workflow_template_marketplace_catalog()

    assert catalog.template_count >= 4
    assert "agrar" in catalog.categories
    assert catalog.curated_count >= 3
    assert catalog.installable_count >= 3


def test_workflow_template_preview_builds_rollout_steps_and_warnings():
    preview = preview_workflow_template_installation(
        template_id="tpl-ap-approval",
        tenant_id="tenant-1",
        workflow_definition_version="2.0.0",
        context={"approval_matrix": "custom"},
        target_scope="tenant",
        requested_by_role="tenant_admin",
    )

    assert preview.process_key == "ap_invoice_approval"
    assert preview.generated_variant_key.startswith("tenant-1:")
    assert preview.warnings
    assert len(preview.rollout_steps) >= 3
    assert preview.governance.scope.value in {"global", "tenant"}


def test_marketplace_endpoints_cover_list_preview_clone_and_install():
    snapshot = _snapshot_tenant_settings()
    client = _client()

    try:
        listing = client.get("/workflow/templates/marketplace")
        assert listing.status_code == 200
        listing_body = listing.json()
        assert listing_body["template_count"] >= 4
        assert "agrar" in listing_body["categories"]

        detail = client.get("/workflow/templates/marketplace/tpl-complaint-e2e")
        assert detail.status_code == 200
        assert detail.json()["process_key"] == "complaint_e2e"

        publish_preview = client.post(
            "/workflow/templates/marketplace/tpl-ap-approval/publish-preview",
            json={"tenant_id": TEST_TENANT_ID, "requested_by_role": "tenant_admin"},
        )
        assert publish_preview.status_code == 200
        assert publish_preview.json()["recommended_next_action"]

        clone = client.post(
            "/workflow/templates/marketplace/tpl-harvest-campaign/clone",
            json={
                "tenant_id": TEST_TENANT_ID,
                "clone_name": "Erntekampagne Pilot",
                "installed_by": "ops-admin",
                "target_scope": "tenant",
            },
        )
        assert clone.status_code == 200
        assert clone.json()["clone_name"] == "Erntekampagne Pilot"

        install = client.post(
            "/workflow/templates/marketplace/tpl-harvest-campaign/install",
            json={
                "tenant_id": TEST_TENANT_ID,
                "installed_by": "ops-admin",
                "clone_name": "Erntekampagne Pilot",
                "target_scope": "tenant",
                "activate": True,
            },
        )
        assert install.status_code == 200
        install_body = install.json()
        assert install_body["lifecycle_status"] == "installed_pending_review"
        assert "/api/v1/workflow/simulation/preview" in install_body["monitoring_hooks"]

        settings = _tenant_settings(TEST_TENANT_ID)
        assert settings["workflow_template_marketplace_installs"]
        assert settings["workflow_template_library"]["tpl-harvest-campaign"]["clone_name"] == "Erntekampagne Pilot"
    finally:
        _restore_tenant_settings(snapshot)
