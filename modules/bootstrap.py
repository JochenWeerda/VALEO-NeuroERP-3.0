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
    registry.register(
        ModuleDefinition(
            name="feeding_advisory",
            title="Fütterungsberatung",
            version="1.0.0",
            description=(
                "Fütterungsberatungs-Vertikal: Rationseditor, Fütterungspläne, "
                "Ist-Erfassung, Controlling-Berichte, Beratung und Assistenz "
                "(FEED-REL-047; per Tenant über TENANT_MODULE_FLAGS schaltbar)."
            ),
            required_modules=["agrar"],
        )
    )
    registry.mark_initialized()

