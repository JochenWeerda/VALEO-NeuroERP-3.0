"""Explicit CRM-subject processing; never substitutes a system-user lookup.

The returned scope and retained-source manifest are part of the result. This
processor does not claim to erase financial records or immutable audit history.
"""
from __future__ import annotations

import hashlib
import json
from typing import Literal

from fastapi import HTTPException
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from sqlalchemy import text

from app.core.business_time import business_now
from app.core.uuid7 import uuid7
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.services.mask_action_runtime_service import _write_audit

SCOPE = 'LOCAL_CRM_SUBJECT'


class ProcessPayload(BaseModel):
    model_config = ConfigDict(extra='forbid', populate_by_name=True, str_strip_whitespace=True)
    subject_type: Literal['CUSTOMER', 'LEAD']
    data_scope: Literal['LOCAL_CRM_SUBJECT']
    reason: str = Field(min_length=3, max_length=1000)
    expected_version: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1, max_length=128, validation_alias=AliasChoices('idempotency_key', '_idempotencyKey'))
    audit_reason: str | None = Field(default=None, max_length=1000, validation_alias=AliasChoices('audit_reason', '_auditReason'))


def _exists(db, table):
    return bool(db.execute(text('SELECT to_regclass(:name)'), {'name': table}).scalar())


def _rows(db, table, sql, params, evidence):
    if not _exists(db, table):
        evidence.append({'source': table, 'state': 'not_installed', 'rows': 0})
        return []
    # All SQL/table names are closed source literals; values are always bound.
    bounded = sql.removesuffix(' FOR UPDATE') + ' LIMIT 10001' + (' FOR UPDATE' if sql.endswith(' FOR UPDATE') else '')
    rows = [dict(row) for row in db.execute(text(bounded), params).mappings().all()]
    if len(rows) > 10000:
        raise HTTPException(413, 'CRM-Datenumfang benoetigt einen gesonderten Exportlauf; kein unvollstaendiger Export erstellt')
    evidence.append({'source': table, 'state': 'read', 'rows': len(rows)})
    return rows


def subject_rows(db, subject_type, subject_id, tenant_id, *, email=None):
    evidence = []
    params = {'sid': subject_id, 'tid': tenant_id}
    if subject_type == 'CUSTOMER':
        primary = _rows(db, 'domain_crm.customers', 'SELECT * FROM domain_crm.customers WHERE id::text=:sid AND tenant_id::text=:tid FOR UPDATE', params, evidence)
        secondary = _rows(db, 'domain_crm.crm_customers', 'SELECT * FROM domain_crm.crm_customers WHERE id::text=:sid AND tenant_id::text=:tid FOR UPDATE', params, evidence)
    elif subject_type == 'LEAD':
        primary = _rows(db, 'public.crm_leads', 'SELECT * FROM public.crm_leads WHERE id::text=:sid AND tenant_id::text=:tid FOR UPDATE', params, evidence)
        secondary = []
    else:
        raise HTTPException(422, 'CUSTOMER oder LEAD muss ausdruecklich ausgewaehlt werden')
    if primary and secondary:
        raise HTTPException(409, "Betroffenen-ID ist in mehreren CRM-Bestaenden nicht eindeutig")
    profiles = primary + secondary
    if not profiles:
        raise HTTPException(404, 'Betroffener Datensatz nicht im aktiven Mandanten gefunden')
    addresses = {str(row.get('email') or '').strip().casefold() for row in profiles}
    if email is not None and email.strip().casefold() not in addresses:
        raise HTTPException(409, 'Antragsadresse stimmt nicht mit dem ausgewaehlten Betroffenen ueberein')
    return profiles, evidence


