"""
Tax Keys API
FIBU-TAX-01: Steuerschlüssel-System vervollständigen
"""

from typing import List, Optional
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
import logging

from ....core.database import get_db
from app.core.read_model_cache import cached_read_model, invalidate_tenant_prefix
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.tax_keys_schemas import (
    TaxKeyCreate,
    TaxKeyResponse,
    TaxKeyUpdate,
)


router = APIRouter(prefix="/tax-keys", tags=["finance", "tax"])

@router.get("", response_model=List[TaxKeyResponse], summary="Tax keys auflisten")
@cached_read_model("tax_keys", ttl=3600)
async def list_tax_keys(
    tenant_id: str = Depends(get_tenant_id),
    active_only: bool = Query(True, description="Show only active tax keys"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    db: Session = Depends(get_db)
):
    """
    List all tax keys.
    """
    try:
        where_clauses = ["tenant_id = :tenant_id"]
        params = {"tenant_id": tenant_id}

        if active_only:
            where_clauses.append("active = true")
        if country:
            where_clauses.append("country = :country")
            params["country"] = country.strip().upper()

        query = text(
            f"""
            SELECT id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                   intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                   debit_account, credit_account, country, region, active,
                   created_at, updated_at
            FROM domain_erp.tax_keys
            WHERE {' AND '.join(where_clauses)}
            ORDER BY code
            """
        )
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            result.append(TaxKeyResponse(
                id=str(row[0]),
                code=str(row[1]),
                bezeichnung=str(row[2]),
                steuersatz=Decimal(str(row[3])),
                ustva_position=str(row[4]),
                ustva_bezeichnung=str(row[5]),
                intracom=bool(row[6]),
                export=bool(row[7]),
                reverse_charge=bool(row[8]),
                gueltig_von=row[9],
                gueltig_bis=row[10],
                notizen=str(row[11]) if row[11] else None,
                debit_account=str(row[12]) if row[12] else None,
                credit_account=str(row[13]) if row[13] else None,
                country=str(row[14]),
                region=str(row[15]) if row[15] else None,
                active=bool(row[16]),
                created_at=row[17],
                updated_at=row[18]
            ))
        
        return result
        
    except Exception as e:
        logger.error("Error listing tax keys: %s", e, exc_info=True)
        return []


@router.get("/{tax_key_id}", response_model=TaxKeyResponse, summary="Tax key abrufen")
async def get_tax_key(
    tax_key_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get a single tax key by ID.
    """
    try:
        query = text("""
            SELECT id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                   intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                   debit_account, credit_account, country, region, active,
                   created_at, updated_at
            FROM domain_erp.tax_keys
            WHERE id = :tax_key_id AND tenant_id = :tenant_id
        """)
        
        row = db.execute(query, {
            "tax_key_id": tax_key_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Tax key not found")
        
        return TaxKeyResponse(
            id=str(row[0]),
            code=str(row[1]),
            bezeichnung=str(row[2]),
            steuersatz=Decimal(str(row[3])),
            ustva_position=str(row[4]),
            ustva_bezeichnung=str(row[5]),
            intracom=bool(row[6]),
            export=bool(row[7]),
            reverse_charge=bool(row[8]),
            gueltig_von=row[9],
            gueltig_bis=row[10],
            notizen=str(row[11]) if row[11] else None,
            debit_account=str(row[12]) if row[12] else None,
            credit_account=str(row[13]) if row[13] else None,
            country=str(row[14]),
            region=str(row[15]) if row[15] else None,
            active=bool(row[16]),
            created_at=row[17],
            updated_at=row[18]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tax key: {str(e)}")


@router.post("", response_model=TaxKeyResponse, status_code=201, summary="Tax key anlegen")
async def create_tax_key(
    tax_key: TaxKeyCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Create a new tax key.
    """
    try:
        # Check if code already exists
        check_query = text("""
            SELECT id FROM domain_erp.tax_keys
            WHERE code = :code AND tenant_id = :tenant_id
        """)
        
        existing = db.execute(check_query, {
            "code": tax_key.code,
            "tenant_id": tenant_id
        }).fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Tax key with code {tax_key.code} already exists")
        
        # Insert new tax key
        tax_key_id = uuid7()
        
        insert_query = text("""
            INSERT INTO domain_erp.tax_keys
            (id, tenant_id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
             intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
             debit_account, credit_account, country, region, active, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :code, :bezeichnung, :steuersatz, :ustva_position, :ustva_bezeichnung,
             :intracom, :export, :reverse_charge, :gueltig_von, :gueltig_bis, :notizen,
             :debit_account, :credit_account, :country, :region, :active, NOW(), NOW())
            RETURNING id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                      intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                      debit_account, credit_account, country, region, active,
                      created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": tax_key_id,
            "tenant_id": tenant_id,
            "code": tax_key.code,
            "bezeichnung": tax_key.bezeichnung,
            "steuersatz": tax_key.steuersatz,
            "ustva_position": tax_key.ustva_position,
            "ustva_bezeichnung": tax_key.ustva_bezeichnung,
            "intracom": tax_key.intracom,
            "export": tax_key.export,
            "reverse_charge": tax_key.reverse_charge,
            "gueltig_von": tax_key.gueltig_von,
            "gueltig_bis": tax_key.gueltig_bis,
            "notizen": tax_key.notizen,
            "debit_account": tax_key.debit_account,
            "credit_account": tax_key.credit_account,
            "country": tax_key.country,
            "region": tax_key.region,
            "active": tax_key.active
        }).fetchone()
        
        db.commit()
        
        return TaxKeyResponse(
            id=str(row[0]),
            code=str(row[1]),
            bezeichnung=str(row[2]),
            steuersatz=Decimal(str(row[3])),
            ustva_position=str(row[4]),
            ustva_bezeichnung=str(row[5]),
            intracom=bool(row[6]),
            export=bool(row[7]),
            reverse_charge=bool(row[8]),
            gueltig_von=row[9],
            gueltig_bis=row[10],
            notizen=str(row[11]) if row[11] else None,
            debit_account=str(row[12]) if row[12] else None,
            credit_account=str(row[13]) if row[13] else None,
            country=str(row[14]),
            region=str(row[15]) if row[15] else None,
            active=bool(row[16]),
            created_at=row[17],
            updated_at=row[18]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating tax key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create tax key: {str(e)}")


@router.put("/{tax_key_id}", response_model=TaxKeyResponse, summary="Tax key aktualisieren")
async def update_tax_key(
    tax_key_id: str,
    tax_key: TaxKeyUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Update an existing tax key.
    """
    try:
        current_row = db.execute(
            text(
                """
                SELECT steuersatz, reverse_charge, gueltig_von
                FROM domain_erp.tax_keys
                WHERE id = :tax_key_id AND tenant_id = :tenant_id
                """
            ),
            {"tax_key_id": tax_key_id, "tenant_id": tenant_id},
        ).fetchone()
        if not current_row:
            raise HTTPException(status_code=404, detail="Tax key not found")

        effective_rate = Decimal(str(tax_key.steuersatz if tax_key.steuersatz is not None else current_row[0]))
        effective_reverse = bool(tax_key.reverse_charge if tax_key.reverse_charge is not None else current_row[1])
        effective_from = tax_key.gueltig_von if tax_key.gueltig_von is not None else current_row[2]
        effective_until = tax_key.gueltig_bis

        if effective_reverse and effective_rate != Decimal("0"):
            raise HTTPException(status_code=422, detail="reverse_charge requires steuersatz = 0")
        if effective_until is not None and effective_from is not None and effective_until < effective_from:
            raise HTTPException(status_code=422, detail="gueltig_bis must be >= gueltig_von")

        # Build update query dynamically
        update_fields = []
        params = {"tax_key_id": tax_key_id, "tenant_id": tenant_id}
        
        if tax_key.bezeichnung is not None:
            update_fields.append("bezeichnung = :bezeichnung")
            params["bezeichnung"] = tax_key.bezeichnung
        if tax_key.steuersatz is not None:
            update_fields.append("steuersatz = :steuersatz")
            params["steuersatz"] = tax_key.steuersatz
        if tax_key.ustva_position is not None:
            update_fields.append("ustva_position = :ustva_position")
            params["ustva_position"] = tax_key.ustva_position
        if tax_key.ustva_bezeichnung is not None:
            update_fields.append("ustva_bezeichnung = :ustva_bezeichnung")
            params["ustva_bezeichnung"] = tax_key.ustva_bezeichnung
        if tax_key.intracom is not None:
            update_fields.append("intracom = :intracom")
            params["intracom"] = tax_key.intracom
        if tax_key.export is not None:
            update_fields.append("export = :export")
            params["export"] = tax_key.export
        if tax_key.reverse_charge is not None:
            update_fields.append("reverse_charge = :reverse_charge")
            params["reverse_charge"] = tax_key.reverse_charge
        if tax_key.gueltig_von is not None:
            update_fields.append("gueltig_von = :gueltig_von")
            params["gueltig_von"] = tax_key.gueltig_von
        if tax_key.gueltig_bis is not None:
            update_fields.append("gueltig_bis = :gueltig_bis")
            params["gueltig_bis"] = tax_key.gueltig_bis
        if tax_key.notizen is not None:
            update_fields.append("notizen = :notizen")
            params["notizen"] = tax_key.notizen
        if tax_key.debit_account is not None:
            update_fields.append("debit_account = :debit_account")
            params["debit_account"] = tax_key.debit_account
        if tax_key.credit_account is not None:
            update_fields.append("credit_account = :credit_account")
            params["credit_account"] = tax_key.credit_account
        if tax_key.country is not None:
            update_fields.append("country = :country")
            params["country"] = tax_key.country
        if tax_key.region is not None:
            update_fields.append("region = :region")
            params["region"] = tax_key.region
        if tax_key.active is not None:
            update_fields.append("active = :active")
            params["active"] = tax_key.active
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = NOW()")
        
        # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        update_query = text(f"""
            UPDATE domain_erp.tax_keys
            SET {', '.join(update_fields)}
            WHERE id = :tax_key_id AND tenant_id = :tenant_id
            RETURNING id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                      intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                      debit_account, credit_account, country, region, active,
                      created_at, updated_at
        """)
        
        row = db.execute(update_query, params).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Tax key not found")
        
        db.commit()
        
        return TaxKeyResponse(
            id=str(row[0]),
            code=str(row[1]),
            bezeichnung=str(row[2]),
            steuersatz=Decimal(str(row[3])),
            ustva_position=str(row[4]),
            ustva_bezeichnung=str(row[5]),
            intracom=bool(row[6]),
            export=bool(row[7]),
            reverse_charge=bool(row[8]),
            gueltig_von=row[9],
            gueltig_bis=row[10],
            notizen=str(row[11]) if row[11] else None,
            debit_account=str(row[12]) if row[12] else None,
            credit_account=str(row[13]) if row[13] else None,
            country=str(row[14]),
            region=str(row[15]) if row[15] else None,
            active=bool(row[16]),
            created_at=row[17],
            updated_at=row[18]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating tax key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update tax key: {str(e)}")


@router.delete("/{tax_key_id}", status_code=204, response_class=Response, response_model=None, summary="Tax key löschen")
async def delete_tax_key(
    tax_key_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Delete a tax key (soft delete by setting active=false).
    """
    try:
        update_query = text("""
            UPDATE domain_erp.tax_keys
            SET active = false, updated_at = NOW()
            WHERE id = :tax_key_id AND tenant_id = :tenant_id
        """)
        
        result = db.execute(update_query, {
            "tax_key_id": tax_key_id,
            "tenant_id": tenant_id
        })
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tax key not found")
        
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting tax key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete tax key: {str(e)}")


@router.get("/code/{code}", response_model=TaxKeyResponse, summary="Tax key by code abrufen")
async def get_tax_key_by_code(
    code: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get tax key by code.
    """
    try:
        query = text("""
            SELECT id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                   intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                   debit_account, credit_account, country, region, active,
                   created_at, updated_at
            FROM domain_erp.tax_keys
            WHERE code = :code AND tenant_id = :tenant_id AND active = true
            ORDER BY gueltig_von DESC
            LIMIT 1
        """)
        
        row = db.execute(query, {
            "code": code,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Tax key with code {code} not found")
        
        return TaxKeyResponse(
            id=str(row[0]),
            code=str(row[1]),
            bezeichnung=str(row[2]),
            steuersatz=Decimal(str(row[3])),
            ustva_position=str(row[4]),
            ustva_bezeichnung=str(row[5]),
            intracom=bool(row[6]),
            export=bool(row[7]),
            reverse_charge=bool(row[8]),
            gueltig_von=row[9],
            gueltig_bis=row[10],
            notizen=str(row[11]) if row[11] else None,
            debit_account=str(row[12]) if row[12] else None,
            credit_account=str(row[13]) if row[13] else None,
            country=str(row[14]),
            region=str(row[15]) if row[15] else None,
            active=bool(row[16]),
            created_at=row[17],
            updated_at=row[18]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax key by code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tax key: {str(e)}")

