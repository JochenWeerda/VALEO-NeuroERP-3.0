"""Mandantengrenze fuer ``public.kunden`` und Satelliten ohne eigene ``tenant_id``.

Die L3-Kompatibilitaetstabellen (``public.kunden``, ``kunden_lookup``,
``kunden_crm360``, ``kunden_ansprechpartner``, …) tragen keinen Mandanten.
Eigentum laeuft ueber ``business_partner_id`` → ``domain_crm.business_partners.tenant_id``
bzw. parallel ueber ``domain_crm.customers.customer_number``.

Jeder lesende oder schreibende Weg auf diese Tabellen muss eine der beiden
Verknuepfungen mit dem verifizierten Token-Mandanten pruefen — sonst entstehen
Mandantenlecks (M4-CR-P0).
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Alias ``k`` = public.kunden / kunden_lookup-Zeile mit business_partner_id + kunden_nr.
KUNDE_GEHOERT_MANDANT = """
(
  EXISTS (
    SELECT 1 FROM domain_crm.business_partners bp
    WHERE k.business_partner_id IS NOT NULL
      AND bp.partner_id::text = k.business_partner_id::text
      AND bp.tenant_id = :tid
  )
  OR EXISTS (
    SELECT 1 FROM domain_crm.customers c
    WHERE c.customer_number = k.kunden_nr
      AND c.tenant_id::text = :tid
      AND c.deleted_at IS NULL
  )
)
"""


def public_kunde_im_mandanten(
    db: Session, *, kunden_nr: str, tenant_id: str
) -> Optional[dict[str, Any]]:
    """Stammzeile aus ``public.kunden``, nur wenn sie zum Mandanten gehoert."""
    if not tenant_id or not kunden_nr:
        return None
    row = db.execute(
        text(
            f"""
            SELECT k.kunden_nr, k.name1, k.strasse, k.plz, k.ort, k.land, k.tel, k.fax,
                   k.email, k.business_partner_id,
                   COALESCE(k.geloescht, false) AS geloescht, k.merged_into
            FROM public.kunden k
            WHERE k.kunden_nr = :nr AND {KUNDE_GEHOERT_MANDANT}
            LIMIT 1
            """
        ),
        {"nr": kunden_nr, "tid": tenant_id},
    ).mappings().first()
    return dict(row) if row else None
