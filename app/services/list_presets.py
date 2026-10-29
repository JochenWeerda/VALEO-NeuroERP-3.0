"""Registered read-only list selectors, shared by REST, MCP and CLI."""
from datetime import datetime, time, timedelta, timezone

from fastapi import HTTPException
from pydantic import ValidationError

from app.core.business_time import business_now, business_timezone
from app.core.identity_context import current_identity
from app.services.studio_list_contracts import ListPreset


def business_instant(value):
    """Undated values stay undated; naive timestamps follow the shared business clock UTC convention."""
    if value is None or value == "":
        return None
    try:
        instant = value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
        return (instant.replace(tzinfo=timezone.utc) if instant.tzinfo is None else instant).astimezone(business_timezone())
    except (ValueError, TypeError, OverflowError):
        return None


def is_business_overdue(value, status, now=None):
    instant = business_instant(value)
    day = (now or business_now()).date()
    return instant is not None and instant.date() < day and str(status).casefold() != "completed"


def registered_presets(experience):
    raw = experience.get("presets", [])
    if not isinstance(raw, list) or len(raw) > 8:
        raise HTTPException(409, "Ungueltiger Listenpresetvertrag")
    try:
        groups = [ListPreset.model_validate(value) for value in raw]
    except ValidationError as error:
        raise HTTPException(409, "Ungueltiger Listenpresetvertrag") from error
    definitions = {group.key: group for group in groups}
    if len(definitions) != len(groups):
        raise HTTPException(409, "Mehrdeutiger Listenpresetvertrag")
    return groups


def apply_list_presets(rows, experience, selections):
    definitions = {group.key: group for group in registered_presets(experience)}
    selected = rows
    now = business_now()
    today = datetime.combine(now.date(), time.min, tzinfo=business_timezone())
    for key, value in selections.items():
        group = definitions.get(key)
        if group is None or value not in {option.value for option in group.options}:
            raise HTTPException(422, "Unbekannter Listenfilter")
        if value == "all":
            continue
        if group.kind == "choice":
            selected = [row for row in selected if str(row.get(group.field, "")).casefold() == value.casefold()]
        elif group.kind == "actor":
            identity = current_identity()
            aliases = {str(item).strip().casefold() for item in
                       [identity.subject, identity.claims.get("email"), identity.claims.get("name")]
                       if isinstance(item, str) and item.strip()}
            selected = [row for row in selected if str(row.get(group.field) or "").strip().casefold() in aliases]
        else:
            start = today if value != "week" else today - timedelta(days=today.weekday())
            end = start + timedelta(days=7 if value == "week" else 1)
            matches = []
            for row in selected:
                instant = business_instant(row.get(group.field))
                if instant is None:
                    continue
                if value == "overdue":
                    done = group.completionField and str(row.get(group.completionField) or "").casefold() == group.completionValue.casefold()
                    keep = instant < today and not done
                else:
                    keep = start <= instant < end
                if keep:
                    matches.append(row)
            selected = matches
    return selected
