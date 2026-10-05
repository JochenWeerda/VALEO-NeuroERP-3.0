#!/usr/bin/env python3
"""Fail-closed L3 cutover contract validator and evidence evaluator.

The runner is read-only unless explicitly asked to write a report/template. It
never invokes productive migration or live integration commands.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "config" / "l3-cutover-uat.yaml"
PASS = "pass"


class ContractError(ValueError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ContractError(f"{path} must contain a YAML object")
    return payload


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ContractError(f"{path} must contain a JSON object")
    return payload


def _ids(items: Any, section: str) -> list[str]:
    if not isinstance(items, list) or not items:
        raise ContractError(f"{section} must be a non-empty list")
    ids: list[str] = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ContractError(f"Every {section} item needs a string id")
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        raise ContractError(f"Duplicate ids in {section}")
    return ids


def validate_contract(contract: dict[str, Any]) -> None:
    required = {
        "schema_version", "program_id", "fail_closed", "phases", "roles",
        "journeys", "migration_domains", "integrations", "habit_bridge",
        "thresholds", "evidence_policy", "migration_rehearsal",
    }
    missing = sorted(required - contract.keys())
    if missing:
        raise ContractError("Missing contract sections: " + ", ".join(missing))
    if contract["fail_closed"] is not True:
        raise ContractError("fail_closed must be true")

    phase_ids = set(_ids(contract["phases"], "phases"))
    role_ids = set(_ids(contract["roles"], "roles"))
    _ids(contract["migration_domains"], "migration_domains")
    _ids(contract["habit_bridge"], "habit_bridge")
    integration_ids = _ids(contract["integrations"], "integrations")
    journey_ids = _ids(contract["journeys"], "journeys")
    if not {"rehearsal_1", "rehearsal_2", "parallel_operation", "go_live"} <= phase_ids:
        raise ContractError("Mandatory cutover phases are missing")
    for journey in contract["journeys"]:
        unknown = set(journey.get("roles", [])) - role_ids
        if unknown:
            raise ContractError(f"Journey {journey['id']} references unknown roles: {sorted(unknown)}")
        if journey.get("critical") is not True:
            raise ContractError(f"Journey {journey['id']} must be critical for L3 cutover")
    for integration in contract["integrations"]:
        if integration.get("required") and integration.get("owner_role") not in role_ids:
            raise ContractError(f"Integration {integration['id']} has no valid owner_role")
    if len(journey_ids) < 6 or len(integration_ids) < 7:
        raise ContractError("The minimum journey/integration coverage is not met")
    rehearsal_ids = contract["migration_rehearsal"].get("required_ids")
    if rehearsal_ids != ["rehearsal_1", "rehearsal_2"]:
        raise ContractError("Exactly rehearsal_1 and rehearsal_2 are mandatory")
    command = contract["migration_rehearsal"].get("dry_run_command", [])
    if "--execute" in command or "--dry-run" not in command:
        raise ContractError("Migration command must be dry-run only")
    if contract["migration_rehearsal"].get("productive_execution_allowed") is not False:
        raise ContractError("Productive execution must be disabled")


def evidence_template(contract: dict[str, Any]) -> dict[str, Any]:
    pending = {"status": "pending", "approver": "", "timestamp": "", "artifact": ""}
    domain_result = {
        "status": "pending", "record_count_variance": None,
        "amount_variance_cents": None, "quantity_variance": None,
        "critical_orphans": None,
    }
    return {
        "program_id": contract["program_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "role_signoffs": {item["id"]: dict(pending) for item in contract["roles"]},
        "journeys": {
            item["id"]: {**pending, "duration_ratio": None, "error_rate": None}
            for item in contract["journeys"]
        },
        "migration_rehearsals": [
            {**pending, "id": rid, "domains": {
                item["id"]: dict(domain_result) for item in contract["migration_domains"]
            }} for rid in contract["migration_rehearsal"]["required_ids"]
        ],
        "integrations": {item["id"]: dict(pending) for item in contract["integrations"]},
        "habit_bridge": {item["id"]: dict(pending) for item in contract["habit_bridge"]},
        "defects": {"p0": 0, "p1": 0, "p2": 0},
        "metrics": {
            "overall_journey_pass_rate": None,
            "median_task_duration_ratio": None,
            "user_error_rate": None,
        },
        "parallel_operation": {**pending, "business_days": 0},
        "go_live_approval": dict(pending),
        "repo_probes": {},
    }


def _valid_evidence(value: Any, policy: dict[str, Any]) -> bool:
    if not isinstance(value, dict) or value.get("status") != PASS:
        return False
    if not all(bool(value.get(field)) for field in policy["required_fields"]):
        return False
    try:
        timestamp = datetime.fromisoformat(str(value["timestamp"]).replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            return False
        age = datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)
        return timedelta(0) <= age <= timedelta(days=int(policy["maximum_age_days"]))
    except (TypeError, ValueError):
        return False


def run_migration_dry_run(
    contract: dict[str, Any], rehearsal_id: str, mapping: Path, source: Path, report: Path
) -> dict[str, Any]:
    """Execute only the contract-pinned L3 dry-run and return its audit envelope."""
    if rehearsal_id not in contract["migration_rehearsal"]["required_ids"]:
        raise ContractError(f"Unknown rehearsal id: {rehearsal_id}")
    if not mapping.is_file() or not source.is_dir():
        raise ContractError("Migration rehearsal requires an existing mapping file and source directory")
    template = contract["migration_rehearsal"]["dry_run_command"]
    command = [part.format(mapping=str(mapping), source=str(source), report=str(report)) for part in template]
    if "--dry-run" not in command or "--execute" in command:
        raise ContractError("Refusing a migration rehearsal that is not dry-run only")
    report.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=1800, shell=False)
    return {
        "rehearsal_id": rehearsal_id,
        "status": PASS if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "dry_run": True,
        "productive_writes": False,
        "mapping": str(mapping),
        "source": str(source),
        "report": str(report),
        "stdout": completed.stdout[-8000:],
        "stderr": completed.stderr[-8000:],
    }


def evaluate(contract: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    policy = contract["evidence_policy"]
    thresholds = contract["thresholds"]

    def block(gate: str, reason: str) -> None:
        blockers.append({"gate": gate, "reason": reason})

    if evidence.get("program_id") != contract["program_id"]:
        block("program", "Evidence program_id does not match contract")

    for section in ("roles", "journeys", "integrations", "habit_bridge"):
        evidence_key = "role_signoffs" if section == "roles" else section
        values = evidence.get(evidence_key, {})
        for item in contract[section]:
            if item.get("required", True) and not _valid_evidence(values.get(item["id"]), policy):
                block(f"{evidence_key}.{item['id']}", "Missing passing, approved artifact evidence")

    repo_probe_results = evidence.get("repo_probes", {})
    for probe in contract.get("repo_probes", []):
        if probe.get("required") and repo_probe_results.get(probe["id"], {}).get("status") != PASS:
            block(f"repo_probes.{probe['id']}", "Required safe repository probe did not pass")

    rehearsals = {item.get("id"): item for item in evidence.get("migration_rehearsals", []) if isinstance(item, dict)}
    domains = contract["migration_domains"]
    for rehearsal_id in contract["migration_rehearsal"]["required_ids"]:
        rehearsal = rehearsals.get(rehearsal_id)
        if not _valid_evidence(rehearsal, policy):
            block(f"migration.{rehearsal_id}", "Rehearsal is missing or not approved")
            continue
        for domain in domains:
            result = rehearsal.get("domains", {}).get(domain["id"])
            gate = f"migration.{rehearsal_id}.{domain['id']}"
            if not isinstance(result, dict) or result.get("status") != PASS:
                block(gate, "Domain reconciliation did not pass")
                continue
            for metric in domain["balances"]:
                if metric == "checksum":
                    if result.get(metric) not in (True, "match"):
                        block(gate, "Checksum does not match")
                    continue
                evidence_key, limit_key = {
                    "record_count": ("record_count_variance", "record_count_variance"),
                    "amount_cents": ("amount_variance_cents", "amount_variance_cents"),
                    "quantity": ("quantity_variance", "quantity_variance"),
                    "critical_orphans": ("critical_orphans", "critical_orphans"),
                }[metric]
                value = result.get(evidence_key)
                if value is None or abs(float(value)) > float(thresholds[limit_key]):
                    block(gate, f"{metric} exceeds threshold {thresholds[limit_key]}")

    defects = evidence.get("defects", {})
    for severity, maximum in thresholds["maximum_open_defects"].items():
        if not isinstance(defects.get(severity), int) or defects[severity] > maximum:
            block(f"defects.{severity}", f"Open defects exceed maximum {maximum}")

    metrics = evidence.get("metrics", {})
    lower_bounds = ("overall_journey_pass_rate",)
    upper_bounds = ("median_task_duration_ratio", "user_error_rate")
    for key in lower_bounds:
        if metrics.get(key) is None or float(metrics[key]) < float(thresholds[key]):
            block(f"metrics.{key}", f"Value must be at least {thresholds[key]}")
    for key in upper_bounds:
        if metrics.get(key) is None or float(metrics[key]) > float(thresholds[key]):
            block(f"metrics.{key}", f"Value must be at most {thresholds[key]}")

    parallel = evidence.get("parallel_operation")
    if not _valid_evidence(parallel, policy):
        block("parallel_operation", "Parallel operation lacks approved evidence")
    elif int(parallel.get("business_days", 0)) < thresholds["minimum_parallel_business_days"]:
        block("parallel_operation", "Minimum parallel business days not reached")
    if not _valid_evidence(evidence.get("go_live_approval"), policy):
        block("go_live_approval", "Final business and operations approval is missing")

    return {
        "program_id": contract["program_id"],
        "decision": "go" if not blockers else "no_go",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "repo_probes": repo_probe_results,
    }


def run_repo_probes(contract: dict[str, Any]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for probe in contract.get("repo_probes", []):
        command = probe.get("command")
        if probe.get("safe") is not True or probe.get("live") is not False:
            raise ContractError(f"Probe {probe.get('id')} is not declared safe and non-live")
        if not isinstance(command, list) or not command or any(not isinstance(x, str) for x in command):
            raise ContractError(f"Probe {probe.get('id')} command must be an argument list")
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120, shell=False)
        results[probe["id"]] = {
            "status": PASS if completed.returncode == 0 else "fail",
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
        }
    return results


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# L3 Cutover Readiness: {report['decision'].upper()}", "",
        f"Programm: `{report['program_id']}`", "",
        f"Blocker: **{report['blocker_count']}**", "",
    ]
    if report["blockers"]:
        lines.extend(["## Sperrgates", ""])
        lines.extend(f"- `{item['gate']}`: {item['reason']}" for item in report["blockers"])
    else:
        lines.append("Alle verpflichtenden Gates besitzen gueltige Evidenz.")
    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--write-evidence-template", type=Path)
    parser.add_argument("--run-repo-probes", action="store_true")
    parser.add_argument("--run-migration-rehearsal", choices=["rehearsal_1", "rehearsal_2"])
    parser.add_argument("--l3-source", type=Path)
    parser.add_argument("--mapping", type=Path, default=ROOT / "config" / "l3_mapping.yaml")
    parser.add_argument("--rehearsal-report", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-markdown", type=Path)
    parser.add_argument("--output-evidence", type=Path, help="Write evidence enriched with safe probe results")
    parser.add_argument("--fail-on-no-go", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        contract = load_yaml(args.contract)
        validate_contract(contract)
        if args.write_evidence_template:
            write_json(args.write_evidence_template, evidence_template(contract))
        if args.run_migration_rehearsal:
            if not args.l3_source or not args.rehearsal_report:
                raise ContractError("--l3-source and --rehearsal-report are required for a rehearsal")
            result = run_migration_dry_run(
                contract, args.run_migration_rehearsal, args.mapping, args.l3_source, args.rehearsal_report
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
            raise SystemExit(0 if result["status"] == PASS else 1)
        if args.contract_only and not args.evidence:
            print(f"VALID {contract['program_id']}")
            return
        evidence = load_json(args.evidence) if args.evidence else evidence_template(contract)
        if args.run_repo_probes:
            evidence["repo_probes"] = run_repo_probes(contract)
        if args.output_evidence:
            write_json(args.output_evidence, evidence)
        report = evaluate(contract, evidence)
        if args.output_json:
            write_json(args.output_json, report)
        if args.output_markdown:
            args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
            args.output_markdown.write_text(render_markdown(report), encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if args.fail_on_no_go and report["decision"] != "go":
            raise SystemExit(1)
    except (ContractError, OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
