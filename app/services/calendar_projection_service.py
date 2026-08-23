"""UIX-063 planning calendar projections.

The service projects time-bearing business objects into one canonical
``domain_shared.calendar_items`` read model. Missing source tables are treated as
empty projections so a fresh or partially migrated tenant never turns the
planning cockpit into a 5xx surface.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Protocol

import yaml
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.services.crm_capture.termin_extraction import build_source_key, extract_termine


CALENDAR_LAYERS = {"finanzen", "fristen", "crm", "logistik", "personal", "saison"}
CALENDAR_STATUSES = {"projected", "proposed", "confirmed", "dismissed"}


@dataclass(frozen=True)
class CalendarItemDraft:
    source: str
    source_key: str
    layer: str
    item_type: str
    title: str
    starts_at: datetime
    ends_at: datetime | None = None
    all_day: bool = False
    status: str = "projected"
    object_type: str | None = None
    object_id: str | None = None
    object_screen_id: str | None = None
    object_route: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    owner_id: str | None = None
    team_id: str | None = None
    visibility: str = "public"
    response_status: str = "accepted"


class CalendarProjector(Protocol):
    source: str
    layer: str

    def project(
        self,
        db: Session,
        tenant_id: str,
        horizon_days: int = 120,
        now: datetime | None = None,
    ) -> list[CalendarItemDraft]: ...


def _as_mapping(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    mapping = getattr(row, "_mapping", None)
    if mapping is not None:
        return dict(mapping)
    return dict(row)


def _safe_mappings(
    db: Session, sql: str, params: dict[str, Any]
) -> list[dict[str, Any]]:
    try:
        result = db.execute(text(sql), params)
        return [_as_mapping(row) for row in result.mappings().all()]
    except (SQLAlchemyError, RuntimeError, AttributeError):
        return []


def _to_datetime(value: Any, fallback: datetime) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, date):
        return datetime.combine(value, time.min, tzinfo=UTC)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            return fallback
    return fallback


def _iso_date_key(value: datetime) -> str:
    return value.date().isoformat()


def _route(path: str, object_id: Any) -> str:
    return f"{path}/{object_id}" if object_id else path


def _month_day_to_datetime(month_day: str, year: int, fallback: datetime) -> datetime:
    try:
        month, day = month_day.split("-", 1)
        return datetime(year, int(month), int(day), tzinfo=UTC)
    except (ValueError, TypeError):
        return fallback


class PeriodischeBuchungenProjector:
    source = "periodische_buchungen"
    layer = "finanzen"

    def project(
        self,
        db: Session,
        tenant_id: str,
        horizon_days: int = 120,
        now: datetime | None = None,
    ) -> list[CalendarItemDraft]:
        base = now or datetime.now(UTC)
        rows = _safe_mappings(
            db,
            """
            SELECT id, buchung_nr, bezeichnung, naechste_ausfuehrung, betrag, rhythmus
            FROM domain_erp.periodische_buchungen
            WHERE tenant_id = :tenant_id
              AND naechste_ausfuehrung >= :from_ts
              AND naechste_ausfuehrung < :to_ts
        """,
            {
                "tenant_id": tenant_id,
                "from_ts": base,
                "to_ts": base + timedelta(days=horizon_days),
            },
        )
        drafts: list[CalendarItemDraft] = []
        for row in rows:
            starts = _to_datetime(row.get("naechste_ausfuehrung"), base)
            object_id = str(row.get("id") or "")
            drafts.append(
                CalendarItemDraft(
                    source=self.source,
                    source_key=f"{object_id}:{_iso_date_key(starts)}",
                    layer=self.layer,
                    item_type="lauf",
                    title=str(
                        row.get("bezeichnung")
                        or row.get("buchung_nr")
                        or "Periodische Buchung"
                    ),
                    starts_at=starts,
                    all_day=True,
                    object_type="periodische_buchung",
                    object_id=object_id,
                    object_screen_id="finance/journal-entry",
                    object_route=_route("/finance/buchungserfassung", object_id),
                    payload={
                        "betrag": row.get("betrag"),
                        "rhythmus": row.get("rhythmus"),
                    },
                )
            )
        return drafts


class OpenItemsProjector:
    source = "open_items"
    layer = "finanzen"

    def project(
        self,
        db: Session,
        tenant_id: str,
        horizon_days: int = 120,
        now: datetime | None = None,
    ) -> list[CalendarItemDraft]:
        base = now or datetime.now(UTC)
        rows = _safe_mappings(
            db,
            """
            SELECT id, beleg_nr, partner_name, faellig_am, offen, status
            FROM domain_erp.open_items
            WHERE tenant_id = :tenant_id
              AND faellig_am >= :from_ts
              AND faellig_am < :to_ts
              AND COALESCE(status, 'open') NOT IN ('paid', 'settled', 'closed')
        """,
            {
                "tenant_id": tenant_id,
                "from_ts": base.date(),
                "to_ts": (base + timedelta(days=horizon_days)).date(),
            },
        )
        return [
            CalendarItemDraft(
                source=self.source,
                source_key=str(row.get("id")),
                layer=self.layer,
                item_type="frist",
                title=f"OP faellig: {row.get('beleg_nr') or row.get('partner_name') or row.get('id')}",
                starts_at=_to_datetime(row.get("faellig_am"), base),
                all_day=True,
                object_type="open_item",
                object_id=str(row.get("id") or ""),
                object_screen_id="finance/ar-open-item",
                object_route=_route("/finance/op-debitoren", row.get("id")),
                payload={"offen": row.get("offen"), "partner": row.get("partner_name")},
            )
            for row in rows
        ]


class KontraktFristenProjector:
    source = "kontrakt_fristen"
    layer = "fristen"

    def project(
        self,
        db: Session,
        tenant_id: str,
        horizon_days: int = 120,
        now: datetime | None = None,
    ) -> list[CalendarItemDraft]:
        base = now or datetime.now(UTC)
        rows = _safe_mappings(
            db,
            """
            SELECT id, kontrakt_nr, partner_name, andienung_bis, fruehbezugsrabatt_bis
            FROM domain_agrar.kontrakte
            WHERE tenant_id = :tenant_id
        """,
            {"tenant_id": tenant_id},
        )
        until = base + timedelta(days=horizon_days)
        drafts: list[CalendarItemDraft] = []
        for row in rows:
            object_id = str(row.get("id") or "")
            for field_name, label in (
                ("andienung_bis", "Andienungsfrist"),
                ("fruehbezugsrabatt_bis", "Ende Fruehbezugsrabatt"),
            ):
                raw = row.get(field_name)
                if not raw:
                    continue
                starts = _to_datetime(raw, base)
                if not (base <= starts < until):
                    continue
                drafts.append(
                    CalendarItemDraft(
                        source=self.source,
                        source_key=f"{object_id}:{field_name}",
                        layer=self.layer,
                        item_type="frist",
                        title=f"{label}: {row.get('kontrakt_nr') or object_id}",
                        starts_at=starts,
                        all_day=True,
                        object_type="kontrakt",
                        object_id=object_id,
                        object_screen_id="agrar/kontrakte",
                        object_route=_route("/kontrakte", object_id),
                        payload={
                            "field": field_name,
                            "partner": row.get("partner_name"),
                        },
                    )
                )
        return drafts


class CrmWiedervorlagenProjector:
    source = "crm_wiedervorlagen"
    layer = "crm"

    def project(
        self,
        db: Session,
        tenant_id: str,
        horizon_days: int = 120,
        now: datetime | None = None,
    ) -> list[CalendarItemDraft]:
        base = now or datetime.now(UTC)
        rows = _safe_mappings(
            db,
            """
            SELECT id, customer_id, customer_name, subject, due_date
            FROM domain_crm.activities
            WHERE tenant_id = :tenant_id
              AND due_date >= :from_ts
              AND due_date < :to_ts
              AND COALESCE(status, 'open') NOT IN ('done', 'closed')
        """,
            {
                "tenant_id": tenant_id,
                "from_ts": base,
                "to_ts": base + timedelta(days=horizon_days),
            },
        )
        return [
            CalendarItemDraft(
                source=self.source,
                source_key=str(row.get("id")),
                layer=self.layer,
                item_type="reminder",
                title=f"Wiedervorlage: {row.get('subject') or row.get('customer_name') or row.get('id')}",
                starts_at=_to_datetime(row.get("due_date"), base),
                object_type="crm_activity",
                object_id=str(row.get("id") or ""),
                object_screen_id="crm/customer-360",
                object_route=_route("/verkauf/kunden-liste", row.get("customer_id")),
                payload={
                    "customerId": row.get("customer_id"),
                    "customer": row.get("customer_name"),
                },
            )
            for row in rows
        ]


class AgrarSachkundeProjector:
    source = "agrar_sachkunde"
    layer = "personal"

    def project(
        self,
        db: Session,
        tenant_id: str,
        horizon_days: int = 120,
        now: datetime | None = None,
    ) -> list[CalendarItemDraft]:
        base = now or datetime.now(UTC)
        rows = _safe_mappings(
            db,
            """
            SELECT id, person_ref, display_name, gueltig_bis, sachkunde_art
            FROM domain_compliance.agrar_sachkunde
            WHERE tenant_id = :tenant_id
              AND gueltig_bis >= :from_date
              AND gueltig_bis < :to_date
        """,
            {
                "tenant_id": tenant_id,
                "from_date": base.date(),
                "to_date": (base + timedelta(days=horizon_days)).date(),
            },
        )
        return [
            CalendarItemDraft(
                source=self.source,
                source_key=str(row.get("id")),
                layer=self.layer,
                item_type="frist",
                title=f"Sachkunde laeuft ab: {row.get('display_name') or row.get('person_ref') or row.get('id')}",
                starts_at=_to_datetime(row.get("gueltig_bis"), base),
                all_day=True,
                object_type="agrar_sachkunde",
                object_id=str(row.get("id") or ""),
                object_screen_id="compliance/sachkunde",
                object_route=_route("/compliance/sachkunde", row.get("id")),
                payload={
                    "personRef": row.get("person_ref"),
                    "art": row.get("sachkunde_art"),
                },
            )
            for row in rows
        ]


class SaisonKalenderProjector:
    source = "saison_kalender"
    layer = "saison"

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or Path("config/saison_kalender.yaml")

    def project(
        self,
        db: Session,
        tenant_id: str,
        horizon_days: int = 120,
        now: datetime | None = None,
    ) -> list[CalendarItemDraft]:
        base = now or datetime.now(UTC)
        until = base + timedelta(days=horizon_days)
        if not self.config_path.exists():
            return []

        data = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        entries = data.get("entries") if isinstance(data, dict) else []
        if not isinstance(entries, list):
            return []

        drafts: list[CalendarItemDraft] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            key = str(entry.get("key") or "").strip()
            title = str(entry.get("title") or "").strip()
            starts_raw = str(entry.get("starts_on") or "").strip()
            if not key or not title or not starts_raw:
                continue
            starts = _month_day_to_datetime(starts_raw, base.year, base)
            if starts < base:
                starts = _month_day_to_datetime(starts_raw, base.year + 1, base)
            if not (base <= starts < until):
                continue
            ends = None
            ends_raw = str(entry.get("ends_on") or "").strip()
            if ends_raw:
                ends = _month_day_to_datetime(ends_raw, starts.year, starts)
                if ends < starts:
                    ends = _month_day_to_datetime(ends_raw, starts.year + 1, starts)
            drafts.append(
                CalendarItemDraft(
                    source=self.source,
                    source_key=f"{key}:{starts.year}",
                    layer=self.layer,
                    item_type=str(entry.get("item_type") or "termin"),
                    title=title,
                    starts_at=starts,
                    ends_at=ends,
                    all_day=True,
                    object_type="saison_kalender",
                    object_id=key,
                    object_screen_id=str(
                        entry.get("object_screen_id") or "planung/kalender"
                    ),
                    object_route=str(entry.get("object_route") or "/planung/kalender"),
                    payload={
                        "region": data.get("region"),
                        "crop": entry.get("crop"),
                        "priority": entry.get("priority"),
                    },
                )
            )
        return drafts


DEFAULT_PROJECTORS: list[CalendarProjector] = [
    PeriodischeBuchungenProjector(),
    OpenItemsProjector(),
    KontraktFristenProjector(),
    CrmWiedervorlagenProjector(),
    AgrarSachkundeProjector(),
    SaisonKalenderProjector(),
]


_EMAIL_OBJECT_ROUTES: dict[str, tuple[str, str]] = {
    "purchase_order": ("einkauf/purchase-order", "/einkauf/bestellungen"),
    "contract": ("agrar/kontrakte", "/kontrakte"),
    "delivery_note": ("sales/delivery-note", "/verkauf/lieferschein-erfassung"),
    "supplier": ("einkauf/supplier", "/einkauf/lieferanten"),
}


def _resource_key(object_type: str | None, object_id: str | None) -> str | None:
    if not object_type or not object_id:
        return None
    return f"{object_type}:{object_id}"


def _payload_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except ValueError:
            return {}
    return {}


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class CalendarProjectionService:
    def __init__(
        self, db: Session, projectors: list[CalendarProjector] | None = None
    ) -> None:
        self.db = db
        self.projectors = projectors or DEFAULT_PROJECTORS

    def _email_conflicts(
        self,
        tenant_id: str,
        *,
        source_key: str,
        starts_at: datetime,
        ends_at: datetime | None,
        resource_key: str | None,
    ) -> list[dict[str, Any]]:
        if not resource_key:
            return []
        window_start = starts_at - timedelta(hours=2)
        window_end = (ends_at or starts_at) + timedelta(hours=2)
        rows = (
            self.db.execute(
                text("""
            SELECT id, title, starts_at, ends_at, object_type, object_id, payload
            FROM domain_shared.calendar_items
            WHERE tenant_id = :tenant_id
              AND layer = 'logistik'
              AND status IN ('projected', 'proposed', 'confirmed')
              AND NOT (source = 'email_capture' AND source_key = :source_key)
              AND starts_at <= :window_end
              AND COALESCE(ends_at, starts_at) >= :window_start
        """),
                {
                    "tenant_id": tenant_id,
                    "source_key": source_key,
                    "window_start": window_start,
                    "window_end": window_end,
                },
            )
            .mappings()
            .all()
        )

        conflicts: list[dict[str, Any]] = []
        for row in rows:
            item = _as_mapping(row)
            row_resource = _resource_key(item.get("object_type"), item.get("object_id"))
            if row_resource is None:
                matched = _payload_dict(item.get("payload")).get("matched_object")
                if isinstance(matched, dict):
                    row_resource = _resource_key(matched.get("type"), matched.get("id"))
            if row_resource != resource_key:
                continue
            conflicts.append(
                {
                    "item_id": str(item.get("id")),
                    "reason": "Slot ueberschneidet bestehenden Logistik-Termin",
                    "title": item.get("title"),
                    "starts_at": item.get("starts_at").isoformat()
                    if hasattr(item.get("starts_at"), "isoformat")
                    else str(item.get("starts_at")),
                }
            )
        return conflicts

    def propose_email_terms(
        self,
        tenant_id: str,
        *,
        mail_id: str,
        subject: str | None,
        body: str,
        received_at: datetime,
        sender_domain: str | None = None,
    ) -> dict[str, Any]:
        """Extrahiert Mail-Termine und schreibt sie als Kalender-Vorschlaege.

        Safety-Vertrag UIX-073: niemals Auto-Confirm. Re-Ingest ist ueber
        source_key=mail_id:n idempotent; bestehende proposed/confirmed Items
        werden durch das Upsert nicht ueberschrieben.
        """
        text_in = "\n".join(
            part for part in (subject or "", body or "") if part.strip()
        )
        candidates = extract_termine(
            text_in, received_at=received_at, sender_domain=sender_domain
        )
        source_keys: list[str] = []
        for index, candidate in enumerate(candidates):
            source_key = build_source_key(mail_id, index)
            source_keys.append(source_key)
            starts_at = _to_datetime(candidate.start, received_at)
            ends_at = (
                _to_datetime(candidate.end, starts_at + timedelta(hours=1))
                if candidate.end
                else None
            )
            matched = (
                asdict(candidate.matched_object) if candidate.matched_object else None
            )
            object_type = matched.get("type") if matched else "email_capture"
            object_id = matched.get("id") if matched else mail_id
            route_info = _EMAIL_OBJECT_ROUTES.get(str(object_type))
            object_screen_id = route_info[0] if route_info else None
            object_route = _route(route_info[1], object_id) if route_info else None
            resource = _resource_key(
                str(object_type) if object_type else None,
                str(object_id) if object_id else None,
            )
            conflicts = self._email_conflicts(
                tenant_id,
                source_key=source_key,
                starts_at=starts_at,
                ends_at=ends_at,
                resource_key=resource,
            )
            self.upsert_draft(
                tenant_id,
                CalendarItemDraft(
                    source="email_capture",
                    source_key=source_key,
                    layer="logistik",
                    item_type="terminvorschlag",
                    title=f"Mail-Termin: {(subject or candidate.extracted_text or mail_id)[:160]}",
                    starts_at=starts_at,
                    ends_at=ends_at,
                    all_day=candidate.all_day,
                    status="proposed",
                    object_type=str(object_type) if object_type else None,
                    object_id=str(object_id) if object_id else None,
                    object_screen_id=object_screen_id,
                    object_route=object_route,
                    payload={
                        "mail_id": mail_id,
                        "mail_subject": subject,
                        "mail_received_at": received_at.isoformat(),
                        "sender_domain": sender_domain,
                        "extracted_text": candidate.extracted_text,
                        "matched_object": matched,
                        "confidence": candidate.confidence,
                        "conflicts": conflicts,
                    },
                ),
            )
        self.db.commit()
        return {
            "mailId": mail_id,
            "candidates": len(candidates),
            "proposed": len(source_keys),
            "sourceKeys": source_keys,
        }

    def reproject(
        self, tenant_id: str, horizon_days: int = 120, now: datetime | None = None
    ) -> dict[str, Any]:
        base = now or datetime.now(UTC)
        by_source: dict[str, list[CalendarItemDraft]] = {}
        for projector in self.projectors:
            drafts = projector.project(
                self.db, tenant_id, horizon_days=horizon_days, now=base
            )
            by_source[projector.source] = drafts
            for draft in drafts:
                self.upsert_draft(tenant_id, draft)
            self.delete_stale_projected(
                tenant_id,
                projector.source,
                [d.source_key for d in drafts],
                base,
                horizon_days,
            )
        self.db.commit()
        return {
            "tenantId": tenant_id,
            "horizonDays": horizon_days,
            "projected": sum(len(items) for items in by_source.values()),
            "sources": {source: len(items) for source, items in by_source.items()},
        }

    def upsert_draft(self, tenant_id: str, draft: CalendarItemDraft) -> None:
        if draft.layer not in CALENDAR_LAYERS:
            raise ValueError(f"Invalid calendar layer: {draft.layer}")
        if draft.status not in CALENDAR_STATUSES:
            raise ValueError(f"Invalid calendar status: {draft.status}")
        self.db.execute(
            text("""
            INSERT INTO domain_shared.calendar_items (
                id, tenant_id, source, source_key, layer, item_type, title,
                starts_at, ends_at, all_day, status, object_type, object_id,
                object_screen_id, object_route, payload, owner_id, team_id,
                visibility, response_status, created_at, updated_at
            ) VALUES (
                :id, :tenant_id, :source, :source_key, :layer, :item_type, :title,
                :starts_at, :ends_at, :all_day, :status, :object_type, :object_id,
                :object_screen_id, :object_route, CAST(:payload AS jsonb), :owner_id,
                :team_id, :visibility, :response_status, NOW(), NOW()
            )
            ON CONFLICT (tenant_id, source, source_key) DO UPDATE SET
                layer = EXCLUDED.layer,
                item_type = EXCLUDED.item_type,
                title = EXCLUDED.title,
                starts_at = EXCLUDED.starts_at,
                ends_at = EXCLUDED.ends_at,
                all_day = EXCLUDED.all_day,
                object_type = EXCLUDED.object_type,
                object_id = EXCLUDED.object_id,
                object_screen_id = EXCLUDED.object_screen_id,
                object_route = EXCLUDED.object_route,
                payload = EXCLUDED.payload,
                owner_id = EXCLUDED.owner_id,
                team_id = EXCLUDED.team_id,
                visibility = EXCLUDED.visibility,
                response_status = EXCLUDED.response_status,
                updated_at = NOW()
            WHERE domain_shared.calendar_items.status = 'projected'
        """),
            {
                "id": uuid7(),
                "tenant_id": tenant_id,
                "source": draft.source,
                "source_key": draft.source_key,
                "layer": draft.layer,
                "item_type": draft.item_type,
                "title": draft.title[:200],
                "starts_at": draft.starts_at,
                "ends_at": draft.ends_at,
                "all_day": draft.all_day,
                "status": draft.status,
                "object_type": draft.object_type,
                "object_id": draft.object_id,
                "object_screen_id": draft.object_screen_id,
                "object_route": draft.object_route,
                "payload": json.dumps(draft.payload, default=str),
                "owner_id": draft.owner_id,
                "team_id": draft.team_id,
                "visibility": draft.visibility,
                "response_status": draft.response_status,
            },
        )

    def delete_stale_projected(
        self,
        tenant_id: str,
        source: str,
        source_keys: list[str],
        now: datetime,
        horizon_days: int,
    ) -> None:
        self.db.execute(
            text("""
            DELETE FROM domain_shared.calendar_items
            WHERE tenant_id = :tenant_id
              AND source = :source
              AND status = 'projected'
              AND starts_at >= :from_ts
              AND starts_at < :to_ts
              AND NOT (source_key = ANY(:source_keys))
        """),
            {
                "tenant_id": tenant_id,
                "source": source,
                "from_ts": now,
                "to_ts": now + timedelta(days=horizon_days),
                "source_keys": source_keys,
            },
        )

    def list_items(
        self,
        tenant_id: str,
        from_ts: datetime,
        to_ts: datetime,
        layers: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "tenant_id": tenant_id,
            "from_ts": from_ts,
            "to_ts": to_ts,
        }
        if layers:
            params["layers"] = layers
            statement = text("""
                SELECT id, tenant_id, source, source_key, layer, item_type, title,
                       starts_at, ends_at, all_day, status, object_type, object_id,
                       object_screen_id, object_route, payload, created_at, updated_at
                FROM domain_shared.calendar_items
                WHERE tenant_id = :tenant_id
                  AND starts_at >= :from_ts
                  AND starts_at < :to_ts
                  AND layer = ANY(:layers)
                ORDER BY starts_at ASC, layer ASC, title ASC
            """)
        else:
            statement = text("""
            SELECT id, tenant_id, source, source_key, layer, item_type, title,
                   starts_at, ends_at, all_day, status, object_type, object_id,
                   object_screen_id, object_route, payload, created_at, updated_at
            FROM domain_shared.calendar_items
            WHERE tenant_id = :tenant_id
              AND starts_at >= :from_ts
              AND starts_at < :to_ts
            ORDER BY starts_at ASC, layer ASC, title ASC
        """)
        rows = self.db.execute(statement, params).mappings().all()
        return [_as_mapping(row) for row in rows]

    def list_team_items(
        self,
        tenant_id: str,
        from_ts: datetime,
        to_ts: datetime,
        *,
        user_ref: str,
        team_ids: list[str] | None = None,
        layers: list[str] | None = None,
        include_declined: bool = False,
        can_view_details: bool = False,
    ) -> list[dict[str, Any]]:
        membership_rows = (
            self.db.execute(
                text("""
          SELECT team_id FROM domain_shared.calendar_team_memberships
           WHERE tenant_id=:tenant_id AND user_ref=:user_ref AND active=true
        """),
                {"tenant_id": tenant_id, "user_ref": user_ref},
            )
            .mappings()
            .all()
        )
        authorized = {str(_as_mapping(row)["team_id"]) for row in membership_rows}
        requested = set(team_ids or authorized)
        if not requested.issubset(authorized):
            raise PermissionError("Teamkalender-Zugriff verweigert")
        params: dict[str, Any] = {
            "tenant_id": tenant_id,
            "from_ts": from_ts,
            "to_ts": to_ts,
            "user_ref": user_ref,
            "team_ids": sorted(requested),
            "include_declined": include_declined,
        }
        layer_clause = ""
        if layers:
            params["layers"] = layers
            layer_clause = "AND layer = ANY(:layers)"
        rows = (
            self.db.execute(
                text(f"""
          SELECT id,tenant_id,source,source_key,layer,item_type,title,starts_at,ends_at,
                 all_day,status,object_type,object_id,object_screen_id,object_route,payload,
                 owner_id,team_id,visibility,response_status,created_at,updated_at
            FROM domain_shared.calendar_items
           WHERE tenant_id=:tenant_id AND starts_at>=:from_ts AND starts_at<:to_ts
             AND (owner_id=:user_ref OR visibility='public' OR team_id = ANY(:team_ids))
             AND (:include_declined OR response_status<>'declined') {layer_clause}
           ORDER BY starts_at,team_id NULLS LAST,owner_id NULLS LAST,title
        """),  # nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
                params,
            )
            .mappings()
            .all()
        )
        result: list[dict[str, Any]] = []
        for raw in rows:
            item = _as_mapping(raw)
            is_own = item.get("owner_id") in {None, user_ref}
            redact = not is_own and (
                item.get("visibility") in {"private", "free_busy"}
                or (item.get("visibility") == "team" and not can_view_details)
            )
            if redact:
                item.update(
                    {
                        "title": "Belegt",
                        "object_type": None,
                        "object_id": None,
                        "object_screen_id": None,
                        "object_route": None,
                        "payload": {"availability": "busy", "redacted": True},
                    }
                )
            else:
                payload = _payload_dict(item.get("payload"))
                payload["availability"] = "busy"
                payload["redacted"] = False
                item["payload"] = payload
            result.append(item)
        return result

    def transition_proposed(
        self, tenant_id: str, item_id: str, status: str
    ) -> dict[str, Any] | None:
        row = (
            self.db.execute(
                text("""
            UPDATE domain_shared.calendar_items
            SET status = :status, updated_at = NOW()
            WHERE tenant_id = :tenant_id AND id = :id AND status = 'proposed'
            RETURNING id, tenant_id, source, source_key, layer, item_type, title,
                      starts_at, ends_at, all_day, status, object_type, object_id,
                      object_screen_id, object_route, payload, created_at, updated_at
        """),
                {"tenant_id": tenant_id, "id": item_id, "status": status},
            )
            .mappings()
            .first()
        )
        self.db.commit()
        return _as_mapping(row) if row else None

    def issue_ics_token(self, tenant_id: str, user_ref: str = "default") -> str:
        token = secrets.token_urlsafe(32)
        self.db.execute(
            text("""
            UPDATE domain_shared.calendar_ics_tokens
            SET active = false, rotated_at = NOW()
            WHERE tenant_id = :tenant_id AND user_ref = :user_ref AND active = true
        """),
            {"tenant_id": tenant_id, "user_ref": user_ref},
        )
        self.db.execute(
            text("""
            INSERT INTO domain_shared.calendar_ics_tokens (id, tenant_id, user_ref, token_hash, active, created_at)
            VALUES (:id, :tenant_id, :user_ref, :token_hash, true, NOW())
        """),
            {
                "id": uuid7(),
                "tenant_id": tenant_id,
                "user_ref": user_ref,
                "token_hash": token_hash(token),
            },
        )
        self.db.commit()
        return token

    def tenant_for_ics_token(self, token: str) -> str | None:
        row = (
            self.db.execute(
                text("""
            SELECT tenant_id
            FROM domain_shared.calendar_ics_tokens
            WHERE token_hash = :token_hash AND active = true
        """),
                {"token_hash": token_hash(token)},
            )
            .mappings()
            .first()
        )
        if not row:
            return None
        return str(_as_mapping(row).get("tenant_id"))

    def ics_content(self, tenant_id: str, from_ts: datetime, to_ts: datetime) -> str:
        items = self.list_items(tenant_id, from_ts, to_ts)
        visible = [
            item for item in items if item.get("status") in {"projected", "confirmed"}
        ]
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//VALEO NeuroERP//Planning Calendar//DE",
        ]
        for item in visible:
            starts = _to_datetime(item.get("starts_at"), from_ts)
            ends = _to_datetime(item.get("ends_at"), starts + timedelta(hours=1))
            if item.get("all_day"):
                lines.extend(
                    [
                        "BEGIN:VEVENT",
                        f"UID:{item.get('id')}@valeo-neuroerp",
                        f"DTSTART;VALUE=DATE:{starts.strftime('%Y%m%d')}",
                        f"DTEND;VALUE=DATE:{(starts + timedelta(days=1)).strftime('%Y%m%d')}",
                        f"SUMMARY:{_ics_escape(str(item.get('title') or 'Termin'))}",
                        f"URL:{_ics_escape(str(item.get('object_route') or ''))}",
                        "END:VEVENT",
                    ]
                )
            else:
                lines.extend(
                    [
                        "BEGIN:VEVENT",
                        f"UID:{item.get('id')}@valeo-neuroerp",
                        f"DTSTART:{starts.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                        f"DTEND:{ends.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                        f"SUMMARY:{_ics_escape(str(item.get('title') or 'Termin'))}",
                        f"URL:{_ics_escape(str(item.get('object_route') or ''))}",
                        "END:VEVENT",
                    ]
                )
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"


def _ics_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )
