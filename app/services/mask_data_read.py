"""Shared GET-source access for Human, CLI and MCP; no SQL or alternate business rights."""
import json
import os
import re
import time
from functools import lru_cache
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit, unquote

import httpx
from fastapi import HTTPException

from app.api.v1.schemas.mask_data_contracts import MaskDataReadIn, MaskDataReadOut
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
from app.services.studio_draft_store import StudioStorageUnavailable

_MAX_BYTES = 2 * 1024 * 1024
_IDENTITY_KEYS = {"tenant_id", "mandanten_id", "actor", "user_id", "performed_by", "authorization"}
_PROJECTION_SEGMENT = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}\Z")
_FORBIDDEN_SEGMENTS = {"__proto__", "prototype", "constructor", "__class__", "__dict__", "__globals__"}


def _entity_projection(body: MaskDataReadIn, tenant: str) -> dict[str, tuple[str, ...]] | None:
    """Validate a registered entity projection before the secured source is called."""
    if body.source_key != "entity" or body.table_key is not None:
        return None
    # Stamm builders join the canonical registry lazily; populate that same
    # registry before deciding whether a projection came from native code.
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry
    ensure_stamm_screen_registry()
    try:
        definition = get_screen_definition(body.screen_id, tenant_id=tenant)
    except StudioStorageUnavailable as error:
        raise HTTPException(503, "Studio-Masken derzeit nicht verfuegbar") from error
    if definition is None:
        raise HTTPException(404, "Maske im Mandanten nicht gefunden")
    declared = definition.get("entityProjection")
    if declared is None:
        return None
    # Published tenant drafts may declare their own JSON. Until the Studio
    # schema has a semantic projection policy, only canonical native builders
    # may opt in to selecting fields from a secured domain response.
    if body.screen_id not in SCREEN_DEFINITION_BUILDERS:
        raise HTTPException(409, "Entity-Projektion ist nicht kanonisch registriert")
    if not isinstance(declared, dict) or not 1 <= len(declared) <= 64 or "id" not in declared:
        raise HTTPException(409, "Ungueltige Entity-Projektion")
    if not body.entity_id:
        raise HTTPException(422, "Entity-ID fuer Projektion fehlt")
    fields = [*(definition.get("fields") or [])]
    for tab in definition.get("tabs") or []:
        if isinstance(tab, dict):
            fields.extend(tab.get("fields") or [])
    visible_keys = {field["key"] for field in fields
                    if isinstance(field, dict) and isinstance(field.get("key"), str)}
    if not set(declared) <= visible_keys:
        raise HTTPException(409, "Entity-Projektion referenziert kein deklariertes Feld")
    validated = {}
    for key, path in declared.items():
        if not isinstance(key, str) or not _PROJECTION_SEGMENT.fullmatch(key) or key.casefold() in _FORBIDDEN_SEGMENTS:
            raise HTTPException(409, "Ungueltiger Projektionsschluessel")
        if not isinstance(path, str):
            raise HTTPException(409, "Ungueltiger Projektionspfad")
        segments = path.split(".")
        if not 1 <= len(segments) <= 8 or any(
            not _PROJECTION_SEGMENT.fullmatch(segment) or segment.casefold() in _FORBIDDEN_SEGMENTS
            for segment in segments
        ):
            raise HTTPException(409, "Ungueltiger Projektionspfad")
        validated[key] = tuple(segments)
    return validated


def _project_entity(body: MaskDataReadIn, output: MaskDataReadOut,
                    projection: dict[str, tuple[str, ...]] | None) -> MaskDataReadOut:
    if projection is None:
        return output
    if not isinstance(output.data, dict):
        raise HTTPException(502, "Entity-Projektion erwartet ein Objekt")
    projected = {}
    for key, segments in projection.items():
        value = output.data
        for segment in segments:
            if not isinstance(value, dict) or segment not in value:
                raise HTTPException(502, "Entity-Projektionspfad fehlt")
            value = value[segment]
        if isinstance(value, (dict, list)):
            raise HTTPException(502, "Entity-Projektionswert ist nicht skalar")
        projected[key] = value
    if isinstance(projected["id"], bool) or projected["id"] is None or str(projected["id"]) != body.entity_id:
        raise HTTPException(502, "Entity-Identitaet stimmt nicht ueberein")
    return output.model_copy(update={"data": projected})


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


@lru_cache(maxsize=1024)
def _query_parameters(path):
    # Query-name translation only, never an authorization heuristic.
    from fastapi.routing import APIRoute
    from starlette.routing import Match
    from main import app
    scope = {"type": "http", "method": "GET", "path": unquote(urlsplit(path).path), "root_path": ""}
    def collect(dependant):
        names = {parameter.alias for parameter in dependant.query_params}
        for dependency in dependant.dependencies:names.update(collect(dependency))
        return names
    for route in app.routes:
        if isinstance(route, APIRoute) and route.matches(scope)[0] == Match.FULL:
            return frozenset(collect(route.dependant))
    return frozenset()


