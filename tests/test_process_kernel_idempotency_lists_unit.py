"""Executable Unit-Tests: Process-Kernel Idempotenz-Listen (Sonar New-Code)."""
from __future__ import annotations

from unittest.mock import patch

from app.api.v1.endpoints import process_kernel_idempotency_lists as pk


def test_idempotency_overview_flacht_kpis():
    overview = {
        "confidence_score": 0.9,
        "recommended_action": "monitor",
        "catalog": {
            "total_commands": 10,
            "idempotent_commands": 8,
            "human_confirmation_commands": 2,
            "agent_ready_commands": 5,
            "idempotent_coverage_pct": 80,
        },
        "store": {
            "total_records": 3,
            "tenant_count": 1,
            "execution_count": 2,
            "command_count": 4,
            "aggregate_count": 1,
            "commands": ["cmd-a", 12, "cmd-b"],
            "aggregates": ["agg-1", None, "agg-2"],
        },
    }
    with patch(
        "app.api.v1.endpoints.process_kernel_idempotency_lists.build_idempotency_overview",
        return_value=overview,
    ) as mock_overview:
        out = pk.get_idempotency_overview(tenant_id="t1")
        assert out["total_commands"] == 10
        assert out["idempotent_coverage_pct"] == 80
        assert out["lookup_paths"][0].endswith("/execute")

        cmds = pk.list_idempotency_commands(tenant_id="t1")
        assert cmds == [{"id": "cmd-a", "name": "cmd-a"}, {"id": "cmd-b", "name": "cmd-b"}]

        aggs = pk.list_idempotency_aggregates(tenant_id="t1")
        assert aggs == [{"id": "agg-1", "name": "agg-1"}, {"id": "agg-2", "name": "agg-2"}]

        assert mock_overview.call_count >= 3

    paths = pk.list_idempotency_lookup_paths(tenant_id="t1")
    assert len(paths) == 3
    assert paths[1]["path"].endswith("{idempotency_key}")
