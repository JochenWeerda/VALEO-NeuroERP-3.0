"""MCP-MASK-GENERIC — generische MCP-Werkzeuge rufen denselben Kommandoweg wie Maske und CLI."""
from __future__ import annotations

import json

import httpx
import pytest
from fastapi import HTTPException

from app.services import mcp_mask_actions as mm
from app.services.mcp_execution_service import ToolExecutionRequest, execute_mcp_tool
from valeo_cli.support import support

TENANT = "00000000-0000-0000-0000-000000000051"


def _registry_actions():
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
    from app.core.screen_definitions_beleg import BELEGARTEN, build_beleg_screen_definition, screen_id

    defs = {sid: get_screen_definition(sid) or {} for sid in SCREEN_DEFINITION_BUILDERS}
    defs.update({screen_id(art): build_beleg_screen_definition(art) for art in BELEGARTEN})
    return [(sid, action) for sid, d in sorted(defs.items()) for action in mm.iter_actions(d)]


def test_paritaet_mit_der_cli_regel():
    """Was ein Agent per MCP darf, kann auch die CLI — und nur der generische Weg ohne Adapter ist fuer Agenten."""
    for sid, action in _registry_actions():
        block = mm.agent_block(action)
        cli = support(action)
        if block is None:
            assert cli.supported and not action.get("commandBinding"), (sid, action["key"])
            assert not action.get("forbiddenForAgents") and not action.get("humanApprovalRequired")
        if action.get("commandBinding"):
            assert block == "adapter_nur_mensch", (sid, action["key"])


def _agent_action():
    for sid, action in _registry_actions():
        if mm.agent_block(action) is None and "{entity_id}" in action["commandEndpoint"] and not action.get("auditReasonRequired"):
            return sid, action
    raise AssertionError("keine agentenfaehige Maskenaktion mit Objektbezug in der Registry")


def _blocked_action():
    for sid, action in _registry_actions():
        if mm.agent_block(action) == "fuer_agenten_gesperrt":
            return sid, action
    raise AssertionError("keine fuer Agenten gesperrte Aktion in der Registry")


def req(parameters, mode="dryRun", key=None):
    return ToolExecutionRequest(tool_name="mask.action.execute", parameters=parameters, mode=mode, idempotency_key=key)


class Target:
    def __init__(self, status=200, body=None):
        self.calls: list[httpx.Request] = []
        self.status, self.body = status, body if body is not None else {"success": True, "summary": "ok"}

    def __call__(self, request):
        self.calls.append(request)
        return httpx.Response(self.status, json=self.body)


def test_liste_nennt_zugang_und_grund():
    sid, action = _agent_action()
    rows = {r["key"]: r for r in mm.list_actions({"screen_id": sid}, TENANT)["actions"]}
    assert rows[action["key"]]["agent_ausfuehrbar"] is True and rows[action["key"]]["needs_entity_id"]
    bsid, blocked = _blocked_action()
    row = next(r for r in mm.list_actions({"screen_id": bsid}, TENANT)["actions"] if r["key"] == blocked["key"])
    assert row["agent_ausfuehrbar"] is False and row["grund"] == "fuer_agenten_gesperrt"


def test_ausfuehren_mit_dem_token_des_aufrufers_und_dem_umschlag_der_maske():
    sid, action = _agent_action()
    target = Target()
    out = mm.execute(req({"screen_id": sid, "action": action["key"], "entity_id": "a/1", "input": {}}),
                     TENANT, "Bearer agent-token", transport=httpx.MockTransport(target))
    [call] = target.calls
    assert call.headers["Authorization"] == "Bearer agent-token" and "X-Tenant-ID" not in call.headers
    assert call.url.raw_path.decode() == action["commandEndpoint"].replace("{entity_id}", "a%2F1").replace("{screen_id}", sid)
    assert json.loads(call.content) == {"_mode": "dryRun"}
    assert out["success"] and out["result"]["summary"] == "ok"


def test_execute_braucht_wiederholungsschluessel_und_gibt_ihn_weiter():
    sid, action = _agent_action()
    with pytest.raises(HTTPException) as err:
        mm.execute(req({"screen_id": sid, "action": action["key"], "entity_id": "1"}, mode="execute"),
                   TENANT, "Bearer t", transport=httpx.MockTransport(Target()))
    assert err.value.status_code == 422
    target = Target()
    mm.execute(req({"screen_id": sid, "action": action["key"], "entity_id": "1"}, mode="execute", key="k-1"),
               TENANT, "Bearer t", transport=httpx.MockTransport(target))
    assert json.loads(target.calls[0].content) == {"_idempotencyKey": "k-1"}


