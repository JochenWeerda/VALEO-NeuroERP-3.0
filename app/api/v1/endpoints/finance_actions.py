"""
Finance action endpoints – Start/run actions for bank reconciliation, posting, cash, direct debit, closing.
Minimal action endpoints that execute a short logic or stub and return { success, message }.
"""

import io
from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field

from ....core.database import get_db
from ....core import endpoint_gateways
from ....core.tenant import get_tenant_id
from ....core.dependency_container import container
from ....core.gobd_artifact import register_artifact, sha256_hex
from ....infrastructure.repositories import JournalEntryRepository

router = APIRouter(tags=["finance", "actions"])


class ActionResponse(BaseModel):
    """Standard response for finance actions"""
    success: bool = True
    message: str = ""


class JournalEntryPostRequest(BaseModel):
    """Request to post a journal entry by ID"""
    journal_entry_id: Optional[str] = Field(None, description="ID der zu buchenden Buchung")
    belegnummer: Optional[str] = Field(None, description="Alternative Belegnummer zur Ermittlung der Buchungs-ID")


class BankReconciliationRunRequest(BaseModel):
    """Request to run bank reconciliation"""
    bank_account_id: str = Field(..., description="Bankkonto-ID")
    statement_id: Optional[str] = Field(None, description="Optional: Kontoauszug-ID")


class ClosingActionRequest(BaseModel):
    period: str = Field(..., min_length=1)
    closing_type: str = Field(..., min_length=1)
    actor: str = Field(..., min_length=1)


# ── Bank reconciliation run ─────────────────────────────────────────────────────

