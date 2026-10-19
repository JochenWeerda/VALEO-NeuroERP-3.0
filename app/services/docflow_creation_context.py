"""Tenant-bound partner references for registered document creation screens."""
from sqlalchemy import text
from app.core.belegvertrag import BELEGARTEN
from app.core.exceptions import ValidationFailedError


def _partner_sql(kind):
    if BELEGARTEN[kind].partnerrolle == 'lieferant':
        return "SELECT id::text AS value, lieferantennummer AS number, firmenname AS name FROM domain_einkauf.lieferanten WHERE tenant_id=:tenant"
    return "SELECT id::text AS value, customer_number AS number, company_name AS name FROM domain_crm.customers WHERE tenant_id=:tenant"


def search_partners(db, tenant_id, kind, query, limit):
    # Both SQL alternatives and the wrapping identifiers are code controlled.
    sql = "SELECT value, number, name FROM (" + _partner_sql(kind) + ") AS partners WHERE COALESCE(number,'') ILIKE :q OR COALESCE(name,'') ILIKE :q ORDER BY number,value LIMIT :limit"  # nosec B608
    rows = db.execute(text(sql), {'tenant': tenant_id, 'q': '%' + query + '%', 'limit': limit}).mappings()
    return [{'value': row['value'], 'label': f"{row['number'] or ''} - {row['name'] or ''}".strip(' -')} for row in rows]


def validate_partner(db, tenant_id, payload):
    kind = payload.doc_type
    if kind not in BELEGARTEN:
        raise ValidationFailedError('Unbekannte Belegvariante.')
    supplier = BELEGARTEN[kind].partnerrolle == 'lieferant'
    selected = payload.supplier_id if supplier else payload.customer_id
    opposite = payload.customer_id if supplier else payload.supplier_id
    if not selected or opposite:
        raise ValidationFailedError('Genau ein Partner der passenden Belegrolle ist erforderlich.')
    sql = "SELECT value FROM (" + _partner_sql(kind) + ") AS partners WHERE value=:selected FOR SHARE"  # nosec B608
    row = db.execute(text(sql), {'tenant': tenant_id, 'selected': selected}).first()
    if row is None:
        raise ValidationFailedError('Partner ist fuer diesen Mandanten und Belegfall nicht verfuegbar.')