@pytest.mark.parametrize("parameters,status", [
    ({"input": {"tenant_id": "fremd"}}, 422), ({"input": {"_mode": "execute"}}, 422),
    ({"mandant": "x"}, 422), ({"entity_id": None}, 422), ({"action": "gibt-es-nicht"}, 404),
])
def test_unzulaessige_aufrufe_erreichen_den_endpunkt_nie(parameters, status):
    sid, action = _agent_action()
    target = Target()
    with pytest.raises(HTTPException) as err:
        mm.execute(req({"screen_id": sid, "action": action["key"], "entity_id": "1", **parameters}),
                   TENANT, "Bearer t", transport=httpx.MockTransport(target))
    assert err.value.status_code == status and not target.calls


def test_gesperrte_aktion_und_fehlender_token():
    sid, action = _blocked_action()
    target = Target()
    with pytest.raises(HTTPException) as err:
        mm.execute(req({"screen_id": sid, "action": action["key"], "entity_id": "1"}), TENANT, "Bearer t",
                   transport=httpx.MockTransport(target))
    assert err.value.status_code == 403 and not target.calls
    asid, agent = _agent_action()
    with pytest.raises(HTTPException) as err:
        mm.execute(req({"screen_id": asid, "action": agent["key"], "entity_id": "1"}), TENANT, None,
                   transport=httpx.MockTransport(target))
    assert err.value.status_code == 401 and not target.calls


def test_ablehnung_des_ziel_endpunkts_wird_weitergereicht():
    sid, action = _agent_action()
    with pytest.raises(HTTPException) as err:
        mm.execute(req({"screen_id": sid, "action": action["key"], "entity_id": "1"}), TENANT, "Bearer t",
                   transport=httpx.MockTransport(Target(403, {"detail": "Insufficient role"})))
    assert err.value.status_code == 403 and err.value.detail == "Insufficient role"


def test_fremde_maske_oder_ungueltige_kennung(monkeypatch):
    from app.services import studio_draft_store
    monkeypatch.setattr(studio_draft_store, "get_published_definition", lambda tenant, screen: None)
    with pytest.raises(HTTPException) as err:
        mm.list_actions({"screen_id": "tenant/gibt-es-nicht"}, TENANT)
    assert err.value.status_code == 404
    with pytest.raises(HTTPException) as err:
        mm.list_actions({"screen_id": "../etc"}, TENANT)
    assert err.value.status_code == 422


def test_studio_speicher_nicht_erreichbar_ist_503(monkeypatch):
    from app.services import studio_draft_store

    def down(tenant, screen):
        raise studio_draft_store.StudioStorageUnavailable("studio_persistenz_nicht_verfuegbar")

    monkeypatch.setattr(studio_draft_store, "get_published_definition", down)
    with pytest.raises(HTTPException) as err:
        mm.list_actions({"screen_id": "tenant/irgendeine"}, TENANT)
    assert err.value.status_code == 503


def _user(scopes):
    return {"sub": "agent-1", "scopes": scopes, "raw": {"tenant_id": TENANT, "sub": "agent-1"}}


def test_mcp_weiche_verlangt_den_scope(monkeypatch):
    sid, _ = _agent_action()
    request = ToolExecutionRequest(tool_name="mask.actions.list", parameters={"screen_id": sid})
    with pytest.raises(HTTPException) as err:
        execute_mcp_tool(None, request, _user(["crm:read"]), None)
    assert err.value.status_code == 403
    assert execute_mcp_tool(None, request, _user(["masks:read"]), None)["screen_id"] == sid


def test_mcp_weiche_gibt_den_token_weiter(monkeypatch):
    sid, action = _agent_action()
    seen = {}
    monkeypatch.setattr(mm, "execute", lambda request, tenant, authorization: seen.update(t=tenant, a=authorization) or {})
    execute_mcp_tool(None, req({"screen_id": sid, "action": action["key"], "entity_id": "1"}), _user(["masks:write"]),
                     None, authorization="Bearer agent-token")
    assert seen == {"t": TENANT, "a": "Bearer agent-token"}


# --------------------------------------------------------------------------------------------- Agentengrenze


