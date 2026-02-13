"""
Module registry for plugin-like vertical modules.
"""

from dataclasses import asdict, dataclass, field
from typing import Dict, List

from app.core.config import settings


@dataclass(frozen=True)
class ModuleDefinition:
    """
    Static module metadata used for runtime visibility and feature gating.
    """

    name: str
    title: str
    version: str
    description: str
    required_modules: List[str] = field(default_factory=list)


class ModuleRegistry:
    def __init__(self) -> None:
        self._definitions: Dict[str, ModuleDefinition] = {}
        self._initialized = False

    def register(self, definition: ModuleDefinition) -> None:
        self._definitions[definition.name] = definition

    def get(self, name: str) -> ModuleDefinition | None:
        return self._definitions.get(name)

    def list_all(self) -> List[ModuleDefinition]:
        return list(self._definitions.values())

    def is_enabled(self, name: str) -> bool:
        installed = set(settings.INSTALLED_MODULES)
        return name in installed

    def enabled_modules(self) -> List[ModuleDefinition]:
        return [m for m in self.list_all() if self.is_enabled(m.name)]

    def as_dict(self) -> List[dict]:
        modules: List[dict] = []
        for definition in self.list_all():
            payload = asdict(definition)
            payload["enabled"] = self.is_enabled(definition.name)
            modules.append(payload)
        return modules

    @property
    def initialized(self) -> bool:
        return self._initialized

    def mark_initialized(self) -> None:
        self._initialized = True


registry = ModuleRegistry()
