"""
VAT Tax Codes Admin API
CRUD operations with full audit trail
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import logging

from pydantic import BaseModel
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.finance.models import VatCode, VatCodeAudit, VatCodeCategory, DEFAULT_VAT_CODES
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/finance/vat-codes", tags=["finance", "vat-codes"])


def _get_user_id_from_request(request: Request | None) -> str | None:
    if request is None:
        return None
    uid = request.headers.get("X-User-ID")
    if uid:
        return uid
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            import base64 as _b64, json as _json
            payload = auth[7:].split(".")[1]
            payload += "=" * (4 - len(payload) % 4)
            return _json.loads(_b64.urlsafe_b64decode(payload)).get("sub")
        except Exception:
            pass
    return None


# ============= Schemas =============

class VatCodeCreate(BaseModel):
    id: str
    name: str
    name_long: Optional[str] = None
    category: VatCodeCategory
    rate: float
    skr03_account: Optional[str] = None
    skr04_account: Optional[str] = None
    legal_basis: Optional[str] = None
    legal_note: Optional[str] = None
    is_standard: bool = False
    is_reduced: bool = False
    is_zero: bool = False
    is_reverse_charge: bool = False
    is_agricultural: bool = False
    paragraph_24: bool = False
    valid_from: Optional[datetime] = None


class VatCodeUpdate(BaseModel):
    name: Optional[str] = None
    name_long: Optional[str] = None
    rate: Optional[float] = None
    skr03_account: Optional[str] = None
    skr04_account: Optional[str] = None
    legal_basis: Optional[str] = None
    legal_note: Optional[str] = None
    is_standard: Optional[bool] = None
    is_reduced: Optional[bool] = None
    is_zero: Optional[bool] = None
    is_reverse_charge: Optional[bool] = None
    is_agricultural: Optional[bool] = None
    paragraph_24: Optional[bool] = None
    is_active: Optional[bool] = None
    valid_to: Optional[datetime] = None


class VatCodeResponse(BaseModel):
    id: str
    name: str
    name_long: Optional[str]
    category: str
    rate: float
    skr03_account: Optional[str]
    skr04_account: Optional[str]
    legal_basis: Optional[str]
    legal_note: Optional[str]
    is_standard: bool
    is_reduced: bool
    is_zero: bool
    is_reverse_charge: bool
    is_agricultural: bool
    paragraph_24: bool
    is_active: bool
    valid_from: datetime
    valid_to: Optional[datetime]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class VatCodeAuditResponse(BaseModel):
    id: str
    vat_code_id: str
    action: str
    change_type: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    changed_by: str
    changed_at: datetime
    reason: Optional[str]
    legal_reference: Optional[str]


# ============= Helper Functions =============

def _create_audit_record(db: Session, vat_code_id: str, action: str, change_type: Optional[str],
                          old_value: any, new_value: any, changed_by: str, 
                          reason: Optional[str] = None, legal_reference: Optional[str] = None,
                          tenant_id: Optional[str] = None):
    """Create audit record for VAT code change"""
    audit = VatCodeAudit(
        id=uuid7(),
        vat_code_id=vat_code_id,
        action=action,
        change_type=change_type,
        old_value=json.dumps(old_value) if old_value is not None else None,
        new_value=json.dumps(new_value) if new_value is not None else None,
        changed_by=changed_by,
        reason=reason,
        legal_reference=legal_reference,
        tenant_id=tenant_id
    )
    db.add(audit)
    return audit


# ============= CRUD Endpoints =============

@router.get("", response_model=List[VatCodeResponse])
async def list_vat_codes(
    category: Optional[VatCodeCategory] = Query(None),
    is_active: Optional[bool] = Query(None),
    include_inactive: bool = Query(False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """List all VAT codes (admin)"""
    query = db.query(VatCode)
    
    # Tenant filtering (NULL = system-wide codes)
    query = query.filter((VatCode.tenant_id == tenant_id) | (VatCode.tenant_id == None))
    
    if category:
        query = query.filter(VatCode.category == category)
    
    if is_active is not None:
        query = query.filter(VatCode.is_active == is_active)
    elif not include_inactive:
        query = query.filter(VatCode.is_active == True)
    
    return query.order_by(VatCode.category, VatCode.rate).all()


@router.get("/{vat_code_id}", response_model=VatCodeResponse)
async def get_vat_code(
    vat_code_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get single VAT code"""
    code = db.query(VatCode).filter(
        VatCode.id == vat_code_id,
        ((VatCode.tenant_id == tenant_id) | (VatCode.tenant_id == None))
    ).first()
    
    if not code:
        raise HTTPException(status_code=404, detail=f"VAT code {vat_code_id} not found")
    
    return code