@pytest.mark.parametrize("tool,parameters,locked", [
    ("agrar.ration.transition", {"action_key": "approve"}, "mask:agrar/ration:approve"),
    ("agrar.ration.transition", {"action_key": "submit_review"}, None),
    ("agrar.ration.transition", {}, "mask:agrar/ration:activate"),
    ("lager.stock_movement.stornieren", {}, "mask:lager/stock-movement:stornieren"),
    ("logistik.fahrzeug.loeschen", {}, "mask:fuhrpark/fahrzeug-stamm:loeschen"),
    ("crm.activity.create", {}, None),
])
def test_spezialwerkzeug_erbt_die_agentengrenze_der_maske(tool, parameters, locked):
    assert mm.human_only_tool_call(tool, parameters) == locked


def _identity(kind):
    raw = {"tenant_id": TENANT, "sub": "x"}
    if kind:
        raw["identity_type"] = kind
    return {"sub": "x", "scopes": ["agrar:write"], "raw": raw}


@pytest.mark.parametrize("kind", ["service", "agent", None])
def test_agent_kann_ueber_mcp_keine_menschliche_freigabe_ausloesen(kind):
    request = ToolExecutionRequest(tool_name="agrar.ration.transition", mode="execute", idempotency_key="k",
                                   parameters={"ration_id": "r1", "action_key": "approve"})
    with pytest.raises(HTTPException) as err:
        execute_mcp_tool(None, request, _identity(kind), None)
    assert err.value.status_code == 403 and "mask:agrar/ration:approve" in err.value.detail


def test_vorschau_bleibt_fuer_agenten_und_mensch_erreicht_den_handler(monkeypatch):
    from app.services import mcp_execution_service as svc
    calls = []
    monkeypatch.setattr(svc, "_ration_transition", lambda db, request, actor, tenant: calls.append(request.mode) or {"ok": True})
    preview = ToolExecutionRequest(tool_name="agrar.ration.transition", mode="dryRun",
                                   parameters={"ration_id": "r1", "action_key": "approve"})
    execute_mcp_tool(None, preview, _identity("service"), None)
    human = ToolExecutionRequest(tool_name="agrar.ration.transition", mode="execute", idempotency_key="k",
                                 parameters={"ration_id": "r1", "action_key": "approve"})
    execute_mcp_tool(None, human, _identity("human"), None)
    assert calls == ["dryRun", "execute"]


def test_werkzeug_mit_eigenem_freigabeschritt_bleibt_fuer_agenten(monkeypatch):
    """sales.gutschrift.buchen: Ein Mensch gibt den Vorschlag frei, der Agent bucht genau ihn (human_approval_required)."""
    from app.services import mcp_execution_service as svc
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service
    assert mcp_tool_registry_service.get_tool("sales.gutschrift.buchen")["human_approval_required"] is True
    calls = []
    monkeypatch.setattr(svc, "_gutschrift_buchen", lambda db, request, actor, tenant: calls.append(1) or {"ok": True})
    request = ToolExecutionRequest(tool_name="sales.gutschrift.buchen", mode="execute", idempotency_key="k",
                                   parameters={"vorschlag_id": "v1"})
    user = {"sub": "agent", "scopes": ["sales:write"], "raw": {"tenant_id": TENANT, "identity_type": "service"}}
    execute_mcp_tool(None, request, user, None)
    assert calls == [1]


def test_kartenentscheidung_ohne_agenten_write_gilt_auch_generisch():
    """Wo die MCP-Karte bewusst keinen Agenten-Write vorsieht, sperrt die Maske Agenten — sonst fuehrte
    mask.action.execute die Aktion trotzdem aus (19.10.2026: Mahnen war so fuer Agenten offen)."""
    import yaml

    from app.core.screen_definitions import get_screen_definition

    karte = yaml.safe_load(open("config/mcp_mask_action_map.yaml", encoding="utf-8"))
    offen = []
    for eintrag in karte["mappings"]:
        if eintrag["coverage"] not in {"mapped_read", "open_high", "open_medium", "blocked_human_only"}:
            continue
        _, sid, key = (eintrag.get("mask_action_id") or "::").split(":")
        action = next((a for a in mm.iter_actions(get_screen_definition(sid) or {}) if a.get("key") == key), None)
        if action and action.get("commandEndpoint") and mm.agent_block(action) is None:
            offen.append(eintrag["mask_action_id"])
    assert offen == []


def test_statusleser_einer_gesperrten_aktion_bleibt_fuer_agenten_offen():
    """Mahnen ist Menschen vorbehalten; das Lesewerkzeug fibu.dunning.status loest es nicht aus."""
    assert mm.human_only_tool_call("fibu.dunning.status", {}) is None
