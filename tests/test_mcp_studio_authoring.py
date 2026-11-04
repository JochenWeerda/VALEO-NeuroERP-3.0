"""Studio-Authoring ueber MCP: ein Agent baut Masken nur ueber Studio-Wege, freigeben kann er nicht."""
from __future__ import annotations

import json
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException

from app.services import mcp_studio_authoring as studio

pytestmark = pytest.mark.unit
TOKEN = "Bearer agent-token"
REV = "a" * 64


def _transport(aufrufe: list, status: int = 200, antwort: dict | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        aufrufe.append((request.method, request.url.path, request.headers.get("authorization"),
                        json.loads(request.content) if request.content else None))
        return httpx.Response(status, json=antwort if antwort is not None else {"violations": [], "readiness": {}})
    return httpx.MockTransport(handler)


def _auftrag(name: str, parameter: dict | None = None, mode: str = "execute", key: str | None = None):
    return SimpleNamespace(tool_name=name, parameters=parameter or {}, mode=mode, idempotency_key=key)


def test_katalog_und_pruefung_lesen_mit_dem_token_des_aufrufers():
    aufrufe: list = []
    studio.dispatch(_auftrag("studio.catalog.read"), TOKEN, transport=_transport(aufrufe))
    studio.dispatch(_auftrag("studio.definition.validate", {"definition": {"id": "x"}}), TOKEN, transport=_transport(aufrufe))
    assert aufrufe == [("GET", "/api/v1/studio/catalog", TOKEN, None),
                       ("POST", "/api/v1/studio/validate", TOKEN, {"definition": {"id": "x"}})]


def test_speichern_ohne_execute_prueft_nur():
    aufrufe: list = []
    ergebnis = studio.dispatch(_auftrag("studio.draft.save", {"definition": {"id": "x"}}, mode="dryRun"), TOKEN,
                               transport=_transport(aufrufe))
    assert ergebnis["persisted"] is False and ergebnis["validation_only"] is True
    assert [(m, p) for m, p, _, _ in aufrufe] == [("POST", "/api/v1/studio/validate")]


def test_anlegen_fortschreiben_und_pruefung_anfordern():
    aufrufe: list = []
    key, draft = str(uuid4()), str(uuid4())
    studio.dispatch(_auftrag("studio.draft.save", {"definition": {"id": "x"}}, key=key), TOKEN, transport=_transport(aufrufe))
    studio.dispatch(_auftrag("studio.draft.save", {"definition": {"id": "x"}, "draft_id": draft, "expected_revision": REV},
                             key=key), TOKEN, transport=_transport(aufrufe))
    studio.dispatch(_auftrag("studio.draft.submit_review", {"draft_id": draft, "expected_revision": REV}, key=key), TOKEN,
                    transport=_transport(aufrufe))
    assert aufrufe == [
        ("POST", "/api/v1/studio/drafts", TOKEN, {"definition": {"id": "x"}, "idempotency_key": key}),
        ("PUT", f"/api/v1/studio/drafts/{draft}", TOKEN, {"definition": {"id": "x"}, "idempotency_key": key, "expected_revision": REV}),
        ("POST", f"/api/v1/studio/drafts/{draft}/submit-review", TOKEN, {"expected_revision": REV, "idempotency_key": key}),
    ]


def test_gate_verletzungen_kommen_beim_agenten_an():
    """Die Verletzungen sind die Auskunft, mit der das Modell nachbessert."""
    verletzung = {"detail": {"violations": ["computed is invalid"]}}
    with pytest.raises(HTTPException) as fehler:
        studio.dispatch(_auftrag("studio.draft.save", {"definition": {"id": "x"}}, key=str(uuid4())), TOKEN,
                        transport=_transport([], status=400, antwort=verletzung))
    assert fehler.value.status_code == 400 and fehler.value.detail == {"violations": ["computed is invalid"]}


@pytest.mark.parametrize("auftrag", [
    _auftrag("studio.draft.save", {"definition": {}}, key="kein-uuid"),
    _auftrag("studio.draft.save", {"definition": {}, "draft_id": str(uuid4())}, key=str(uuid4())),
    _auftrag("studio.draft.save", {"definition": {}, "tenant_id": "fremd"}, key=str(uuid4())),
])
def test_unvollstaendige_oder_fremde_angaben_werden_abgelehnt(auftrag):
    with pytest.raises(HTTPException) as fehler:
        studio.dispatch(auftrag, TOKEN, transport=_transport([]))
    assert fehler.value.status_code == 422


def test_ohne_token_kein_aufruf():
    with pytest.raises(HTTPException) as fehler:
        studio.dispatch(_auftrag("studio.catalog.read"), None, transport=_transport([]))
    assert fehler.value.status_code == 401


def test_freigeben_gibt_es_fuer_agenten_nicht():
    assert not any("publish" in name or "retire" in name for name in studio.TOOLS)
    with pytest.raises(HTTPException) as fehler:
        studio.dispatch(_auftrag("studio.draft.publish", {}), TOKEN, transport=_transport([]))
    assert fehler.value.status_code == 404


def test_registry_schaltet_nur_die_schreibwerkzeuge_frei():
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service

    for name in studio.TOOLS:
        tool = mcp_tool_registry_service.get_tool(name)
        assert (tool.get("agent_write_enabled") is True) == (name in studio.SCHREIBEND), name
        assert tool["scope"] == ("belege:write" if name in studio.SCHREIBEND else "masks:read"), name


def test_ohne_freigeschaltete_capability_wird_nicht_geschrieben(monkeypatch):
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service

    monkeypatch.setattr(mcp_tool_registry_service, "get_tool", lambda name: {"agent_write_enabled": False})
    with pytest.raises(HTTPException) as fehler:
        studio.dispatch(_auftrag("studio.draft.save", {"definition": {}}, key=str(uuid4())), TOKEN, transport=_transport([]))
    assert fehler.value.status_code == 403
