import asyncio
from datetime import datetime, timezone

import pytest

from app.agrar.rations.integrations.herd_data import (
    normalize_genetic_profiles,
    normalize_group_kpis,
    normalize_health_alerts,
)
from app.api.v1.endpoints.rations_integrations import HerdDataConnectionIn
from app.services.rations_herd_data_sync_service import (
    HerdDataConnection,
    HerdDataSyncBlocked,
    HerdDataSyncService,
    validate_connection_for_live,
)

GROUP_KPI = {
    "herd_id": "US-WI-99482",
    "sync_timestamp": "2026-07-14T02:15:00Z",
    "currency_date": "2026-07-13",
    "group_metrics": [{
        "group_id": "4", "group_name": "High Yielding Fresh Cows", "cow_count": 142,
        "kpis": {"avg_milk_yield_kg": 42.5, "dry_matter_intake_kg_actual": 23.8},
    }],
}
HEALTH = {
    "herd_id": "US-WI-99482", "sync_timestamp": "2026-07-14T02:15:00Z",
    "alerts": [{"alert_id": "risk-1", "animal_id": "DDW-7740192", "group_id": "4",
                "previous_group_id": "3", "updated_at": "2026-07-14T01:00:00Z",
                "predicta_health_score": "High Risk", "predicted_conditions": [{"disease": "Subclinical Ketosis", "probability": 0.84}]},
               {"alert_id": "risk-2", "animal_id": "DDW-removed", "event_type": "culled",
                "updated_at": "2026-07-14T01:10:00Z"}],
}
GENETICS = {
    "herd_id": "US-WI-99482", "sync_timestamp": "2026-07-14T02:15:00Z",
    "animals": [{"animal_id": "DDW-8830114", "birth_date": "2024-03-12", "breed": "HO",
                 "pedigree": {"sire_naab_code": "007HO15123", "dam_id": "DDW-5510482"}}],
}


def _connection(**overrides) -> HerdDataConnection:
    values = dict(
        id="conn-1", tenant_id="tenant-a", provider="ddw", herd_id="US-WI-99482",
        base_url="https://api.dairydatawarehouse.com",
        endpoint_templates={
            "group_kpi": "/mock/{herd_id}/kpis",
            "health_alert": "/mock/{herd_id}/health-alerts",
            "genetic_profile": "/mock/{herd_id}/genetic-profiles",
        },
        query_parameters={"group_kpi": "date", "health_alert": "updated_since", "genetic_profile": "updated_since"},
        credential_env_key="DDW_HERD_DATA_TOKEN", contract_ref="contract-42", consent_ref="consent-17",
        enabled=True, live_enabled=True,
    )
    values.update(overrides)
    return HerdDataConnection(**values)


def test_ddw_payloads_normalize_to_canonical_observations():
    kpi = normalize_group_kpis(GROUP_KPI)[0]
    health = normalize_health_alerts(HEALTH)
    genetics = normalize_genetic_profiles(GENETICS)[0]

    assert kpi.kind == "group_kpi" and kpi.group_id == "4"
    assert kpi.payload["kpis"]["avg_milk_yield_kg"] == 42.5
    assert health[0].previous_group_id == "3"
    assert health[1].deleted is True
    assert genetics.entity_id == "DDW-8830114"
    assert genetics.payload["pedigree"]["sire_naab_code"] == "007HO15123"


def test_connection_contract_rejects_missing_or_absolute_templates():
    with pytest.raises(ValueError, match="Endpoint-Templates"):
        HerdDataConnectionIn(
            herd_id="h1", base_url="https://api.example.com", endpoint_templates={"group_kpi": "/kpi"},
            contract_ref="c", consent_ref="x",
        )
    with pytest.raises(ValueError, match="relative Pfade"):
        HerdDataConnectionIn(
            herd_id="h1", base_url="https://api.example.com",
            endpoint_templates={"group_kpi": "https://evil.example/kpi", "health_alert": "/h", "genetic_profile": "/g"},
            contract_ref="c", consent_ref="x",
        )


def test_live_gate_requires_contract_consent_and_secret(monkeypatch):
    monkeypatch.delenv("DDW_HERD_DATA_TOKEN", raising=False)
    with pytest.raises(HerdDataSyncBlocked, match="Vertrags- und Einwilligungsreferenz"):
        validate_connection_for_live(_connection(consent_ref=""))
    with pytest.raises(HerdDataSyncBlocked, match="Credential-Secret fehlt"):
        validate_connection_for_live(_connection())


def test_delta_fetch_uses_configured_paths_and_query_names(monkeypatch):
    monkeypatch.setenv("DDW_HERD_DATA_TOKEN", "test-token")
    monkeypatch.setenv("HERD_DATA_ALLOWED_DOMAINS", "dairydatawarehouse.com")
    calls = []

    async def transport(url, headers, params):
        calls.append((url, headers, params))
        if url.endswith("/kpis"):
            return GROUP_KPI
        if url.endswith("/health-alerts"):
            return HEALTH
        return GENETICS

    service = HerdDataSyncService(None, transport=transport)
    result = asyncio.run(service.fetch_delta(
        _connection(), updated_since=datetime(2026, 7, 13, tzinfo=timezone.utc)
    ))

    assert len(result) == 4
    assert [set(call[2]) for call in calls] == [
        {"date"}, {"updated_since"}, {"updated_since"}
    ]
    assert all(call[1]["Authorization"] == "Bearer test-token" for call in calls)
