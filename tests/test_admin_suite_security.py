from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import admin_suite


def test_security_cockpit_keeps_agent_roles_separate():
    human_roles = admin_suite._security_roles()
    agent_roles = admin_suite._agent_roles()

    assert all(role.actor_type == "human" for role in human_roles)
    assert all(role.actor_type == "agent" for role in agent_roles)
    assert all("manage_system" not in role.permissions for role in agent_roles)


def test_security_simulation_surfaces_sod_warning_without_persisting():
    simulation = admin_suite._simulate_security(["finance_manager"])

    assert "create_finance" in simulation.effective_permissions
    assert "approve_payments" in simulation.effective_permissions
    assert any("Finance-Erfassung" in warning for warning in simulation.sod_warnings)


def test_security_simulation_rejects_unknown_role():
    with pytest.raises(HTTPException) as error:
        admin_suite._simulate_security(["root-agent"])

    assert error.value.status_code == 422
