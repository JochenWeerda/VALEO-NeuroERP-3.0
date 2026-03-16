from __future__ import annotations

import pytest

from app.core.data_quality_enforcement import DQValidationException
from modules.agrar.services.quality_protocol_service import (
    QualityProtocolCreate,
    create_quality_protocol,
    import_from_csv,
    import_from_json,
)


class FailQualityRepo:
    def get_by_harvest_acceptance(self, *args, **kwargs):
        raise AssertionError("Repository access should not happen before DQ validation")

    def create(self, *args, **kwargs):
        raise AssertionError("Repository create should not happen before DQ validation")


def test_create_quality_protocol_rejects_invalid_payload_before_repo_access():
    payload = QualityProtocolCreate(
        tenant_id="tenant-1",
        harvest_acceptance_id=None,
        source_type="manual",
        moisture_pct=15.5,
    )

    with pytest.raises(DQValidationException) as exc:
        create_quality_protocol(FailQualityRepo(), payload)

    assert exc.value.entity_typ == "Qualitaetsprotokoll"


def test_quality_protocol_csv_import_rejects_invalid_values_before_repo_access():
    csv_content = "moisture_pct,protein_pct,hl_weight_kg_per_hl\n120,12,72\n"

    with pytest.raises(DQValidationException) as exc:
        import_from_csv(
            FailQualityRepo(),
            tenant_id="tenant-1",
            harvest_acceptance_id="HA-1",
            csv_content=csv_content,
            file_name="quality.csv",
            created_by="tester",
        )

    assert exc.value.entity_typ == "Qualitaetsprotokoll"


def test_quality_protocol_json_import_rejects_invalid_values_before_repo_access():
    json_content = '{"moisture_pct": 120, "protein_pct": 12, "hl_weight_kg_per_hl": 72}'

    with pytest.raises(DQValidationException) as exc:
        import_from_json(
            FailQualityRepo(),
            tenant_id="tenant-1",
            harvest_acceptance_id="HA-1",
            json_content=json_content,
            file_name="quality.json",
            created_by="tester",
        )

    assert exc.value.entity_typ == "Qualitaetsprotokoll"
