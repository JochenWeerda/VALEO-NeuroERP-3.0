"""Pure Unit-Tests: Adaptive-Workspace-Fachaktionen (kein DB, kein MagicMock-DB)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.workspace.events import IST_TO_SOLL, canonical_event, project_workspace_event
from app.workspace.fachaktionen import (
    WorkspaceFachaktionenError,
    list_catalog,
    load_catalog,
    normalize_command,
    resolve_command,
)

EXAMPLES = {
    "nicht disponierte LKW": "logistik.undispatched_vehicles.list",
    "ueberfaellige Kontrakte": "agrar.contract.overdue.list",
    "Angebot Kunde": "sales.customer_quote.list",
    "WE Mengenabweichung": "einkauf.goods_receipt.quantity_variance.list",
    "Rechnungen Freigabe": "finance.ap_invoice.approval.worklist",
}

READ_SCOPES = {
    "logistik.undispatched_vehicles.list": "logistics:read",
    "agrar.contract.overdue.list": "agrar:read",
    "sales.customer_quote.list": "sales:read",
    "einkauf.goods_receipt.quantity_variance.list": "einkauf:read",
    "finance.ap_invoice.approval.worklist": "finance:read",
}

HANDSHAKE_FRONTEND_IDS = {
    "harvest.intake-queue": "logistics:read",
    "workspace.document-inbox": "dms:read",
    "agrar.qualitaets-handlungsbedarf": "agrar:read",
    "sales.credit_note.list": "sales:read",
    "einkauf.gutschrift.list": "einkauf:read",
    "weighing.tickets.list": "logistics:read",
    "einkauf.lieferschein.list": "einkauf:read",
}

REQUIRED_EXISTING_IDS = (
    "logistik.undispatched_vehicles.list",
    "agrar.contract.overdue.list",
    "sales.customer_quote.list",
    "einkauf.goods_receipt.quantity_variance.list",
    "finance.ap_invoice.approval.worklist",
)


@pytest.mark.unit
def test_catalog_loads_and_has_five_examples() -> None:
    catalog = load_catalog()
    ids = {a["action_id"] for a in catalog["actions"]}
    assert set(EXAMPLES.values()) <= ids
    assert set(REQUIRED_EXISTING_IDS) <= ids
    assert catalog["meta"]["registry_id"] == "AW-FACHAKTIONEN-001"
    assert catalog["meta"]["lead_contract"].get("frontend_catalog_id") == "action_id"


@pytest.mark.unit
def test_handshake_frontend_catalog_ids_exist_and_resolve() -> None:
    catalog = load_catalog()
    by_id = catalog["by_id"]
    for action_id, scope in HANDSHAKE_FRONTEND_IDS.items():
        assert action_id in by_id, action_id
        action = by_id[action_id]
        assert action["access"] == "read"
        assert action["risk_level"] == "R0"
        assert action["permission"]["scope"] == scope
        by_id_result = resolve_command(action_id, scopes=[scope], identity_type="agent")
        assert by_id_result.action_id == action_id
        assert by_id_result.authorized is True
        assert by_id_result.action is not None
        assert by_id_result.action["executable"] is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "command, action_id, scope",
    [
        ("Annahme-Warteschlange", "harvest.intake-queue", "logistics:read"),
        ("ernte annahme", "harvest.intake-queue", "logistics:read"),
        ("warteschlange", "harvest.intake-queue", "logistics:read"),
        ("Beleg-Inbox", "workspace.document-inbox", "dms:read"),
        ("dokumenteneingang", "workspace.document-inbox", "dms:read"),
        ("workspace.document-inbox", "workspace.document-inbox", "dms:read"),
        ("Qualitaets-Handlungsbedarf", "agrar.qualitaets-handlungsbedarf", "agrar:read"),
        ("qualitaets-check", "agrar.qualitaets-handlungsbedarf", "agrar:read"),
        ("agrar.qualitaets-handlungsbedarf", "agrar.qualitaets-handlungsbedarf", "agrar:read"),
    ],
)
def test_handshake_aliases_resolve(command: str, action_id: str, scope: str) -> None:
    result = resolve_command(command, scopes=[scope], identity_type="agent")
    assert result.action_id == action_id
    assert result.authorized is True
    assert result.reason == "authorized"


@pytest.mark.unit
def test_document_capture_open_is_not_auto_approved() -> None:
    catalog = load_catalog()
    action = catalog["by_id"]["document.capture.open"]
    assert action["executable"] is False
    assert action["enabled_for_agents"] is False
    assert action["forbidden_for_agents"] is True
    inbox = catalog["by_id"]["workspace.document-inbox"]
    assert "document.capture.open" in inbox["follow_up_writes"]
    agent = resolve_command(
        "document.capture.open",
        scopes=["dms:read"],
        identity_type="agent",
    )
    assert agent.action_id == "document.capture.open"
    assert agent.authorized is False
    assert agent.reason == "forbidden_for_agents"
    assert agent.action is not None
    assert agent.action["executable"] is False
    human = resolve_command(
        "document.capture.open",
        scopes=["dms:read"],
        identity_type="human",
    )
    assert human.action_id == "document.capture.open"
    assert human.authorized is True
    assert human.action is not None
    assert human.action["executable"] is False


@pytest.mark.unit
@pytest.mark.parametrize("command, action_id", list(EXAMPLES.items()))
def test_five_example_queries_resolve_authorized_with_scope(command: str, action_id: str) -> None:
    result = resolve_command(
        command,
        scopes=[READ_SCOPES[action_id]],
        identity_type="agent",
    )
    assert result.action_id == action_id
    assert result.authorized is True
    assert result.reason == "authorized"
    assert result.action is not None
    assert result.action["access"] == "read"
    assert result.action["audit"] == "read"
    assert result.action["permission"]["scope"] == READ_SCOPES[action_id]


@pytest.mark.unit
@pytest.mark.parametrize("command, action_id", list(EXAMPLES.items()))
def test_five_example_queries_forbidden_without_scope(command: str, action_id: str) -> None:
    result = resolve_command(command, scopes=["crm:read"], identity_type="agent")
    assert result.action_id == action_id
    assert result.authorized is False
    assert result.reason == "missing_scope"


@pytest.mark.unit
def test_umlaut_and_filler_words_are_deterministic() -> None:
    assert normalize_command("Überfällige Kontrakte!") == "ueberfaellige kontrakte"
    result = resolve_command(
        "Bitte zeige mir alle überfälligen Kontrakte",
        scopes=["agrar:read"],
        identity_type="agent",
    )
    assert result.action_id == "agrar.contract.overdue.list"
    assert result.authorized is True


@pytest.mark.unit
def test_action_id_match_is_accepted() -> None:
    result = resolve_command(
        "logistik.undispatched_vehicles.list",
        scopes=["logistics:read"],
        identity_type="agent",
    )
    assert result.authorized is True
    assert result.action_id == "logistik.undispatched_vehicles.list"


@pytest.mark.unit
def test_invoice_release_verb_is_forbidden_for_agents() -> None:
    result = resolve_command(
        "rechnungen freigeben",
        scopes=["finance:write"],
        identity_type="agent",
    )
    assert result.action_id == "finance.ap_invoice.freigeben"
    assert result.authorized is False
    assert result.reason == "forbidden_for_agents"
    assert result.action is not None
    assert result.action["four_eyes"] is True
    assert result.action["risk_level"] == "R4"


@pytest.mark.unit
def test_invoice_release_is_authorized_for_human_with_scope() -> None:
    result = resolve_command(
        "rechnungen freigeben",
        scopes=["finance:write"],
        identity_type="human",
    )
    assert result.action_id == "finance.ap_invoice.freigeben"
    assert result.authorized is True
    assert result.reason == "authorized"


@pytest.mark.unit
def test_four_eyes_propose_is_authorized_for_agent_with_write_scope() -> None:
    result = resolve_command(
        "rechnungsfreigabe vorschlagen",
        scopes=["finance:write"],
        identity_type="agent",
    )
    assert result.action_id == "finance.ap_invoice.propose"
    assert result.authorized is True
    assert result.action is not None
    assert result.action["four_eyes"] is True
    assert result.action["mcp_tool_id"] == "finance.ap_invoice.propose"


@pytest.mark.unit
def test_quote_create_and_contract_reminder_are_forbidden_for_agents() -> None:
    quote = resolve_command("angebot anlegen", scopes=["sales:write"], identity_type="agent")
    reminder = resolve_command("kontrakt mahnen", scopes=["agrar:write"], identity_type="agent")
    assert quote.authorized is False
    assert quote.reason == "forbidden_for_agents"
    assert reminder.authorized is False
    assert reminder.reason == "forbidden_for_agents"


@pytest.mark.unit
def test_unknown_command_is_forbidden() -> None:
    result = resolve_command("kasse stornieren heimlich", scopes=["admin:all"], identity_type="human")
    assert result.action_id is None
    assert result.authorized is False
    assert result.reason == "unknown"


@pytest.mark.unit
def test_empty_command_is_forbidden() -> None:
    result = resolve_command("   ", scopes=["finance:read"], identity_type="agent")
    assert result.authorized is False
    assert result.reason == "empty_command"


@pytest.mark.unit
def test_admin_all_grants_read_examples() -> None:
    result = resolve_command("WE Mengenabweichung", scopes=["admin:all"], identity_type="agent")
    assert result.authorized is True
    assert result.action_id == "einkauf.goods_receipt.quantity_variance.list"


@pytest.mark.unit
def test_tour_assign_write_requires_logistics_write() -> None:
    denied = resolve_command("lkw disponieren", scopes=["logistics:read"], identity_type="agent")
    allowed = resolve_command("lkw disponieren", scopes=["logistics:write"], identity_type="agent")
    assert denied.authorized is False
    assert denied.action_id == "logistik.tour.anlegen"
    assert allowed.authorized is True
    assert allowed.action is not None
    assert allowed.action["idempotency"] == "required"
    assert allowed.action["audit"] == "write"


@pytest.mark.unit
def test_duplicate_alias_is_a_catalog_collision(tmp_path: Path) -> None:
    payload = {
        "actions": [
            {
                "action_id": "a.one",
                "domain": "x",
                "access": "read",
                "risk_level": "R0",
                "permission": {"scope": "x:read"},
                "idempotency": "not_required",
                "audit": "read",
                "aliases": ["kollision"],
            },
            {
                "action_id": "a.two",
                "domain": "x",
                "access": "read",
                "risk_level": "R0",
                "permission": {"scope": "x:read"},
                "idempotency": "not_required",
                "audit": "read",
                "aliases": ["Kollision"],
            },
        ]
    }
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    load_catalog.cache_clear()
    with pytest.raises(WorkspaceFachaktionenError, match="Alias-Kollision"):
        load_catalog(str(path))
    load_catalog.cache_clear()


@pytest.mark.unit
def test_ambiguous_longest_tie_is_rejected(tmp_path: Path) -> None:
    payload = {
        "actions": [
            {
                "action_id": "a.alpha",
                "domain": "x",
                "access": "read",
                "risk_level": "R0",
                "permission": {"scope": "x:read"},
                "idempotency": "not_required",
                "audit": "read",
                "aliases": ["gleiche laenge x"],
            },
            {
                "action_id": "a.beta",
                "domain": "x",
                "access": "read",
                "risk_level": "R0",
                "permission": {"scope": "x:read"},
                "idempotency": "not_required",
                "audit": "read",
                "aliases": ["gleiche laenge y"],
            },
        ]
    }
    path = tmp_path / "tie.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    load_catalog.cache_clear()
    result = resolve_command(
        "gleiche laenge x und gleiche laenge y",
        scopes=["x:read"],
        catalog_path=str(path),
    )
    load_catalog.cache_clear()
    assert result.authorized is False
    assert result.reason == "ambiguous"
    assert result.action_id is None


@pytest.mark.unit
def test_list_catalog_lead_contract_and_write_filter() -> None:
    full = list_catalog()
    writes = list_catalog(access="write")
    assert full["lead_contract"]["catalog_path"] == "config/adaptive_workspace_fachaktionen.yaml"
    assert full["lead_contract"]["frontend_catalog_id"] == "action_id"
    assert "workspace.fachaktion.resolve" in full["lead_contract"]["mcp_tools"].values()
    assert all(item["access"] == "write" for item in writes["actions"])
    assert writes["count"] < full["count"]


@pytest.mark.unit
def test_event_mapping_ist_to_soll() -> None:
    assert canonical_event("logistik.tour.created") == "assignment_confirmed"
    assert canonical_event("LOADING_STARTED") == "assignment_confirmed"
    assert canonical_event("LOADING_FINISHED") == "assignment_confirmed"
    assert canonical_event("finance.ap_invoice.approval_requested") == "document_proposed"
    assert canonical_event("goods_receipt.created") == "document_posted"
    assert canonical_event("sales.offer.created") is None
    projected = project_workspace_event("finance.ap_invoice.approved", tenant_id="t-1")
    assert projected is not None
    assert projected["canonical"] == "assignment_confirmed"
    assert projected["type"] == "finance.ap_invoice.approved"
    assert projected["event_type"] == "finance.ap_invoice.approved"
    assert projected["sse_channel"] == "workspace"
    assert projected["wired"] is True
    assert "t-1" in projected["nats_subject"]


@pytest.mark.unit
def test_yaml_event_gaps_cover_ist_to_soll() -> None:
    """YAML event_gaps.ist muss IST_TO_SOLL abdecken — kein stiller Mapping-Drift."""
    load_catalog.cache_clear()
    catalog = load_catalog()
    by_soll: dict[str, set[str]] = {}
    for gap in catalog["meta"]["event_gaps"]:
        soll = gap["soll"]
        by_soll.setdefault(soll, set()).update(gap.get("ist") or [])
    missing = [
        f"{ist}→{soll}"
        for ist, soll in IST_TO_SOLL.items()
        if ist not in by_soll.get(soll, set())
    ]
    assert missing == [], f"event_gaps Drift gegen IST_TO_SOLL: {missing}"
    assert "LOADING_STARTED" in by_soll["assignment_confirmed"]
    assert "LOADING_FINISHED" in by_soll["assignment_confirmed"]


@pytest.mark.unit
def test_mcp_katalog_and_resolve_do_not_touch_db() -> None:
    from app.services.mcp_execution_service import ToolExecutionRequest, execute_mcp_tool
    from app.services.mcp_mask_actions import workspace_action_agent_block

    class ForbiddenDB:
        def __getattr__(self, name: str) -> None:
            raise AssertionError(f"DB accessed: {name}")

    user = {
        "sub": "agent-1",
        "scopes": ["agent:read", "finance:read"],
        "raw": {"tenant_id": "tenant-a", "identity_type": "agent"},
    }
    katalog = execute_mcp_tool(
        ForbiddenDB(),
        ToolExecutionRequest(tool_name="workspace.fachaktion.katalog", parameters={}),
        user,
        None,
    )
    assert katalog["registry_id"] == "AW-FACHAKTIONEN-001"
    assert katalog["count"] >= 5
    resolved = execute_mcp_tool(
        ForbiddenDB(),
        ToolExecutionRequest(
            tool_name="workspace.fachaktion.resolve",
            parameters={"command": "Rechnungen Freigabe"},
        ),
        user,
        None,
    )
    assert resolved["action_id"] == "finance.ap_invoice.approval.worklist"
    assert resolved["authorized"] is True
    harvest_user = {
        "sub": "agent-1",
        "scopes": ["agent:read", "logistics:read", "dms:read"],
        "raw": {"tenant_id": "tenant-a", "identity_type": "agent"},
    }
    harvest = execute_mcp_tool(
        ForbiddenDB(),
        ToolExecutionRequest(
            tool_name="workspace.fachaktion.resolve",
            parameters={"command": "harvest.intake-queue"},
        ),
        harvest_user,
        None,
    )
    assert harvest["action_id"] == "harvest.intake-queue"
    assert harvest["authorized"] is True
    inbox = execute_mcp_tool(
        ForbiddenDB(),
        ToolExecutionRequest(
            tool_name="workspace.fachaktion.resolve",
            parameters={"command": "Beleg-Inbox"},
        ),
        harvest_user,
        None,
    )
    assert inbox["action_id"] == "workspace.document-inbox"
    assert inbox["authorized"] is True
    capture = execute_mcp_tool(
        ForbiddenDB(),
        ToolExecutionRequest(
            tool_name="workspace.fachaktion.resolve",
            parameters={"command": "document.capture.open"},
        ),
        harvest_user,
        None,
    )
    assert capture["action_id"] == "document.capture.open"
    assert capture["authorized"] is False
    assert capture["executable"] is False
    assert workspace_action_agent_block("finance.ap_invoice.freigeben") == "fuer_agenten_gesperrt"
    assert workspace_action_agent_block("logistik.undispatched_vehicles.list") is None


@pytest.mark.unit
def test_every_write_declares_idempotency_audit_and_event_out() -> None:
    for action in load_catalog()["actions"]:
        if action["access"] != "write":
            continue
        assert action["idempotency"] == "required"
        assert action["audit"] == "write"
        assert "event_out" in action
        if action.get("four_eyes"):
            assert action["risk_level"] in {"R3", "R4"}
