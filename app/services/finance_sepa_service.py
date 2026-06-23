"""DOM-FINANCE-004.2 — SEPA-Zahlungsträger Service (Mandate + Batch-Export)."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class SEPAError(Exception):
    """Raised when SEPA constraints are violated."""


def _fetch_mandat(db: Session, mandat_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_finance.finance_sepa_mandate WHERE id = :id"),
        {"id": mandat_id},
    ).mappings().first()
    return dict(row) if row else None


def create_sepa_mandat(
    db: Session,
    tenant_id: str,
    glaeubiger_id: str,
    iban: str,
    bic: str,
    typ: str = "CORE",
    erteilung_am: Optional[str] = None,
) -> Dict[str, Any]:
    """Legt ein neues SEPA-Lastschriftmandat an."""
    if typ not in {"CORE", "B2B"}:
        raise SEPAError(f"Ungültiger SEPA-Typ: {typ}. Erlaubt: CORE, B2B")

    mandat_id = str(uuid.uuid4())
    mandat_ref = f"MAND-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{mandat_id[:8].upper()}"
    erteilung = erteilung_am or datetime.now(timezone.utc).date().isoformat()

    db.execute(
        text("""
            INSERT INTO domain_finance.finance_sepa_mandate
                (id, tenant_id, mandat_ref, glaeubiger_id, iban, bic, typ, status, erteilung_am, created_at)
            VALUES (:id, :tenant_id, :mandat_ref, :glaeubiger_id, :iban, :bic, :typ, 'AKTIV', :erteilung_am, NOW())
        """),
        {
            "id": mandat_id, "tenant_id": tenant_id, "mandat_ref": mandat_ref,
            "glaeubiger_id": glaeubiger_id, "iban": iban, "bic": bic,
            "typ": typ, "erteilung_am": erteilung,
        },
    )
    db.commit()
    logger.info("sepa_mandat created: %s", mandat_ref)
    return {
        "id": mandat_id, "mandat_ref": mandat_ref, "glaeubiger_id": glaeubiger_id,
        "iban": iban, "bic": bic, "typ": typ, "status": "AKTIV", "erteilung_am": erteilung,
    }


def widerruf_sepa_mandat(
    db: Session,
    mandat_id: str,
    tenant_id: str,
    widerruf_am: Optional[str] = None,
) -> Dict[str, Any]:
    """Widerruft ein SEPA-Mandat (idempotent wenn bereits widerrufen)."""
    mandat = _fetch_mandat(db, mandat_id)
    if not mandat:
        raise SEPAError(f"SEPA-Mandat {mandat_id} nicht gefunden")
    if mandat.get("tenant_id") != tenant_id:
        raise SEPAError(f"Mandat {mandat_id} gehört nicht zu Tenant {tenant_id}")

    if mandat.get("status") == "WIDERRUFEN":
        return {**mandat, "idempotent": True}

    datum = widerruf_am or datetime.now(timezone.utc).date().isoformat()
    db.execute(
        text("""
            UPDATE domain_finance.finance_sepa_mandate
            SET status = 'WIDERRUFEN', widerruf_am = :widerruf_am
            WHERE id = :id
        """),
        {"widerruf_am": datum, "id": mandat_id},
    )
    db.commit()
    logger.info("sepa_mandat %s widerrufen", mandat_id)
    return {**mandat, "status": "WIDERRUFEN", "widerruf_am": datum, "idempotent": False}


def create_sepa_batch(
    db: Session,
    tenant_id: str,
    faellig_am: str,
    eintraege: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Erstellt einen SEPA-Lastschrift-Batch mit vereinfachtem PAIN.008 XML."""
    if not eintraege:
        raise SEPAError("Mindestens ein Eintrag für SEPA-Batch erforderlich")

    gesamt_eur = sum(float(e.get("betrag_eur", 0)) for e in eintraege)
    batch_id = str(uuid.uuid4())

    # Build simplified PAIN.008 XML
    root = Element("Document")
    ci = SubElement(root, "CstmrDrctDbtInitn")
    grphdr = SubElement(ci, "GrpHdr")
    SubElement(grphdr, "MsgId").text = batch_id[:16]
    SubElement(grphdr, "CreDtTm").text = datetime.now(timezone.utc).isoformat()
    SubElement(grphdr, "NbOfTxs").text = str(len(eintraege))
    SubElement(grphdr, "CtrlSum").text = f"{gesamt_eur:.2f}"
    for e in eintraege:
        tx = SubElement(ci, "DrctDbtTxInf")
        SubElement(tx, "MndtRltdInf").text = e.get("mandat_ref", "")
        SubElement(tx, "InstdAmt", Ccy="EUR").text = f"{float(e.get('betrag_eur', 0)):.2f}"
        SubElement(tx, "DbtrAcct").text = e.get("iban", "")

    xml_payload = tostring(root, encoding="unicode")

    db.execute(
        text("""
            INSERT INTO domain_finance.finance_sepa_batches
                (id, tenant_id, faellig_am, gesamt_eur, status, xml_payload, created_at)
            VALUES (:id, :tenant_id, :faellig_am, :gesamt_eur, 'ERSTELLT', :xml_payload, NOW())
        """),
        {
            "id": batch_id, "tenant_id": tenant_id, "faellig_am": faellig_am,
            "gesamt_eur": gesamt_eur, "xml_payload": xml_payload,
        },
    )
    db.commit()
    logger.info("sepa_batch created: %s, %d Einträge, %.2f EUR", batch_id, len(eintraege), gesamt_eur)
    return {
        "id": batch_id, "faellig_am": faellig_am, "gesamt_eur": gesamt_eur,
        "anzahl_eintraege": len(eintraege), "status": "ERSTELLT", "xml_payload": xml_payload,
    }
