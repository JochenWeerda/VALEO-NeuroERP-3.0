"""
Chart of Accounts management endpoints
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field

from ....core.config import settings
from ....core.database import get_db
from ....core.fibu_audit import log_fibu_audit
from ....core.tenant import get_tenant_id
from ....infrastructure.models import Account as AccountModel
from ....finance.export_datev import DATEVExporter
from ..schemas.base import PaginatedResponse
from ..schemas.finance import Account, AccountCreate, AccountUpdate

from app.api.v1.schemas.base import BaseSchema, StatusResponse
from app.api.v1.schemas.chart_of_accounts_schemas import ChartOfAccountsOut


from app.auth.finance_roles import (
    KONTENRAHMEN_PFLEGE,
    finance_read,
    kontenpflege,
    kontenplan_read,
)

router = APIRouter(prefix="/chart-of-accounts")

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID

VALID_ACCOUNT_TYPES = {"asset", "liability", "equity", "revenue", "expense"}


class ValidateResponse(BaseModel):
    """Response for chart of accounts validation"""
    valid: bool
    errors: List[str] = Field(default_factory=list)


#: Unter dieser Kennung liegt der gemeinsame Kontenrahmen (SKR03-Saat).
SHARED_TENANT = "system"


def _spalten(werte: dict) -> dict:
    """Nur, was die Tabelle auch speichert."""
    return {k: v for k, v in werte.items() if k in AccountModel.__table__.columns}


def _konto(db: Session, account_id: str, tenant_id: str) -> AccountModel:
    """Das Konto des Mandanten oder des gemeinsamen Rahmens — ein fremdes gibt es nicht (404).

    Bis zum 12.10.2026 wurde nur nach der Kennung gesucht: Lesen, aendern und loeschen
    trafen auch das Konto eines anderen Mandanten.
    """
    account = (
        db.query(AccountModel)
        .filter(
            AccountModel.id == account_id,
            (AccountModel.tenant_id == tenant_id) | (AccountModel.tenant_id == SHARED_TENANT),
        )
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


def _bebucht(db: Session, account_id: str) -> bool:
    """Ob gegen das Konto schon gebucht wurde (auch als Entwurf)."""
    return db.execute(
        text("SELECT 1 FROM domain_erp.journal_entry_lines WHERE account_id = :id LIMIT 1"),
        {"id": account_id},
    ).first() is not None


def _pflegbar(account: AccountModel, nutzer: dict) -> None:
    """Ein Konto des gemeinsamen Rahmens pflegt nur, wer das Recht dazu hat.

    Sehen darf es jeder Mandant. Bis zum 12.10.2026 durfte es auch jeder mit Schreibrolle
    aendern und deaktivieren — fuer alle Mandanten zugleich.
    """
    if account.tenant_id != SHARED_TENANT:
        return
    if KONTENRAHMEN_PFLEGE.isdisjoint(nutzer.get("roles") or []):
        raise HTTPException(
            status_code=403,
            detail=(
                "Dieses Konto gehoert zum gemeinsamen Kontenrahmen. Aendern und deaktivieren darf es nur, "
                "wer das Recht KONTENRAHMEN_PFLEGE hat."
            ),
        )


@router.get("/", response_model=PaginatedResponse[Account], summary="Accounts auflisten", dependencies=[Depends(kontenplan_read)])
async def list_accounts(
    tenant_id: str = Depends(get_tenant_id),
    search: Optional[str] = Query(None, description="Search in account number or name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Kontenplan: die eigenen Konten und die gemeinsamen.

    Gefiltert wurde streng nach Mandant — und damit war der gemeinsame
    Kontenrahmen unsichtbar. Der Kontenplan zeigte einen einzigen Eintrag,
    waehrend gegen achtundzwanzig Konten gebucht wurde.

    Das passte auch nicht zusammen: ``FinanceTransactionService`` sucht das
    Buchungskonto ohne Mandantenfilter, behandelt den Rahmen also als
    gemeinsam. Wer ihn pflegen soll, muss ihn auch sehen. Die Herkunft bleibt
    am Eintrag (``tenant_id``) erkennbar: ``system`` ist gemeinsam, alles
    andere gehoert dem Mandanten.

    Der Mandant kommt aus dem Mandantenkontext. Bis zum 12.10.2026 kam er aus dem
    Query-Parameter ``tenant_id`` — wer lesen durfte, las damit jeden Mandanten.
    """
    effective_tenant = tenant_id

    query = db.query(AccountModel).filter(AccountModel.is_active == True)  # noqa: E712
    query = query.filter(
        (AccountModel.tenant_id == effective_tenant)
        | (AccountModel.tenant_id == SHARED_TENANT)
    )

    if search:
        like = f"%{search}%"
        query = query.filter(
            (AccountModel.account_number.ilike(like)) | (AccountModel.account_name.ilike(like))
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse[Account](
        items=[Account.model_validate(item) for item in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{account_id}", response_model=Account, summary="Account abrufen", dependencies=[Depends(kontenplan_read)])
async def get_account(
    account_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Fetch a single account by identifier."""
    account = _konto(db, account_id, tenant_id)
    return Account.model_validate(account)


@router.post("/", response_model=Account, summary="Account anlegen", dependencies=[Depends(kontenpflege)])
async def create_account(
    account: AccountCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a new account.

    Das Konto gehoert dem Mandanten der Anmeldung. Das Feld ``tenant_id`` im Rumpf
    entscheidet nichts mehr; bis zum 12.10.2026 legte es das Konto bei jedem Mandanten an.
    """
    # Check if account number already exists
    existing = db.query(AccountModel).filter(
        AccountModel.account_number == account.account_number,
        AccountModel.tenant_id == tenant_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account number already exists")

    # ``currency`` und ``allow_manual_entries`` stehen im Schema, aber nicht in der Tabelle: Bis zum
    # 12.10.2026 scheiterte jedes Anlegen daran mit 500.
    db_account = AccountModel(**{**_spalten(account.model_dump()), "tenant_id": tenant_id})
    db.add(db_account)
    db.flush()
    db.refresh(db_account)
    log_fibu_audit(
        db, tenant_id, "create", "finance_account", db_account.id,
        {"account_number": account.account_number, "account_name": account.account_name},
        request=request,
    )
    return Account.model_validate(db_account)


@router.put("/{account_id}", response_model=Account, summary="Account aktualisieren", dependencies=[Depends(kontenpflege)])
async def update_account(
    account_id: str,
    account_update: AccountUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(kontenpflege),
    db: Session = Depends(get_db),
):
    """Update an existing account."""
    account = _konto(db, account_id, tenant_id)
    _pflegbar(account, nutzer)

    # Die Kontenart eines bebuchten Kontos bleibt: Sie entscheidet, ob das Konto in Bilanz oder GuV steht —
    # ein Wechsel wuerde abgeschlossene Auswertungen nachtraeglich verschieben.
    neue_art = account_update.account_type
    if neue_art is not None and neue_art != account.account_type and _bebucht(db, account_id):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Konto {account.account_number} ist bebucht. Die Kontenart laesst sich nicht mehr aendern; "
                "Bezeichnung und Kategorie schon."
            ),
        )

    # Geaendert wurde nur, wenn auch der Name im Rumpf stand — sonst meldete der Weg Erfolg ohne Wirkung.
    for field, value in _spalten(account_update.model_dump(exclude_unset=True)).items():
        setattr(account, field, value)

    db.flush()
    db.refresh(account)
    log_fibu_audit(
        db, tenant_id, "update", "finance_account", account_id,
        {"updated_fields": list(account_update.model_dump(exclude_unset=True).keys())},
        request=request,
    )
    return Account.model_validate(account)


@router.delete("/{account_id}", summary="Account löschen",
    response_model=StatusResponse, dependencies=[Depends(kontenpflege)])
async def delete_account(
    account_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(kontenpflege),
    db: Session = Depends(get_db),
):
    """Delete an account (soft delete by setting is_active to False)."""
    account = _konto(db, account_id, tenant_id)
    _pflegbar(account, nutzer)

    # Die Pruefung fragte eine Beziehung ab, die das Modell nicht hat — sie griff nie. Ein bebuchtes Konto
    # verschwaende mit dem Deaktivieren aus dem Kontenplan, seine Buchungen blieben ohne sichtbares Konto.
    if _bebucht(db, account_id):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Konto {account.account_number} ist bebucht und laesst sich nicht deaktivieren. "
                "Soll es nicht mehr bebucht werden, das Konto sperren."
            ),
        )

    account.is_active = False
    db.flush()
    log_fibu_audit(
        db, tenant_id, "delete", "finance_account", account_id,
        {"is_active": False, "account_number": account.account_number},
        request=request,
    )
    # Ohne ``success`` scheiterte die Antwort am Antwortschema: Das Konto war deaktiviert, der Aufrufer sah 500.
    return StatusResponse(success=True, message="Account deactivated successfully")


@router.post("/validate", response_model=ValidateResponse, summary="Chart of accounts validieren", dependencies=[Depends(finance_read)])
async def validate_chart_of_accounts(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Validate the chart of accounts (duplicate account numbers, valid account types).
    """
    effective_tenant = tenant_id
    errors: List[str] = []

    accounts = (
        db.query(AccountModel)
        .filter(AccountModel.tenant_id == effective_tenant, AccountModel.is_active == True)
        .all()
    )

    seen_numbers: set = set()
    for acc in accounts:
        if acc.account_number in seen_numbers:
            errors.append(f"Doppelte Kontonummer: {acc.account_number}")
        seen_numbers.add(acc.account_number)

        if acc.account_type not in VALID_ACCOUNT_TYPES:
            errors.append(
                f"Ungültige Kontenart '{acc.account_type}' für Konto {acc.account_number}. "
                f"Erlaubt: {', '.join(VALID_ACCOUNT_TYPES)}"
            )

    return ValidateResponse(valid=len(errors) == 0, errors=errors)


@router.post("/datev-export", summary="Export chart of accounts datev",
    response_model=ChartOfAccountsOut, dependencies=[Depends(finance_read)])
async def datev_export_chart_of_accounts(
    von_datum: str = Query(..., description="Start date YYYY-MM-DD"),
    bis_datum: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Export bookings (journal entries) in DATEV format for the given date range.
    Returns DATEV CSV as downloadable file.
    """
    effective_tenant = tenant_id
    bis = bis_datum or von_datum

    # domain_erp.journal_entries / journal_entry_lines (debit, credit; chart_of_accounts)
    q = text("""
        SELECT jel.journal_entry_id, jel.account_id, jel.debit, jel.credit,
               jel.description, CAST(NULL AS VARCHAR) AS tax_code, je.entry_date, je.reference,
               coa.account_number
        FROM domain_erp.journal_entry_lines jel
        JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
        LEFT JOIN domain_erp.chart_of_accounts coa ON coa.id = jel.account_id
        WHERE je.tenant_id = :tenant_id
          AND je.status = 'posted'
          AND DATE(je.entry_date) >= :von_datum
          AND DATE(je.entry_date) <= :bis_datum
        ORDER BY je.entry_date, jel.journal_entry_id, jel.line_number
    """)
    rows = db.execute(
        q,
        {
            "tenant_id": effective_tenant,
            "von_datum": von_datum,
            "bis_datum": bis,
        },
    ).fetchall()

    # Build list of lines per entry for Gegenkonto
    from collections import defaultdict
    entry_lines = defaultdict(list)
    for r in rows:
        entry_lines[r[0]].append(
            {
                "account_number": (r[8] or "").strip() or str(r[1]),
                "debit": float(r[2] or 0),
                "credit": float(r[3] or 0),
                "description": (r[4] or "")[:60],
                "tax_code": (r[5] or "")[:4],
                "entry_date": r[6],
                "reference": (r[7] or "")[:36],
            }
        )

    buchungen: List[dict] = []
    for _je_id, lines in entry_lines.items():
        for i, line in enumerate(lines):
            amount = line["debit"] or line["credit"]
            if amount <= 0:
                continue
            other = next(
                (ll for j, ll in enumerate(lines) if j != i),
                lines[0] if len(lines) > 1 else line,
            )
            soll_konto = line["account_number"] if line["debit"] else other["account_number"]
            haben_konto = line["account_number"] if line["credit"] else other["account_number"]
            buchungen.append({
                "betrag": amount if line["debit"] else -amount,
                "soll_konto": soll_konto,
                "haben_konto": haben_konto,
                "buchungsdatum": line["entry_date"],
                "belegnummer": line["reference"],
                "buchungstext": line["description"],
                "steuerschluessel": line["tax_code"] or "",
            })

    von_ddmm = datetime.strptime(von_datum, "%Y-%m-%d").strftime("%d%m%Y")
    bis_ddmm = datetime.strptime(bis, "%Y-%m-%d").strftime("%d%m%Y")
    exporter = DATEVExporter(mandant_nr="1000", berater_nr="1000", wj_beginn="0101")
    csv_content = exporter.export_buchungen(buchungen, von_ddmm, bis_ddmm)

    return Response(
        content=csv_content.encode("windows-1252"),
        media_type="text/csv; charset=windows-1252",
        headers={
            "Content-Disposition": f'attachment; filename="DATEV_Export_{von_datum}_{bis}.csv"',
        },
    )