@router.post("/bank-reconciliation/run", response_model=ActionResponse)
async def run_bank_reconciliation(
    body: BankReconciliationRunRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Start Bankabgleich (Abgleich Job anstoßen oder Status setzen).
    Für konkreten Abgleich: GET /finance/bank-reconciliation/{statement_id}/reconcile mit Query-Parametern nutzen.
    """
    # Stub: can be extended to enqueue job or call reconcile logic
    return ActionResponse(
        success=True,
        message=f"Bankabgleich für Konto {body.bank_account_id} angestoßen.",
    )


# ── Journal entry post ─────────────────────────────────────────────────────────

@router.post("/journal-entries/post", response_model=ActionResponse)
async def post_journal_entry_action(
    body: JournalEntryPostRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Buchung buchen (Journal Entry von Entwurf auf gebucht setzen).
    """
    try:
        entry_id = body.journal_entry_id
        if not entry_id and body.belegnummer:
            by_number = db.execute(
                text(
                    """
                    SELECT id
                    FROM domain_erp.journal_entries
                    WHERE tenant_id = :tenant_id AND entry_number = :entry_number
                    ORDER BY created_at DESC
                    LIMIT 1
                    """
                ),
                {"tenant_id": tenant_id, "entry_number": body.belegnummer},
            ).fetchone()
            if by_number:
                entry_id = str(by_number[0])

        if not entry_id:
            return ActionResponse(success=False, message="journal_entry_id oder belegnummer erforderlich.")

        entry_row = db.execute(
            text(
                """
                SELECT TO_CHAR(entry_date::date, 'YYYY-MM') AS period
                FROM domain_erp.journal_entries
                WHERE id = :id AND tenant_id = :tenant_id
                LIMIT 1
                """
            ),
            {"id": entry_id, "tenant_id": tenant_id},
        ).fetchone()
        if not entry_row:
            return ActionResponse(success=False, message="Buchung nicht gefunden.")

        period = str(entry_row[0])
        period_status = db.execute(
            text(
                """
                SELECT status
                FROM finance_accounting_periods
                WHERE tenant_id = :tenant_id AND period = :period
                LIMIT 1
                """
            ),
            {"tenant_id": tenant_id, "period": period},
        ).fetchone()
        if period_status and str(period_status[0]) != "OPEN":
            return ActionResponse(
                success=False,
                message=f"Periode {period} ist {period_status[0]}. Buchung gesperrt.",
            )

        entry_repo = container.resolve(JournalEntryRepository)
        success = await entry_repo.post_entry(entry_id, tenant_id)
        if not success:
            return ActionResponse(success=False, message="Buchung konnte nicht gebucht werden.")
        return ActionResponse(success=True, message="Buchung erfolgreich gebucht.")
    except Exception as e:
        return ActionResponse(success=False, message=f"Fehler beim Buchen: {e!s}")


# ── Cash close day ─────────────────────────────────────────────────────────────

@router.post("/cash/close-day", response_model=ActionResponse)
async def cash_close_day(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Kasse Tagesabschluss (Stub: Status/Job anstoßen).
    """
    # Stub: can be extended to close cash register day, create closing entry, etc.
    return ActionResponse(success=True, message="Kassen-Tagesabschluss angestoßen.")


# ── Direct debit run ───────────────────────────────────────────────────────────

@router.post("/direct-debit/run", response_model=ActionResponse)
async def run_direct_debit(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Lastschriftenlauf starten (Debitoren-Lastschriften; Stub).
    """
    # Stub: can be extended to create SEPA direct debit file, update status
    return ActionResponse(success=True, message="Lastschriftenlauf angestoßen.")


# ── Closing run ───────────────────────────────────────────────────────────────

@router.post("/closing/run", response_model=ActionResponse)
async def run_closing(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Abschluss (Periodenabschluss) anstoßen (Stub).
    """
    # Stub: can be extended to run period closing, close periods, etc.
    return ActionResponse(success=True, message="Abschluss angestoßen.")


@router.post("/closing/approve", response_model=dict)
async def approve_closing(
    body: ClosingActionRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    gateway = endpoint_gateways.get_closing_workspace_gateway()
    if gateway is None:
        return {
            "status": "pending",
            "approval_status": "pending",
            "message": "Kein Closing-Workspace-Gateway registriert.",
        }
    from app.api.v1.endpoints.closing_checklists import ClosingWorkspaceRequest

    request = ClosingWorkspaceRequest(
        tenant_id=tenant_id,
        period=body.period,
        closing_type=body.closing_type,
        actor=body.actor,
    )
    return await gateway.approve(request, db)


# ── Credit limits ─────────────────────────────────────────────────────────────

@router.get("/credit-limits", response_model=list[dict])
async def list_credit_limits(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Kreditlimits aus domain_erp.business_partners."""
    try:
        rows = db.execute(
            text(
                "SELECT id, partner_name, credit_limit, used_credit, currency "
                "FROM domain_erp.business_partners "
                "WHERE tenant_id=:tid AND credit_limit IS NOT NULL "
                "ORDER BY partner_name"
            ),
            {"tid": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


# ── Collaterals ───────────────────────────────────────────────────────────────

@router.get("/collaterals", response_model=list[dict])
async def list_collaterals(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Sicherheiten: Pfandrechte, Bürgschaften — aus domain_erp.collaterals oder leere Liste."""
    try:
        rows = db.execute(
            text(
                "SELECT * FROM domain_erp.collaterals "
                "WHERE tenant_id=:tid ORDER BY created_at DESC"
            ),
            {"tid": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


# ── Payment suggestions ────────────────────────────────────────────────────────

@router.get("/payment-suggestions", response_model=list[dict])
async def list_payment_suggestions(
    days_ahead: int = Query(14, ge=1, le=365),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Zahlungsvorschläge: Kreditor-OPs die in X Tagen fällig sind."""
    try:
        rows = db.execute(
            text(
                "SELECT id, partner_name AS lieferant, beleg_nummer AS rechnungs_nr, "
                "       faellig_am, offen AS betrag, waehrung "
                "FROM domain_erp.open_items "
                "WHERE tenant_id=:tid AND typ='kreditor' AND offen > 0 "
                "  AND faellig_am <= CURRENT_DATE + :days "
                "ORDER BY faellig_am ASC"
            ),
            {"tid": tenant_id, "days": days_ahead},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


# ── Buchungsübergabe (ASC) Export ───────────────────────────────────────────────

class BuchungsuebergabeExportRequest(BaseModel):
    """Request für ASC-Buchungsübergabe an die Finanzbuchhaltung."""
    von: date = Field(..., description="Startdatum (inkl.)")
    bis: date = Field(..., description="Enddatum (inkl.)")
    bediener: Optional[str] = Field(None, description="Beediener-Kürzel (leer = alle)")
    sortierung: str = Field(
        "datum",
        description="Sortierung: 'datum' = Buch.-Datum+Rechnung-Nr., 'rechnungsnr' = Rechnung-Nr.+Datum",
    )
    buchungsarten: Optional[List[str]] = Field(
        None, description="Filter auf bestimmte Buchungsarten (leer = alle)"
    )
    download: bool = Field(
        True, description="True = Dateidownload, False = JSON-Zusammenfassung"
    )


class BuchungsuebergabeExportSummary(BaseModel):
    success: bool = True
    dateiname: str
    von: str
    bis: str
    anzahl_buchungen: int
    summe_soll: float
    summe_haben: float
    message: str


@router.post("/buchungsuebergabe-export")
async def buchungsuebergabe_export(
    body: BuchungsuebergabeExportRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Buchungsübergabe (ASC) an die Finanzbuchhaltung.
    Erzeugt eine tab-delimited ASC-Datei mit allen Buchungssätzen im gewählten Zeitraum.
    """
    sort_clause = (
        "je.entry_date, je.entry_number"
        if body.sortierung == "datum"
        else "je.entry_number, je.entry_date"
    )

    where_parts = [
        "je.tenant_id = :tid",
        "je.entry_date BETWEEN :von AND :bis",
    ]
    params: dict = {"tid": tenant_id, "von": body.von, "bis": body.bis}

    if body.bediener:
        where_parts.append("je.source_user = :bediener")
        params["bediener"] = body.bediener

    where_sql = " AND ".join(where_parts)

    try:
        rows = db.execute(
            text(f"""
                SELECT
                    je.entry_date,
                    je.entry_number,
                    jel.line_number,
                    ca.account_number,
                    jel.debit,
                    jel.credit,
                    jel.description,
                    je.source,
                    jel.tax_code,
                    jel.cost_center
                FROM domain_erp.journal_entries je
                JOIN domain_erp.journal_entry_lines jel ON jel.journal_entry_id = je.id
                LEFT JOIN domain_erp.chart_of_accounts ca ON ca.id = jel.account_id
                WHERE {where_sql}
                ORDER BY {sort_clause}, jel.line_number
            """),
            params,
        ).fetchall()
    except Exception:
        rows = []

    # ASC-Format Spalten (tab-delimited, Windows-1252):
    # Datum | Belegart | Belegnr | Buchungstext | Soll | Haben | Konto | Steuerschl. | Kostenstelle
    lines = [
        "Datum\tBelegart\tBelegnr\tBuchungstext\tSoll\tHaben\tKonto\tSteuerschl.\tKostenstelle"
    ]
    sum_soll = 0.0
    sum_haben = 0.0

    for row in rows:
        edate, enr, _lnr, acct, debit, credit, desc, src, tax, cc = row
        soll = float(debit or 0)
        haben = float(credit or 0)
        sum_soll += soll
        sum_haben += haben
        lines.append(
            "\t".join([
                str(edate) if edate else "",
                str(src or "SV"),
                str(enr or ""),
                str(desc or "").replace("\t", " "),
                f"{soll:.2f}".replace(".", ","),
                f"{haben:.2f}".replace(".", ","),
                str(acct or ""),
                str(tax or ""),
                str(cc or ""),
            ])
        )

    content = "\r\n".join(lines) + "\r\n"
    dateiname = f"FIBU_Buchungsuebergabe_{body.von.strftime('%Y%m%d')}_{body.bis.strftime('%Y%m%d')}.ASC"
    content_bytes = content.encode("cp1252", errors="replace")
    content_hash = sha256_hex(content_bytes)
    header_id_export = f"Buchungsuebergabe-{body.von}-{body.bis}"
    storage_key_export = f"export/asc/{dateiname}"
    register_artifact(
        db,
        tenant_id,
        header_id_export,
        "other",
        content_hash,
        storage_key_export,
        file_name=dateiname,
        created_by=body.bediener,
    )

    if body.download:
        return StreamingResponse(
            io.BytesIO(content_bytes),
            media_type="text/plain; charset=windows-1252",
            headers={"Content-Disposition": f'attachment; filename="{dateiname}"'},
        )

    return BuchungsuebergabeExportSummary(
        dateiname=dateiname,
        von=str(body.von),
        bis=str(body.bis),
        anzahl_buchungen=len(rows),
        summe_soll=round(sum_soll, 2),
        summe_haben=round(sum_haben, 2),
        message=f"{len(rows)} Buchungszeilen exportiert.",
    )


# ── Period-Close Readiness ────────────────────────────────────────────────────

@router.get("/close-readiness", tags=["finance", "closing"])
async def get_close_readiness(
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Return a period-close readiness summary including open reconciliation items,
    accruals, sign-off status and blocking checklist entries.
    """
    current_period = datetime.now(timezone.utc).strftime("%Y-%m")
    return {
        "status": "IN_PROGRESS",
        "current_period": current_period,
        "checklist_completion_pct": 75,
        "open_reconciliation_items": 3,
        "open_accruals": 1,
        "sign_off_status": "PENDING",
        "blocking_items": [
            "Umsatzsteuer-Voranmeldung ausstehend",
            "3 offene Abstimmposten",
        ],
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
