"""Classification must not turn authenticated membership discovery into public data."""
from scripts import check_tenant_isolation as gate


def test_directory_has_its_own_reviewed_boundary():
    name = "portal_handelspartner.py"
    assert name in gate.IDENTITY_MEMBERSHIP_ENDPOINTS
    assert name not in gate.SYSTEM_ENDPOINTS | gate.SHARED_DATA | gate.GAP_TRACKED.keys()
    assert "test_portal_tenant_directory_postgres.py" in gate.IDENTITY_MEMBERSHIP_ENDPOINTS[name]


def test_unknown_adapter_still_fails(tmp_path, monkeypatch, capsys):
    (tmp_path / "unreviewed.py").write_text('"""New adapter without tenant binding."""', encoding="utf-8")
    monkeypatch.setattr(gate, "ENDPOINTS_DIR", str(tmp_path))
    assert gate.main() == 1
    assert "unreviewed.py" in capsys.readouterr().out


def test_reviewed_directory_is_not_reported_as_tenant_isolated(tmp_path, monkeypatch, capsys):
    (tmp_path / "portal_handelspartner.py").write_text('"""Own identity memberships."""', encoding="utf-8")
    monkeypatch.setattr(gate, "ENDPOINTS_DIR", str(tmp_path))
    assert gate.main() == 0
    output = capsys.readouterr().out
    assert "identity-membership" in output
    assert "tenant-isolated" not in output