def collect(db, subject_type, subject_id, tenant_id, email):
    profiles, evidence = subject_rows(db, subject_type, subject_id, tenant_id, email=email)
    params = {'sid': subject_id, 'tid': tenant_id}
    contacts = []
    numbers = []
    if subject_type == 'CUSTOMER':
        contacts = _rows(db, 'domain_crm.contacts', 'SELECT c.* FROM domain_crm.contacts c JOIN domain_crm.customers p ON p.id=c.customer_id WHERE p.id::text=:sid AND p.tenant_id::text=:tid', params, evidence)
        numbers = sorted({str(row['customer_number']) for row in profiles if row.get('customer_number')})
    params['numbers'] = numbers
    if contacts:
        db.execute(text('SELECT c.id FROM domain_crm.contacts c JOIN domain_crm.customers p ON p.id=c.customer_id WHERE p.id::text=:sid AND p.tenant_id::text=:tid FOR UPDATE OF c'), params).all()
    contact_logs = _rows(db, 'public.kunden_kontakte', 'SELECT * FROM public.kunden_kontakte WHERE tenant_id::text=:tid AND kunden_nr=ANY(:numbers)', params, evidence) if numbers else []
    # Art. 15/17 DSGVO: Aktivitaeten am Kunden (customer_id) und solche, die den Klarnamen im Freitext nennen.
    # Die Loeschung entfernt den Klarnamen (compliance_dsgvo._klarnamen_anonymisieren); die Auskunft nennt beide.
    activities = []
    if subject_type == 'CUSTOMER':
        params['namen'] = sorted({str(row[k]) for row in profiles for k in ('company_name', 'contact_person') if row.get(k)})
        activities = _rows(db, 'domain_crm.activities', 'SELECT * FROM domain_crm.activities WHERE tenant_id::text=:tid '
                           'AND (customer_id::text=:sid OR customer=ANY(:namen) OR contact_person=ANY(:namen))',
                           params, evidence)
    # Consent contact IDs refer to the external CRM-core registry. Local
    # contact IDs are not evidence of identity across the two registries.
    consents, consent_history = [], []
    data = {'profiles': profiles, 'contacts': contacts, 'activities': activities, 'contact_logs': contact_logs,
            'consents': consents, 'consent_history': consent_history}
    return data, evidence, params


def retained_manifest():
    return [
        {'source': 'commercial_documents_and_tax_identifiers', 'reason': 'Nicht Teil der operativen CRM-Personendatenanonymisierung; gesonderte Aufbewahrungspruefung erforderlich'},
        {'source': 'audit_and_consent_history', 'reason': 'Bestehende unveraenderliche Nachweise bleiben erhalten; keine Umschreibung der Herkunft'},
        {'source': 'external_crm_consents_and_other_external_systems', 'reason': 'Ohne belegte Personenverknuepfung keine automatische Zuordnung oder Loeschung'},
    ]


def _audit(db, obj, actor, action, reason, result):
    summary = {'scope': SCOPE, 'subject_type': obj.subject_type, 'subject_id': obj.subject_id,
               'status': obj.status, 'version': obj.version, 'sources': result.get('sources', [])}
    _write_audit(db, tenant_id=obj.tenant_id, action_key='gdpr.request.' + action, entity_type='gdpr_request',
        entity_id=obj.id, audit_reason=reason, idempotency_key=result['idempotency_key'], summary=json.dumps(summary), performed_by=actor)
    db.add(OutboxEvent(id=str(uuid7()), event_type='gdpr.request.' + action, aggregate_id=obj.id,
        tenant_id=obj.tenant_id, payload=json.dumps({**summary, 'actor': actor}), timestamp=business_now().replace(tzinfo=None)))


