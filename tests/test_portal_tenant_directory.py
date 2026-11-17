"""Unit tests: the directory never trusts a caller-selected subject or a weak DB role."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.auth.portal_kunde import NUR_DURCH_DAS_HAUS, PORTAL_RECHTE, UEBERSICHT
from app.core.tenant_context import cross_tenant_reason, current_tenant_or_none, tenant_scope
from app.services import portal_tenant_directory as directory

pytestmark = pytest.mark.unit

USER = {"sub": "subject-a", "raw": {"sub": "subject-a", "tenant_id": "tenant-a"}}


class Result:
    def __init__(self, value):
        self.value = value

    def one(self):
        return self.value

    def all(self):
        return self.value


class FakeSession:
    def __init__(self, role=("valeo_system", False, True), rows=()):
        self.role, self.rows, self.calls = role, rows, []
        self.rolled_back = self.closed = False

    def execute(self, statement, params=None):
        assert cross_tenant_reason() and current_tenant_or_none() is None
        self.calls.append((str(statement), params))
        if len(self.calls) == 1:
            return Result(None)
        if len(self.calls) == 2:
            return Result(self.role)
        return Result(self.rows)

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


@pytest.mark.parametrize("user", [None, {}, {"sub": "a", "raw": {"sub": "b", "tenant_id": "x"}},
                                  {"sub": " ", "raw": {"sub": " ", "tenant_id": "x"}}])
def test_ungueltige_identitaet_ohne_datenbank(monkeypatch, user):
    monkeypatch.setattr(directory, "system_session", lambda: pytest.fail("unexpected session"))
    with pytest.raises(HTTPException) as exc:
        directory.eigene_handelspartner(user)
    assert exc.value.status_code == 403


def test_fehlende_systemkonfiguration_oeffnet_keine_datenbank(monkeypatch):
    monkeypatch.setattr(directory.settings, "SYSTEM_DATABASE_URL", None)
    monkeypatch.setattr(directory, "system_session", lambda: pytest.fail("unexpected session"))
    with pytest.raises(HTTPException) as exc:
        directory.eigene_handelspartner(USER)
    assert exc.value.status_code == 503


@pytest.mark.parametrize("role", [("valeo_app", False, True), ("valeo_system", True, True),
                                  ("valeo_system", False, False)])
def test_falsche_rolle_sperrt_abfrage(monkeypatch, role):
    db = FakeSession(role=role)
    monkeypatch.setattr(directory.settings, "SYSTEM_DATABASE_URL", "configured")
    monkeypatch.setattr(directory, "system_session", lambda: db)
    with pytest.raises(HTTPException) as exc:
        directory.eigene_handelspartner(USER)
    assert exc.value.status_code == 503
    assert len(db.calls) == 2 and db.rolled_back and db.closed


def test_eigene_abfrage_mit_readonly_scope_und_gebundenem_subject(monkeypatch):
    db = FakeSession(rows=[("tenant-a", "A", 2), ("tenant-b", "B", 1)])
    monkeypatch.setattr(directory.settings, "SYSTEM_DATABASE_URL", "configured")
    monkeypatch.setattr(directory, "system_session", lambda: db)
    with tenant_scope("tenant-a", "test"):
        result = directory.eigene_handelspartner(USER)
        assert current_tenant_or_none() == "tenant-a"
    assert db.calls[0][0] == "SET TRANSACTION READ ONLY"
    assert "current_user" in db.calls[1][0]
    sql, params = db.calls[2]
    assert "z.subject = :subject" in sql and "subject-a" not in sql
    for fragment in ("z.widerrufen_am IS NULL", "z.gueltig_bis > now()", "c.deleted_at IS NULL",
                     "t.is_active IS TRUE", "c.tenant_id = z.tenant_id", "LIMIT :limit"):
        assert fragment in sql
    assert params["subject"] == USER["sub"] and params["limit"] == 101
    assert set(params["roles"]) == {role for role, rights in PORTAL_RECHTE.items()
                                    if UEBERSICHT in rights and role not in NUR_DURCH_DAS_HAUS}
    assert result == [{"id": "tenant-a", "name": "A", "customer_count": 2, "active": True},
                      {"id": "tenant-b", "name": "B", "customer_count": 1, "active": False}]
    assert db.rolled_back and db.closed


def test_zu_viele_tenants_keine_teilantwort(monkeypatch):
    db = FakeSession(rows=[(str(i), "A", 1) for i in range(101)])
    monkeypatch.setattr(directory.settings, "SYSTEM_DATABASE_URL", "configured")
    monkeypatch.setattr(directory, "system_session", lambda: db)
    with pytest.raises(HTTPException) as exc:
        directory.eigene_handelspartner(USER)
    assert exc.value.status_code == 503 and db.rolled_back and db.closed


@pytest.mark.parametrize("claims", [{"sub": "subject-a"},
    {"sub": "subject-a", "tenant_id": "a", "mandanten_id": "b"}])
def test_fehlender_oder_widerspruechlicher_tokenmandant(monkeypatch, claims):
    monkeypatch.setattr(directory, "system_session", lambda: pytest.fail("unexpected session"))
    with pytest.raises(HTTPException) as exc:
        directory.eigene_handelspartner({"sub": "subject-a", "raw": claims})
    assert exc.value.status_code == 403


def test_datenbankfehler_gibt_keine_internen_daten_aus(monkeypatch):
    monkeypatch.setattr(directory.settings, "SYSTEM_DATABASE_URL", "configured")
    def broken():
        raise RuntimeError("private connection and query details")
    monkeypatch.setattr(directory, "system_session", broken)
    with pytest.raises(HTTPException) as exc:
        directory.eigene_handelspartner(USER)
    assert exc.value.status_code == 503
    assert "private" not in exc.value.detail
