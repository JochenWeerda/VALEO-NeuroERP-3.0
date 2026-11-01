"""Tenant-bound ASCII import into the canonical weighing-ticket aggregate.

Each W record and its Q records form one retryable unit. A receipt is retained
after success or dismissal; replay cannot create another ticket.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from decimal import Decimal, InvalidOperation

from fastapi import HTTPException
from sqlalchemy import Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import Session

from app.core.database import Base
from app.core.business_time import business_now
from app.core.uuid7 import uuid7
from app.domains.operations.models import Waage
from app.infrastructure.models import Article, WeighingTicket
from app.infrastructure.eventbus.outbox import OutboxEvent
from modules.agrar.services.weighing_domain import validate_and_compute_weights, derive_billing_weight


class WaageImportEntry(Base):
    __tablename__ = 'waage_import_entries'
    __table_args__ = {'schema': 'domain_ops', 'extend_existing': True}
    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    waage_id = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    error = Column(Text)
    ticket_id = Column(String)
    retry_count = Column(Integer, nullable=False, default=0)
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=business_now)


def reference_allowed(db: Session, scale_id: str | None) -> None:
    """External names remain names; registered foreign/NULL-owner IDs are denied.

    The narrow DB predicate sees registry existence despite RLS, and returns
    only permission. A normal scoped lookup would mistake a foreign ID for an
    unknown external identifier. No ownership is derived from the name.
    """
    if scale_id and not db.execute(text('SELECT public.waage_reference_allowed(:ref)'), {'ref': scale_id}).scalar_one():
        raise HTTPException(404, 'Waage nicht gefunden')


def locked_scale(db: Session, tenant_id: str, scale_id: str):
    scale = db.query(Waage).filter(Waage.tenant_id == tenant_id, Waage.id == scale_id).with_for_update().first()
    if scale is None:
        raise HTTPException(404, 'Waage nicht gefunden')
    return scale


def split_records(content: str) -> list[str]:
    groups: list[list[str]] = []
    by_number: dict[str, list[str]] = {}
    for line in content.lstrip('\ufeff').splitlines():
        if not line.strip():
            continue
        parts = line.split(';')
        if parts[0] == 'W':
            group = [line]
            groups.append(group)
            if len(parts) > 1:
                if parts[1] in by_number:
                    raise HTTPException(422, 'Doppelte W-Satznummer in Datei')
                by_number[parts[1]] = group
        elif parts[0] == 'Q' and len(parts) > 1 and parts[1] in by_number:
            by_number[parts[1]].append(line)
        else:
            groups.append([line])
        if len(groups) > 1000:
            raise HTTPException(422, 'Maximal 1000 Wiegesaetze pro Datei')
    if not groups:
        raise HTTPException(422, 'Datei enthaelt keine Wiegesaetze')
    return ['\n'.join(group) for group in groups]


def parse_record(raw: str) -> dict:
    lines = raw.splitlines()
    p = lines[0].split(';')
    if len(p) != 17 or p[0] != 'W' or not p[1].strip() or len(p[1]) > 50:
        raise ValueError('W-Satz braucht 17 Felder und eine eindeutige Nummer')
    when = datetime.fromisoformat(p[2] + 'T' + p[3])
    if when.tzinfo is None:
        from app.core.business_time import business_timezone
        when = when.replace(tzinfo=business_timezone())
    def number(value: str, *, optional=False):
        if optional and not value:
            return None
        try:
            result = Decimal(value)
            if not result.is_finite() or result < 0:
                raise ValueError('Ungueltiger Zahlenwert')
            converted = float(result)
            if not math.isfinite(converted) or converted > 999999999.999:
                raise ValueError('Zahlenwert ueberschreitet die Beleggrenze')
            return converted
        except InvalidOperation as exc:
            raise ValueError('Ungueltiger Zahlenwert') from exc
    gross, tare, stated = [number(v) for v in p[4:7]]
    net = validate_and_compute_weights(gross, tare, stated)
    if net is None or net <= 0 or abs(net - stated) > 0.001:
        raise ValueError('Nettogewicht stimmt nicht mit Brutto minus Tara ueberein')
    moisture, hl, impurities = [number(v, optional=True) for v in (p[13], p[14], p[15])]
    if any(v is not None and v > 100 for v in (moisture, impurities)):
        raise ValueError('Prozentwerte muessen zwischen 0 und 100 liegen')
    quality = {'source': 'waage_ascii', 'lieferant_id': p[8], 'sorte': p[10], 'partie_id': p[11], 'silo_id': p[12], 'additional': []}
    for line in lines[1:]:
        q = line.split(';')
        if len(q) != 5 or q[0] != 'Q' or q[1] != p[1] or not q[2]:
            raise ValueError('Q-Satz ist keinem gueltigen W-Satz zugeordnet')
        quality['additional'].append({'parameter': q[2], 'wert': q[3], 'einheit': q[4]})
    if len(p[11]) > 100:
        raise ValueError('Partiereferenz ist zu lang')
    if len(p[7]) > 20:
        raise ValueError('Kennzeichen ist zu lang')
    return dict(ticket_number=p[1], vehicle_plate=p[7] or None, gross_weight=gross, tare_weight=tare,
                net_weight=net, first_weighing_at=when, second_weighing_at=when, moisture_pct=moisture,
                hl_weight=hl, impurities_pct=impurities, article_id=p[9] or None,
                reference_doc=p[11] or None, quality_data=quality)


def _persist_ticket(db: Session, tenant_id: str, scale_id: str, raw: str) -> str:
    values = parse_record(raw)
    from app.core.data_quality_enforcement import evaluate_weighing_ticket_datensatz
    from app.api.v1.endpoints.weighing_tickets import _build_weighing_ticket_dq_datensatz
    if not evaluate_weighing_ticket_datensatz(_build_weighing_ticket_dq_datensatz(values)).bestanden:
        raise ValueError('Wiegeschein besteht die kanonische Datenqualitaetspruefung nicht')
    article = values['article_id']
    if article and db.query(Article.id).filter(Article.id == article, Article.tenant_id == tenant_id).first() is None:
        raise ValueError('Artikel nicht im aktiven Mandanten gefunden')
    if db.query(WeighingTicket.id).filter(WeighingTicket.tenant_id == tenant_id, WeighingTicket.ticket_number == values['ticket_number']).first() is not None:
        raise ValueError('Wiegescheinnummer bereits vorhanden')
    ident = str(uuid7())
    values['billing_weight'] = derive_billing_weight(net_weight=values['net_weight'], billing_weight=None,
        moisture_pct=values['moisture_pct'], impurities_pct=values['impurities_pct'], quality_data=values['quality_data'])
    db.add(WeighingTicket(id=ident, tenant_id=tenant_id, scale_id=scale_id, direction='in', status='closed', **values))
    return ident


def _event(db, tenant_id, actor, entry, action):
    payload = {'tenant_id': tenant_id, 'actor': actor, 'entry_id': entry.id, 'ticket_id': entry.ticket_id,
               'scale_id': entry.waage_id, 'status': entry.status, 'action': action}
    # The receipt itself is the immutable import provenance; event is atomic.
    from app.services.mask_action_runtime_service import _write_audit
    _write_audit(db, tenant_id=tenant_id, action_key='waage.import.' + action, entity_type='waage_import',
        entity_id=entry.id, audit_reason=None, idempotency_key=entry.id, summary=json.dumps(payload), performed_by=actor)
    db.add(OutboxEvent(id=str(uuid7()), event_type='waage.import.' + action, aggregate_id=entry.id,
        tenant_id=tenant_id, payload=json.dumps(payload), timestamp=business_now().replace(tzinfo=None)))


def import_records(db, tenant_id: str, scale_id: str, content: str, tolerant: bool, actor: str) -> dict:
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"), {"key": "waage-import:" + tenant_id})
    locked_scale(db, tenant_id, scale_id)  # serialize file/retry/delete on this scale
    records = split_records(content)
    result = {'imported': 0, 'skipped': 0, 'errors': [], 'wiegung_ids': [], 'replayed': 0}
    for raw in records:
        ident = hashlib.sha256(json.dumps([tenant_id, scale_id, raw], ensure_ascii=False).encode()).hexdigest()
        entry = db.query(WaageImportEntry).filter(WaageImportEntry.id == ident, WaageImportEntry.tenant_id == tenant_id).first()
        if entry is not None:
            result['replayed'] += 1
            if entry.ticket_id:
                result['wiegung_ids'].append(entry.ticket_id)
            elif entry.status == 'error':
                if not tolerant:
                    raise HTTPException(422, entry.error or 'Vorhandener Importfehler')
                result['errors'].append({'id': ident, 'fehler': entry.error})
            continue
        entry = WaageImportEntry(id=ident, tenant_id=tenant_id, waage_id=scale_id, raw_text=raw,
                                 status='error', created_by=actor, retry_count=0)
        try:
            entry.ticket_id = _persist_ticket(db, tenant_id, scale_id, raw)
            entry.status = 'imported'
            result['imported'] += 1
            result['wiegung_ids'].append(entry.ticket_id)
        except (ValueError, HTTPException) as exc:
            message = str(exc.detail) if isinstance(exc, HTTPException) else str(exc)
            if not tolerant:
                raise HTTPException(422, message) from exc
            entry.error = message
            result['skipped'] += 1
            result['errors'].append({'id': ident, 'fehler': message})
        db.add(entry)
        _event(db, tenant_id, actor, entry, 'processed')
    db.flush()
    return result


def queue_entry(db, tenant_id, ident, *, allow_processed=False):
    item = db.query(WaageImportEntry).filter(WaageImportEntry.id == ident, WaageImportEntry.tenant_id == tenant_id).first()
    if item is None or (item.status != 'error' and not allow_processed):
        raise HTTPException(404, 'Fehlerqueue-Eintrag nicht gefunden')
    locked_scale(db, tenant_id, item.waage_id)
    db.refresh(item)  # a concurrent retry may have completed while acquiring lock
    return item


def serialize_entry(item):
    return {'id': item.id, 'waage_id': item.waage_id, 'rohdaten': item.raw_text,
            'fehler_beschreibung': item.error, 'retry_count': item.retry_count, 'status': item.status,
            'timestamp': item.created_at.isoformat() if item.created_at else None, 'ticket_id': item.ticket_id}


def retry_entry(db, tenant_id, ident, actor):
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"), {"key": "waage-import:" + tenant_id})
    item = queue_entry(db, tenant_id, ident, allow_processed=True)
    if item.status == 'imported':
        return {'entry': serialize_entry(item), 'replayed': True}
    if item.status != 'error':
        raise HTTPException(404, 'Fehlerqueue-Eintrag nicht gefunden')
    item.retry_count += 1
    try:
        item.ticket_id = _persist_ticket(db, tenant_id, item.waage_id, item.raw_text)
        item.status, item.error = 'imported', None
    except (ValueError, HTTPException) as exc:
        item.error = str(exc.detail) if isinstance(exc, HTTPException) else str(exc)
    _event(db, tenant_id, actor, item, 'retried')
    db.flush()
    return {'entry': serialize_entry(item), 'replayed': False}
