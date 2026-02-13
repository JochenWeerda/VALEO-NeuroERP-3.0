"""
Module bootstrap and registration.
"""

from app.core.module_registry import ModuleDefinition, registry
from modules.agrar.module import AGRAR_MODULE


def initialize_module_registry() -> None:
    if registry.initialized:
        return

    registry.register(
        ModuleDefinition(
            name="core",
            title="Core Platform",
            version="1.0.0",
            description="Shared ERP platform capabilities (auth, finance base, inventory base, docs).",
            required_modules=[],
        )
    )
    registry.register(AGRAR_MODULE)
    registry.mark_initialized()