@router.post("", response_model=VatCodeResponse)
async def create_vat_code(
    data: VatCodeCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Create new VAT code (admin only)"""
    current_user = _get_user_id_from_request(request) or "system"
    # Check if exists
    existing = db.query(VatCode).filter(VatCode.id == data.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"VAT code {data.id} already exists")
    
    # Parse valid_from
    valid_from = data.valid_from or datetime.utcnow()
    
    vat_code = VatCode(
        id=data.id,
        name=data.name,
        name_long=data.name_long,
        category=data.category,
        rate=data.rate,
        skr03_account=data.skr03_account,
        skr04_account=data.skr04_account,
        legal_basis=data.legal_basis,
        legal_note=data.legal_note,
        is_standard=data.is_standard,
        is_reduced=data.is_reduced,
        is_zero=data.is_zero,
        is_reverse_charge=data.is_reverse_charge,
        is_agricultural=data.is_agricultural,
        paragraph_24=data.paragraph_24,
        valid_from=valid_from,
        is_active=True,
        tenant_id=tenant_id,
        created_by=current_user,
        updated_by=current_user
    )
    
    db.add(vat_code)
    
    # Create audit record
    _create_audit_record(
        db, data.id, "CREATE", None, None, 
        {"name": data.name, "rate": data.rate, "category": data.category.value},
        current_user, f"Created new VAT code {data.id}"
    )
    
    db.commit()
    db.refresh(vat_code)
    
    return vat_code


@router.patch("/{vat_code_id}", response_model=VatCodeResponse)
async def update_vat_code(
    vat_code_id: str,
    data: VatCodeUpdate,
    reason: Optional[str] = Query(None, description="Reason for change (e.g., 'Gesetzesänderung 2025')"),
    legal_reference: Optional[str] = Query(None, description="Legal reference (e.g., '§24 UStG neu ab 2025')"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Update VAT code (admin only) - creates audit trail"""
    current_user = _get_user_id_from_request(request) or "system"
    vat_code = db.query(VatCode).filter(
        VatCode.id == vat_code_id,
        ((VatCode.tenant_id == tenant_id) | (VatCode.tenant_id == None))
    ).first()
    
    if not vat_code:
        raise HTTPException(status_code=404, detail=f"VAT code {vat_code_id} not found")
    
    # Track changes
    changes = {}
    
    update_data = data.model_dump(exclude_unset=True)
    for field, new_value in update_data.items():
        old_value = getattr(vat_code, field)
        if old_value != new_value:
            changes[field] = {"old": old_value, "new": new_value}
            setattr(vat_code, field, new_value)
    
    if changes:
        vat_code.updated_by = current_user
        
        # Create audit records for each change
        for field, values in changes.items():
            _create_audit_record(
                db, vat_code_id, "UPDATE", field,
                values["old"], values["new"],
                current_user, reason, legal_reference
            )
    
    db.commit()
    db.refresh(vat_code)
    
    return vat_code


@router.delete("/{vat_code_id}")
async def delete_vat_code(
    vat_code_id: str,
    reason: Optional[str] = Query(None, description="Reason for deletion"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: str = "system"
):
    """Soft-delete VAT code (admin only) - sets is_active=False"""
    vat_code = db.query(VatCode).filter(
        VatCode.id == vat_code_id,
        ((VatCode.tenant_id == tenant_id) | (VatCode.tenant_id == None))
    ).first()
    
    if not vat_code:
        raise HTTPException(status_code=404, detail=f"VAT code {vat_code_id} not found")
    
    # Soft delete
    old_value = vat_code.is_active
    vat_code.is_active = False
    vat_code.updated_by = current_user
    
    # Audit
    _create_audit_record(
        db, vat_code_id, "DELETE", "is_active",
        old_value, False,
        current_user, reason, "Soft delete"
    )
    
    db.commit()
    
    return {"ok": True, "message": f"VAT code {vat_code_id} deactivated"}


@router.get("/{vat_code_id}/audit", response_model=List[VatCodeAuditResponse])
async def get_vat_code_audit(
    vat_code_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get audit trail for VAT code (who changed what when)"""
    # Verify access
    vat_code = db.query(VatCode).filter(
        VatCode.id == vat_code_id,
        ((VatCode.tenant_id == tenant_id) | (VatCode.tenant_id == None))
    ).first()
    
    if not vat_code:
        raise HTTPException(status_code=404, detail=f"VAT code {vat_code_id} not found")
    
    return db.query(VatCodeAudit).filter(
        VatCodeAudit.vat_code_id == vat_code_id
    ).order_by(VatCodeAudit.changed_at.desc()).all()


@router.post("/seed-defaults")
async def seed_default_vat_codes(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: str = "system"
):
    """Seed default German VAT codes (one-time admin action)"""
    seeded = []
    skipped = []
    
    for code_data in DEFAULT_VAT_CODES:
        code_id = code_data["id"]
        
        # Check if exists
        existing = db.query(VatCode).filter(VatCode.id == code_id).first()
        if existing:
            skipped.append(code_id)
            continue
        
        vat_code = VatCode(
            id=code_id,
            name=code_data["name"],
            name_long=code_data.get("name_long"),
            category=code_data["category"],
            rate=code_data["rate"],
            skr03_account=code_data.get("skr03_account"),
            skr04_account=code_data.get("skr04_account"),
            legal_basis=code_data.get("legal_basis"),
            is_standard=code_data.get("is_standard", False),
            is_reduced=code_data.get("is_reduced", False),
            is_zero=code_data.get("is_zero", False),
            is_reverse_charge=code_data.get("is_reverse_charge", False),
            is_agricultural=code_data.get("is_agricultural", False),
            paragraph_24=code_data.get("paragraph_24", False),
            is_active=True,
            valid_from=datetime.utcnow(),
            tenant_id=None,  # System-wide
            created_by=current_user,
            updated_by=current_user
        )
        
        db.add(vat_code)
        seeded.append(code_id)
        
        # Audit
        _create_audit_record(
            db, code_id, "CREATE", None, None,
            {"name": code_data["name"], "rate": code_data["rate"]},
            current_user, "Initial seed of default VAT codes"
        )
    
    db.commit()
    
    return {
        "ok": True,
        "seeded": seeded,
        "skipped": skipped,
        "message": f"Seeded {len(seeded)} VAT codes, {len(skipped)} already existed"
    }
