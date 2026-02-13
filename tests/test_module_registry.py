from app.core.module_registry import registry
from app.core.config import settings
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


def test_module_registry_supports_tenant_specific_flags():
    initialize_module_registry()
    original_flags = settings.TENANT_MODULE_FLAGS
    try:
        settings.TENANT_MODULE_FLAGS = {
            "tenant-alpha": ["core"],
            "tenant-beta": ["core", "agrar"],
        }
        modules_alpha = {item["name"]: item for item in registry.as_dict(tenant_id="tenant-alpha")}
        modules_beta = {item["name"]: item for item in registry.as_dict(tenant_id="tenant-beta")}

        assert modules_alpha["core"]["enabled"] is True
        assert modules_alpha["agrar"]["enabled"] is False
        assert modules_beta["core"]["enabled"] is True
        assert modules_beta["agrar"]["enabled"] is True
    finally:
        settings.TENANT_MODULE_FLAGS = original_flags
