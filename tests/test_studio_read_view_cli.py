"""CLI read views use only the declared safe GET and enforce action policy."""
import base64
import io
import json

import httpx
import pytest

from valeo_cli import cli, support


def token(identity=None):
    def encode(value):
        return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")
    claims = {"sub": "fixture", "tenant_id": "t1", "exp": 4_000_000_000}
    if identity is not None:
        claims["identity_type"] = identity
    return f"{encode({'alg': 'none'})}.{encode(claims)}.sig"


def action(endpoint="/api/v1/studio/webhooks/{entity_id}/history", **extra):
    return {"key": "history", "localEffect": "view", "readView": {"endpoint": endpoint}, **extra}


def run(monkeypatch, tmp_path, declared, *args, identity="human"):
    monkeypatch.setenv("VALEO_API_URL", "https://api.invalid")
    monkeypatch.setenv("VALEO_CLI_SESSION", str(tmp_path / "session.json"))
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", token(identity))
    calls = []
    def handler(request):
        if request.url.path.endswith("/screen-definition"):
            return httpx.Response(200, json={"id": "studio/webhooks", "actions": [declared]})
        calls.append(request)
        return httpx.Response(200, json={"events": [{"status": "delivered"}]})
    lines = []
    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        code = cli.main(["ausfuehren", "studio/webhooks", "history", *args], http=http,
                        out=lines.append, ask=lambda _: "ja", stdin=io.StringIO("{}"))
    return code, "\n".join(lines), calls


def test_history_get_escapes_entity_id_and_returns_result(monkeypatch, tmp_path):
    code, output, calls = run(monkeypatch, tmp_path, action(), "--id", "one/two ?#")
    assert code == 0
    assert json.loads(output) == {"events": [{"status": "delivered"}]}
    assert len(calls) == 1
    assert calls[0].method == "GET"
    assert calls[0].url.raw_path == b"/api/v1/studio/webhooks/one%2Ftwo%20%3F%23/history"
    assert calls[0].content == b""


@pytest.mark.parametrize("parameter", ["tenant_id", "mandant_id", "actor_id", "user_id", "agent_id"])
def test_identity_placeholders_rejected_before_read(monkeypatch, tmp_path, parameter):
    declared = action(f"/api/v1/studio/webhooks/{{{parameter}}}/history")
    assert not support.support(declared).supported
    code, _, calls = run(monkeypatch, tmp_path, declared, "--id", "other")
    assert code != 0 and calls == []


@pytest.mark.parametrize("endpoint", [
    "/api/v1/studio/../history", "/api/v1/studio/%2e%2e/history",
    "/api/v1/studio/history?tenant=other", "https://evil.invalid/api/v1/history",
    "/api/v1/studio/{one}/{two}/history",
])
def test_invalid_paths_never_issue_read(monkeypatch, tmp_path, endpoint):
    code, _, calls = run(monkeypatch, tmp_path, action(endpoint), "--id", "item")
    assert code != 0 and calls == []


@pytest.mark.parametrize("extra", [
    ["--id", "."], ["--id", ".."], [],
    ["--id", "item", "--modus", "dryRun"],
    ["--id", "item", "--modus", "validate"],
    ["--id", "item", "--modus", "propose"],
    ["--id", "item", "--feld", "x=y"],
    ["--id", "item", "--daten", "-"],
])
def test_invalid_execution_arguments_never_issue_read(monkeypatch, tmp_path, extra):
    code, _, calls = run(monkeypatch, tmp_path, action(), *extra)
    assert code != 0 and calls == []


@pytest.mark.parametrize("flag", ["forbiddenForAgents", "humanApprovalRequired"])
@pytest.mark.parametrize("identity", ["service", None])
def test_agent_and_unknown_identity_are_blocked(monkeypatch, tmp_path, flag, identity):
    code, _, calls = run(monkeypatch, tmp_path, action(**{flag: True}), "--id", "item", identity=identity)
    assert code == 1 and calls == []


@pytest.mark.parametrize("flag", ["forbiddenForAgents", "humanApprovalRequired"])
def test_human_can_read_when_agent_policy_applies(monkeypatch, tmp_path, flag):
    code, _, calls = run(monkeypatch, tmp_path, action(**{flag: True}), "--id", "item")
    assert code == 0 and len(calls) == 1 and calls[0].method == "GET"
