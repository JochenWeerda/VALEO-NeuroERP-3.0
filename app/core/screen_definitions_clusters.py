"""Alle Masken-Cluster (Studio-Listen aus vorhandenen Lesewegen, ab 02.11.2026) an einer Stelle.

Die Registry nimmt sie nach batch15 auf (sie ersetzen dortige Platzhalter); Vertragstests, die Studio-Listen
zaehlen, lesen dieselbe Sammlung. Ein neuer Batch traegt sich nur hier ein.
"""
from __future__ import annotations

from typing import Any

from app.core.screen_definitions_cluster_eigene_wege import CLUSTER_EIGENE_WEGE_SCREEN_BUILDERS
from app.core.screen_definitions_cluster_fibu import CLUSTER_FIBU_SCREEN_BUILDERS
from app.core.screen_definitions_cluster_futter import CLUSTER_FUTTER_SCREEN_BUILDERS
from app.core.screen_definitions_cluster_lager import CLUSTER_LAGER_SCREEN_BUILDERS

CLUSTER_SCREEN_BUILDERS: dict[str, Any] = {
    **CLUSTER_FIBU_SCREEN_BUILDERS,
    **CLUSTER_LAGER_SCREEN_BUILDERS,
    **CLUSTER_FUTTER_SCREEN_BUILDERS,
    **CLUSTER_EIGENE_WEGE_SCREEN_BUILDERS,
}
