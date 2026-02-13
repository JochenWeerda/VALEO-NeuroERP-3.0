from app.core.module_registry import registry
from modules.bootstrap import initialize_module_registry


def test_module_registry_contains_core_and_agrar():
    initialize_module_registry()
    modules = {item["name"]: item for item in registry.as_dict()}

    assert "core" in modules
    assert "agrar" in modules


def test_module_registry_enabled_flag_is_boolean():
    initialize_module_registry()
    for item in registry.as_dict():
        assert isinstance(item["enabled"], bool)
