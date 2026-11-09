"""Maskenfamilien in der Registry: jede aktuelle Variante als ``<familie>/<variante>`` (ab 08.11.2026).

Ausgeliefert wird die **versionierte** Fassung aus ``config/mask_families/<familie>.json`` (Basis + Patch, gehasht),
nicht der Builder. Dass Builder und Registry gleich laufen, prueft ``tests/test_mask_family_versions.py``; ein
neues Release schreibt ``python scripts/generate_mask_family_versions.py --family <f> --release-version <v>``.
"""
from __future__ import annotations

from functools import partial
from typing import Any, Callable

from app.core.mask_family_versions import family_definition, versioned_screen_ids


def _materialisiert(family: str, variant_id: str) -> dict[str, Any]:
    return family_definition(family, variant_id)


def family_screen_builders() -> dict[str, Callable[[], dict[str, Any]]]:
    return {sid: partial(_materialisiert, family, variant)
            for sid, (family, variant) in versioned_screen_ids().items()}


FAMILY_SCREEN_BUILDERS = family_screen_builders()
