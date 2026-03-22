"""
Mandantenbezogene Futtermittellisten für die LP (z. B. Raufutter aus default ergänzen).
"""
from __future__ import annotations

import logging
from typing import Any, List, Tuple

from ..schemas.feed import FeedGroup, FeedIngredient

logger = logging.getLogger(__name__)

DEFAULT_SUPPLEMENT_SOURCE_TENANT = "default"

FORAGE_SUPPLEMENT_WARNING_DE = (
    "Mandant ohne Raufutter — Grassilage/Maissilage aus Mandant 'default' "
    "für erfüllbaren Mindest-Raufutteranteil ergänzt."
)


def ensure_forage_feeds_for_lp(
    feeds: List[FeedIngredient],
    tenant_id: str,
    feed_service: Any,
) -> Tuple[List[FeedIngredient], bool, List[str]]:
    """
    Wenn der Mandant nicht ``default`` ist und die Liste kein FORAGE enthält,
    werden aktive Raufutter-Futtermittel aus ``default`` vorangestellt (wie Demo).

    Returns:
        (feeds_out, supplemented, extra_warnings)
    """
    if tenant_id == DEFAULT_SUPPLEMENT_SOURCE_TENANT:
        return feeds, False, []
    if any(f.group == FeedGroup.FORAGE for f in feeds):
        return feeds, False, []

    forages = [
        f
        for f in feed_service.get_all_feeds(
            active_only=True, tenant_id=DEFAULT_SUPPLEMENT_SOURCE_TENANT
        )
        if f.group == FeedGroup.FORAGE
    ]
    if not forages:
        return feeds, False, []

    out = forages + list(feeds)
    logger.info(
        "Tenant '%s': %s Grundfutterzeilen aus '%s' ergänzt",
        tenant_id,
        len(forages),
        DEFAULT_SUPPLEMENT_SOURCE_TENANT,
    )
    return out, True, [FORAGE_SUPPLEMENT_WARNING_DE]
