"""
Finance Router
CRUD für Zahlungsläufe, SEPA-Export, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database_pg import get_db
from . import models, schemas

router = APIRouter(prefix="/api/finance", tags=["Finance"])


def get_tenant_id(x_tenant: Optional[str] = Header(None)) -> str:
    """Extract Tenant ID from Header"""
    return x_tenant or "default"


# --- ZAHLUNGSLÄUFE KREDITOREN ---

@router.post("/zahlungslauf-kreditoren", response_model=schemas.Zahlungslauf, status_code=201)
async def create_zahlungslauf(
    zahlungslauf: schemas.ZahlungslaufCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new Zahlungslauf Kreditoren"""
    db_zahlungslauf = models.Zahlungslauf(
        id=str(uuid.uuid4()),
        **zahlungslauf.model_dump(),
        tenant_id=tenant_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_zahlungslauf)
    db.commit()
    db.refresh(db_zahlungslauf)
    return db_zahlungslauf


@router.get("/zahlungslauf-kreditoren", response_model=List[schemas.Zahlungslauf])
async def list_zahlungslaufe(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all Zahlungsläufe"""
    query = db.query(models.Zahlungslauf).filter(models.Zahlungslauf.tenant_id == tenant_id)

    if status:
        query = query.filter(models.Zahlungslauf.status == status)

    return query.order_by(models.Zahlungslauf.created_at.desc()).all()


@router.get("/zahlungslauf-kreditoren/{zahlungslauf_id}", response_model=schemas.Zahlungslauf)
async def get_zahlungslauf(
    zahlungslauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get Zahlungslauf by ID"""
    zahlungslauf = db.query(models.Zahlungslauf).filter(
        models.Zahlungslauf.id == zahlungslauf_id,
        models.Zahlungslauf.tenant_id == tenant_id
    ).first()

    if not zahlungslauf:
        raise HTTPException(status_code=404, detail="Zahlungslauf not found")

    return zahlungslauf


@router.put("/zahlungslauf-kreditoren/{zahlungslauf_id}", response_model=schemas.Zahlungslauf)
async def update_zahlungslauf(
    zahlungslauf_id: str,
    zahlungslauf_update: schemas.ZahlungslaufUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update Zahlungslauf"""
    db_zahlungslauf = db.query(models.Zahlungslauf).filter(
        models.Zahlungslauf.id == zahlungslauf_id,
        models.Zahlungslauf.tenant_id == tenant_id
    ).first()

    if not db_zahlungslauf:
        raise HTTPException(status_code=404, detail="Zahlungslauf not found")

    # Update fields
    for field, value in zahlungslauf_update.model_dump(exclude_unset=True).items():
        setattr(db_zahlungslauf, field, value)

    db_zahlungslauf.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_zahlungslauf)
    return db_zahlungslauf


@router.delete("/zahlungslauf-kreditoren/{zahlungslauf_id}", status_code=204)
async def delete_zahlungslauf(
    zahlungslauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete Zahlungslauf"""
    db_zahlungslauf = db.query(models.Zahlungslauf).filter(
        models.Zahlungslauf.id == zahlungslauf_id,
        models.Zahlungslauf.tenant_id == tenant_id
    ).first()

    if not db_zahlungslauf:
        raise HTTPException(status_code=404, detail="Zahlungslauf not found")

    db.delete(db_zahlungslauf)
    db.commit()
    return None


@router.get("/zahlungslauf-kreditoren/{zahlungslauf_id}/preview")
async def preview_zahlungslauf(
    zahlungslauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """SEPA Preview für Zahlungslauf"""
    zahlungslauf = db.query(models.Zahlungslauf).filter(
        models.Zahlungslauf.id == zahlungslauf_id,
        models.Zahlungslauf.tenant_id == tenant_id
    ).first()

    if not zahlungslauf:
        raise HTTPException(status_code=404, detail="Zahlungslauf not found")

    # Mock SEPA XML Preview
    sepa_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>{zahlungslauf.lauf_nummer}</MsgId>
            <CreDtTm>{datetime.utcnow().isoformat()}</CreDtTm>
            <NbOfTxs>{len(zahlungslauf.zahlungen)}</NbOfTxs>
            <CtrlSum>{zahlungslauf.gesamt_betrag}</CtrlSum>
            <InitgPty>
                <Nm>{zahlungslauf.auftraggeber_name}</Nm>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>{zahlungslauf.lauf_nummer}-001</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <NbOfTxs>{len(zahlungslauf.zahlungen)}</NbOfTxs>
            <CtrlSum>{zahlungslauf.gesamt_betrag}</CtrlSum>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>SEPA</Cd>
                </SvcLvl>
            </PmtTpInf>
            <ReqdExctnDt>{zahlungslauf.ausfuehrungs_datum}</ReqdExctnDt>
            <Dbtr>
                <Nm>{zahlungslauf.auftraggeber_name}</Nm>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <IBAN>{zahlungslauf.auftraggeber_iban}</IBAN>
                </Id>
            </DbtrAcct>
            <DbtrAgt>
                <FinInstnId>
                    <BIC>{zahlungslauf.auftraggeber_bic}</BIC>
                </FinInstnId>
            </DbtrAgt>
            <!-- Zahlungen würden hier eingefügt -->
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""

    return {
        "zahlungslauf_id": zahlungslauf_id,
        "lauf_nummer": zahlungslauf.lauf_nummer,
        "anzahl_zahlungen": len(zahlungslauf.zahlungen),
        "gesamt_betrag": zahlungslauf.gesamt_betrag,
        "sepa_xml_preview": sepa_xml
    }


@router.get("/zahlungslauf-kreditoren/{zahlungslauf_id}/export")
async def export_zahlungslauf(
    zahlungslauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """SEPA Export für Zahlungslauf"""
    zahlungslauf = db.query(models.Zahlungslauf).filter(
        models.Zahlungslauf.id == zahlungslauf_id,
        models.Zahlungslauf.tenant_id == tenant_id
    ).first()

    if not zahlungslauf:
        raise HTTPException(status_code=404, detail="Zahlungslauf not found")

    # Mock SEPA XML Export
    sepa_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <!-- Vollständiges SEPA XML würde hier generiert -->
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>{zahlungslauf.lauf_nummer}</MsgId>
            <CreDtTm>{datetime.utcnow().isoformat()}</CreDtTm>
            <NbOfTxs>{len(zahlungslauf.zahlungen)}</NbOfTxs>
            <CtrlSum>{zahlungslauf.gesamt_betrag}</CtrlSum>
        </GrpHdr>
        <!-- Zahlungsdaten -->
    </CstmrCdtTrfInitn>
</Document>"""

    return {
        "zahlungslauf_id": zahlungslauf_id,
        "filename": f"SEPA_{zahlungslauf.lauf_nummer}.xml",
        "content": sepa_xml,
        "content_type": "application/xml"
    }


@router.post("/zahlungslauf-kreditoren/{zahlungslauf_id}/approve")
async def approve_zahlungslauf(
    zahlungslauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Zahlungslauf freigeben"""
    db_zahlungslauf = db.query(models.Zahlungslauf).filter(
        models.Zahlungslauf.id == zahlungslauf_id,
        models.Zahlungslauf.tenant_id == tenant_id
    ).first()

    if not db_zahlungslauf:
        raise HTTPException(status_code=404, detail="Zahlungslauf not found")

    if db_zahlungslauf.status != "entwurf":
        raise HTTPException(status_code=400, detail="Nur Entwürfe können freigegeben werden")

    db_zahlungslauf.status = "freigegeben"
    db_zahlungslauf.freigegeben_am = datetime.utcnow()
    # In real app: db_zahlungslauf.freigegeben_durch = current_user.id
    db_zahlungslauf.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_zahlungslauf)
    return {"success": True, "status": "freigegeben"}


@router.post("/zahlungslauf-kreditoren/{zahlungslauf_id}/execute")
async def execute_zahlungslauf(
    zahlungslauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Zahlungslauf ausführen"""
    db_zahlungslauf = db.query(models.Zahlungslauf).filter(
        models.Zahlungslauf.id == zahlungslauf_id,
        models.Zahlungslauf.tenant_id == tenant_id
    ).first()

    if not db_zahlungslauf:
        raise HTTPException(status_code=404, detail="Zahlungslauf not found")

    if db_zahlungslauf.status != "freigegeben":
        raise HTTPException(status_code=400, detail="Nur freigegebene Läufe können ausgeführt werden")

    db_zahlungslauf.status = "ausgefuehrt"
    db_zahlungslauf.ausgefuehrt_am = datetime.utcnow()
    db_zahlungslauf.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_zahlungslauf)
    return {"success": True, "status": "ausgefuehrt"}
