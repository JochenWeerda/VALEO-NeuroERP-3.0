"""DOM-DOC-004.2 — Dokumenten-Nachweisraum Lifecycle (Upload/Freigabe/GoBD)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_DOKUMENT_TRANSITIONS = {
    ("EINGEGANGEN", "IN_PRUEFUNG"),
    ("EINGEGANGEN", "ABGELEHNT"),
    ("IN_PRUEFUNG", "FREIGEGEBEN"),
    ("IN_PRUEFUNG", "ABGELEHNT"),
    ("IN_PRUEFUNG", "WIEDERVORLAGE"),
    ("WIEDERVORLAGE", "IN_PRUEFUNG"),
    ("WIEDERVORLAGE", "ABGELEHNT"),
    ("FREIGEGEBEN", "ARCHIVIERT"),
}

VALID_GOBD_TRANSITIONS = {
    ("OFFEN", "IN_ERSTELLUNG"),
    ("IN_ERSTELLUNG", "EXPORTIERT"),
    ("EXPORTIERT", "PRUEFBAR"),
    ("PRUEFBAR", "ABGENOMMEN"),
    ("IN_ERSTELLUNG", "FEHLER"),
}


class NachweisraumError(Exception):
    pass


def create_dokument(
    db: Session,
    tenant_id: str,
    dokument_typ: str,
    bezeichnung: str,
    referenz_id: str,
    referenz_typ: str,
    datei_pfad: str,
    operator: str = "system",
) -> Dict[str, Any]:
    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_nachweisraum.nachweisraum_dokumente
                (id, tenant_id, dokument_typ, bezeichnung, referenz_id, referenz_typ,
                 datei_pfad, version, status, operator, created_at)
            VALUES (:id, :tenant_id, :dokument_typ, :bezeichnung, :referenz_id, :referenz_typ,
                    :datei_pfad, 1, 'EINGEGANGEN', :operator, NOW())
        """),
        {
            "id": rec_id,
            "tenant_id": tenant_id,
            "dokument_typ": dokument_typ,
            "bezeichnung": bezeichnung,
            "referenz_id": referenz_id,
            "referenz_typ": referenz_typ,
            "datei_pfad": datei_pfad,
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_nachweisraum.nachweisraum_dokumente WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def transition_dokument(
    db: Session,
    dokument_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    kommentar: str = "",
    wiedervorlage_datum: Optional[str] = None,
) -> Dict[str, Any]:
    rec = db.execute(
        text("""
            SELECT * FROM domain_nachweisraum.nachweisraum_dokumente
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": dokument_id, "tid": tenant_id},
    ).mappings().first()
    if not rec:
        raise NachweisraumError(f"Dokument {dokument_id} nicht gefunden")
    old_status = rec["status"]
    if (old_status, new_status) not in VALID_DOKUMENT_TRANSITIONS:
        raise NachweisraumError(f"Ungültiger Übergang {old_status} → {new_status}")

    params: Dict[str, Any] = {
        "new_status": new_status,
        "id": dokument_id,
        "tid": tenant_id,
    }
    extra = ""
    if wiedervorlage_datum:
        extra += ", wiedervorlage_datum = :wv"
        params["wv"] = wiedervorlage_datum

    db.execute(
        text(f"""
            UPDATE domain_nachweisraum.nachweisraum_dokumente
            SET status = :new_status{extra}, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),  # nosec B608  # extra is assembled only from fixed code-controlled fragments; values are parameterized.
        params,
    )
    db.execute(
        text("""
            INSERT INTO domain_nachweisraum.nachweisraum_audit_log
                (id, dokument_id, tenant_id, old_status, new_status, operator, kommentar, created_at)
            VALUES (:id, :did, :tid, :old, :new, :op, :kom, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "did": dokument_id,
            "tid": tenant_id,
            "old": old_status,
            "new": new_status,
            "op": operator,
            "kom": kommentar,
        },
    )
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_nachweisraum.nachweisraum_dokumente WHERE id = :id"),
        {"id": dokument_id},
    ).mappings().first()
    return dict(updated)


def create_gobd_export(
    db: Session,
    tenant_id: str,
    periode: str,
    referenz_ids: List[str],
    operator: str = "system",
) -> Dict[str, Any]:
    """Erstellt einen GoBD-Exportauftrag für eine Periode."""
    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_nachweisraum.gobd_exporte
                (id, tenant_id, periode, anzahl_dokumente, status, operator, created_at)
            VALUES (:id, :tenant_id, :periode, :anzahl, 'OFFEN', :operator, NOW())
        """),
        {
            "id": rec_id,
            "tenant_id": tenant_id,
            "periode": periode,
            "anzahl": len(referenz_ids),
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_nachweisraum.gobd_exporte WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def transition_gobd_export(
    db: Session,
    export_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    export_pfad: Optional[str] = None,
    fehler: Optional[str] = None,
) -> Dict[str, Any]:
    rec = db.execute(
        text("""
            SELECT * FROM domain_nachweisraum.gobd_exporte
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": export_id, "tid": tenant_id},
    ).mappings().first()
    if not rec:
        raise NachweisraumError(f"GoBD-Export {export_id} nicht gefunden")
    old_status = rec["status"]
    if (old_status, new_status) not in VALID_GOBD_TRANSITIONS:
        raise NachweisraumError(f"Ungültiger Übergang {old_status} → {new_status}")

    params: Dict[str, Any] = {
        "new_status": new_status,
        "id": export_id,
        "tid": tenant_id,
    }
    extra = ""
    if export_pfad:
        extra += ", export_pfad = :pfad"
        params["pfad"] = export_pfad
    if fehler:
        extra += ", fehler_grund = :fehler"
        params["fehler"] = fehler

    db.execute(
        text(f"""
            UPDATE domain_nachweisraum.gobd_exporte
            SET status = :new_status{extra}, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),  # nosec B608  # extra is assembled only from fixed code-controlled fragments; values are parameterized.
        params,
    )
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_nachweisraum.gobd_exporte WHERE id = :id"),
        {"id": export_id},
    ).mappings().first()
    return dict(updated)
