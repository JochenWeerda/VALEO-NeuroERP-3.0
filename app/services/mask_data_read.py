"""Shared GET-source access for Human, CLI and MCP; no SQL or alternate business rights."""
import json
import os
import re
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit, unquote

import httpx
from fastapi import HTTPException

from app.api.v1.schemas.mask_data_contracts import MaskDataReadIn, MaskDataReadOut
from app.core.screen_definitions import get_screen_definition
from app.services.studio_draft_store import StudioStorageUnavailable

_MAX_BYTES = 2 * 1024 * 1024
_IDENTITY_KEYS = {"tenant_id", "mandanten_id", "actor", "user_id", "performed_by", "authorization"}


def resolve_source(body: MaskDataReadIn, tenant: str) -> str:
    if not tenant:
        raise HTTPException(403, "Verifizierter Mandant fehlt")
    try:
        definition = get_screen_definition(body.screen_id, tenant_id=tenant)
    except StudioStorageUnavailable as error:
        raise HTTPException(503, "Studio-Masken derzeit nicht verfuegbar") from error
    if definition is None:
        raise HTTPException(404, "Maske im Mandanten nicht gefunden")
    declared = definition.get("dataSources")
    if not isinstance(declared, list):
        raise HTTPException(409, "Maske besitzt keinen gueltigen Datenquellenvertrag")
    sources = [source for source in declared
               if isinstance(source, dict) and source.get("key") == body.source_key]
    if len(sources) != 1:
        raise HTTPException(404 if not sources else 409, "Datenquelle fehlt oder ist nicht eindeutig")
    source = sources[0]
    if source.get("method", "GET") != "GET":
        raise HTTPException(409, "Datenquelle besitzt keinen freigegebenen GET-Leseweg")
    endpoint = source.get("endpoint")
    if not isinstance(endpoint, str) or not endpoint.startswith("/api/v1/") or "\\" in endpoint:
        raise HTTPException(409, "Datenquelle muss ein deklarierter lokaler API-Weg sein")
    if any(ord(char) < 32 or ord(char) == 127 for char in endpoint):
        raise HTTPException(409, "Ungueltiger Datenquellenweg")
    variables = {"tenant_id": tenant}
    if body.entity_id:
        variables["entity_id"] = body.entity_id
    if body.q is not None:
        variables["q"] = body.q
    for key in re.findall(r"\{([^}]+)\}", endpoint):
        if key not in variables:
            raise HTTPException(422, "Datenquellenkontext fehlt oder wird nicht unterstuetzt")
        endpoint = endpoint.replace("{" + key + "}", quote(variables[key], safe=""))
    parts = urlsplit(endpoint)
    if parts.scheme or parts.netloc or parts.fragment or "{" in endpoint or "}" in endpoint:
        raise HTTPException(409, "Ungueltiger lokaler Datenquellenweg")
    # Native definitions are trusted configuration, but never authorize another tenant via a fixed query.
    decoded_path = unquote(parts.path)
    if ("\\" in decoded_path or any(ord(char) < 32 or ord(char) == 127 for char in decoded_path)
            or any(segment in {".", ".."} for segment in decoded_path.split("/"))):
        raise HTTPException(409, "Datenquelle darf keine Pfadnavigation enthalten")
    pairs = parse_qsl(parts.query, keep_blank_values=True)
    for key, value in pairs:
        if key.casefold() in _IDENTITY_KEYS and not (key.casefold() in {"tenant_id", "mandanten_id"} and value == tenant):
            raise HTTPException(409, "Datenquelle darf keinen fremden Identitaetskontext vorgeben")
    query = [(key, value) for key, value in pairs if key not in {"page", "limit"}]
    query.extend([("page", str(body.page)), ("limit", str(body.limit))])
    if body.q is not None:
        search_key = source.get("searchParam") or "q"
        if not isinstance(search_key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", search_key) or search_key.lower() in _IDENTITY_KEYS:
            raise HTTPException(409, "Ungueltige Suchparameterbindung")
        query = [(key, value) for key, value in query if key != search_key]
        query.append((search_key, body.q))
    return urlunsplit(("", "", parts.path, urlencode(query), ""))


def _base():
    return os.environ.get("MASK_ACTION_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _headers(authorization):
    if not isinstance(authorization, str) or not authorization.startswith("Bearer ") or not authorization[7:].strip():
        raise HTTPException(401, "Bearer-Token des Aufrufers fehlt")
    return {"Authorization": authorization, "Accept": "application/json"}


def _json_constant(_value):
    raise ValueError("Non-finite JSON value")


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _result(body, response, content):
    if response.status_code >= 400:
        raise HTTPException(response.status_code, "Datenabruf vom Fach-Endpunkt abgelehnt")
    if response.status_code != 200:
        raise HTTPException(502, "Datenquelle lieferte keine gueltige JSON-Antwort")
    try:
        data = json.loads(content, parse_constant=_json_constant, object_pairs_hook=_json_object)
    except (ValueError, UnicodeError) as error:
        raise HTTPException(502, "Datenquelle lieferte keine gueltige JSON-Antwort") from error
    if not isinstance(data, (dict, list)):
        raise HTTPException(502, "Datenquelle lieferte kein Objekt oder keine Liste")
    if isinstance(data, dict) and data.get("_stub"):
        raise HTTPException(503, "Datenquelle ist noch nicht funktional implementiert")
    return MaskDataReadOut(screen_id=body.screen_id, source_key=body.source_key,
                           page=body.page, limit=body.limit, data=data)


def _append(parts, chunk, size):
    size += len(chunk)
    if size > _MAX_BYTES:
        raise HTTPException(502, "Datenquelle ueberschreitet das Antwortlimit")
    parts.append(chunk)
    return size


def read_sync(body: MaskDataReadIn, tenant: str, authorization: str | None, *, transport=None) -> MaskDataReadOut:
    headers = _headers(authorization)
    path = resolve_source(body, tenant)
    try:
        with httpx.Client(base_url=_base(), timeout=30, transport=transport, follow_redirects=False) as client:
            with client.stream("GET", path, headers=headers) as response:
                chunks, size = [], 0
                for chunk in response.iter_bytes():
                    size = _append(chunks, chunk, size)
                return _result(body, response, b"".join(chunks))
    except httpx.HTTPError as error:
        raise HTTPException(503, "Datenquelle derzeit nicht erreichbar") from error


async def read_async(body: MaskDataReadIn, tenant: str, authorization: str | None, *, transport=None) -> MaskDataReadOut:
    headers = _headers(authorization)
    path = resolve_source(body, tenant)
    try:
        async with httpx.AsyncClient(base_url=_base(), timeout=30, transport=transport, follow_redirects=False) as client:
            async with client.stream("GET", path, headers=headers) as response:
                chunks, size = [], 0
                async for chunk in response.aiter_bytes():
                    size = _append(chunks, chunk, size)
                return _result(body, response, b"".join(chunks))
    except httpx.HTTPError as error:
        raise HTTPException(503, "Datenquelle derzeit nicht erreichbar") from error
