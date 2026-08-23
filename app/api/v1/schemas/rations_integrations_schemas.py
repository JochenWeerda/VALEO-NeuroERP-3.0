"""Response-Schemas fuer die Rations-Schnittstellen und Herd-Data.

SPEC-P1-06 Welle 5: ersetzt ``response_model=dict`` bzw. ``list[dict]`` in
``app/api/v1/endpoints/rations_integrations.py``.

Alle Spaltenlisten stehen explizit in den SELECT- bzw. RETURNING-Klauseln der
Endpunkte, sind also exakt ableitbar. Die JSONB-Nutzlasten (``result``,
``payload``, ``endpoint_templates``, ``query_parameters``) bleiben offen — ihr
Inhalt haengt am jeweiligen Fremdstandard.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class RationsImportOut(BaseSchema):
    """Eintrag im Importjournal ``domain_agrar.rations_integration_imports``.

    ``duplicate`` kennzeichnet den Idempotenzpfad: bei bereits bekannter
    ``external_id`` liefert der Endpunkt die gespeicherte Zeile zurueck.
    """

    id: Optional[str] = None
    adapter: Optional[str] = None
    external_id: Optional[str] = None
    source_version: Optional[str] = None
    target_model: Optional[str] = None
    result: Optional[Any] = Field(default=None, description="Normalisiertes Zielmodell (JSONB)")
    imported_at: Optional[datetime] = None
    duplicate: Optional[bool] = Field(
        default=None, description="True, wenn die external_id bereits importiert war"
    )


class HerdDataConnectionOut(BaseSchema):
    """Zeile aus ``domain_agrar.herd_data_connections``.

    Zugangsdaten werden nie zurueckgegeben — nur der Schluesselname der
    Umgebungsvariablen (``credential_env_key``).
    """

    id: Optional[str] = None
    provider: Optional[str] = None
    herd_id: Optional[str] = None
    base_url: Optional[str] = None
    endpoint_templates: Optional[Any] = None
    query_parameters: Optional[Any] = None
    credential_env_key: Optional[str] = Field(
        default=None, description="Name der Umgebungsvariablen, nicht das Geheimnis selbst"
    )
    contract_ref: Optional[str] = None
    consent_ref: Optional[str] = Field(default=None, description="Einwilligungsnachweis")
    enabled: Optional[bool] = None
    live_enabled: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HerdDataSyncOut(BaseSchema):
    """``POST /herd-data/connections/{id}/sync`` — Delta-Sync-Lauf."""

    run_id: Optional[str] = None
    status: Optional[str] = None
    cursor_from: Optional[Any] = None
    cursor_to: Optional[Any] = None
    imported_count: Optional[int] = None


class HerdDataObservationOut(BaseSchema):
    """Zeile aus ``domain_agrar.herd_data_observations``."""

    id: Optional[str] = None
    provider: Optional[str] = None
    herd_id: Optional[str] = None
    kind: Optional[str] = None
    entity_id: Optional[str] = None
    effective_at: Optional[datetime] = None
    provider_updated_at: Optional[datetime] = None
    group_id: Optional[str] = None
    previous_group_id: Optional[str] = None
    is_deleted: Optional[bool] = None
    payload: Optional[Any] = Field(default=None, description="Rohbeobachtung (JSONB)")
    imported_at: Optional[datetime] = None


class HerdDataMockImportOut(BaseSchema):
    """``POST /herd-data/mock-import`` — Normalisierung ohne Fremdsystem."""

    kind: Optional[str] = None
    normalized_count: Optional[int] = None
    imported_count: Optional[int] = Field(
        default=None, description="0, wenn nicht persistiert wurde"
    )
    observations: list[dict[str, Any]] = Field(
        default_factory=list, description="Normalisierte Beobachtungen"
    )
