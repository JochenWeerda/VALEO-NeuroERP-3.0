"""Manager is historical metadata, never an independent authorization grant."""
import asyncio
import inspect

import pytest
from fastapi import HTTPException
from app.auth import deps, deps_oidc, finance_roles
from app.auth.beleg_roles import RECHTE, darf
from app.auth.bereich_roles import SCHREIBEN
from app.auth.scopes import get_scopes_for_roles
from app.core.belegvertrag import BELEGARTEN
from scripts.keycloak_document_scopes import DOCUMENT_SCOPE_ROLES
from test_system_tenant_binding import keys, probe


def call(guard, user):
    result = guard(user=user)
    return asyncio.run(result) if inspect.isawaitable(result) else result


@pytest.mark.parametrize("guard", [deps.require_roles("manager", "SALES_BEARBEITEN"),
    deps_oidc.require_roles("manager", "SALES_BEARBEITEN"),
    deps_oidc.require_roles_and_scopes(["manager", "SALES_BEARBEITEN"], ["sales:write"])])
@pytest.mark.parametrize("roles,allowed", [(["manager"], False), (["manager", "FINANCE_LESEN"], False),
    (["manager", "SALES_BEARBEITEN"], True), (["SALES_BEARBEITEN"], True)])
def test_all_role_guards_ignore_manager_without_mutating_verified_identity(guard, roles, allowed):
    user = {"sub": "synthetic", "roles": roles.copy(), "scopes": ["sales:write"]}
    if allowed:
        assert call(guard, user) is user
    else:
        with pytest.raises(HTTPException) as error:
            call(guard, user)
        assert error.value.status_code == 403
    assert user["roles"] == roles


@pytest.mark.parametrize("area", [k for k in SCHREIBEN if k not in {"EIGENE_DATEN", "GERAET"}])
def test_current_area_dependencies_deny_manager_alone(area):
    for dependency in SCHREIBEN[area]:
        with pytest.raises(HTTPException) as error:
            call(dependency.dependency, {"sub": "synthetic", "roles": ["manager"]})
        assert error.value.status_code == 403


@pytest.mark.parametrize("right", RECHTE)
def test_manager_has_no_document_right_on_any_variant(right):
    for kind in BELEGARTEN:
        assert not darf({"roles": ["manager"]}, right, kind), (right, kind)


@pytest.mark.parametrize("role", ["SALES_LESEN", "SALES_BEARBEITEN", "SALES_ADMIN", "EINKAUF_BEARBEITEN",
    "LAGER_BEARBEITEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN"])
def test_additional_manager_role_never_expands_a_domain_role(role):
    for right in RECHTE:
        for kind in BELEGARTEN:
            assert darf({"roles": [role, "manager"]}, right, kind) == darf({"roles": [role]}, right, kind)


@pytest.mark.parametrize("guard", [finance_roles.finance_read, finance_roles.finance_write,
    finance_roles.finance_admin, finance_roles.beleg_read, finance_roles.beleg_write, finance_roles.kontenpflege])
def test_finance_guards_deny_manager(guard):
    with pytest.raises(HTTPException) as error:
        call(guard, {"sub": "synthetic", "roles": ["manager"]})
    assert error.value.status_code == 403


def test_manager_has_no_projected_scopes():
    assert get_scopes_for_roles(["manager"]) == []
    assert all("manager" not in roles for roles in DOCUMENT_SCOPE_ROLES.values())
    assert get_scopes_for_roles(["manager", "operator"]) == get_scopes_for_roles(["operator"])


@pytest.mark.parametrize("roles,expected", [(["manager"],403), (["manager","FINANCE_LESEN"],403),
    (["manager","FINANCE_BEARBEITEN"],200)])
def test_signed_real_token_cannot_use_manager_for_finance(probe, roles, expected):
    response = probe.client.get("/api/probe", headers={"Authorization": "Bearer "+probe.token(changes={"roles": roles})})
    assert response.status_code == expected
    assert len(probe.calls) == int(expected == 200)
