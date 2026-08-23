from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.l3_cutover_readiness import (
    ContractError,
    evaluate,
    evidence_template,
    load_yaml,
    run_migration_dry_run,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_yaml(ROOT / "config" / "l3-cutover-uat.yaml")


def approved() -> dict[str, object]:
    return {
        "status": "pass",
        "approver": "UAT Owner",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "artifact": "evidence://signed-protocol/1",
    }


def complete_evidence() -> dict:
    evidence = evidence_template(CONTRACT)
    evidence["role_signoffs"] = {item["id"]: approved() for item in CONTRACT["roles"]}
    evidence["journeys"] = {
        item["id"]: {**approved(), "duration_ratio": 1.0, "error_rate": 0.0}
        for item in CONTRACT["journeys"]
    }
    evidence["integrations"] = {item["id"]: approved() for item in CONTRACT["integrations"]}
    evidence["habit_bridge"] = {item["id"]: approved() for item in CONTRACT["habit_bridge"]}
    for rehearsal in evidence["migration_rehearsals"]:
        rehearsal.update(approved())
        for domain in rehearsal["domains"].values():
            domain.update({
                "status": "pass", "record_count_variance": 0,
                "amount_variance_cents": 0, "quantity_variance": 0,
                "critical_orphans": 0, "checksum": True,
            })
    evidence["metrics"] = {
        "overall_journey_pass_rate": 1.0,
        "median_task_duration_ratio": 1.0,
        "user_error_rate": 0.0,
    }
    evidence["parallel_operation"] = {**approved(), "business_days": 10}
    evidence["go_live_approval"] = approved()
    evidence["repo_probes"] = {
        item["id"]: {"status": "pass", "returncode": 0}
        for item in CONTRACT["repo_probes"]
    }
    return evidence


def test_contract_is_valid_and_productive_execution_is_disabled() -> None:
    validate_contract(CONTRACT)
    assert CONTRACT["migration_rehearsal"]["productive_execution_allowed"] is False
    assert "--dry-run" in CONTRACT["migration_rehearsal"]["dry_run_command"]


def test_pending_template_is_fail_closed() -> None:
    report = evaluate(CONTRACT, evidence_template(CONTRACT))
    assert report["decision"] == "no_go"
    assert report["blocker_count"] > 20


def test_complete_current_evidence_results_in_go() -> None:
    report = evaluate(CONTRACT, complete_evidence())
    assert report["decision"] == "go"
    assert report["blocker_count"] == 0


def test_second_rehearsal_and_p1_defects_are_hard_gates() -> None:
    evidence = complete_evidence()
    evidence["migration_rehearsals"] = evidence["migration_rehearsals"][:1]
    evidence["defects"]["p1"] = 1
    gates = {item["gate"] for item in evaluate(CONTRACT, evidence)["blockers"]}
    assert "migration.rehearsal_2" in gates
    assert "defects.p1" in gates


def test_external_evidence_requires_current_approval_and_artifact() -> None:
    evidence = complete_evidence()
    evidence["integrations"]["scale"]["artifact"] = ""
    evidence["integrations"]["mde"]["timestamp"] = (
        datetime.now(timezone.utc) - timedelta(days=100)
    ).isoformat()
    gates = {item["gate"] for item in evaluate(CONTRACT, evidence)["blockers"]}
    assert {"integrations.scale", "integrations.mde"} <= gates


def test_migration_runner_rejects_execute_or_unknown_rehearsal(tmp_path: Path) -> None:
    unsafe = deepcopy(CONTRACT)
    unsafe["migration_rehearsal"]["dry_run_command"] = ["python", "x.py", "--execute"]
    with pytest.raises(ContractError, match="dry-run only"):
        validate_contract(unsafe)
    with pytest.raises(ContractError, match="Unknown rehearsal"):
        run_migration_dry_run(CONTRACT, "rehearsal_3", tmp_path / "m", tmp_path, tmp_path / "r")
