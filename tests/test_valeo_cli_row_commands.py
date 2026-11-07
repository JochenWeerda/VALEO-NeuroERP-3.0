import io
import json

import httpx
import pytest

from app.core.screen_definitions import get_screen_definition
from valeo_cli import cli

CASES = [
    ("personal/onboarding", "/api/v1/training/onboarding/runs/row-1/actions/loeschen", "expected_revision=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", []),
    ("personal/qualifikationen", "/api/v1/training/qualifications/row-1/actions/loeschen", "expected_revision=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", []),
    ("personal/schulungen", "/api/v1/training/assignments/row-1/actions/loeschen", "expected_revision=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", []),
    ("logistik/versandprofile", "/api/v1/logistik/versand/profile/row-1/actions/deactivate", "expected_active=true", ["--grund", "Pruefung"]),
]


def run(monkeypatch, screen, field, extra=(), *, claims=None, fail=False, status=200):
    monkeypatch.setenv("VALEO_API_URL", "https://api.invalid")
    monkeypatch.setenv("VALEO_OIDC_ISSUER", "https://idp.invalid")
    monkeypatch.setattr(cli.auth, "access_token", lambda *args: "token")
    monkeypatch.setattr(cli.auth, "claims", lambda _: claims or {"identity_type": "human"})
    calls, lines = [], []
    def handler(request):
        if request.url.path.endswith("/screen-definition"):
            return httpx.Response(200, json=get_screen_definition(screen))
        calls.append(request)
        if fail:
            raise httpx.ReadTimeout("uncertain", request=request)
        return httpx.Response(status, json={"success": True} if status == 200 else {"detail": "verweigert"})
    argv = ["ausfuehren", screen, "loeschen", "--id", "row-1", "--feld", field, "--ja", "--json", *extra]
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        code = cli.main(argv, http=client, out=lines.append, ask=lambda _: "nein", stdin=io.StringIO())
    return code, calls, "\n".join(lines)


@pytest.mark.parametrize("screen,path,field,extra", CASES)
def test_row_command_exact_body_and_retry_key(monkeypatch, screen, path, field, extra):
    code, calls, output = run(monkeypatch, screen, field, [*extra, "--idempotenz", "same-key"])
    assert code == 0 and len(calls) == 1
    sent = calls[0]
    assert sent.method == "POST" and sent.url.path == path
    assert sent.headers["Authorization"] == "Bearer token"
    expected = {"_idempotencyKey": "same-key"}
    if field.startswith("expected_active"):
        expected.update(expected_active=True, _auditReason="Pruefung")
    else:
        expected["expected_revision"] = field.split("=", 1)[1]
    assert json.loads(sent.content) == expected


@pytest.mark.parametrize("screen,path,field,extra", CASES)
def test_row_command_no_dry_run(monkeypatch, screen, path, field, extra):
    code, calls, _ = run(monkeypatch, screen, field, [*extra, "--modus", "dryRun"])
    assert code != 0 and not calls


@pytest.mark.parametrize("screen,path,field,extra", CASES)
def test_agent_receives_server_capability_decision_with_original_token(monkeypatch, screen, path, field, extra):
    status = 200 if screen == "logistik/versandprofile" else 403
    code, calls, _ = run(monkeypatch, screen, field, extra, claims={"identity_type": "agent"}, status=status)
    assert code == (0 if status == 200 else 3) and len(calls) == 1
    assert calls[0].headers["Authorization"] == "Bearer token"


@pytest.mark.parametrize("screen,path,field,extra", CASES)
def test_delegated_identity_server_rejection_is_not_bypassed(monkeypatch, screen, path, field, extra):
    code, calls, _ = run(monkeypatch, screen, field, extra,
                         claims={"identity_type": "human", "act": {"sub": "agent"}}, status=403)
    assert code == 3 and len(calls) == 1
    assert calls[0].headers["Authorization"] == "Bearer token"


def test_uncertain_result_prints_reusable_key(monkeypatch):
    screen, _, field, extra = CASES[0]
    code, calls, output = run(monkeypatch, screen, field, extra, fail=True)
    key = json.loads(calls[0].content)["_idempotencyKey"]
    assert code == 4 and f"--idempotenz {key}" in output
    code, calls, _ = run(monkeypatch, screen, field, ["--idempotenz", key])
    assert code == 0 and json.loads(calls[0].content)["_idempotencyKey"] == key


@pytest.mark.parametrize("field,extra", [("expected_revision=abc", []),
    ("expected_revision=" + "A" * 64, []),
    ("expected_updated_at=2026-11-07T12:00:00Z", []),
    ("expected_revision=" + "a" * 64, ["--version", "3"]),
    ("expected_revision=" + "a" * 64, ["--feld", "tenant_id=other"])])
def test_rejects_bad_version_or_extra_fields(monkeypatch, field, extra):
    code, calls, _ = run(monkeypatch, CASES[0][0], field, extra)
    assert code != 0 and not calls
