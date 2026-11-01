from app.core.public_auth_screen_definitions import build_public_auth_screen
from scripts.generate_public_auth_screens import render, OUT


def test_generated_auth_surfaces_have_no_protected_transport_or_agent_execution():
    for sid in ("auth/login", "auth/callback"):
        definition = build_public_auth_screen(sid)
        assert not definition["dataSources"]
        assert all(action["forbiddenForAgents"] and action["localEffect"] == "view" and not action.get("commandEndpoint")
                   for action in definition["actions"])
    assert OUT.read_text(encoding="utf-8") == render()
