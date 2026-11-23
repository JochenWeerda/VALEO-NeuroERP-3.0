"""Tenant-scoped customer master profile; mutations stay within the caller's transaction."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Annotated

from fastapi import HTTPException
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.customer_master_profile import master_catalog
from app.infrastructure.models import BusinessPartner, Customer
from app.services.customer_service import CustomerService
from app.services.business_partner_service import _feldwert
from app.api.v1.endpoints import business_partners as dto

# These fields overlap with the customer projection or belong to consent/identity
# workflows. They cannot be changed safely through this isolated BP command.
EXCLUDED_FIELDS = frozenset({
    'name_1', 'street', 'house_number', 'postal_code', 'city', 'country',
    'phone', 'email', 'website', 'credit_limit', 'vat_id',
    'email_opt_in', 'sms_opt_in', 'whatsapp_opt_in', 'newsletter_opt_in',
    'email_opt_in_timestamp', 'sms_opt_in_timestamp', 'whatsapp_opt_in_timestamp',
    'flyer_subscription', 'consent_valid_until', 'consent_note',
})
FORBIDDEN_GROUPS = frozenset({'roles', 'gdpr', 'audit'})


def field_specs() -> dict[str, Any]:
    result = {}
    columns = BusinessPartner.__table__.columns
    for group in master_catalog()['groups']:
        if group['key'] in FORBIDDEN_GROUPS:
            continue
        model = getattr(dto, group['model'])
        for field in group['fields']:
            key = field['key']
            if field.get('readOnly') or key in EXCLUDED_FIELDS or key not in model.model_fields or key not in columns:
                continue
            # Only scalar fields are supported by this command.
            if key in {'tab_23', 'discount_items', 'price_agreements'}:
                continue
            result[key] = model.model_fields[key]
    return result


def validate_changes(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    version = payload.get('expected_version')
    if type(version) is not int or not 0 < version <= 9007199254740991:
        raise ValueError('expected_version muss eine gültige Versionsnummer sein.')
    specs = field_specs()
    changes = {}
    for name, value in payload.items():
        if name == 'expected_version':
            continue
        if not name.startswith('partner_') or name[8:] not in specs:
            raise ValueError(f'Feld {name} darf nicht geändert werden.')
        key = name[8:]
        field = specs[key]
        column = BusinessPartner.__table__.columns[key]
        if value is None and not column.nullable:
            raise ValueError(f'Feld {name} darf nicht leer sein.')
        try:
            annotation = Annotated[field.annotation, *field.metadata] if field.metadata else field.annotation
            # Strict JSON scalar types prevent coercing strings to booleans/numbers.
            strict = isinstance(value, (bool, int, float, str)) and column.type.python_type not in (datetime,)
            from datetime import date
            if column.type.python_type is date:
                strict = False
            parsed = TypeAdapter(annotation).validate_python(value, strict=strict)
            if key in {'iban', 'bic'} and parsed is not None:
                parsed = _feldwert(key, parsed)
            if isinstance(parsed, str) and getattr(column.type, 'length', None) and len(parsed) > column.type.length:
                raise ValueError('Wert zu lang')
            changes[key] = parsed
        except (ValidationError, ValueError, TypeError) as exc:
            raise ValueError(f'Ungültiger Wert für {name}.') from exc
    if not changes:
        raise ValueError('Keine änderbaren Felder angegeben.')
    return version, changes


def version_of(partner: BusinessPartner) -> int:
    stamp = partner.updated_at or partner.created_at
    if stamp is None:
        raise ValueError('Geschäftspartner ohne Versionszeitpunkt.')
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = stamp.astimezone(timezone.utc) - epoch
    version = (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
    if not 0 < version <= 9007199254740991:
        raise ValueError('Versionszeitpunkt außerhalb des gültigen Bereichs.')
    return version


def _one(rows: list[Any]):
    if len(rows) > 1:
        raise HTTPException(409, 'Kundenidentität ist nicht eindeutig.')
    return rows[0] if rows else None


def scoped_pair(db: Session, tenant: str, customer_id: str, *, lock: bool = False, allow_unlinked: bool = False):
    """Resolve only tenant-local customer aliases, never the public legacy fallback."""
    if not tenant or not tenant.strip():
        raise HTTPException(403, 'Verified tenant context required')
    customer_query = select(Customer).where(
        Customer.tenant_id == tenant, Customer.deleted_at.is_(None),
        or_(Customer.id == customer_id, Customer.customer_number == customer_id,
            Customer.business_partner_id == customer_id))
    if lock:
        customer_query = customer_query.with_for_update()
    customer = _one(db.execute(customer_query).scalars().all())
    partner = None
    if customer is None:
        # Resolve the partner alias without locking, then lock any customer first.
        partner_query = select(BusinessPartner).where(
            BusinessPartner.tenant_id == tenant, BusinessPartner.is_customer.is_(True),
            or_(BusinessPartner.partner_id == customer_id, BusinessPartner.partner_number == customer_id))
        partner = _one(db.execute(partner_query).scalars().all())
        if partner is None:
            raise HTTPException(404, 'Kunde oder Geschäftspartner nicht gefunden')
        related = select(Customer).where(Customer.tenant_id == tenant, Customer.deleted_at.is_(None),
                                         Customer.business_partner_id == partner.partner_id)
        if lock:
            related = related.with_for_update()
        customer = _one(db.execute(related).scalars().all())
        if customer is None:
            # A soft-deleted customer must not reappear as a BP-only customer.
            tombstones = select(Customer).where(Customer.tenant_id == tenant, Customer.deleted_at.is_not(None),
                                                Customer.business_partner_id == partner.partner_id)
            if db.execute(tombstones).scalars().all():
                raise HTTPException(404, 'Kunde oder Geschäftspartner nicht gefunden')
    elif customer.business_partner_id is None and allow_unlinked:
        aliases = select(BusinessPartner).where(
            BusinessPartner.tenant_id == tenant, BusinessPartner.is_customer.is_(True),
            or_(BusinessPartner.partner_id == customer_id, BusinessPartner.partner_number == customer_id))
        if db.execute(aliases).scalars().all():
            raise HTTPException(409, 'Kundenidentität ist nicht eindeutig.')
        return customer, None
    elif not customer.business_partner_id:
        raise HTTPException(404, 'Kunde oder Geschäftspartner nicht gefunden')

    partner_id = customer.business_partner_id if customer is not None else partner.partner_id
    partner_query = select(BusinessPartner).where(BusinessPartner.partner_id == partner_id,
                                                   BusinessPartner.tenant_id == tenant)
    if customer is None:
        partner_query = partner_query.where(BusinessPartner.is_customer.is_(True))
    if lock:
        partner_query = partner_query.with_for_update()
    partner = _one(db.execute(partner_query).scalars().all())
    if partner is None:
        raise HTTPException(404, 'Kunde oder Geschäftspartner nicht gefunden')
    if customer is not None:
        aliases = select(BusinessPartner).where(
            BusinessPartner.tenant_id == tenant, BusinessPartner.is_customer.is_(True),
            or_(BusinessPartner.partner_id == customer_id, BusinessPartner.partner_number == customer_id))
        candidates = db.execute(aliases).scalars().all()
        if any(str(candidate.partner_id) != str(partner.partner_id) for candidate in candidates):
            raise HTTPException(409, 'Kundenidentität ist nicht eindeutig.')
    return customer, partner


def _partner_only_projection(partner: BusinessPartner, tenant: str) -> dict[str, Any]:
    """The local BP customer projection without the legacy public.kunden fallback."""
    from app.services.customer_service import attach_mask_aliases
    name = str(partner.name_1 or partner.partner_number)[:100]
    return attach_mask_aliases({
        'id': str(partner.partner_id), 'tenant_id': tenant,
        'customer_number': str(partner.partner_number)[:50], 'company_name': name, 'name': name,
        'contact_person': None, 'email': partner.email, 'phone': partner.phone,
        'address': partner.street, 'city': partner.city, 'postal_code': partner.postal_code,
        'country': partner.country, 'industry': None, 'website': partner.website,
        'price_group': None, 'tax_category': None, 'credit_limit': None, 'payment_terms': 30,
        'tax_id': None, 'chefanweisung': None, 'business_partner_id': str(partner.partner_id),
        'is_active': True, 'deleted_at': None, 'created_at': None, 'updated_at': None,
        'fax': partner.fax,
    })


def read_profile(db: Session, tenant: str, customer_id: str) -> dict[str, Any]:
    customer, partner = scoped_pair(db, tenant, customer_id, allow_unlinked=True)
    if customer is None:
        projection = _partner_only_projection(partner, tenant)
    else:
        service = CustomerService(db, tenant)
        projection = service.get_from_db_any_key(str(customer.id))
        expected_partner = str(customer.business_partner_id) if customer.business_partner_id is not None else None
        actual_partner = projection.get('business_partner_id') if projection else None
        if (projection is None or str(projection.get('id')) != str(customer.id)
                or str(projection.get('tenant_id')) != tenant
                or (str(actual_partner) if actual_partner is not None else None) != expected_partner):
            raise HTTPException(404, 'Kunde nicht gefunden')
        projection = service.merge_extensions(projection)
        projection['business_partner_id'] = expected_partner
        if partner is None:
            projection.pop('version', None)
            return projection
    for group in master_catalog()['groups']:
        for field in group['fields']:
            key = field['key']
            if key in BusinessPartner.__table__.columns:
                projection['partner_' + key] = getattr(partner, key)
    projection['version'] = version_of(partner)
    return projection


def check_profile(db: Session, payload: dict[str, Any], customer_id: str, tenant: str) -> None:
    expected, _ = validate_changes(payload)
    _, partner = scoped_pair(db, tenant, customer_id, lock=True)
    if version_of(partner) != expected:
        raise ValueError('Stammdaten wurden zwischenzeitlich geändert. Bitte erneut laden.')


def update_profile(db: Session, payload: dict[str, Any], customer_id: str, tenant: str, *, actor: str | None = None) -> str:
    expected, changes = validate_changes(payload)
    _, partner = scoped_pair(db, tenant, customer_id, lock=True)
    current = version_of(partner)
    if current != expected:
        raise ValueError('Stammdaten wurden zwischenzeitlich geändert. Bitte erneut laden.')
    for key, value in changes.items():
        setattr(partner, key, value)
    if actor is not None:
        partner.updated_by = actor
    previous = partner.updated_at or partner.created_at
    if previous.tzinfo is None:
        previous = previous.replace(tzinfo=timezone.utc)
    partner.updated_at = max(datetime.now(timezone.utc), previous + timedelta(microseconds=1))
    db.flush()
    return 'Kundenstammdaten gespeichert.'
