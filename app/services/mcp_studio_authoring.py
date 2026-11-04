"""Studio-Authoring fuer Agenten (MCP/CLI): ein LLM baut Masken nur ueber Studio, nie daran vorbei.

Werkzeuge:

* ``studio.catalog.read`` - Floorplans, Feldtypen, Datenquellen, Aktionen (was eine Maske enthalten darf).
* ``studio.definition.validate`` - eine ScreenDefinition gegen Katalog und Gates pruefen (schreibt nichts).
* ``studio.draft.save`` - Entwurf anlegen oder (mit ``draft_id`` + ``expected_revision``) fortschreiben.
* ``studio.draft.submit_review`` - Entwurf zur Vier-Augen-Pruefung geben.

Freigeben (``publish``) und Zurueckziehen bleiben Menschen vorbehalten: dafuer gibt es kein Werkzeug. Jeder Aufruf
geht mit dem Bearer-Token des Aufrufers an denselben HTTP-Weg wie das Studio im Browser; Rolle, Mandant, Gates,
Revision und Wiederholungsschutz prueft der Ziel-Endpunkt, dieses Modul gewaehrt nichts.
"""
from __future__ import annotations

import json
import os
from typing import Any
from uuid import UUID

import httpx
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.services.mask_data_read import _json_constant, _json_object

TOOLS = {"studio.catalog.read", "studio.definition.validate", "studio.draft.save", "studio.draft.submit_review"}
SCHREIBEND = {"studio.draft.save", "studio.draft.submit_review"}
_LIMIT = 2 * 1024 * 1024


class _DefinitionParameter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    definition: dict[str, Any]


class _SaveParameter(_DefinitionParameter):
    draft_id: UUID | None = None
    expected_revision: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class _ReviewParameter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    draft_id: UUID
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")


def studio_http(method: str, path: str, authorization: str | None, body: dict | None = None, *,
                transport: Any = None) -> dict:
    """Ruft einen Studio-Weg mit dem Token des Aufrufers; Fehler des Servers bleiben sein Urteil."""
    if not authorization or not authorization.startswith("Bearer ") or not authorization[7:].strip():
        raise HTTPException(401, "Bearer-Token des Aufrufers fehlt")
    base = os.environ.get("MASK_ACTION_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        with httpx.Client(base_url=base, timeout=30, transport=transport, follow_redirects=False) as client:
            with client.stream(method, path, headers={"Authorization": authorization}, json=body) as response:
                data = bytearray()
                for chunk in response.iter_bytes():
                    data.extend(chunk)
                    if len(data) > _LIMIT:
                        raise HTTPException(502, "Studio-Antwort ueberschreitet das Limit")
                try:
                    result = json.loads(data, object_pairs_hook=_json_object, parse_constant=_json_constant) if data else {}
                except (ValueError, UnicodeError) as error:
                    if response.status_code >= 400:
                        raise HTTPException(response.status_code, "Studio-Auftrag vom Server abgelehnt") from error
                    raise HTTPException(502, "Ungueltige Studio-Antwort") from error
                if response.status_code >= 400:
                    # Die Gate-Verletzungen (400) sind die Auskunft, die das Modell zum Nachbessern braucht.
                    detail = result.get("detail") if isinstance(result, dict) else None
                    raise HTTPException(response.status_code, detail or "Studio-Auftrag vom Server abgelehnt")
                if response.status_code != 200 or not isinstance(result, dict):
                    raise HTTPException(502, "Ungueltige Studio-Antwort")
                return result
    except httpx.HTTPError as error:
        raise HTTPException(503, "Studio derzeit nicht erreichbar") from error


def _parameter(modell: type[BaseModel], roh: Any) -> Any:
    try:
        return modell.model_validate(roh)
    except ValidationError as error:
        raise HTTPException(422, "Ungueltiger Studio-Auftrag") from error


def _idempotenz(request: Any) -> str:
    try:
        return str(UUID(str(request.idempotency_key)))
    except (TypeError, ValueError) as error:
        raise HTTPException(422, "Gueltiger Wiederholungsschluessel (UUID) ist erforderlich") from error


def _schreibrecht_freigeschaltet(name: str) -> None:
    """Wie studio.migration.plan: schreiben nur, wenn die Registry die Capability ausdruecklich freischaltet."""
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service

    capability = mcp_tool_registry_service.get_tool(name)
    if (capability.get("agent_write_enabled") is not True or capability.get("domain_command") != name
            or capability.get("command_version") != 1 or capability.get("role_policy") != "beleg_write"):
        raise HTTPException(403, "Studio-Capability ist nicht freigeschaltet")


def dispatch(request: Any, authorization: str | None, *, transport: Any = None) -> dict:
    name = request.tool_name
    if name == "studio.catalog.read":
        return studio_http("GET", "/api/v1/studio/catalog", authorization, transport=transport)
    if name == "studio.definition.validate":
        p = _parameter(_DefinitionParameter, request.parameters)
        return studio_http("POST", "/api/v1/studio/validate", authorization, {"definition": p.definition}, transport=transport)
    if name in SCHREIBEND and request.mode == "execute":
        _schreibrecht_freigeschaltet(name)
    if name == "studio.draft.save":
        p = _parameter(_SaveParameter, request.parameters)
        if (p.draft_id is None) != (p.expected_revision is None):
            raise HTTPException(422, "Fortschreiben braucht draft_id und expected_revision zusammen")
        if request.mode != "execute":
            # Ohne Ausfuehrung: dieselbe Pruefung wie beim Speichern, nichts wird gespeichert.
            report = studio_http("POST", "/api/v1/studio/validate", authorization, {"definition": p.definition}, transport=transport)
            return {**report, "persisted": False, "validation_only": True}
        body = {"definition": p.definition, "idempotency_key": _idempotenz(request)}
        if p.draft_id is None:
            return studio_http("POST", "/api/v1/studio/drafts", authorization, body, transport=transport)
        return studio_http("PUT", f"/api/v1/studio/drafts/{p.draft_id}", authorization,
                           {**body, "expected_revision": p.expected_revision}, transport=transport)
    if name == "studio.draft.submit_review":
        p = _parameter(_ReviewParameter, request.parameters)
        if request.mode != "execute":
            return {"persisted": False, "validation_only": True, "draft_id": str(p.draft_id)}
        return studio_http("POST", f"/api/v1/studio/drafts/{p.draft_id}/submit-review", authorization,
                           {"expected_revision": p.expected_revision, "idempotency_key": _idempotenz(request)},
                           transport=transport)
    raise HTTPException(404, "Unbekanntes Studio-Werkzeug")
