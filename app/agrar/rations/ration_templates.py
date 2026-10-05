"""Domain rules for immutable ration templates and provenance-preserving copies."""

from __future__ import annotations


class RationTemplateValidationError(ValueError):
    pass


def normalize_template_name(value: str) -> str:
    name = " ".join(value.split())
    if not name:
        raise RationTemplateValidationError("Vorlagenname ist erforderlich.")
    if len(name) > 240:
        raise RationTemplateValidationError("Vorlagenname darf hoechstens 240 Zeichen enthalten.")
    return name


def validate_copy_reason(value: str) -> str:
    reason = " ".join(value.split())
    if len(reason) < 10:
        raise RationTemplateValidationError("Der Kopiergrund muss mindestens 10 Zeichen enthalten.")
    if len(reason) > 2_000:
        raise RationTemplateValidationError("Der Kopiergrund darf hoechstens 2000 Zeichen enthalten.")
    return reason
