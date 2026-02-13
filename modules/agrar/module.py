"""
Agrar module manifest.
"""

from app.core.module_registry import ModuleDefinition


AGRAR_MODULE = ModuleDefinition(
    name="agrar",
    title="Agrar Vertical",
    version="1.0.0",
    description=(
        "Agrar-spezifische Kernfunktionen wie Wiegeschein, Kontraktlogik, "
        "Silo-/Partieverwaltung, Gutschrift und Compliance-Exports."
    ),
    required_modules=["core"],
)

