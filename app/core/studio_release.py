"""Server-side binding of simulation evidence to immutable Studio candidates."""
import hashlib
import json
from functools import lru_cache


class SimulationBusy(RuntimeError):
    """The shared probe is already executing one Studio chain."""


def definition_hash(definition):
    return hashlib.sha256(json.dumps(definition,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def simulate_candidate(item):
    from app.services.studio_process_simulation import simulate_process
    errors = profile_errors(item["definition"])
    if not errors:
        ensure_interface_sync()
    report = ({"passed": False, "error": "simulation_profile_not_supported", "checks": {}, "failed_checks": errors}
              if errors else simulate_process(item["definition"]))
    return {**report,"tenant_id":item["tenant_id"],"draft_id":item["id"],
            "candidate_revision":item["revision"],"definition_hash":definition_hash(item["definition"])}


def require_simulation(item, entries):
    from app.services.studio_process_simulation import simulation_artifact_hash, _REQUIRED
    from app.services.studio_validation import validate_studio_draft
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS
    if profile_errors(item["definition"]) or validate_studio_draft(item["definition"], native_screen_ids=set(SCREEN_DEFINITION_BUILDERS)):
        raise ValueError("studio_definition_nicht_freigabefaehig")
    ensure_interface_sync()
    for entry in reversed(entries):
        proof=entry.get("snapshot",{}).get("simulation")
        if entry.get("action")!="simulation" or not isinstance(proof,dict):
            continue
        if proof.get("candidate_revision")!=item["revision"]:
            continue
        if (proof.get("tenant_id")!=item["tenant_id"] or proof.get("draft_id")!=item["id"]
                or proof.get("definition_hash")!=definition_hash(item["definition"])
                or proof.get("artifact_hash")!=simulation_artifact_hash()
                or proof.get("passed") is not True
                or proof.get("profile")!="grain.v1"
                or any(proof.get("checks",{}).get(name) is not True for name in _REQUIRED)):
            raise ValueError("simulation_unvollstaendig_veraltet_oder_fehlgeschlagen")
        return proof
    raise ValueError("simulation_fuer_diese_revision_fehlt")



def published_definition(record):
    """Previously published development records get no invented release evidence."""
    from app.services.studio_process_simulation import simulation_artifact_hash, _REQUIRED
    proof=(record.get("readiness") or {}).get("release_evidence")
    if (record.get("status")!="published_temp" or not isinstance(proof,dict)
            or proof.get("passed") is not True or proof.get("profile")!="grain.v1"
            or proof.get("tenant_id")!=record.get("tenant_id") or proof.get("draft_id")!=record.get("id")
            or proof.get("definition_hash")!=definition_hash(record.get("definition"))
            or proof.get("artifact_hash")!=simulation_artifact_hash()
            or any(proof.get("checks",{}).get(name) is not True for name in _REQUIRED)):
        return None
    from copy import deepcopy
    definition=deepcopy(record["definition"])
    definition["studioRelease"]={"draftId":record["id"],"candidateRevision":proof["candidate_revision"],
                                "artifactHash":proof["artifact_hash"]}
    return definition


def profile_errors(definition):
    """grain.v1 proves the fixed domain chain; unmodeled commands/rules never pass."""
    from app.services.studio_validation import _iter_actions, _nodes
    errors=[]
    if definition.get("studioSemantic") is not None:
        errors.append("semantic_preview_not_a_release_profile")
    if definition.get("domain")!="agrar":
        errors.append("domain_not_covered")
    requested=definition.get("processSimulation") or {}
    if not isinstance(requested,dict) or set(requested)-{"profile"} or requested.get("profile","grain.v1")!="grain.v1":
        errors.append("profile_not_covered")
    if any(_iter_actions(definition)):
        errors.append("screen_commands_not_covered")
    if any(node.get("editableFields") not in (None, []) for node in _nodes(definition)):
        errors.append("editable_agent_fields_not_covered")
    keys={"workflowRules","processRules","qualityRules","accountingRules","businessRules"}
    if any(node[key] not in (None, [], {}) for node in _nodes(definition) for key in keys & node.keys()):
        errors.append("rules_not_covered")
    return errors


def ensure_interface_sync():
    from app.services.studio_process_simulation import simulation_artifact_hash
    _checked_interfaces(simulation_artifact_hash())


@lru_cache(maxsize=4)
def _checked_interfaces(stamp):
    """Current deployed REST/MCP/agent projections, not a stale development file."""
    from scripts.generate_openapi import build_spec
    from app.core.mcp_tool_contracts import get_process_kernel_mcp_tools
    from app.core.mcp_rest_binding import check_read_binding, check_request_binding
    from app.core.agent_tool_contract_manifest import build_agent_tool_contract_manifest
    spec = build_spec()
    tools = get_process_kernel_mcp_tools().tools
    if any(check_read_binding(spec, tool) or check_request_binding(spec, tool) for tool in tools):
        raise ValueError("studio_interface_contracts_not_synchronized")
    entries = {entry.tool_name:entry for entry in build_agent_tool_contract_manifest().tools}
    for tool in tools:
        entry=entries.get(tool.tool_name)
        mcp=tool.as_mcp_tool()
        if entry is None or entry.schema_version!=tool.schema_version or entry.mcp_definition!=mcp:
            raise ValueError("studio_agent_contract_version_mismatch")
    return stamp
