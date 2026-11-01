"""Deterministic table projection; all channels share this implementation."""
from functools import cmp_to_key
import json
import math
import re
import unicodedata

from fastapi import HTTPException


def _text(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return "".join(char for char in unicodedata.normalize("NFKD", str(value).lower().replace("ß", "ss"))
                   if not unicodedata.combining(char))


def _compare(left, right):
    if isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(right, (int, float)) and not isinstance(right, bool):
        return (left > right) - (left < right)
    def natural(value):
        return [(1, int(part)) if part.isdigit() else (0, part) for part in re.split(r"(\d+)", _text(value))]
    a, b = natural(left), natural(right)
    return (a > b) - (a < b)


def _matches(value, filter):
    wanted, operation = filter.value, filter.op
    if operation == "eq":return _text(value) == _text(wanted)
    if operation == "neq":return _text(value) != _text(wanted)
    if operation == "contains":return _text(wanted) in _text(value)
    if operation == "in":return any(_text(value) == _text(item) for item in wanted)
    if operation == "between":return _compare(value, wanted[0]) >= 0 and _compare(value, wanted[1]) <= 0
    comparison = _compare(value, wanted)
    return {"lt": comparison < 0, "lte": comparison <= 0, "gt": comparison > 0, "gte": comparison >= 0}[operation]


def project_rows(rows, table, query):
    columns = {column["key"]: column for column in table.get("columns", []) if isinstance(column, dict) and "key" in column}
    if query.sort and (query.sort not in columns or columns[query.sort].get("sortable") is False):
        raise HTTPException(422, "Sortierfeld ist in der Tabelle nicht freigegeben")
    for key in query.filter_plan:
        if key not in columns or columns[key].get("filterable") is False:
            raise HTTPException(422, "Filterfeld ist in der Tabelle nicht freigegeben")
    from app.services.list_presets import apply_list_presets
    rows = apply_list_presets(rows, table.get("listExperience") or {}, getattr(query, "preset_filters", {}))
    search = _text(query.q).strip()
    selected = [row for row in rows if not search or any(search in _text(row.get(key)) for key in table.get("searchFields", columns))]
    for key, filter in query.filter_plan.items():
        selected = [row for row in selected if _matches(row.get(key), filter)]
    if query.sort:
        direction = -1 if query.sort_dir == "desc" else 1
        selected = sorted(selected, key=cmp_to_key(lambda a,b: direction * _compare(a.get(query.sort), b.get(query.sort))))
    total = len(selected)
    if getattr(query, "complete", False) and total > 5000:
        raise HTTPException(409, "Vollstaendiger Listenabruf ueberschreitet die Obergrenze")
    page_limit = 5000 if getattr(query, "complete", False) else query.limit
    start = 0 if getattr(query, "complete", False) else (query.page - 1) * page_limit
    result = {"items": selected[start:start+page_limit], "total": total, "page": query.page, "size": page_limit,
              "pages": math.ceil(total/page_limit) if total else 1, "has_next": start+page_limit < total,
              "has_prev": query.page > 1}
    if table.get("listExperience"):
        from app.services.list_experience_metrics import list_metrics, metric_currencies
        try:
            result["aggregates"] = list_metrics(table["listExperience"], selected)
            currencies = metric_currencies(table["listExperience"], selected)
            if currencies:
                result["aggregate_currencies"] = currencies
        except HTTPException as error:
            if error.status_code != 409:
                raise
            result["aggregate_error"] = "Listenkennzahlen konnten nicht sicher berechnet werden"
    return result


def table_definition(definition, query):
    found = []
    def walk(node):
        if isinstance(node, dict):
            for table in node.get("tables", []) if isinstance(node.get("tables"), list) else []:
                if isinstance(table, dict) and table.get("key") == query.table_key:
                    found.append(table)
            for child in node.values():walk(child)
        elif isinstance(node, list):
            for child in node:walk(child)
    walk(definition)
    if len(found) != 1 or found[0].get("dataSourceKey") != query.source_key:
        raise HTTPException(409, "Tabelle besitzt keine eindeutige Bindung an diese Quelle")
    table = found[0]
    experience = definition.get("listExperience")
    if isinstance(experience, dict):
        from app.services.list_presets import registered_presets
        for preset in registered_presets(experience):
            fields = {preset.field, preset.completionField} - {None}
            if not fields <= {column.get("key") for column in table.get("columns", []) if isinstance(column, dict)}:
                raise HTTPException(409, "Listenpreset verwendet ein nicht deklariertes Feld")
    if isinstance(experience, dict) and "searchFields" in experience:
        fields = experience["searchFields"]
        columns = {column.get("key") for column in table.get("columns", []) if isinstance(column, dict)}
        if (not isinstance(fields, list) or not 1 <= len(fields) <= 100
                or any(not isinstance(field, str) or field not in columns for field in fields)
                or len(set(fields)) != len(fields)):
            raise HTTPException(409, "Ungueltiger deklarierter Suchfeldvertrag")
        table = {**table, "searchFields": fields, "listExperience": definition["listExperience"]}
    return table


class TableCollector:
    """Collect a complete bounded source before filtering, never filter one partial page."""
    def __init__(self, table, query, fetch_limit=50):
        self.table, self.query, self.fetch_limit = table, query, fetch_limit
        self.rows, self.total, self.page, self.fingerprints = [], None, 1, set()
        self.identities = set()

    def receive(self, data, can_page):
        rows = data if isinstance(data, list) else data.get("items")
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise HTTPException(409, "Datenquelle besitzt keinen geprueften Tabellenvertrag")
        total = data.get("total") if isinstance(data, dict) else None
        if total is not None and (type(total) is not int or total < 0 or self.total is not None and total != self.total):
            raise HTTPException(409, "Quellbestand waehrend des Abrufs geaendert")
        self.total = total if total is not None else self.total
        fingerprint = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        if rows and fingerprint in self.fingerprints:
            raise HTTPException(409, "Datenquelle wiederholt dieselbe Seite")
        for row in rows:
            identity = row.get("id")
            if identity is not None:
                identity = json.dumps(identity, sort_keys=True)
                if identity in self.identities:
                    raise HTTPException(409, "Datenquelle wiederholt eine Datensatzkennung")
                self.identities.add(identity)
        self.fingerprints.add(fingerprint)
        self.rows.extend(rows)
        if len(self.rows) > 5000 or self.page > 100:
            raise HTTPException(409, "Tabellenquelle benoetigt serverseitige Filterung")
        if self.total is not None:
            complete = len(self.rows) == self.total
            if len(self.rows) > self.total:
                raise HTTPException(409, "Inkonsistenter Quellbestand")
        else:
            complete = not can_page or len(rows) < self.fetch_limit
        if complete:
            return project_rows(self.rows, self.table, self.query)
        if not can_page or not rows:
            raise HTTPException(409, "Unvollstaendiger Quellbestand; Tabellenquelle muss erweitert werden")
        if self.page >= 100:
            raise HTTPException(409, "Tabellenquelle benoetigt serverseitige Filterung")
        self.page += 1
        return None
