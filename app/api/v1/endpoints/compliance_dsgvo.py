"""DSGVO Löschkonzept — Erasure request management (Art. 17 DSGVO)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema, IDResponse
from app.api.v1.schemas.compliance_dsgvo_schemas import ComplianceDsgvoOut


router = APIRouter(prefix="/compliance/dsgvo", tags=["compliance", "dsgvo"])

ERASURE_STATUSES = {"EINGEGANGEN", "IN_BEARBEITUNG", "ABGESCHLOSSEN", "ABGELEHNT"}
SUBJECT_TYPES = {"CUSTOMER", "EMPLOYEE", "LEAD"}


class ErasureRequestIn(BaseModel):
    requester_name: str = Field(..., max_length=200)
    requester_email: str = Field(..., max_length=200)
    subject_id: str = Field(..., description="ID des betroffenen Datensatzes")
    subject_type: str = Field(..., description="CUSTOMER/EMPLOYEE/LEAD")


class ErasureProcessIn(BaseModel):
    deletion_notes: str | None = None


class ErasureLogEntry(BaseModel):
    """Eine Zeile des Loeschprotokolls."""

    model_config = ConfigDict(extra="allow")

    table: str | None = None
    rows_affected: int = 0
    action: str | None = None
    error: str | None = None
    note: str | None = None


class ErasureProcessOut(BaseModel):
    """Was die Verarbeitung eines Loeschantrags zurueckmeldet.

    Zuvor antwortete der Endpunkt mit ``IDResponse`` — das Protokoll, also die
    einzige Auskunft darueber, *was* geloescht wurde, fiel bei der Serialisierung
    weg. Der Aufrufer bekam eine ID und musste glauben, dass etwas geschah.
    """

    id: str
    status: str
    deletion_log: list[ErasureLogEntry] = Field(default_factory=list)


class ErasureRejectIn(BaseModel):
    reason: str = Field(..., max_length=1000, description="z.B. gesetzliche Aufbewahrungspflicht")


def _namen_des_betroffenen(
    db: Session, subject_type: str, subject_id: str, tenant_id: str
) -> list[str]:
    """Unter welchen Namen ist der Betroffene sonst noch vermerkt?

    ``domain_crm.activities`` kennt seinen Kunden nur als Text (`customer` ist
    ein String(100), keine Referenz). Ohne den Namen ist die Aktivitaet nicht
    auffindbar — sie muss also **vor** dem Anonymisieren gelesen werden.
    """
    abfragen = {
        "CUSTOMER": [
            "SELECT company_name FROM domain_crm.customers WHERE id::text = :sid AND tenant_id::text = :tid",
            "SELECT company_name FROM domain_crm.crm_customers WHERE id::text = :sid AND tenant_id::text = :tid",
        ],
        "LEAD": [
            "SELECT company_name FROM domain_crm.leads WHERE id::text = :sid AND tenant_id::text = :tid",
            "SELECT contact_person FROM domain_crm.leads WHERE id::text = :sid AND tenant_id::text = :tid",
        ],
    }
    namen: list[str] = []
    for sql in abfragen.get(subject_type, []):
        try:
            wert = db.execute(text(sql), {"sid": subject_id, "tid": tenant_id}).scalar()
        except Exception:  # noqa: BLE001 — eine fehlende Quelle ist kein Name, kein Abbruch
            continue
        if wert and wert not in namen:
            namen.append(wert)
    return namen


def _anonymize_subject(db: Session, subject_type: str, subject_id: str, tenant_id: str) -> list[dict]:
    """Anonymisiert/loescht Datensaetze und gibt ein Protokoll zurueck.

    Jede einzelne Anweisung hier zeigte auf Tabellen oder Spalten, die es nicht
    gibt: ``domain_crm.crm_customers`` hat kein `name`, `telefon`, `adresse`;
    ``domain_crm.contacts`` hat kein `tenant_id`; ``domain_crm.activities`` hat
    weder `customer_id` noch `lead_id`; ``domain_hr.employees`` gibt es gar
    nicht. Der Fehler landete im Protokoll, der Antrag wurde trotzdem auf
    ABGESCHLOSSEN gesetzt — eine Rechtspflicht (Art. 17 DSGVO) galt als
    erfuellt, waehrend kein einziger Datensatz angefasst worden war.

    Gefuehrt werden die Kunden in ``domain_crm.customers``; ``crm_customers``
    steht daneben. Beide werden bedient, damit die Loeschung nicht davon
    abhaengt, in welcher der Kunde liegt.
    """
    log: list[dict] = []
    anon_name = "ANONYM (DSGVO Art.17)"
    anon_email = "geloescht@dsgvo.invalid"
    namen = _namen_des_betroffenen(db, subject_type, subject_id, tenant_id)

    def anweisungen(typ: str) -> list[tuple[str, str, dict]]:
        basis = {"anon_name": anon_name, "anon_email": anon_email,
                 "sid": subject_id, "tid": tenant_id}
        if typ == "CUSTOMER":
            schritte = [
                ("domain_crm.customers",
                 "UPDATE domain_crm.customers SET company_name = :anon_name,"
                 " contact_person = :anon_name, email = :anon_email, phone = NULL,"
                 " address = NULL, city = NULL, postal_code = NULL, website = NULL,"
                 " chefanweisung = NULL"
                 " WHERE id::text = :sid AND tenant_id::text = :tid", basis),
                ("domain_crm.crm_customers",
                 # street/postal_code/city sind NOT NULL — anonymisieren, nicht leeren.
                 "UPDATE domain_crm.crm_customers SET company_name = :anon_name,"
                 " first_name = NULL, last_name = :anon_name, email = :anon_email,"
                 " phone = NULL, mobile = NULL, street = :anon_name,"
                 " postal_code = '00000', city = :anon_name"
                 " WHERE id::text = :sid AND tenant_id::text = :tid", basis),
                ("domain_crm.contacts",
                 # Kein tenant_id in der Tabelle — der Mandant haengt am Kunden,
                 # der oben bereits mandantenrein geprueft wurde.
                 "DELETE FROM domain_crm.contacts WHERE customer_id::text = :sid", basis),
            ]
        elif typ == "LEAD":
            schritte = [
                ("domain_crm.leads",
                 "UPDATE domain_crm.leads SET company_name = :anon_name,"
                 " contact_person = :anon_name, email = :anon_email, phone = NULL"
                 " WHERE id::text = :sid AND tenant_id::text = :tid", basis),
            ]
        elif typ == "EMPLOYEE":
            # Einen Personalstamm gibt es in dieser Datenbank nicht. Das als
            # „nichts zu tun" zu protokollieren waere eine Auskunft, die nicht
            # stimmt — es ist eine offene Luecke.
            return []
        else:
            return []

        for name in namen:
            schritte.append((
                "domain_crm.activities",
                "DELETE FROM domain_crm.activities"
                " WHERE customer = :kunde AND (tenant_id IS NULL OR tenant_id::text = :tid)",
                {**basis, "kunde": name},
            ))
        return schritte

    schritte = anweisungen(subject_type)
    if not schritte:
        log.append({
            "table": "-",
            "rows_affected": 0,
            "error": f"Fuer subject_type {subject_type} gibt es in dieser Datenbank "
                     f"keinen Datenbestand, der geloescht werden koennte.",
        })
        return log

    for table, sql, params in schritte:
        try:
            result = db.execute(text(sql), params)
            log.append({"table": table, "rows_affected": result.rowcount,
                        "action": "anonymized_or_deleted"})
        except Exception as exc:  # noqa: BLE001 — jeder Fehlschlag muss sichtbar bleiben
            log.append({"table": table, "rows_affected": 0, "error": str(exc)})
    return log


def _loeschung_ist_vollstaendig(log: list[dict]) -> bool:
    """Kein Eintrag mit Fehler — sonst ist der Antrag nicht abgeschlossen."""
    return bool(log) and not any(eintrag.get("error") for eintrag in log)


@router.post("/erasure-requests", status_code=201, summary="Erasure request anlegen",
    response_model=IDResponse
)
async def create_erasure_request(
    payload: ErasureRequestIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löschantrag (Art. 17 DSGVO) einreichen."""
    if payload.subject_type not in SUBJECT_TYPES:
        raise HTTPException(status_code=400, detail=f"subject_type must be one of: {', '.join(SUBJECT_TYPES)}")
    req_id = str(uuid4())
    try:
        db.execute(
            text("""
                INSERT INTO domain_compliance.data_erasure_requests
                    (id, requester_name, requester_email, subject_id, subject_type,
                     request_date, status, deletion_log, tenant_id)
                VALUES
                    (:id, :requester_name, :requester_email, :subject_id, :subject_type,
                     NOW(), 'EINGEGANGEN', '[]'::jsonb, :tenant_id)
            """),
            {
                "id": req_id,
                "requester_name": payload.requester_name,
                "requester_email": payload.requester_email,
                "subject_id": payload.subject_id,
                "subject_type": payload.subject_type,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    return {"id": req_id, "status": "EINGEGANGEN"}


@router.get("/erasure-requests", summary="Erasure requests auflisten",
    response_model=list[ComplianceDsgvoOut]
)
async def list_erasure_requests(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alle Löschanträge auflisten, optional nach Status filtern."""
    where = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id}
    if status:
        if status not in ERASURE_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(ERASURE_STATUSES)}")
        where.append("status = :status")
        params["status"] = status
    try:
        rows = db.execute(
            text(f"SELECT * FROM domain_compliance.data_erasure_requests WHERE {' AND '.join(where)} ORDER BY request_date DESC"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            params,
        ).fetchall()
    except Exception:
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    return [dict(r._mapping) for r in rows]


@router.get("/erasure-requests/{request_id}", summary="Erasure request abrufen",
    response_model=ComplianceDsgvoOut
)
async def get_erasure_request(
    request_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Detail eines Löschantrags."""
    try:
        row = db.execute(
            text("SELECT * FROM domain_compliance.data_erasure_requests WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": request_id, "tenant_id": tenant_id},
        ).fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    if not row:
        raise HTTPException(status_code=404, detail=f"ErasureRequest {request_id} not found")
    return dict(row._mapping)


@router.post("/erasure-requests/{request_id}/process", summary="Erasure request verarbeiten",
    response_model=ErasureProcessOut
)
async def process_erasure_request(
    request_id: str,
    payload: ErasureProcessIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löschantrag ausführen: Daten anonymisieren/löschen und protokollieren."""
    try:
        row = db.execute(
            text("SELECT * FROM domain_compliance.data_erasure_requests WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": request_id, "tenant_id": tenant_id},
        ).fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    if not row:
        raise HTTPException(status_code=404, detail=f"ErasureRequest {request_id} not found")
    r = dict(row._mapping)
    if r["status"] == "ABGESCHLOSSEN":
        raise HTTPException(status_code=409, detail="Erasure request already completed")
    if r["status"] == "ABGELEHNT":
        raise HTTPException(status_code=409, detail="Erasure request was rejected")

    deletion_log = _anonymize_subject(db, r["subject_type"], r["subject_id"], tenant_id)
    if payload.deletion_notes:
        deletion_log.append({"note": payload.deletion_notes})

    # Ein Loeschantrag gilt nur als abgeschlossen, wenn wirklich geloescht
    # wurde. Zuvor wurde der Status unabhaengig vom Protokoll auf
    # ABGESCHLOSSEN gesetzt — ein Antrag, bei dem jede einzelne Anweisung
    # scheiterte, sah damit aus wie erledigt. Bleibt etwas offen, bleibt der
    # Antrag IN_BEARBEITUNG und der Aufrufer bekommt das Protokoll zu sehen.
    vollstaendig = _loeschung_ist_vollstaendig(
        [e for e in deletion_log if "note" not in e]
    )
    neuer_status = "ABGESCHLOSSEN" if vollstaendig else "IN_BEARBEITUNG"

    try:
        db.execute(
            text("""
                UPDATE domain_compliance.data_erasure_requests
                SET status = :neuer_status,
                    completion_date = CASE WHEN :vollstaendig THEN NOW() ELSE NULL END,
                    deletion_log = CAST(:deletion_log AS jsonb)
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {
                "deletion_log": json.dumps(deletion_log),
                "neuer_status": neuer_status,
                "vollstaendig": vollstaendig,
                "id": request_id,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Failed to update erasure request")

    if not vollstaendig:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Die Loeschung ist unvollstaendig — der Antrag bleibt offen.",
                "id": request_id,
                "status": neuer_status,
                "deletion_log": deletion_log,
            },
        )
    return {"id": request_id, "status": "ABGESCHLOSSEN", "deletion_log": deletion_log}


@router.post("/erasure-requests/{request_id}/reject", summary="Erasure request ablehnen",
    response_model=IDResponse
)
async def reject_erasure_request(
    request_id: str,
    payload: ErasureRejectIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löschantrag ablehnen (z.B. gesetzliche Aufbewahrungspflicht)."""
    try:
        result = db.execute(
            text("""
                UPDATE domain_compliance.data_erasure_requests
                SET status = 'ABGELEHNT',
                    deletion_log = jsonb_build_array(jsonb_build_object('rejected_reason', :reason, 'rejected_at', NOW()::text))
                WHERE id = :id AND tenant_id = :tenant_id AND status NOT IN ('ABGESCHLOSSEN', 'ABGELEHNT')
            """),
            {"reason": payload.reason, "id": request_id, "tenant_id": tenant_id},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"ErasureRequest {request_id} not found or already finalized")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    return {"id": request_id, "status": "ABGELEHNT", "reason": payload.reason}
