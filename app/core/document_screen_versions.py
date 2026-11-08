"""Immutable, content-bound document-screen bases and variants (no business writes).

Die Belegfamilie ist die erste Maskenfamilie; der Mechanismus liegt seit 08.11.2026 allgemein in
``app.core.mask_family_versions``. Datei, Variantenfeld (``variant.belegart``), Bindungsschluessel
(``documentVariant``) und Fehlercodes (``document_screen_*``) bleiben unveraendert.
"""
from functools import lru_cache
import json
from pathlib import Path

from app.core import mask_family_versions as _family

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "config/document_screen_versions.json"
BELEG = _family.FamilySpec(name="beleg", error_prefix="document_screen", binding_key="documentVariant",
                           variant_field="belegart")


def resolve_variant(registry, variant_id, version=None, *, expected=None):
    """Resolve an exact version; an expected binding never follows a changed alias."""
    return _family.resolve_variant(registry, variant_id, version, expected=expected, spec=BELEG)


def check_registry(registry):
    """Check historical entries too, not just the current aliases."""
    _family.check_registry(registry, spec=BELEG)


@lru_cache(maxsize=2)
def _read_registry(path, modified, size):
    registry = json.loads(Path(path).read_text(encoding="utf-8"))
    check_registry(registry)
    return registry


def document_definition(variant_id, version=None, *, expected=None):
    stat = REGISTRY_PATH.stat()
    registry = _read_registry(str(REGISTRY_PATH), stat.st_mtime_ns, stat.st_size)
    return resolve_variant(registry, variant_id, version, expected=expected)


def extend_registry(definitions, version, previous=None):
    """Append a release. Existing base/variant records are never overwritten."""
    return _family.extend_registry(definitions, version, previous, spec=BELEG)