def _page_path(path, page, limit, aliases):
    parts = urlsplit(path)
    paging = {"page": page, "skip": (page-1)*limit, "offset": (page-1)*limit,
              "limit": limit, "page_size": limit}
    pairs = [(key,value) for key,value in parse_qsl(parts.query, keep_blank_values=True) if key not in paging]
    pairs.extend((key,str(value)) for key,value in paging.items() if key in aliases)
    return urlunsplit(("", "", parts.path, urlencode(pairs), ""))


def _sequence(body, tenant):
    if body.table_key is None:
        projection = _entity_projection(body, tenant)
        output = yield resolve_source(body, tenant)
        return _project_entity(body, output, projection)
    from app.services.mask_table_query import TableCollector, table_definition, project_rows
    try:
        definition = get_screen_definition(body.screen_id, tenant_id=tenant)
    except StudioStorageUnavailable as error:
        raise HTTPException(503, "Studio-Masken derzeit nicht verfuegbar") from error
    if definition is None:raise HTTPException(404, "Maske im Mandanten nicht gefunden")
    table = table_definition(definition, body)
    project_rows([], table, body)  # Validate field policy before the first network/SQL access.
    raw = body.model_copy(update={"table_key": None, "q": None, "sort": None, "filter_plan": {}, "page": 1, "limit": 50})
    path = resolve_source(raw, tenant)
    aliases = _query_parameters(path)
    can_page = bool(aliases & {"page", "skip", "offset"})
    if table.get("serverPagination") is True:
        if not can_page:raise HTTPException(409, "Serverblaetterung besitzt keinen passenden Fachvertrag")
        required = {"sort", "sort_dir"} if body.sort else set()
        if body.filter_plan:required.add("filter_plan")
        if not required <= aliases:raise HTTPException(409, "Fachquelle muss ihren Sortier-/Filtervertrag erweitern")
        path = _page_path(path, body.page, body.limit, aliases)
        parts=urlsplit(path);pairs=parse_qsl(parts.query,keep_blank_values=True)
        params={}
        if body.q is not None:
            search = "q" if "q" in aliases else "search" if "search" in aliases else None
            if not search:raise HTTPException(409, "Fachquelle besitzt keinen Suchvertrag")
            params[search]=body.q
        if body.sort:params.update(sort=body.sort,sort_dir=body.sort_dir)
        if body.filter_plan:params["filter_plan"]=json.dumps({key:value.model_dump() for key,value in body.filter_plan.items()},separators=(",",":"))
        pairs=[(key,value) for key,value in pairs if key not in params]+list(params.items())
        output=yield urlunsplit(("","",parts.path,urlencode(pairs),""))
        return output
    collector = TableCollector(table, body)
    while True:
        output = yield _page_path(path, collector.page, collector.fetch_limit, aliases)
        projected = collector.receive(output.data, can_page)
        if projected is not None:return output.model_copy(update={"data": projected})


def read_sync(body: MaskDataReadIn, tenant: str, authorization: str | None, *, transport=None) -> MaskDataReadOut:
    headers = _headers(authorization)
    sequence = _sequence(body, tenant); path = next(sequence)
    started, consumed = time.monotonic(), 0
    try:
        with httpx.Client(base_url=_base(), timeout=30, transport=transport, follow_redirects=False) as client:
            while True:
                if time.monotonic()-started > 30:raise HTTPException(503, "Zeitbudget der Tabellenquelle ueberschritten")
                with client.stream("GET", path, headers=headers) as response:
                    chunks=[]
                    for chunk in response.iter_bytes():consumed=_append(chunks,chunk,consumed)
                    output=_result(body,response,b"".join(chunks))
                try:path=sequence.send(output)
                except StopIteration as done:return done.value
    except httpx.HTTPError as error:
        raise HTTPException(503, "Datenquelle derzeit nicht erreichbar") from error


async def read_async(body: MaskDataReadIn, tenant: str, authorization: str | None, *, transport=None) -> MaskDataReadOut:
    headers = _headers(authorization)
    sequence = _sequence(body, tenant); path = next(sequence)
    started, consumed = time.monotonic(), 0
    try:
        async with httpx.AsyncClient(base_url=_base(), timeout=30, transport=transport, follow_redirects=False) as client:
            while True:
                if time.monotonic()-started > 30:raise HTTPException(503, "Zeitbudget der Tabellenquelle ueberschritten")
                async with client.stream("GET", path, headers=headers) as response:
                    chunks=[]
                    async for chunk in response.aiter_bytes():consumed=_append(chunks,chunk,consumed)
                    output=_result(body,response,b"".join(chunks))
                try:path=sequence.send(output)
                except StopIteration as done:return done.value
    except httpx.HTTPError as error:
        raise HTTPException(503, "Datenquelle derzeit nicht erreichbar") from error