def process(db, obj, body: ProcessPayload, actor: str, action: str):
    fingerprint = hashlib.sha256(json.dumps({'actor': actor, 'action': action, **body.model_dump()}, sort_keys=True).encode()).hexdigest()
    previous = json.loads(obj.processing_result) if obj.processing_result else None
    if previous and previous.get('idempotency_key') == body.idempotency_key:
        if previous.get('fingerprint') != fingerprint:
            raise HTTPException(409, 'Wiederholungsschluessel gehoert zu einem anderen Aufruf')
        return obj
    if obj.status != 'VERIFIED':
        raise HTTPException(409, 'Antrag muss verifiziert und noch unverarbeitet sein')
    if obj.version != body.expected_version:
        raise HTTPException(409, 'Antrag wurde zwischenzeitlich geaendert')
    if obj.data_scope is not None and obj.data_scope != body.data_scope:
        raise HTTPException(409, 'Verarbeitungsumfang stimmt nicht mit dem Antrag ueberein')
    if obj.subject_type is not None and obj.subject_type != body.subject_type:
        raise HTTPException(409, 'Betroffenentyp stimmt nicht mit dem Antrag ueberein')
    if action == 'export' and obj.request_type not in {'ACCESS', 'PORTABILITY'}:
        raise HTTPException(409, 'Export nur fuer ACCESS oder PORTABILITY')
    if action == 'erase' and obj.request_type != 'ERASURE':
        raise HTTPException(409, 'Anonymisierung nur fuer ERASURE')
    data, evidence, params = collect(db, body.subject_type, obj.subject_id, obj.tenant_id, obj.subject_email)
    result = {'scope': SCOPE, 'subject_type': body.subject_type, 'actor': actor, 'action': action,
              'idempotency_key': body.idempotency_key, 'fingerprint': fingerprint,
              'sources': evidence, 'retained': retained_manifest()}
    if action == 'export':
        payload = {'subject_id': obj.subject_id, 'subject_type': body.subject_type, 'tenant_id': obj.tenant_id,
                   'request_type': obj.request_type, 'scope': SCOPE, 'exported_at': business_now().isoformat(),
                   'data': data, 'sources': evidence, 'retained': result['retained']}
        serialized = json.dumps(payload, ensure_ascii=False, default=str)
        if len(serialized.encode('utf-8')) > 10485760:
            raise HTTPException(413, 'CRM-Export uebersteigt 10 MB; gesonderter Exportlauf erforderlich')
        obj.export_payload = serialized
    else:
        from app.api.v1.endpoints.compliance_dsgvo import _anonymize_subject, _loeschung_ist_vollstaendig
        deletion_log = _anonymize_subject(db, body.subject_type, obj.subject_id, obj.tenant_id)
        if not _loeschung_ist_vollstaendig(deletion_log):
            raise HTTPException(422, {'message': 'CRM-Anonymisierung unvollstaendig; gesamte Transaktion zurueckgenommen', 'deletion_log': deletion_log})
        if data['contact_logs']:
            affected = db.execute(text('DELETE FROM public.kunden_kontakte WHERE tenant_id::text=:tid AND kunden_nr=ANY(:numbers)'), params).rowcount
            deletion_log.append({'table': 'public.kunden_kontakte', 'action': 'deleted', 'rows_affected': affected})
        # Invalidate previously prepared own-subject downloads; no old personal
        # payload survives a successful anonymization in the request store.
        db.execute(text("UPDATE public.gdpr_requests SET subject_email='geloescht@dsgvo.invalid', notes=NULL, export_payload=NULL, version=version+1 WHERE tenant_id::text=:tid AND subject_id::text=:sid AND id<>:request_id AND subject_type=:subject_type"), {**params, 'request_id': obj.id, 'subject_type': body.subject_type})
        obj.subject_email, obj.notes, obj.export_payload = 'geloescht@dsgvo.invalid', None, None
        result['deletion_log'] = deletion_log
    obj.subject_type = body.subject_type
    obj.data_scope = body.data_scope
    obj.status, obj.completed_at, obj.version = 'PARTIALLY_COMPLETED', business_now(), obj.version + 1
    obj.processing_result = json.dumps(result, ensure_ascii=False)
    _audit(db, obj, actor, action, body.reason, result)
    return obj
